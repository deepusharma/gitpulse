"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import CommitFrequencyChart from "@/components/analytics/CommitFrequencyChart";
import RepoActivityChart from "@/components/analytics/RepoActivityChart";
import InsightsPanel, { InsightsData } from "@/components/analytics/InsightsPanel";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertCircle } from "lucide-react";

function AnalyticsContent() {
  const searchParams = useSearchParams();
  const username = searchParams?.get("username");
  const fallbackDays = searchParams?.get("days") || "30";
  const [days, setDays] = useState(parseInt(fallbackDays, 10));

  const [commitsData, setCommitsData] = useState([]);
  const [repoData, setRepoData] = useState([]);
  const [insightsData, setInsightsData] = useState<InsightsData | null>(null);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!username) {
      setLoading(false);
      return;
    }

    async function fetchAnalytics() {
      setLoading(true);
      setError("");
      try {
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        
        const [commitsRes, reposRes, insightsRes] = await Promise.all([
          fetch(`${baseUrl}/analytics/commits-per-day?username=${username}&days=${days}`),
          fetch(`${baseUrl}/analytics/repos-breakdown?username=${username}&days=${days}`),
          fetch(`${baseUrl}/analytics/insights?username=${username}&days=${days}`)
        ]);

        if (!commitsRes.ok || !reposRes.ok || !insightsRes.ok) {
            throw new Error("Failed to fetch analytics data");
        }

        const commits = await commitsRes.json();
        const repos = await reposRes.json();
        const insights = await insightsRes.json();

        setCommitsData(commits);
        setRepoData(repos);
        setInsightsData(insights);
      } catch (err: any) {
        setError(err.message || "An error occurred");
      } finally {
        setLoading(false);
      }
    }

    fetchAnalytics();
  }, [username, days]);

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 to-blue-500">
            Analytics Dashboard
          </h1>
          <p className="text-zinc-400 mt-1">
            {username ? `Deep dive into ${username}'s recent git pulse.` : "Please provide a username in the URL to view analytics."}
          </p>
        </div>
        
        {username && (
          <div className="flex items-center gap-3">
            <span className="text-sm text-zinc-400">Lookback window:</span>
            <select 
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              className="bg-black/50 border border-white/10 text-white rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-emerald-500"
            >
              <option value={7}>Last 7 Days</option>
              <option value={14}>Last 14 Days</option>
              <option value={30}>Last 30 Days</option>
              <option value={90}>Last 90 Days</option>
            </select>
          </div>
        )}
      </div>

      {error && (
        <Alert variant="destructive" className="border-red-500/50 bg-red-500/10 text-red-200">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error Loading Analytics</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {!username && !loading && (
        <div className="text-center py-20 border border-dashed border-white/20 rounded-xl bg-black/40">
          <p className="text-zinc-400">You must provide a username parameter (e.g. ?username=deepusharma) to view this page.</p>
        </div>
      )}

      {username && (
        <div className="space-y-6">
          {/* Top Row: Commits Per Day */}
          <div className="w-full relative">
            {loading && (
              <div className="absolute inset-0 z-10 flex items-center justify-center bg-black/60 backdrop-blur-sm rounded-xl border border-white/5">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-500"></div>
              </div>
            )}
            <CommitFrequencyChart data={commitsData} />
          </div>

          {/* Bottom Row: 2 columns */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 relative">
             {loading && (
              <div className="absolute inset-0 z-10 flex items-center justify-center bg-black/60 backdrop-blur-sm rounded-xl border border-white/5">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-500"></div>
              </div>
            )}
            <RepoActivityChart data={repoData} />
            <InsightsPanel data={insightsData} />
          </div>
        </div>
      )}
    </div>
  );
}

export default function AnalyticsPage() {
  return (
    <div className="min-h-screen bg-black text-gray-100 selection:bg-emerald-500/30 font-sans flex flex-col">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_#10b981_0%,_transparent_25%)] opacity-20 pointer-events-none" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom_left,_#3b82f6_0%,_transparent_25%)] opacity-10 pointer-events-none" />

      <Header />

      <main className="flex-grow container mx-auto px-4 py-8 relative z-10">
        <Suspense fallback={<div className="text-center py-20 text-zinc-400">Loading Dashboard Context...</div>}>
          <AnalyticsContent />
        </Suspense>
      </main>

      <Footer />
    </div>
  );
}
