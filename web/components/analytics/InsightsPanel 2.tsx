import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Flame, Trophy, Calendar, Hash } from "lucide-react";

export type InsightsData = {
  most_active_day: string;
  streak: number;
  top_repo: string;
  total_summaries: number;
  average_commits_per_day: number;
}

export default function InsightsPanel({ data }: { data: InsightsData | null }) {
  if (!data) {
    return (
      <div className="grid grid-cols-2 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i} className="border-white/10 bg-black/40 backdrop-blur-md h-32 flex items-center justify-center text-zinc-500">
            Loading...
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 gap-4">
      <Card className="border-white/10 bg-black/40 backdrop-blur-md flex flex-col justify-center">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium text-zinc-400">Longest Streak</CardTitle>
          <Flame className="h-4 w-4 text-orange-500" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-white">{data.streak} Days</div>
        </CardContent>
      </Card>
      
      <Card className="border-white/10 bg-black/40 backdrop-blur-md flex flex-col justify-center overflow-hidden">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium text-zinc-400">Top Repository</CardTitle>
          <Trophy className="h-4 w-4 text-yellow-500 min-w-4" />
        </CardHeader>
        <CardContent>
          <div className="text-lg font-bold text-white truncate" title={data.top_repo}>{data.top_repo}</div>
        </CardContent>
      </Card>

      <Card className="border-white/10 bg-black/40 backdrop-blur-md flex flex-col justify-center">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium text-zinc-400">Most Active Day</CardTitle>
          <Calendar className="h-4 w-4 text-blue-500" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-white">{data.most_active_day}</div>
        </CardContent>
      </Card>
      
      <Card className="border-white/10 bg-black/40 backdrop-blur-md flex flex-col justify-center">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium text-zinc-400">Avg. Commits/Day</CardTitle>
          <Hash className="h-4 w-4 text-emerald-500" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-white">{data.average_commits_per_day}</div>
        </CardContent>
      </Card>
    </div>
  );
}
