import type { PublicProfile } from "@/types/profile";

interface ProfileStatsProps {
  profile: PublicProfile;
}

interface StatCardProps {
  label: string;
  value: string | number;
  subtitle?: string;
  highlight?: boolean;
}

function StatCard({ label, value, subtitle, highlight }: StatCardProps) {
  return (
    <div
      className={`flex flex-col gap-1 p-4 rounded-xl border ${
        highlight
          ? "border-primary/40 bg-primary/5"
          : "border-border bg-card"
      }`}
    >
      <span className="text-xs text-muted-foreground uppercase tracking-wider font-medium">
        {label}
      </span>
      <span
        className={`text-3xl font-bold tabular-nums ${
          highlight ? "text-primary" : "text-foreground"
        }`}
      >
        {value}
      </span>
      {subtitle && (
        <span className="text-xs text-muted-foreground">{subtitle}</span>
      )}
    </div>
  );
}

export function ProfileStats({ profile }: ProfileStatsProps) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <StatCard
        label="Current Streak"
        value={`${profile.current_streak}d`}
        subtitle="consecutive days"
        highlight={profile.current_streak > 0}
      />
      <StatCard
        label="Longest Streak"
        value={`${profile.longest_streak}d`}
        subtitle="all time best"
      />
      <StatCard
        label="Health Score"
        value={`${profile.health_score}/100`}
        subtitle="activity health"
        highlight={profile.health_score >= 70}
      />
      <StatCard
        label="Standups"
        value={profile.total_summaries}
        subtitle="total generated"
      />
    </div>
  );
}
