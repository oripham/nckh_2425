from typing import List, Optional
import os
import csv
import json

from fastapi import FastAPI, HTTPException

from openai import OpenAI
from dotenv import load_dotenv
from datetime import date, datetime, timedelta, timezone
from fastapi.middleware.cors import CORSMiddleware

from dateutil.parser import parse

from models import PostRequest

# Import the functions directly from utils.py
from untils import *

from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

# Load API key from .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY_3")

# MODEL = "deepseek/deepseek-chat-v3-0324:free"
# MODEL = "google/gemini-2.5-pro-exp-03-25:free"
MODEL = "meta-llama/llama-4-maverick:free"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENAI_API_KEY,
)

app = FastAPI()

origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sentiment constants
POS = "Tích cực"
NEG = "Tiêu cực"
NEU = "Trung lập"

# Topic mapping
topic_labels = {
    "LABEL_0": "facility",
    "LABEL_1": "lecturer",
    "LABEL_2": "others",
    "LABEL_3": "training_program"
}


class Post():
    def __init__(self, text):
        if POS in text:
            self.sentiment = POS
        elif NEG in text:
            self.sentiment = NEG
        else:
            self.sentiment = NEU

        self.sentences = [
            sentence.strip() for sentence in text.split(";") if sentence.strip()]
        self.sentences[0] = text.split("Các câu văn nổi bật:")[-1].strip()


