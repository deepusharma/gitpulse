"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Search,
  Calendar,
  AlertCircle,
  GitCommit,
  GitPullRequest,
  CircleDot,
  Activity,
} from "lucide-react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
} from "recharts";
import { fetchComparison, CompareResponse } from "@/lib/api";
import { MetricCard } from "@/components/insights/MetricCard";
import { ComparisonChart } from "@/components/insights/ComparisonChart";
import { RecommendationsPanel } from "@/components/RecommendationsPanel";

interface HealthData {
  health_score: number;
  total_stars: number;
  total_forks: number;
  total_open_issues: number;
  repos: { repo: string; stars: number; forks: number; open_issues: number }[];
}

function InsightsContent() {
  const { data: session } = useSession();
  const searchParams = useSearchParams();
  const router = useRouter();

  const paramUsername = searchParams?.get("username");
  const paramDays = searchParams?.get("days") || "30";

  const [username, setUsername] = useState(paramUsername || "");
  const [days, setDays] = useState(parseInt(paramDays, 10));
  const [daysInput, setDaysInput] = useState(paramDays);
  const [inputValue, setInputValue] = useState(paramUsername || "");

  const [metricsData, setMetricsData] = useState<
    { date: string; commits: number; prs: number; issues: number }[]
  >([]);
  const [healthData, setHealthData] = useState<HealthData | null>(null);
  const [comparisonData, setComparisonData] = useState<CompareResponse | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (paramUsername) {
      setUsername(paramUsername);
      setInputValue(paramUsername);
    }
  }, [paramUsername]);

  useEffect(() => {
    if (!paramUsername && session?.user?.username) {
      router.replace(`/insights?username=${session.user.username}`);
    }
  }, [session, paramUsername, router]);

  useEffect(() => {
    if (!username) return;

    async function fetchInsights() {
      setLoading(true);
      setError(null);
      try {
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

        const [metricsRes, healthRes, compData] = await Promise.all([
          fetch(`${baseUrl}/insights/metrics?username=${username}&repos=&days=${days}`),
          fetch(`${baseUrl}/insights/health?username=${username}&repos=`),
          fetchComparison(username, days),
        ]);

        if (!metricsRes.ok || !healthRes.ok) {
          throw new Error("Failed to fetch insights data.");
        }

        const mData = await metricsRes.json();
        const hData = await healthRes.json();

        setMetricsData(mData);
        setHealthData(hData);
        setComparisonData(compData);
      } catch (err: unknown) {
        const e = err as Error;
        setError(e.message || "An error occurred");
      } finally {
        setLoading(false);
      }
    }

    fetchInsights();
  }, [username, days]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim()) {
      const d = parseInt(daysInput, 10) || 30;
      setDays(d);
      router.push(`/insights?username=${inputValue.trim()}&days=${d}`);
    }
  };

  const totalCommits = metricsData.reduce((acc, val) => acc + val.commits, 0);
  const totalPRs = metricsData.reduce((acc, val) => acc + val.prs, 0);
  const totalIssues = metricsData.reduce((acc, val) => acc + val.issues, 0);

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-20">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div className="flex-1">
          <h1 className="text-4xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 via-teal-500 to-blue-600">
            Insights
          </h1>
          <p className="text-zinc-400 mt-2 text-lg">
            {username ? `Composite metrics for ${username}.` : "Explore composite tracking."}
          </p>
        </div>

        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 bg-zinc-900/40 p-2 rounded-xl border border-white/5 backdrop-blur-sm">
          <form onSubmit={handleSearch} className="relative flex items-center">
            <Search className="absolute left-3 h-4 w-4 text-zinc-500" />
            <Input
              placeholder="GitHub Username"
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
              onChange={(e) => setDaysInput(e.target.value)}
              onBlur={() => {
                const d = parseInt(daysInput, 10) || 30;
                setDaysInput(String(d));
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
          <AlertTitle>Error Loading Insights</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {loading && (
        <div className="h-64 flex items-center justify-center bg-black/20 rounded-xl border border-white/5">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-500"></div>
        </div>
      )}

      {!loading && username && metricsData.length > 0 && healthData && (
        <div className="space-y-6">
          {/* Summary metric cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <MetricCard title="Total Commits" value={totalCommits} icon={GitCommit} />
            <MetricCard
              title="Merged PRs"
              value={totalPRs}
              icon={GitPullRequest}
              iconClassName="text-teal-500"
            />
            <MetricCard
              title="Closed Issues"
              value={totalIssues}
              icon={CircleDot}
              iconClassName="text-purple-500"
            />
            <MetricCard
              title="Health Score"
              value={`${healthData.health_score}/100`}
              icon={Activity}
              iconClassName="text-emerald-500"
              cardClassName="border-emerald-500/20"
              valueClassName="text-emerald-400"
            />
          </div>

          {/* Tabbed charts */}
          <Tabs defaultValue="velocity" className="space-y-4">
            <TabsList className="bg-zinc-900 border border-zinc-800">
              <TabsTrigger value="velocity">Daily Velocity</TabsTrigger>
              <TabsTrigger value="comparison">Period Comparison</TabsTrigger>
              <TabsTrigger value="nerds">Stats for Nerds</TabsTrigger>
            </TabsList>

            <TabsContent value="velocity" className="space-y-4">
              <Card className="bg-black/40 border-zinc-800">
                <CardHeader>
                  <CardTitle>Composite Activity Trends</CardTitle>
                  <CardDescription>
                    Commits, Pull Requests, and Issues over the last {days} days.
                  </CardDescription>
                </CardHeader>
                <CardContent className="pl-2 h-[400px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart
                      data={metricsData}
                      margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                    >
                      <defs>
                        <linearGradient id="colorCommits" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                        </linearGradient>
                        <linearGradient id="colorPRs" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#14b8a6" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="#14b8a6" stopOpacity={0} />
                        </linearGradient>
                        <linearGradient id="colorIssues" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#a855f7" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="#a855f7" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid
                        strokeDasharray="3 3"
                        stroke="#3f3f46"
                        vertical={false}
                      />
                      <XAxis
                        dataKey="date"
                        stroke="#a1a1aa"
                        fontSize={12}
                        tickLine={false}
                        axisLine={false}
                      />
                      <YAxis
                        stroke="#a1a1aa"
                        fontSize={12}
                        tickLine={false}
                        axisLine={false}
                        tickFormatter={(value) => `${value}`}
                      />
                      <RechartsTooltip
                        contentStyle={{
                          backgroundColor: "#18181b",
                          borderColor: "#27272a",
                          borderRadius: "8px",
                        }}
                        itemStyle={{ color: "#e4e4e7" }}
                      />
                      <Area
                        type="monotone"
                        dataKey="commits"
                        stroke="#10b981"
                        fillOpacity={1}
                        fill="url(#colorCommits)"
                      />
                      <Area
                        type="monotone"
                        dataKey="prs"
                        stroke="#14b8a6"
                        fillOpacity={1}
                        fill="url(#colorPRs)"
                      />
                      <Area
                        type="monotone"
                        dataKey="issues"
                        stroke="#a855f7"
                        fillOpacity={1}
                        fill="url(#colorIssues)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="comparison" className="space-y-4">
              {comparisonData && (
                <ComparisonChart comparisonData={comparisonData} days={days} />
              )}
            </TabsContent>

            <TabsContent value="nerds">
              <Card className="bg-black/40 border-zinc-800">
                <CardHeader>
                  <CardTitle>Health Diagnostics</CardTitle>
                  <CardDescription>
                    Repository stars, forks, and open issues tracking.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="grid grid-cols-3 gap-4 text-center">
                      <div className="bg-zinc-900 p-4 rounded-lg">
                        <div className="text-zinc-400 text-sm mb-1">Total Stars</div>
                        <div className="text-xl font-medium">{healthData.total_stars}</div>
                      </div>
                      <div className="bg-zinc-900 p-4 rounded-lg">
                        <div className="text-zinc-400 text-sm mb-1">Total Forks</div>
                        <div className="text-xl font-medium">{healthData.total_forks}</div>
                      </div>
                      <div className="bg-zinc-900 p-4 rounded-lg">
                        <div className="text-zinc-400 text-sm mb-1">Total Open Issues</div>
                        <div className="text-xl font-medium">{healthData.total_open_issues}</div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          {/* AI Recommendations panel — non-blocking, below charts */}
          <RecommendationsPanel username={username} days={days} />
        </div>
      )}
    </div>
  );
}

export default function InsightsPage() {
  return (
    <div className="py-8 relative">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_#14b8a6_0%,_transparent_25%)] opacity-10 pointer-events-none" />
      <main className="container mx-auto px-4 relative z-10">
        <Suspense
          fallback={<div className="text-center py-20 text-zinc-400">Loading Insights...</div>}
        >
          <InsightsContent />
        </Suspense>
      </main>
    </div>
  );
}
