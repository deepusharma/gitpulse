"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { GitCommit, GitPullRequest, CircleDot, Activity } from "lucide-react";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import type { CompareResponse } from "@/lib/api";

interface ComparisonChartProps {
  comparisonData: CompareResponse;
  days: number;
}

type MetricKey = "commits" | "prs" | "issues" | "active_days";

const METRIC_LABELS: Record<MetricKey, string> = {
  commits: "Commits",
  prs: "Merged PRs",
  issues: "Closed Issues",
  active_days: "Active Days",
};

const METRIC_ICONS: Record<MetricKey, React.ComponentType<{ className?: string }>> = {
  commits: GitCommit,
  prs: GitPullRequest,
  issues: CircleDot,
  active_days: Activity,
};

/**
 * Renders a period-over-period comparison grid and a contextual explanation card.
 *
 * @param comparisonData - The current/previous/delta comparison payload from the API.
 * @param days - Number of days in the selected period, used in the explanation copy.
 */
export function ComparisonChart({ comparisonData, days }: ComparisonChartProps) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {(["commits", "prs", "issues", "active_days"] as MetricKey[]).map((key) => {
          const deltaValue = comparisonData.delta[key];
          const isPositive = deltaValue > 0;
          const isZero = deltaValue === 0;
          const Icon = METRIC_ICONS[key];

          return (
            <Card key={key} className="bg-black/40 border-zinc-800">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{METRIC_LABELS[key]}</CardTitle>
                <Icon className="h-4 w-4 text-zinc-500" />
              </CardHeader>
              <CardContent>
                <div className="flex items-baseline justify-between">
                  <div className="text-2xl font-bold">{comparisonData.current[key]}</div>
                  <div
                    className={cn(
                      "flex items-center text-xs font-bold px-1.5 py-0.5 rounded",
                      isPositive
                        ? "text-emerald-500 bg-emerald-500/10"
                        : isZero
                          ? "text-zinc-500 bg-zinc-500/10"
                          : "text-rose-500 bg-rose-500/10"
                    )}
                  >
                    {isPositive ? (
                      <TrendingUp className="h-3 w-3 mr-1" />
                    ) : isZero ? (
                      <Minus className="h-3 w-3 mr-1" />
                    ) : (
                      <TrendingDown className="h-3 w-3 mr-1" />
                    )}
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

      <Card className="bg-black/40 border-zinc-800">
        <CardHeader>
          <CardTitle className="text-sm">Why this matters</CardTitle>
        </CardHeader>
        <CardContent className="text-xs text-zinc-400">
          Comparing the last {days} days against the previous {days} day period helps identify
          momentum shifts. A positive delta in Active Days often indicates better work-life balance
          or consistent focus, while PR delta tracks delivery throughput.
        </CardContent>
      </Card>
    </div>
  );
}
