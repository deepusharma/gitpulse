from typing import List, Optional, Literal
from pydantic import BaseModel

class SummariseRequest(BaseModel):
    username: str
    repos: List[str]
    days: int = 7
    tone: str = "professional"
    language: str = "English"

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

class EmailDeliverRequest(BaseModel):
    to: str
    summary: str

class GistDeliverRequest(BaseModel):
    summary: str
    is_public: bool = False

class GistDeliverResponse(BaseModel):
    url: str

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


class AdminStatsResponse(BaseModel):
    total_summaries: int
    unique_users: int
    summaries_last_n_days: int
    top_repos: List[dict]
    error_rate_pct: float
    generated_at: str


class PublicProfileResponse(BaseModel):
    username: str
    avatar_url: str
    bio: Optional[str]
    recent_summary: Optional[str]
    current_streak: int
    longest_streak: int
    top_repos: List[str]
    health_score: int
    total_summaries: int
    generated_at: str

class DigestScheduleRequest(BaseModel):
    username: str
    enabled: bool = True
    frequency: Literal["daily", "weekly"]
    hour_utc: int
    day_of_week: Optional[int] = None
    channel: Literal["email", "slack"]
    email_to: Optional[str] = None
    slack_webhook: Optional[str] = None
    repos: List[str]
    days: int = 7
    tone: str = "professional"
    language: str = "English"

class DigestScheduleResponse(BaseModel):
    id: str
    username: str
    enabled: bool
    frequency: str
    hour_utc: int
    day_of_week: Optional[int]
    channel: str
    repos: List[str]
    days: int
    last_sent_at: Optional[str]
    created_at: str
