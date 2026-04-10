"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Search, Calendar, AlertCircle, GitCommit, GitPullRequest, CircleDot, Activity } from "lucide-react";
import { Area, AreaChart, CartesianGrid, XAxis, YAxis, Tooltip as RechartsTooltip, ResponsiveContainer } from "recharts";
import { fetchComparison, CompareResponse } from "@/lib/api";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { cn } from "@/lib/utils";



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

  const [metricsData, setMetricsData] = useState<{date: string, commits: number, prs: number, issues: number}[]>([]);
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
          fetchComparison(username, days)
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
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="bg-black/40 border-zinc-800">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Commits</CardTitle>
                <GitCommit className="h-4 w-4 text-zinc-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{totalCommits}</div>
              </CardContent>
            </Card>
            <Card className="bg-black/40 border-zinc-800">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Merged PRs</CardTitle>
                <GitPullRequest className="h-4 w-4 text-teal-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{totalPRs}</div>
              </CardContent>
            </Card>
            <Card className="bg-black/40 border-zinc-800">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Closed Issues</CardTitle>
                <CircleDot className="h-4 w-4 text-purple-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{totalIssues}</div>
              </CardContent>
            </Card>
            <Card className="bg-black/40 border-emerald-500/20">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Health Score</CardTitle>
                <Activity className="h-4 w-4 text-emerald-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-emerald-400">{healthData.health_score}/100</div>
              </CardContent>
            </Card>
          </div>

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
                          <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                          <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                        </linearGradient>
                        <linearGradient id="colorPRs" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#14b8a6" stopOpacity={0.3}/>
                          <stop offset="95%" stopColor="#14b8a6" stopOpacity={0}/>
                        </linearGradient>
                        <linearGradient id="colorIssues" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#a855f7" stopOpacity={0.3}/>
                          <stop offset="95%" stopColor="#a855f7" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#3f3f46" vertical={false} />
                      <XAxis dataKey="date" stroke="#a1a1aa" fontSize={12} tickLine={false} axisLine={false} />
                      <YAxis stroke="#a1a1aa" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `${value}`} />
                      <RechartsTooltip 
                        contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '8px' }}
                        itemStyle={{ color: '#e4e4e7' }}
                      />
                      <Area type="monotone" dataKey="commits" stroke="#10b981" fillOpacity={1} fill="url(#colorCommits)" />
                      <Area type="monotone" dataKey="prs" stroke="#14b8a6" fillOpacity={1} fill="url(#colorPRs)" />
                      <Area type="monotone" dataKey="issues" stroke="#a855f7" fillOpacity={1} fill="url(#colorIssues)" />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </TabsContent>
            <TabsContent value="comparison" className="space-y-4">
              {comparisonData && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {(["commits", "prs", "issues", "active_days"] as const).map((key) => {
                    const labels = { commits: "Commits", prs: "Merged PRs", issues: "Closed Issues", active_days: "Active Days" };
                    const icons = { commits: GitCommit, prs: GitPullRequest, issues: CircleDot, active_days: Activity };
                    
                    const deltaValue = comparisonData.delta[key];
                    const isPositive = deltaValue > 0;
                    const isZero = deltaValue === 0;
                    const Icon = icons[key];
                    
                    return (
                      <Card key={key} className="bg-black/40 border-zinc-800">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                          <CardTitle className="text-sm font-medium">{labels[key]}</CardTitle>
                          <Icon className="h-4 w-4 text-zinc-500" />
                        </CardHeader>
                        <CardContent>
                          <div className="flex items-baseline justify-between">
                            <div className="text-2xl font-bold">{comparisonData.current[key]}</div>
                            <div className={cn(
                              "flex items-center text-xs font-bold px-1.5 py-0.5 rounded",
                              isPositive ? "text-emerald-500 bg-emerald-500/10" : 
                              isZero ? "text-zinc-500 bg-zinc-500/10" : "text-rose-500 bg-rose-500/10"
                            )}>
                              {isPositive ? <TrendingUp className="h-3 w-3 mr-1" /> : 
                               isZero ? <Minus className="h-3 w-3 mr-1" /> : <TrendingDown className="h-3 w-3 mr-1" />}
                              {Math.abs(deltaValue)}%
                            </div>
                          </div>
                          <p className="text-[10px] text-zinc-500 mt-2">
                            Prev. period: {comparisonData.previous[key]}
                          </p>
                        </CardContent>
                      </Card>
                    );
                  })}

                </div>
              )}
              {comparisonData && (
                <Card className="bg-black/40 border-zinc-800">
                   <CardHeader>
                      <CardTitle className="text-sm">Why this matters</CardTitle>
                   </CardHeader>
                   <CardContent className="text-xs text-zinc-400">
                      Comparing the last {days} days against the previous {days} day period helps identify momentum shifts. 
                      A positive delta in Active Days often indicates better work-life balance or consistent focus, 
                      while PR delta tracks delivery throughput.
                   </CardContent>
                </Card>
              )}
            </TabsContent>

            <TabsContent value="nerds">
              <Card className="bg-black/40 border-zinc-800">
                <CardHeader>
                  <CardTitle>Health Diagnostics</CardTitle>
                  <CardDescription>Repository stars, forks, and open issues tracking.</CardDescription>
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
        <Suspense fallback={<div className="text-center py-20 text-zinc-400">Loading Insights...</div>}>
          <InsightsContent />
        </Suspense>
      </main>
    </div>
  );
}
