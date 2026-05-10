interface RecentSummaryCardProps {
  summary: string | null;
}

export function RecentSummaryCard({ summary }: RecentSummaryCardProps) {
  if (!summary) {
    return (
      <div className="p-4 rounded-xl border border-border bg-card text-sm text-muted-foreground">
        No public standups yet.
      </div>
    );
  }

  return (
    <div className="p-4 rounded-xl border border-border bg-card">
      <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-3">
        Latest Public Standup
      </h2>
      <pre className="text-sm text-foreground whitespace-pre-wrap font-mono leading-relaxed max-h-64 overflow-y-auto scrollbar-thin">
        {summary}
      </pre>
    </div>
  );
}
