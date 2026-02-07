"""
Demo: Phan tich cam xuc, chu de va tom tat van ban tieng Viet
Su dung API tu HuggingFace Space hoac chay model local

Cach dung:
  # Che do API (mac dinh - chi can cai requests):
  python demo.py "Truong dai hoc co so vat chat rat tot"

  # Che do local (can tai model tu Dropbox):
  python demo.py --local "Truong dai hoc co so vat chat rat tot"
"""

import argparse
import json
import sys

# ============================================================
# CAU HINH
# ============================================================
API_BASE = "https://oripham-npl-ml-backend.hf.space"

TOPIC_MAP = {
    "LABEL_0": "Co so vat chat (facility)",
    "LABEL_1": "Giang vien (lecturer)",
    "LABEL_2": "Sinh vien (student)",
    "LABEL_3": "Chuong trinh dao tao (program)",
}


# ============================================================
# CHE DO 1: GOI API HUGGINGFACE SPACE
# ============================================================

def build_post_request(text):
    """Tao PostRequest object cho API."""
    return {
        "text": text,
        "url": "https://example.com",
        "likes": 0,
        "comments": 0,
        "shares": 0,
        "time": "2024-01-01T00:00:00Z",
    }


def api_sentiment(text):
    """Goi POST /sentiment - phan tich cam xuc."""
    import requests

    payload = [build_post_request(text)]
    resp = requests.post(f"{API_BASE}/sentiment", json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()

    # Xac dinh nhan sentiment
    if text in data.get("positive", []):
        return "Positive (Tich cuc)"
    elif text in data.get("negative", []):
        return "Negative (Tieu cuc)"
    else:
        return "Neutral (Trung lap)"


def api_summary(text):
    """Goi POST /school-summary-2 - tom tat trich xuat."""
    import requests

    payload = [build_post_request(text)]
    resp = requests.post(f"{API_BASE}/school-summary-2", json=payload, timeout=120)
    resp.raise_for_status()
    return resp.text.strip().strip('"')


def api_posts_with_topic():
    """Goi GET /posts - lay posts co topic tu DB."""
    import requests

    resp = requests.get(f"{API_BASE}/posts", params={"limit": 5}, timeout=120)
    resp.raise_for_status()
    return resp.json()


def analyze_via_api(text):
    """Goi API HuggingFace Space de phan tich van ban."""
    print("  Dang goi API sentiment...")
    sentiment = api_sentiment(text)

    print("  Dang goi API summary...")
    try:
        summary = api_summary(text)
    except Exception as e:
        summary = f"(Loi khi goi API: {e})"

    return {
        "sentiment": sentiment,
        "summary": summary,
    }


# ============================================================
# CHE DO 2: CHAY MODEL LOCAL
# ============================================================

def analyze_local(text):
    """Chay model multi-task PhoBERT truc tiep tren may."""
    try:
        import torch
        from transformers import AutoTokenizer
    except ImportError:
        print("Loi: Can cai them thu vien de chay local:")
        print("  pip install torch transformers")
        sys.exit(1)

    # Them duong dan be/ de import model
    sys.path.insert(0, "be")
    try:
        from models.multitask_model import MultiTaskPhoBERT
    except ImportError:
        print("Loi: Khong tim thay file model. Hay tai model tu Dropbox")
        print("va dat vao thu muc be/")
        sys.exit(1)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_path = "be/mtl_phobert.pth"

    print(f"  Dang tai model tu {model_path} ...")
    tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base", use_fast=False)
    checkpoint = torch.load(model_path, map_location=device)
    model = MultiTaskPhoBERT()

    if isinstance(checkpoint, dict):
        if "state_dict" in checkpoint:
            model.load_state_dict(checkpoint["state_dict"])
        elif "model_state_dict" in checkpoint:
            model.load_state_dict(checkpoint["model_state_dict"])
        else:
            model.load_state_dict(checkpoint)
    elif isinstance(checkpoint, torch.nn.Module):
        model = checkpoint

    model.to(device)
    model.eval()

    # Tokenize
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    sentiment_labels = ["Negative (Tieu cuc)", "Neutral (Trung lap)", "Positive (Tich cuc)"]

    with torch.no_grad():
        # Sentiment
        sent_logits = model(**inputs, task_name="sentiment")
        sent_probs = torch.softmax(sent_logits, dim=-1)[0]
        sent_idx = sent_probs.argmax().item()

        # Topic
        topic_logits = model(**inputs, task_name="topic")
        topic_probs = torch.softmax(topic_logits, dim=-1)[0]
        topic_idx = topic_probs.argmax().item()

        # Summary
        summ_logits = model(**inputs, task_name="summary")
        summ_probs = torch.softmax(summ_logits, dim=-1)[0]

    return {
        "sentiment": f"{sentiment_labels[sent_idx]} ({sent_probs[sent_idx]:.2%})",
        "topic": f"{TOPIC_MAP.get(f'LABEL_{topic_idx}', 'unknown')} ({topic_probs[topic_idx]:.2%})",
        "summary_score": f"{summ_probs[1]:.2%}",
    }


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Demo phan tich cam xuc, chu de & tom tat van ban tieng Viet"
    )
    parser.add_argument("text", help="Cau van ban can phan tich")
    parser.add_argument(
        "--local",
        action="store_true",
        help="Chay model tren may thay vi goi API",
    )
    args = parser.parse_args()

    print(f"\n[INPUT] Van ban: {args.text}\n")
    print("=" * 55)

    if args.local:
        print("[MODE] LOCAL (chay model tren may)\n")
        result = analyze_local(args.text)
        print(f"  [Sentiment] Cam xuc    : {result['sentiment']}")
        print(f"  [Topic]     Chu de     : {result['topic']}")
        print(f"  [Summary]   Diem TT    : {result['summary_score']}")
    else:
        print("[MODE] API (goi HuggingFace Space)")
        print(f"  Base URL: {API_BASE}\n")
        result = analyze_via_api(args.text)
        print(f"\n  [Sentiment] Cam xuc    : {result['sentiment']}")
        print(f"  [Summary]   Tom tat    : {result['summary']}")
        print(f"\n  Luu y: Topic chi kha dung khi chay model local (--local)")

    print("\n" + "=" * 55)
    print("[DONE] Hoan tat!\n")


if __name__ == "__main__":
    main()
