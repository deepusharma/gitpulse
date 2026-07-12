"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { DigestSchedule, DigestScheduleRequest } from "@/lib/types";
import { saveSchedule, deleteSchedule } from "@/lib/api";

export function ScheduleForm({
  username,
  initialSchedule,
}: {
  username: string;
  initialSchedule: DigestSchedule | null;
}) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [enabled, setEnabled] = useState(initialSchedule?.enabled ?? true);
  const [frequency, setFrequency] = useState<"daily" | "weekly">(initialSchedule?.frequency ?? "daily");
  const [hourUtc, setHourUtc] = useState(initialSchedule?.hour_utc ?? 12);
  const [dayOfWeek, setDayOfWeek] = useState(initialSchedule?.day_of_week ?? 0);
  const [channel, setChannel] = useState<"email" | "slack">(initialSchedule?.channel ?? "email");
  const [emailTo, setEmailTo] = useState(initialSchedule?.email_to ?? "");
  const [slackWebhook, setSlackWebhook] = useState(initialSchedule?.slack_webhook ?? "");
  const [repos, setRepos] = useState(initialSchedule?.repos?.join(", ") ?? "");
  const [days, setDays] = useState(initialSchedule?.days ?? 7);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const req: DigestScheduleRequest = {
        username,
        enabled,
        frequency,
        hour_utc: hourUtc,
        day_of_week: frequency === "weekly" ? dayOfWeek : undefined,
        channel,
        email_to: channel === "email" ? emailTo : undefined,
        slack_webhook: channel === "slack" ? slackWebhook : undefined,
        repos: repos.split(",").map((r) => r.trim()).filter(Boolean),
        days,
      };
      await saveSchedule(req);
      router.refresh();
    } catch (err) {
      console.error(err);
      alert("Failed to save schedule.");
    } finally {
      setLoading(false);
    }
  }

  async function onDelete() {
    if (!confirm("Are you sure you want to delete this schedule?")) return;
    setLoading(true);
    try {
      await deleteSchedule(username);
      router.refresh();
    } catch (err) {
      console.error(err);
      alert("Failed to delete schedule.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <div className="flex items-center gap-2">
        <input type="checkbox" id="enabled" checked={enabled} onChange={(e) => setEnabled(e.target.checked)} className="h-4 w-4" />
        <label htmlFor="enabled" className="text-sm font-medium">Enable schedule</label>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Frequency</label>
          <select value={frequency} onChange={(e) => setFrequency(e.target.value as "daily" | "weekly")} className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Hour (UTC)</label>
          <input type="number" min="0" max="23" value={hourUtc} onChange={(e) => setHourUtc(Number(e.target.value))} className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
        </div>
      </div>

      {frequency === "weekly" && (
        <div>
          <label className="block text-sm font-medium mb-1">Day of Week</label>
          <select value={dayOfWeek} onChange={(e) => setDayOfWeek(Number(e.target.value))} className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
            <option value={0}>Monday</option>
            <option value={1}>Tuesday</option>
            <option value={2}>Wednesday</option>
            <option value={3}>Thursday</option>
            <option value={4}>Friday</option>
            <option value={5}>Saturday</option>
            <option value={6}>Sunday</option>
          </select>
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Channel</label>
          <select value={channel} onChange={(e) => setChannel(e.target.value as "email" | "slack")} className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
            <option value="email">Email</option>
            <option value="slack">Slack</option>
          </select>
        </div>
        {channel === "email" ? (
          <div>
            <label htmlFor="emailTo" className="block text-sm font-medium mb-1">Email Address</label>
            <input id="emailTo" type="email" value={emailTo} onChange={(e) => setEmailTo(e.target.value)} required className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
          </div>
        ) : (
          <div>
            <label htmlFor="slackWebhook" className="block text-sm font-medium mb-1">Slack Webhook URL</label>
            <input id="slackWebhook" type="url" value={slackWebhook} onChange={(e) => setSlackWebhook(e.target.value)} required className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
          </div>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Repositories (comma separated)</label>
        <input type="text" value={repos} onChange={(e) => setRepos(e.target.value)} placeholder="repo1, repo2" required className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Lookback Days</label>
        <input type="number" min="1" max="30" value={days} onChange={(e) => setDays(Number(e.target.value))} className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
      </div>

      <div className="flex gap-4 pt-4">
        <button type="submit" disabled={loading} className="bg-primary text-primary-foreground hover:bg-primary/90 px-4 py-2 rounded-md text-sm font-medium transition-colors">
          {loading ? "Saving..." : "Save Schedule"}
        </button>
        {initialSchedule && (
          <button type="button" onClick={onDelete} disabled={loading} className="border border-destructive text-destructive hover:bg-destructive/10 px-4 py-2 rounded-md text-sm font-medium transition-colors">
            Delete
          </button>
        )}
      </div>
    </form>
  );
}
