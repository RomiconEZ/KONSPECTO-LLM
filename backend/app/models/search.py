# backend/app/models/search.py
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class SearchRequest(BaseModel):
    query: str = Field(..., example="Find relevant documents about AI")

class SearchItem(BaseModel):
    modified_at: datetime
    file_name: str
    file_id: str
    text: str
    score: float
    start_char_idx: int
    end_char_idx: int

class SearchResult(BaseModel):
    results: List[SearchItem]