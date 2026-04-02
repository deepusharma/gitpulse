"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import CommitFrequencyChart from "@/components/analytics/CommitFrequencyChart";
import RepoActivityChart from "@/components/analytics/RepoActivityChart";
import InsightsPanel, { InsightsData } from "@/components/analytics/InsightsPanel";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { AlertCircle, Search, Calendar, ChevronDown, ChevronUp } from "lucide-react";

interface AnalyticsError {
  message: string;
  traceback?: string | null;
}

function AnalyticsContent() {
  const { data: session } = useSession();
  const searchParams = useSearchParams();
  const router = useRouter();

  // Get initial state from URL params
  const paramUsername = searchParams?.get("username");
  const paramDays = searchParams?.get("days") || "30";

  const [username, setUsername] = useState(paramUsername || "");
  const [days, setDays] = useState(parseInt(paramDays, 10));
  const [daysInput, setDaysInput] = useState(paramDays);
  const [inputValue, setInputValue] = useState(paramUsername || "");

  const [commitsData, setCommitsData] = useState([]);
  const [repoData, setRepoData] = useState([]);
  const [insightsData, setInsightsData] = useState<InsightsData | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<AnalyticsError | null>(null);
  const [showTrace, setShowTrace] = useState(false);

  // Sync state with URL params
  useEffect(() => {
    if (paramUsername) {
      setUsername(paramUsername);
      setInputValue(paramUsername);
    }
  }, [paramUsername]);

  // Handle Default Username from Session if params are missing
  useEffect(() => {
    if (!paramUsername && session?.user?.username) {
      router.replace(`/analytics?username=${session.user.username}`);
    }
  }, [session, paramUsername, router]);

  useEffect(() => {
    if (!username) {
      setLoading(false);
      return;
    }

    async function fetchAnalytics() {
      setLoading(true);
      setError(null);
      setShowTrace(false);
      try {
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const res = await fetch(`${baseUrl}/analytics/all?username=${username}&days=${days}`);

        if (!res.ok) {
          const body = await res.json().catch(() => ({}));
          const detail = body.detail;
          const message =
            (typeof detail === "object" && !Array.isArray(detail) && detail?.error) ||
            (Array.isArray(detail) && detail[0]?.msg) ||
            body.error ||
            `Request failed (${res.status})`;
          const traceback =
            typeof detail === "object" && !Array.isArray(detail) ? detail?.traceback : null;
          throw Object.assign(new Error(message), { traceback });
        }

        const data = await res.json();
        setCommitsData(data.commits_per_day);
        setRepoData(data.repos_breakdown);
        setInsightsData(data.insights);
      } catch (err: unknown) {
        const e = err as Error & { traceback?: string | null };
        setError({ message: e.message || "An error occurred", traceback: e.traceback });
      } finally {
        setLoading(false);
      }
    }

    fetchAnalytics();
  }, [username, days]);

  const handleDaysChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value.replace(/^0+(?=\d)/, "");
    if (raw === "" || /^\d+$/.test(raw)) setDaysInput(raw);
  };

  const commitDays = () => {
    const n = parseInt(daysInput, 10);
    return isNaN(n) || n < 1 ? 30 : Math.min(n, 90);
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim()) {
      const d = commitDays();
      setDays(d);
      setDaysInput(String(d));
      router.push(`/analytics?username=${inputValue.trim()}&days=${d}`);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-20">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div className="flex-1">
          <h1 className="text-4xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 via-teal-500 to-blue-600">
            Analytics
          </h1>
          <p className="text-zinc-400 mt-2 text-lg">
            {username ? `Insight metrics for ${username}.` : "Connect your pulse."}
          </p>
        </div>
        
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 bg-zinc-900/40 p-2 rounded-xl border border-white/5 backdrop-blur-sm">
           <form onSubmit={handleSearch} className="relative flex items-center">
              <Search className="absolute left-3 h-4 w-4 text-zinc-500" />
              <Input
                placeholder="User/Org Username"
                className="pl-9 bg-black/40 border-zinc-800 text-sm h-10 w-full sm:w-48"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
              />
           </form>

           <div className="flex items-center gap-2 border-l border-zinc-800 pl-3">
              <Calendar className="h-4 w-4 text-zinc-500" />
              <Input
                inputMode="numeric"
                pattern="[0-9]*"
                placeholder="30"
                value={daysInput}
                onChange={handleDaysChange}
                onBlur={() => {
                  const d = commitDays();
                  setDaysInput(String(d));
                  setDays(d);
                }}
                className="bg-black/40 border-zinc-800 h-10 w-20 text-sm"
              />
              <span className="text-xs text-zinc-500 font-medium whitespace-nowrap">Days</span>
           </div>
        </div>
      </div>

      {error && (
        <Alert variant="destructive" className="border-red-500/50 bg-red-500/10 text-red-200">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle className="flex items-center justify-between">
            <span>Error Loading Analytics</span>
            {error.traceback && (
              <button
                type="button"
                onClick={() => setShowTrace((v) => !v)}
                className="flex items-center gap-1 text-xs font-normal underline underline-offset-2 opacity-80 hover:opacity-100"
              >
                {showTrace ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
                {showTrace ? "Hide details" : "Show details"}
              </button>
            )}
          </AlertTitle>
          <AlertDescription className="space-y-2">
            <p>{error.message}</p>
            {error.traceback && showTrace && (
              <pre className="mt-2 max-h-40 overflow-auto rounded bg-black/40 p-2 text-xs text-red-200 whitespace-pre-wrap">
                {error.traceback}
              </pre>
            )}
          </AlertDescription>
        </Alert>
      )}

      {!username && !loading && !session?.user?.username && (
        <div className="text-center py-20 border border-dashed border-white/10 rounded-2xl bg-black/20 backdrop-blur-sm group hover:border-emerald-500/20 transition-colors">
          <div className="bg-emerald-500/10 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
             <Search className="h-8 w-8 text-emerald-500" />
          </div>
          <h3 className="text-xl font-semibold mb-2">No User Targeted</h3>
          <p className="text-zinc-400 max-w-sm mx-auto px-4">
            Enter a GitHub username or Organization above to visualize their git activity dashboard.
          </p>
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
    <div className="py-8 relative">
       {/* Background gradients managed by RootLayout's theme but adding subtle page-specific polish */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_#10b981_0%,_transparent_25%)] opacity-10 pointer-events-none" />
      
      <main className="container mx-auto px-4 relative z-10">
        <Suspense fallback={<div className="text-center py-20 text-zinc-400">Syncing Dashboard...</div>}>
          <AnalyticsContent />
        </Suspense>
      </main>
    </div>
  );
}
