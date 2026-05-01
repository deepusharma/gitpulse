import type {
  SummariseRequest,
  SummariseResponse,
  HistoryResponse,
  PublicSummaryResponse,
  CompareResponse,
  RosterRequest,
  RosterResponse,
  TeamSummariseRequest,
  TeamSummariseResponse,
  RecommendationsRequest,
  RecommendationsResponse,
  PromptTemplate,
  PromptTemplateCreate,
} from "./types";
export { ApiError } from "./types";

export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function generateSummary(
  req: SummariseRequest,
  refresh: boolean = false,
  token?: string
): Promise<SummariseResponse> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) {
    headers["X-GitHub-Token"] = token;
  }

  const response = await fetch(`${API_URL}/summarise?refresh=${refresh}`, {
    method: "POST",
    headers,
    body: JSON.stringify(req),
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
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

export async function togglePublicSummary(id: string, isPublic: boolean): Promise<{ id: string; is_public: boolean }> {
  const response = await fetch(`${API_URL}/history/${id}/public`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ public: isPublic }),
  });
  if (!response.ok) throw new Error("Failed to toggle public status");
  return response.json();
}

export async function fetchPublicSummary(id: string): Promise<PublicSummaryResponse> {
  const response = await fetch(`${API_URL}/summary/public/${id}`);
  if (!response.ok) throw new Error("Public summary not found");
  return response.json();
}

export async function fetchComparison(username: string, days: number = 30): Promise<CompareResponse> {
  const response = await fetch(`${API_URL}/analytics/compare?username=${encodeURIComponent(username)}&days=${days}`);
  if (!response.ok) throw new Error("Failed to fetch comparison data");
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

// --- Sprint 15: Team & Reach ---

export async function createRoster(req: RosterRequest): Promise<RosterResponse> {
  const response = await fetch(`${API_URL}/team/roster`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!response.ok) throw new Error("Failed to create roster");
  return response.json();
}

export async function listRosters(): Promise<RosterResponse[]> {
  const response = await fetch(`${API_URL}/team/rosters`);
  if (!response.ok) throw new Error("Failed to list rosters");
  return response.json();
}

export async function getRoster(id: string): Promise<RosterResponse> {
  const response = await fetch(`${API_URL}/team/roster/${id}`);
  if (!response.ok) throw new Error("Failed to get roster");
  return response.json();
}

export async function deleteRoster(id: string): Promise<{ status: string }> {
  const response = await fetch(`${API_URL}/team/roster/${id}`, { method: "DELETE" });
  if (!response.ok) throw new Error("Failed to delete roster");
  return response.json();
}

export async function generateTeamSummary(req: TeamSummariseRequest): Promise<TeamSummariseResponse> {
  const response = await fetch(`${API_URL}/team/summarise`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail || "Failed to generate team summary");
  }
  return response.json();
}

export async function deliverSlack(summary: string, webhookUrl: string, channel?: string): Promise<{ ok: boolean }> {
  const response = await fetch(`${API_URL}/deliver/slack`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ summary, webhook_url: webhookUrl, channel }),
  });
  if (!response.ok) throw new Error("Failed to deliver to Slack");
  return response.json();
}

export async function deliverEmail(summary: string, to: string): Promise<{ ok: boolean; id: string }> {
  const response = await fetch(`${API_URL}/deliver/email`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ summary, to }),
  });
  if (!response.ok) throw new Error("Failed to deliver Email");
  return response.json();
}

export async function deliverGist(summary: string, isPublic: boolean, token?: string): Promise<{ url: string }> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) {
    headers["X-GitHub-Token"] = token;
  }
  const response = await fetch(`${API_URL}/deliver/gist`, {
    method: "POST",
    headers,
    body: JSON.stringify({ summary, is_public: isPublic }),
  });
  if (!response.ok) throw new Error("Failed to create Gist");
  return response.json();
}

// --- Sprint 17: AI Recommendations & Prompt Templates ---

export async function fetchRecommendations(
  req: RecommendationsRequest
): Promise<RecommendationsResponse> {
  const response = await fetch(`${API_URL}/insights/recommendations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!response.ok) throw new Error("Failed to fetch recommendations");
  return response.json();
}

export async function listPromptTemplates(username: string): Promise<PromptTemplate[]> {
  const response = await fetch(
    `${API_URL}/prompt-templates?username=${encodeURIComponent(username)}`
  );
  if (!response.ok) throw new Error("Failed to list templates");
  return response.json();
}

export async function createPromptTemplate(
  req: PromptTemplateCreate
): Promise<PromptTemplate> {
  const response = await fetch(`${API_URL}/prompt-templates`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!response.ok) throw new Error("Failed to create template");
  return response.json();
}

export async function deletePromptTemplate(id: string): Promise<void> {
  const response = await fetch(`${API_URL}/prompt-templates/${id}`, {
    method: "DELETE",
  });
  if (!response.ok) throw new Error("Failed to delete template");
}

export async function fetchAnalyticsFull(
  username: string,
  days: number = 30,
  refresh: boolean = false
): Promise<any> {
  const response = await fetch(
    `${API_URL}/analytics/all?username=${encodeURIComponent(username)}&days=${days}&refresh=${refresh}`
  );
  if (!response.ok) throw new Error("Failed to fetch full analytics");
  return response.json();
}

export async function fetchYearInReview(
  username: string,
  year?: number
): Promise<any> {
  let url = `${API_URL}/analytics/year-in-review?username=${encodeURIComponent(username)}`;
  if (year) url += `&year=${year}`;
  const response = await fetch(url);
  if (!response.ok) throw new Error("Failed to fetch year in review");
  return response.json();
}

