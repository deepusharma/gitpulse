export interface PublicProfile {
  username: string;
  avatar_url: string;
  bio: string | null;
  recent_summary: string | null;
  current_streak: number;
  longest_streak: number;
  top_repos: string[];
  health_score: number;
  total_summaries: number;
  generated_at: string;
}
