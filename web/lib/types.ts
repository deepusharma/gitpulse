export interface SummariseRequest {
  username: string;
  repos: string[];
  days: number;
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
    top_repo: string;
    total_summaries: number;
    average_commits_per_day: number;
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
