from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional


class PostRequest(BaseModel):
    text: str
    url: HttpUrl
    likes: int
    comments: int
    shares: int
    time: datetime
    topic: Optional[str] = None


class BatchPostRequest(BaseModel):
    texts: list[PostRequest]
