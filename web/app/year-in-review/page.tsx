"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  Trophy, 
  Calendar, 
  GitCommit, 
  Zap, 
  ArrowLeft,
  Share2,
  Sparkles
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  Cell
} from "recharts";
import { fetchYearInReview } from "@/lib/api";
import { YearInReviewResponse } from "@/lib/types";

function YearInReviewContent() {
  const { data: session } = useSession();
  const searchParams = useSearchParams();
  const router = useRouter();
  const username = searchParams?.get("username") || session?.user?.username;
  const year = parseInt(searchParams?.get("year") || String(new Date().getFullYear()), 10);

  const [data, setData] = useState<YearInReviewResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!username) return;

    async function loadData() {
      setLoading(true);
      try {
        const res = await fetchYearInReview(username, year);
        setData(res);
      } catch (err: any) {
        setError(err.message || "Failed to load your Year in Review.");
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [username, year]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <Sparkles className="h-12 w-12 text-emerald-500 animate-pulse" />
        <p className="text-zinc-400 animate-pulse">Reliving your code journey for {year}...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="max-w-md mx-auto text-center py-20 space-y-6">
        <div className="bg-red-500/10 p-6 rounded-2xl border border-red-500/20">
          <h2 className="text-xl font-bold text-red-200 mb-2">No data for {year}</h2>
          <p className="text-zinc-400">{error || "We couldn't find enough activity to generate your review."}</p>
        </div>
        <Button variant="outline" onClick={() => router.back()}>
          <ArrowLeft className="mr-2 h-4 w-4" /> Go Back
        </Button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-12 pb-20">
      {/* Header section */}
      <div className="text-center space-y-4 pt-10">
        <Badge variant="outline" className="px-4 py-1 border-emerald-500/30 text-emerald-400 bg-emerald-500/5">
          {year} YEAR IN REVIEW
        </Badge>
        <h1 className="text-5xl md:text-7xl font-black tracking-tighter bg-clip-text text-transparent bg-gradient-to-b from-white to-zinc-500">
          {username}
        </h1>
        <p className="text-zinc-400 text-lg max-w-lg mx-auto italic">
          "{data.ai_wrap_up.split('.')[0]}."
        </p>
      </div>

      {/* Main stats grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="bg-zinc-900/40 border-white/5 backdrop-blur-xl relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
            <GitCommit className="h-24 w-24 text-emerald-500" />
          </div>
          <CardHeader>
            <CardTitle className="text-emerald-400 flex items-center gap-2">
              <Zap className="h-5 w-5" /> Activity
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <div className="text-6xl font-black text-white">{data.total_stats.summaries}</div>
              <div className="text-zinc-400 font-medium">Standups Generated</div>
            </div>
            <div className="pt-4 border-t border-white/5 grid grid-cols-2 gap-4">
              <div>
                <div className="text-2xl font-bold text-white">{data.total_stats.unique_repos}</div>
                <div className="text-zinc-500 text-xs uppercase tracking-widest">Repositories</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-white">{data.busiest_day.count}</div>
                <div className="text-zinc-500 text-xs uppercase tracking-widest">Peak Daily Commits</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-zinc-900/40 border-white/5 backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="text-purple-400 flex items-center gap-2">
              <Trophy className="h-5 w-5" /> Top Projects
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {data.top_repos.map((repo, idx) => (
                <div key={repo.name} className="flex items-center justify-between p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
                  <div className="flex items-center gap-3">
                    <span className="text-zinc-600 font-bold">{idx + 1}</span>
                    <span className="font-medium text-zinc-200">{repo.name}</span>
                  </div>
                  <Badge variant="secondary" className="bg-zinc-800 text-zinc-300">
                    {repo.count}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Monthly chart */}
      <Card className="bg-zinc-900/40 border-white/5 backdrop-blur-xl">
        <CardHeader>
          <CardTitle className="text-teal-400 flex items-center gap-2">
            <Calendar className="h-5 w-5" /> Monthly Consistency
          </CardTitle>
        </CardHeader>
        <CardContent className="h-[300px] pl-0">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data.monthly_breakdown}>
              <CartesianGrid strokeDasharray="3 3" stroke="#ffffff05" vertical={false} />
              <XAxis dataKey="month" stroke="#71717a" fontSize={12} tickLine={false} axisLine={false} />
              <YAxis hide />
              <RechartsTooltip 
                cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                contentStyle={{ backgroundColor: '#18181b', borderColor: '#ffffff10', borderRadius: '12px' }}
              />
              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                {data.monthly_breakdown.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.count > 0 ? '#10b981' : '#27272a'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* AI Summary card */}
      <div className="bg-gradient-to-br from-emerald-500/20 via-teal-500/10 to-transparent p-8 rounded-3xl border border-emerald-500/20 relative overflow-hidden">
        <Sparkles className="absolute top-8 right-8 h-12 w-12 text-emerald-500/20" />
        <h3 className="text-2xl font-bold text-white mb-4">Your Year in Focus</h3>
        <div className="prose prose-invert max-w-none text-zinc-300 leading-relaxed">
          {data.ai_wrap_up.split('\n').map((para, i) => (
            <p key={i} className="mb-4">{para}</p>
          ))}
        </div>
      </div>

      <div className="flex justify-center gap-4 pt-10">
        <Button onClick={() => window.print()} className="bg-emerald-600 hover:bg-emerald-500 text-white rounded-full px-8">
          <Share2 className="mr-2 h-4 w-4" /> Share Review
        </Button>
        <Button variant="outline" onClick={() => router.push('/insights')} className="rounded-full px-8 border-white/10 hover:bg-white/5">
           Back to Insights
        </Button>
      </div>
    </div>
  );
}

export default function YearInReviewPage() {
  return (
    <div className="min-h-screen bg-black text-white selection:bg-emerald-500/30">
      <div className="fixed inset-0 bg-[radial-gradient(circle_at_50%_50%,_#10b98110_0%,_transparent_50%)] pointer-events-none" />
      <main className="container mx-auto px-4 relative z-10">
        <Suspense fallback={<div className="text-center py-20 text-zinc-400">Preparing your review...</div>}>
          <YearInReviewContent />
        </Suspense>
      </main>
    </div>
  );
}
