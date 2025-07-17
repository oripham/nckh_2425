import torch
import re
import pandas as pd
import numpy as np
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from collections import defaultdict

# Properly configure device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Hàm tiền xử lý văn bản
def load_stopwords(file_path):
    with open(file_path, "r", encoding="utf-8") as ins:
        stopwords = [line.strip('\n') for line in ins]
    return set(stopwords)

def filter_stop_words(text, stop_words):
    new_sent = [word for word in text.split() if word not in stop_words]
    return ' '.join(new_sent)

def deEmojify(text):
    regrex_pattern = re.compile(pattern="["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        "]+", flags=re.UNICODE)
    return regrex_pattern.sub(r'', text)

def remove_special_chars_and_numbers(text):
    """
    Remove special characters and numbers if they are adjacent to special characters.
    This function will:
    1. Remove all standalone special characters
    2. Remove numbers connected to special characters
    """
    # First replace special chars that might be legitimate in Vietnamese
    text = re.sub(r'[^\w\s\u00C0-\u1EF9]', ' ', text)  # Keep Vietnamese diacritics
    
    # Remove numbers adjacent to special characters
    text = re.sub(r'[^\w\s\u00C0-\u1EF9]*\d+[^\w\s\u00C0-\u1EF9]*', ' ', text)
    
    # Clean up extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def preprocess_text(text, tokenizer=None, remove_stopwords=False, stopwords=None,
                    remove_emoji=True, lowercase=True, remove_special=True):
    if remove_emoji:
        text = deEmojify(text)
    
    if remove_special:
        text = remove_special_chars_and_numbers(text)
    
    if tokenizer:
        sentences = tokenizer.tokenize(text)
        text = " ".join([" ".join(sentence) for sentence in sentences])
    
    if remove_stopwords and stopwords:
        text = filter_stop_words(text, stopwords)
    
    if lowercase:
        text = text.lower()
    
    return text

# Tải mô hình
def load_sentiment_model(model_path, tokenizer_name="vinai/phobert-base-v2"):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    try:
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, use_fast=False)
        model = AutoModelForSequenceClassification.from_pretrained(
            model_path,
            torch_dtype=torch.float32,  # Explicitly set dtype
            low_cpu_mem_usage=True
        )
        # Move model to device before creating pipeline
        model = model.to(device)
        device_id = 0 if device.type == "cuda" else -1
        sentiment_classifier = pipeline(
            "text-classification",
            model=model,
            tokenizer=tokenizer,
            device=device_id
        )
        return sentiment_classifier, tokenizer
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Falling back to CPU")
        try:
            # Fallback with explicit CPU loading
            tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, use_fast=False)
            model = AutoModelForSequenceClassification.from_pretrained(
                model_path,
                torch_dtype=torch.float32,
                low_cpu_mem_usage=True
            )
            model = model.to("cpu")
            sentiment_classifier = pipeline(
                "text-classification",
                model=model,
                tokenizer=tokenizer,
                device=-1
            )
            return sentiment_classifier, tokenizer
        except Exception as e:
            print(f"Error in CPU fallback: {e}")
            raise



# Alternative to underthesea's word_tokenize
def simple_word_tokenize(text):
    """
    Simple Vietnamese word tokenizer (alternative to underthesea)
    """
    # Split by whitespace
    words = text.split()
    return words

# Alternative to underthesea's pos_tag with simpler rules
def simple_pos_tag(text):
    """
    Simple part-of-speech tagger (alternative to underthesea)
    Uses a rule-based approach for basic tagging
    """
    words = simple_word_tokenize(text)
    # Dictionary of common Vietnamese words with their POS tags
    common_nouns = {'hệ thống', 'trường', 'sinh viên', 'giáo viên', 'học phần', 'thời khóa biểu', 
                    'phòng', 'tòa nhà', 'máy tính', 'thiết bị', 'sách', 'tài liệu'}
    common_verbs = {'đăng ký', 'học', 'dạy', 'làm', 'bị', 'thi', 'kiểm tra', 'đọc', 'viết', 'hiểu'}
    common_adjs = {'tốt', 'xấu', 'hay', 'dở', 'khó', 'dễ', 'mới', 'cũ', 'nhanh', 'chậm', 'lỗi'}
    
    # Simple rule-based POS tagging
    pos_tags = []
    for word in words:
        word_lower = word.lower()
        if word_lower in common_nouns:
            pos_tags.append((word, 'N'))
        elif word_lower in common_verbs:
            pos_tags.append((word, 'V'))
        elif word_lower in common_adjs:
            pos_tags.append((word, 'A'))
        else:
            # Default to noun if unknown
            pos_tags.append((word, 'N'))
    
    return pos_tags

# Simple NER function (alternative to underthesea's ner)
def simple_ner(text):
    """
    Simple named entity recognition function (alternative to underthesea)
    """
    # This is a very simplified version that looks for common patterns
    entities = []
    
    # Look for phrases that might be entities using regex patterns
    # Example: Match potential organization names
    org_pattern = r'(Trường|Đại học|Học viện|Viện|Trung tâm|Khoa|Phòng) [A-ZÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬĐÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴ][a-zàáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ ]+'
    orgs = re.finditer(org_pattern, text)
    for org in orgs:
        entities.append((org.group(), 'ORG', org.start(), org.end()))
    
    return entities

