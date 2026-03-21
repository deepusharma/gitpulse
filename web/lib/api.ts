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

export async function generateSummary(
  req: SummariseRequest,
): Promise<SummariseResponse> {
  const response = await fetch(`${API_URL}/summarise`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || error.detail?.[0]?.msg || "Failed to generate summary");
  }
  return response.json();
}
