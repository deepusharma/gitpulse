export interface SummariseRequest {
  username: string;
  repos: string[];
  days: number;
  tone?: string;
  language?: string;
}

export interface SummariseResponse {
  id: string;
  display: string;
  summary: string;
  repos: string[];
  username: string;
  days: number;
  generated_at: string;
  is_public: boolean;
}

export interface HistoryRecord {
  id: string;
  username: string;
  repos: string[];
  days: number;
  summary: string;
  generated_at: string;
}

export interface HistoryResponse {
  summaries: HistoryRecord[];
  total: number;
}

export interface PublicSummaryResponse {
  id: string;
  username: string;
  repos: string[];
  days: number;
  summary: string;
  generated_at: string;
}

export interface CompareRecord {
  commits: number;
  prs: number;
  issues: number;
  active_days: number;
}

export interface CompareResponse {
  username: string;
  days: number;
  current: CompareRecord;
  previous: CompareRecord;
  delta: {
    commits: number;
    prs: number;
    issues: number;
    active_days: number;
  };
}

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public traceback?: string | null,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export interface RosterRequest {
  name: string;
  usernames: string[];
}

export interface RosterResponse {
  id: string;
  name: string;
  usernames: string[];
  created_at: string;
}

export interface TeamSummariseRequest {
  usernames: string[];
  repos: string[];
  days: number;
}

export interface TeamSummariseResponse {
  display: string;
  summary: string;
  repos: string[];
  days: number;
  contributors: string[];
  generated_at: string;
}

export interface RecommendationsRequest {
  username: string;
  days: number;
}

export interface RecommendationsResponse {
  recommendations: string;
  generated_at: string;
}

export interface PromptTemplate {
  id: string;
  username: string;
  name: string;
  content: string;
  created_at: string;
}

export interface PromptTemplateCreate {
  username: string;
  name: string;
  content: string;
}

export interface AnalyticsFullResponse {
  commits_per_day: { date: string; count: number }[];
  repos_breakdown: { repo: string; count: number; percentage: number }[];
  insights: {
    most_active_day: string;
    streak: number;
    longest_streak: number;
    top_repo: string;
    total_summaries: number;
    average_commits_per_day: number;
    health_score: number;
  };
  last_updated: string;
}

export interface YearInReviewResponse {
  username: string;
  year: number;
  total_stats: {
    summaries: number;
    unique_repos: number;
  };
  top_repos: { name: string; count: number }[];
  monthly_breakdown: { month: string; count: number }[];
  busiest_day: {
    date: string;
    count: number;
  };
  ai_wrap_up: string;
}

export interface DigestScheduleRequest {
  username: string;
  enabled?: boolean;
  frequency: "daily" | "weekly";
  hour_utc: number;
  day_of_week?: number;
  channel: "email" | "slack";
  email_to?: string;
  slack_webhook?: string;
  repos: string[];
  days: number;
  tone?: string;
  language?: string;
}

export interface DigestSchedule {
  id: string;
  username: string;
  enabled: boolean;
  frequency: "daily" | "weekly";
  hour_utc: number;
  day_of_week?: number;
  channel: "email" | "slack";
  email_to?: string;
  slack_webhook?: string;
  repos: string[];
  days: number;
  last_sent_at?: string;
  created_at: string;
}
