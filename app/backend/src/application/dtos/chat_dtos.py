from pydantic import BaseModel
from typing import List


class ChatRequest(BaseModel):
    session_id: str
    question: str

class SourceReference(BaseModel):
    file: str
    uri: str
    pages: List[int] = []

class ChatResponse(BaseModel):
    answer: str
    session_id: str
    sources: List[SourceReference] = []