def get_data(path):
    # path = "Utc2Confessions.csv"
    posts = []
    with open(f"data/{path}", mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                row['text'] = row.pop('Text')
                row['likes'] = int(row['Likes'])
                row['comments'] = int(row['Comments'])
                row['shares'] = int(row['Shares'])
                row['time'] = datetime.fromisoformat(
                    row['Time'].replace("Z", "+00:00"))
                row['url'] = row['URL']

                post = PostRequest(**row)
                posts.append(post)
            except Exception as e:
                continue
    return posts


@app.get("/posts")
async def get_posts(page: Optional[int] = 1,
                    limit: Optional[int] = 10,
                    selected_page: Optional[int] = None,
                    topic: Optional[str] = None,
                    tag: Optional[str] = None,
                    start_date: Optional[str] = None,
                    end_date: Optional[str] = None):
    try:
        # Initialize with empty list in case of errors
        all_posts = []
        
        try:
            # Get initial data
            all_posts = get_data("Utc2Confessions.csv")
            print(f"Loaded {len(all_posts)} posts initially")
        except Exception as e:
            print(f"Error loading initial data: {e}")
            return {
                "message": "Error loading posts",
                "total": 0,
                "page": page,
                "limit": limit,
                "posts": []
            }

        # Pages
        if selected_page is not None:
            try:
                page_mapping = {
                    0: "Utc2Confessions.csv",
                    1: "Utc2NoiChiaSeCamXuc.csv",
                    2: "Utc2Zone.csv",
                    3: "DienDanNgheSVNoi.csv",
                }
                if selected_page in page_mapping:
                    all_posts = get_data(page_mapping[selected_page])
                    print(f"Loaded {len(all_posts)} posts from page {selected_page}")
            except Exception as e:
                print(f"Error loading page data: {e}")

        # For backward compatibility, use tag parameter if provided and topic is not
        search_term = tag if tag and not topic else None

        # Filter by tag if that's what we're using (old method)
        if search_term:
            all_posts = [post for post in all_posts if search_term in post.text]
            print(f"After tag filtering: {len(all_posts)} posts")

        # Load topic model for all posts
        topic_model, topic_tokenizer, device = load_topic_model()
        
        # Add topic information to each post
        if topic_model and topic_tokenizer:
            for post in all_posts:
                result = analyze_topic(post.text, topic_model, topic_tokenizer, device)
                if result:
                    # Create a new PostRequest with the topic
                    post_dict = post.dict()
                    post_dict["topic"] = result["topic"]
                    all_posts[all_posts.index(post)] = PostRequest(**post_dict)
                else:
                    # Create a new PostRequest with default topic
                    post_dict = post.dict()
                    post_dict["topic"] = "LABEL_2"  # Default to "student" if analysis fails
                    all_posts[all_posts.index(post)] = PostRequest(**post_dict)

        # Filter by topic if provided (new method)
        if topic:
            try:
                print(f"Filtering by topic: {topic}")
                filtered_posts = [post for post in all_posts if post.topic == topic]
                all_posts = filtered_posts
                print(f"After topic filtering: {len(filtered_posts)} posts")
            except Exception as e:
                print(f"Error filtering by topic: {e}")

        # Date filtering with improved error handling and date parsing
        if start_date:
            try:
                # Parse the start date string to datetime with timezone
                start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
                # Set time to beginning of day and add timezone
                start_datetime = start_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
                start_datetime = start_datetime.replace(tzinfo=timezone.utc)
                print(f"Start date: {start_datetime}")
                
                filtered_posts = []
                for post in all_posts:
                    if post.time >= start_datetime:
                        filtered_posts.append(post)
                
                all_posts = filtered_posts
                print(f"After start date filtering: {len(filtered_posts)} posts")
            except ValueError as e:
                print(f"Invalid start date format: {e}")
            except Exception as e:
                print(f"Error filtering by start date: {e}")

        if end_date:
            try:
                # Parse the end date string to datetime with timezone
                end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
                # Set time to end of day and add timezone
                end_datetime = end_datetime.replace(hour=23, minute=59, second=59, microsecond=999999)
                end_datetime = end_datetime.replace(tzinfo=timezone.utc)
                print(f"End date: {end_datetime}")
                
                filtered_posts = []
                for post in all_posts:
                    if post.time <= end_datetime:
                        filtered_posts.append(post)
                
                all_posts = filtered_posts
                print(f"After end date filtering: {len(filtered_posts)} posts")
            except ValueError as e:
                print(f"Invalid end date format: {e}")
            except Exception as e:
                print(f"Error filtering by end date: {e}")

        # Calculate pagination
        try:
            start_idx = (page - 1) * limit
            end_idx = start_idx + limit
            paginated_posts = all_posts[start_idx:end_idx]
            print(f"Final paginated results: {len(paginated_posts)} posts")
        except Exception as e:
            print(f"Error in pagination: {e}")
            paginated_posts = all_posts[:limit]  # Fallback to first page

        return {
            "message": "Get posts successfully",
            "total": len(all_posts),
            "page": page,
            "limit": limit,
            "posts": paginated_posts
        }
    except Exception as e:
        print(f"Unexpected error in get_posts: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/sentiment")
def sentiment_post(request: Optional[List[PostRequest]] = None):
    try:
        # Load data from Utc2Confessions.csv if no request body is provided
        if not request:
            request = get_data("Utc2Confessions.csv")

        # Load the sentiment analysis model
        model_path = "fine_tuned_model"  # Path to your fine-tuned model
        sentiment_classifier, tokenizer = load_sentiment_model(model_path)

        # Load stopwords if needed
        stopwords_path = "data/vietnamese-stopwords.txt"  # Path to stopwords file
        stopwords = load_stopwords(stopwords_path)

        # Initialize result arrays
        positive_sentences = []
        negative_sentences = []
        neutral_sentences = []

        for post in request:
            # Preprocess the text with special character and number removal
            processed_text = preprocess_text(
                post.text,
                remove_emoji=True,
                lowercase=True,
                remove_stopwords=True,
                stopwords=stopwords,
                remove_special=True  # Enable special character and number removal
            )

            # Run the processed text through the sentiment model
            try:
                result = sentiment_classifier(
                    processed_text, truncation=True, max_length=100)
                label = result[0]["label"]
                sentiment = {"LABEL_0": "negative",
                             "LABEL_1": "neutral", "LABEL_2": "positive"}[label]

                # Add the sentence to the corresponding array
                if sentiment == "positive":
                    # Original text for display
                    positive_sentences.append(post.text)
                elif sentiment == "negative":
                    # Original text for display
                    negative_sentences.append(post.text)
                else:
                    # Original text for display
                    neutral_sentences.append(post.text)
            except Exception as e:
                print(f"⚠️ Error analyzing sentence '{processed_text}': {e}")
                continue

        # Return the results
        return {
            "positive": positive_sentences,
            "negative": negative_sentences,
            "neutral": neutral_sentences
        }

    except Exception as e:
        return {"error": str(e)}


@app.post("/word-analysis")
def word_analysis(request: PostRequest):
    try:
        # Load the sentiment analysis model
        model_path = "fine_tuned_model"
        sentiment_classifier, tokenizer = load_sentiment_model(model_path)

        # Load stopwords
        stopwords_path = "data/vietnamese-stopwords.txt"
        stopwords = load_stopwords(stopwords_path)

        # Preprocess the input text
        processed_text = preprocess_text(
            request.text,
            remove_emoji=True,
            lowercase=True,
            remove_stopwords=True,
            stopwords=stopwords,
            remove_special=True
        )

        # Extract sentiment words/phrases from the single text
        sentiment_words = extract_sentiment_words(
            processed_text, sentiment_classifier)

        # Trả kết quả sắp xếp theo độ tin cậy
        return {
            "positive": dict(sorted(sentiment_words["positive"].items(), key=lambda x: x[1]["confidence"], reverse=True)),
            "negative": dict(sorted(sentiment_words["negative"].items(), key=lambda x: x[1]["confidence"], reverse=True)),
            "neutral": dict(sorted(sentiment_words["neutral"].items(), key=lambda x: x[1]["confidence"], reverse=True)),
        }

    except Exception as e:
        return {"error": str(e)}


@app.post("/school-summary")
def summarize_shool(request: List[PostRequest]):

    system_prompt = """
    Bạn là một quản trị viên trường học. Bạn sẽ được cung cấp nhiều đoạn văn phản ánh từ sinh viên về tình hình của trường.

    Nhiệm vụ của bạn là đọc và phân tích các đoạn này để viết một đoạn tổng kết ngắn gọn (dưới 200 từ) nêu lên
    tình hình chung của trường — bao gồm điểm tích cực, điểm tiêu cực nếu có, và xu hướng chung.

    Định dạng đầu ra:
    Một đoạn văn bán tóm tắt, mang tính khái quát tình hình gần đây của trường học.

    Ví dụ:
    Trường thời gian gần đây có nhiều hoạt động sôi nổi thu hút sinh viên, các hoạt động ngoại khoá ...
    Tuy nhiên, vẫn còn một số vấn đề tồn tại như ...

    Chỉ trả về đoạn văn đúng định dạng, không thêm giải thích hoặc bất kỳ thông tin nào khác.
    """

    content = ""
    for post in request:
        content += post.text
        content += "/n"

    user_prompt = f"""
        Bạn chỉ có thông tin sau và không hỏi thêm bất cứ điều gì.
        Nội dung các bài đăng trên Facebook: {content}
        Hãy phân tích và trả lời đúng theo định dạng đã cho, không thêm giải thích.
        """

    # completion = client.chat.completions.create(
    #     model=MODEL,
    #     messages=[
    #         {"role": "system", "content": system_prompt},{"role": "user", "content": user_prompt},
    #     ]
    # )

    # return completion.choices[0].message.content
    return "Trường có nhiều hoạt động nổi bật và thành công, đặc biệt là trong công tác giảng dạy và tổ chức các sự kiện ngoại khóa. Các giáo viên luôn tận tâm và sáng tạo trong phương pháp giảng dạy, giúp học sinh hiểu bài tốt hơn và đạt kết quả cao trong các kỳ thi. Tuy nhiên, một số vấn đề cũng cần phải cải thiện, chẳng hạn như cơ sở vật chất còn thiếu thốn và một số lớp học chưa được trang bị đầy đủ thiết bị học tập hiện đại. Ngoài ra, việc quản lý thời gian và lịch học còn đôi lúc chưa hợp lý, khiến học sinh cảm thấy áp lực. Mặc dù vậy, tinh thần học tập của học sinh vẫn rất tốt, và các hoạt động ngoại khóa đã giúp các em phát triển kỹ năng giao tiếp và làm việc nhóm. Trường cần tiếp tục phát huy điểm mạnh và khắc phục những điểm yếu để tạo ra một môi trường học tập ngày càng tốt hơn."


@app.get("/post/{post_id}")
def get_post_by_id(post_id: int):
    try:
        # Load data from CSV file
        all_posts = get_data("Utc2Confessions.csv")

        # Check if post_id is within range
        if post_id < 0 or post_id >= len(all_posts):
            raise HTTPException(status_code=404, detail="Post not found")

        # Return the post at the specified index
        return all_posts[post_id]
    except IndexError:
        raise HTTPException(status_code=404, detail="Post not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sentiment-trend")
async def get_sentiment_trend(start_date: Optional[str] = None, end_date: Optional[str] = None, topic: Optional[str] = None):
    try:
        # Load data from CSV file
        all_posts = get_data("Utc2Confessions.csv")
        print(f"Loaded {len(all_posts)} posts for sentiment trend")

        # Load the sentiment analysis model
        model_path = "fine_tuned_model"
        sentiment_classifier, tokenizer = load_sentiment_model(model_path)
        if not sentiment_classifier or not tokenizer:
            raise Exception("Failed to load sentiment model")

        # Load stopwords
        stopwords_path = "data/vietnamese-stopwords.txt"
        stopwords = load_stopwords(stopwords_path)

        # Sort posts by time
        all_posts.sort(key=lambda post: post.time)

        # Parse date parameters
        if start_date:
            try:
                start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
                start_datetime = start_datetime.replace(tzinfo=timezone.utc)
            except ValueError as e:
                print(f"Invalid start date format: {e}")
                start_datetime = datetime.now(timezone.utc) - timedelta(days=365)
        else:
            # Default to 1 year ago
            start_datetime = datetime.now(timezone.utc) - timedelta(days=365)

        if end_date:
            try:
                end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
                end_datetime = end_datetime.replace(hour=23, minute=59, second=59, microsecond=999999)
                end_datetime = end_datetime.replace(tzinfo=timezone.utc)
            except ValueError as e:
                print(f"Invalid end date format: {e}")
                end_datetime = datetime.now(timezone.utc)
        else:
            # Default to now
            end_datetime = datetime.now(timezone.utc)

        print(f"Date range: {start_datetime} to {end_datetime}")

        # Filter posts within the time period
        relevant_posts = [
            post for post in all_posts 
            if start_datetime <= post.time <= end_datetime
        ]
        print(f"Found {len(relevant_posts)} posts in date range")

        # Filter by topic if provided
        if topic:
            try:
                # Load topic model
                topic_model, topic_tokenizer, device = load_topic_model()
                if topic_model and topic_tokenizer:
                    filtered_posts = []
                    for post in relevant_posts:
                        result = analyze_topic(post.text, topic_model, topic_tokenizer, device)
                        if result and result["topic"] == topic:
                            filtered_posts.append(post)
                    relevant_posts = filtered_posts
                    print(f"After topic filtering: {len(relevant_posts)} posts")
            except Exception as e:
                print(f"Error in topic filtering: {e}")

        # Group posts by month
        monthly_data = {}
        for post in relevant_posts:
            try:
                # Get the month key (format: "MM/YYYY")
                month_key = post.time.strftime("%m/%Y")
                
                # Initialize the month data if it doesn't exist
                if month_key not in monthly_data:
                    monthly_data[month_key] = {
                        "Positive": 0, "Negative": 0, "Neutral": 0
                    }

                # Analyze sentiment
                processed_text = preprocess_text(
                    post.text,
                    remove_emoji=True,
                    lowercase=True,
                    remove_stopwords=True,
                    stopwords=stopwords,
                    remove_special=True
                )

                result = sentiment_classifier(
                    processed_text, truncation=True, max_length=100)
                label = result[0]["label"]
                sentiment = {"LABEL_0": "Negative",
                             "LABEL_1": "Neutral", "LABEL_2": "Positive"}[label]

                # Increment the sentiment counter
                monthly_data[month_key][sentiment] += 1
            except Exception as e:
                print(f"Error processing post: {e}")
                continue

        # Convert to the required format and sort by date
        result = []
        for month, counts in monthly_data.items():
            try:
                # Convert month key to display format
                month_date = datetime.strptime(month, "%m/%Y")
                display_month = month_date.strftime("%m/%Y")
                
                result.append({
                    "day": display_month,
                    "Positive": counts["Positive"],
                    "Negative": counts["Negative"],
                    "Neutral": counts["Neutral"]
                })
            except Exception as e:
                print(f"Error formatting month data: {e}")
                continue

        # Sort by date (ascending)
        result.sort(key=lambda x: datetime.strptime(x["day"], "%m/%Y"))

        return {
            "message": "Sentiment trend data retrieved successfully",
            "data": result
        }
    except Exception as e:
        print(f"Error in sentiment trend: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def load_topic_model():
    try:
        # Kiểm tra CUDA availability
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device for topic model: {device}")
        
        # Load model với device cụ thể
        model = AutoModelForSequenceClassification.from_pretrained(
            "topic_model",
            num_labels=4,  # 4 topics: facility, lecturer, student, program
            device_map=device
        )
        model.eval()  # Set model to evaluation mode
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base-v2", use_fast=False)
        
        return model, tokenizer, device
    except Exception as e:
        print(f"Error loading topic model: {str(e)}")
        return None, None, None

def analyze_topic(text, model, tokenizer, device):
    try:
        if model is None or tokenizer is None:
            print("Topic model or tokenizer is not loaded")
            return None
            
        # Tokenize và chuyển sang tensor
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=100)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Thực hiện inference
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=1)
            
            # Chuyển về CPU trước khi chuyển sang numpy
            probabilities = probabilities.cpu().numpy()[0]
            
            # Lấy nhãn có xác suất cao nhất
            topic = np.argmax(probabilities)
            confidence = float(probabilities[topic])
            
            # Map topic index to label
            topic_labels = {
                0: "LABEL_0",  # facility
                1: "LABEL_1",  # lecturer
                2: "LABEL_2",  # student
                3: "LABEL_3"   # program
            }
            
            return {
                "topic": topic_labels[topic],
                "confidence": confidence,
                "probabilities": probabilities.tolist()
            }
    except Exception as e:
        print(f"Error analyzing topic: {str(e)}")
        return None
