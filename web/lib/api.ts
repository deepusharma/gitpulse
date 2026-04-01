export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface SummariseRequest {
  username: string;
  repos: string[];
  days: number;
}

export interface SummariseResponse {
  display: string;
  summary: string;
  repos: string[];
  days: number;
  generated_at: string;
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

export class ApiError extends Error {
  constructor(message: string, public status: number) {
    super(message);
    this.name = "ApiError";
  }
}

export async function generateSummary(
  req: SummariseRequest,
): Promise<SummariseResponse> {
  const response = await fetch(`${API_URL}/summarise`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    const message = error.error || error.detail?.[0]?.msg || "Failed to generate summary";
    throw new ApiError(message, response.status);
  }
  return response.json();
}

export async function fetchHistory(username: string, limit: number = 20): Promise<HistoryResponse> {
  const response = await fetch(`${API_URL}/history?username=${encodeURIComponent(username)}&limit=${limit}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" }
  });
  if (!response.ok) {
    throw new Error("Failed to fetch history");
  }
  return response.json();
}
