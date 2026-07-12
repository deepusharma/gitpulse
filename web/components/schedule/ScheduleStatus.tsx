import { DigestSchedule } from "@/lib/types";

export function ScheduleStatus({ schedule }: { schedule: DigestSchedule | null }) {
  if (!schedule) {
    return (
      <div className="text-sm text-muted-foreground">
        No schedule configured.
      </div>
    );
  }

  const daysMap = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  
  return (
    <div className="space-y-3 text-sm">
      <div className="flex justify-between">
        <span className="text-muted-foreground">Status</span>
        <span className={schedule.enabled ? "text-green-500 font-medium" : "text-amber-500 font-medium"}>
          {schedule.enabled ? "Active" : "Disabled"}
        </span>
      </div>
      <div className="flex justify-between">
        <span className="text-muted-foreground">Frequency</span>
        <span className="capitalize">
          {schedule.frequency} 
          {schedule.frequency === "weekly" && ` on ${daysMap[schedule.day_of_week ?? 0]}`}
          {' at '}{String(schedule.hour_utc).padStart(2, '0')}:00 UTC
        </span>
      </div>
      <div className="flex justify-between">
        <span className="text-muted-foreground">Channel</span>
        <span className="capitalize">{schedule.channel}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-muted-foreground">Target</span>
        <span className="truncate max-w-[150px]">{schedule.channel === "email" ? schedule.email_to : schedule.slack_webhook}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-muted-foreground">Last Sent</span>
        <span>
          {schedule.last_sent_at ? new Date(schedule.last_sent_at).toLocaleString() : "Never"}
        </span>
      </div>
    </div>
  );
}
