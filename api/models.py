from typing import List, Optional
from pydantic import BaseModel

class SummariseRequest(BaseModel):
    username: str
    repos: List[str]
    days: int = 7

class SummariseResponse(BaseModel):
    id: str
    display: str
    summary: str
    repos: List[str]
    days: int
    username: str
    generated_at: str
    is_public: bool = False

class HistoryRecord(BaseModel):
    id: str
    username: str
    repos: List[str]
    days: int
    summary: str
    generated_at: str

class HistoryResponse(BaseModel):
    summaries: List[HistoryRecord]
    total: int

class RosterRequest(BaseModel):
    name: str
    usernames: List[str]

class RosterResponse(BaseModel):
    id: str
    name: str
    usernames: List[str]
    created_at: str

class TeamSummariseRequest(BaseModel):
    usernames: List[str]
    repos: List[str]
    days: int = 7

class TeamSummariseResponse(BaseModel):
    display: str
    summary: str
    repos: List[str]
    days: int
    contributors: List[str]
    generated_at: str

class SlackDeliverRequest(BaseModel):
    summary: str
    webhook_url: str
    channel: Optional[str] = None

class PublicToggleRequest(BaseModel):
    public: bool

class PublicToggleResponse(BaseModel):
    id: str
    is_public: bool

class PublicSummaryResponse(BaseModel):
    id: str
    username: str
    repos: List[str]
    days: int
    summary: str
    generated_at: str

class CompareRecord(BaseModel):
    commits: int
    prs: int
    issues: int
    active_days: int

class CompareResponse(BaseModel):
    username: str
    days: int
    current: CompareRecord
    previous: CompareRecord
    delta: dict

class RecommendationsRequest(BaseModel):
    username: str
    days: int = 30

class RecommendationsResponse(BaseModel):
    recommendations: str
    generated_at: str

class PromptTemplateCreate(BaseModel):
    username: str
    name: str
    content: str

class PromptTemplateResponse(BaseModel):
    id: str
    username: str
    name: str
    content: str
    created_at: str
