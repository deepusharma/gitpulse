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
  username: string;
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
  constructor(
    message: string,
    public status: number,
    public traceback?: string | null,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function generateSummary(
  req: SummariseRequest,
  refresh: boolean = false
): Promise<SummariseResponse> {
  const response = await fetch(`${API_URL}/summarise?refresh=${refresh}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    // Backend returns { detail: { error: "...", code: N, traceback: "..." } }
    // or { detail: [{ msg: "..." }] } for Pydantic validation errors
    const detail = body.detail;
    const message =
      (typeof detail === "object" && !Array.isArray(detail) && detail?.error) ||
      (Array.isArray(detail) && detail[0]?.msg) ||
      body.error ||
      "Failed to generate summary.";
    const traceback =
      typeof detail === "object" && !Array.isArray(detail)
        ? detail?.traceback
        : null;
    throw new ApiError(message, response.status, traceback);
  }
  return response.json();
}


export async function fetchHistory(
  username: string, 
  limit: number = 20,
  search?: string,
  startDate?: string,
  endDate?: string
): Promise<HistoryResponse> {
  let url = `${API_URL}/history?username=${encodeURIComponent(username)}&limit=${limit}`;
  if (search) url += `&search=${encodeURIComponent(search)}`;
  if (startDate) url += `&start_date=${encodeURIComponent(startDate)}`;
  if (endDate) url += `&end_date=${encodeURIComponent(endDate)}`;

  const response = await fetch(url, {
    method: "GET",
    headers: { "Content-Type": "application/json" }
  });
  if (!response.ok) {
    throw new Error("Failed to fetch history");
  }
  return response.json();
}

export async function validateUser(username: string): Promise<{ valid: boolean; avatar_url?: string; error?: string }> {
  const response = await fetch(`${API_URL}/github/validate?username=${encodeURIComponent(username)}`);
  if (!response.ok) return { valid: false, error: "Validation failed" };
  return response.json();
}

export async function fetchUserRepos(username: string): Promise<{ repos: string[] }> {
  const response = await fetch(`${API_URL}/github/repos?username=${encodeURIComponent(username)}`);
  if (!response.ok) return { repos: [] };
  return response.json();
}
