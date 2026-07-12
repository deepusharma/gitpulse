import { redirect } from "next/navigation";
import { getServerSession } from "next-auth/next";
import { authOptions } from "@/app/api/auth/[...nextauth]/route";
import { getSchedule } from "@/lib/api";
import { ScheduleForm } from "@/components/schedule/ScheduleForm";
import { ScheduleStatus } from "@/components/schedule/ScheduleStatus";

export const metadata = {
  title: "Settings - GitPulse",
};

export default async function SettingsPage() {
  const session = await getServerSession(authOptions);
  if (!session || !session.user?.name) {
    redirect("/");
  }

  const username = session.user.name;
  let initialSchedule = null;
  try {
    initialSchedule = await getSchedule(username);
  } catch (e) {
    console.error("Failed to fetch schedule:", e);
  }

  return (
    <div className="container mx-auto max-w-4xl py-12 px-4">
      <h1 className="text-3xl font-bold tracking-tight mb-8">Settings</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="md:col-span-2 space-y-8">
          <section className="bg-card text-card-foreground rounded-lg border shadow-sm p-6">
            <h2 className="text-xl font-semibold mb-4">Scheduled Digests</h2>
            <p className="text-sm text-muted-foreground mb-6">
              Configure automated delivery of your standup summaries via Email or Slack.
            </p>
            <ScheduleForm username={username} initialSchedule={initialSchedule} />
          </section>
        </div>
        
        <div className="space-y-8">
          <section className="bg-card text-card-foreground rounded-lg border shadow-sm p-6">
            <h2 className="text-lg font-semibold mb-4">Status</h2>
            <ScheduleStatus schedule={initialSchedule} />
          </section>
        </div>
      </div>
    </div>
  );
}