def analyze_words_sentiment_adaptive(text, sentiment_classifier, min_window=3, max_window=7):
    """
    Analyze sentiment of individual words using an adaptive window approach
    """
    words = simple_word_tokenize(text)
    pos_tags = simple_pos_tag(text)
    filtered_words_with_pos = [(word, tag) for word, tag in pos_tags if tag in ('N', 'V', 'A', 'R')]
    filtered_words = [word for word, _ in filtered_words_with_pos]
    word_sentiments = {}

    for i, word in enumerate(words):
        if word not in filtered_words:
            continue
        word_tag = next((tag for w, tag in filtered_words_with_pos if w == word), None)
        if word_tag and word_tag == 'A':
            window_size = min_window
        elif word_tag and word_tag == 'N':
            window_size = (min_window + max_window) // 2
        else:
            window_size = max_window

        start = max(0, i - window_size // 2)
        end = min(len(words), i + window_size // 2 + 1)
        phrase = " ".join(words[start:end])

        try:
            result = sentiment_classifier(phrase)
            label = result[0]["label"]
            score = result[0]["score"]
            sentiment = {"LABEL_0": "Negative", "LABEL_1": "Neutral", "LABEL_2": "Positive"}[label]
            word_sentiments[word] = {
                "sentiment": sentiment,
                "confidence": score,
                "context": phrase
            }
        except Exception as e:
            print(f"⚠️ Bỏ qua cụm '{phrase}' do lỗi: {e}")
            continue

    return word_sentiments

def analyze_phrases_sentiment(text, sentiment_classifier):
    """
    Analyze sentiment of meaningful phrases in the text
    """
    entities = simple_ner(text)
    pos_tags = simple_pos_tag(text)
    phrases = []
    i = 0
    while i < len(pos_tags) - 1:
        word, tag = pos_tags[i]
        if (tag == 'N' and i+1 < len(pos_tags) and pos_tags[i+1][1] == 'A') or \
           (tag == 'A' and i+1 < len(pos_tags) and pos_tags[i+1][1] == 'N'):
            phrases.append(" ".join([pos_tags[i][0], pos_tags[i+1][0]]))
            i += 2
        elif tag == 'V' and i+1 < len(pos_tags) and pos_tags[i+1][1] == 'N':
            phrases.append(" ".join([pos_tags[i][0], pos_tags[i+1][0]]))
            i += 2
        elif (tag == 'V' and i+1 < len(pos_tags) and pos_tags[i+1][1] == 'R') or \
             (tag == 'R' and i+1 < len(pos_tags) and pos_tags[i+1][1] == 'V'):
            phrases.append(" ".join([pos_tags[i][0], pos_tags[i+1][0]]))
            i += 2
        elif tag == 'R' and i+1 < len(pos_tags) and pos_tags[i+1][1] == 'A':
            phrases.append(" ".join([pos_tags[i][0], pos_tags[i+1][0]]))
            i += 2
        else:
            if tag in ('N', 'V', 'A') and len(word) > 1:
                phrases.append(word)
            i += 1

    for entity in entities:
        if isinstance(entity, tuple) and len(entity) >= 3:
            entity_text = entity[0]
            if len(entity_text.split()) > 1:
                phrases.append(entity_text)

    phrases = list(set(phrases))
    phrase_sentiments = {}
    for phrase in phrases:
        try:
            result = sentiment_classifier(phrase)
            label = result[0]["label"]
            score = result[0]["score"]
            sentiment = {"LABEL_0": "Negative", "LABEL_1": "Neutral", "LABEL_2": "Positive"}[label]
            if score > 0.7 and sentiment != "Neutral":
                phrase_sentiments[phrase] = {
                    "sentiment": sentiment,
                    "confidence": score
                }
        except Exception as e:
            print(f"⚠️ Bỏ qua cụm '{phrase}' do lỗi: {e}")
            continue

    return phrase_sentiments

def extract_sentiment_words(text, sentiment_classifier, threshold=0.75):
    """
    Extract sentiment-charged words from the text
    """
    processed_text = preprocess_text(text, remove_emoji=True, lowercase=True)
    word_sentiments = analyze_words_sentiment_adaptive(processed_text, sentiment_classifier)
    phrase_sentiments = analyze_phrases_sentiment(processed_text, sentiment_classifier)
    all_sentiment_items = {}

    for word, data in word_sentiments.items():
        if data["confidence"] >= threshold:
            all_sentiment_items[word] = data

    for phrase, data in phrase_sentiments.items():
        if data["confidence"] >= threshold:
            all_sentiment_items[phrase] = data

    positive_items = {k: v for k, v in all_sentiment_items.items() if v["sentiment"] == "Positive"}
    negative_items = {k: v for k, v in all_sentiment_items.items() if v["sentiment"] == "Negative"}
    neutral_items = {k: v for k, v in all_sentiment_items.items() if v["sentiment"] == "Neutral"}

    positive_items = dict(sorted(positive_items.items(), key=lambda x: x[1]["confidence"], reverse=True))
    negative_items = dict(sorted(negative_items.items(), key=lambda x: x[1]["confidence"], reverse=True))
    neutral_items = dict(sorted(neutral_items.items(), key=lambda x: x[1]["confidence"], reverse=True))

    return {
        "positive": positive_items,
        "negative": negative_items,
        "neutral": neutral_items
    }

