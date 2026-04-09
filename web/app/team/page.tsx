"use client";

import { useState, useEffect } from "react";
import { generateTeamSummary, TeamSummariseResponse, listRosters, createRoster, RosterResponse } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Loader2, AlertCircle, Save, Users, Presentation, Send } from "lucide-react";
import { Results } from "@/components/Results";
import { SlackDeliveryModal } from "@/components/team/SlackDeliveryModal";
import Link from "next/link";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";

export default function TeamPage() {
  const [data, setData] = useState<TeamSummariseResponse | null>(null);
  const [generationTimeMs, setGenerationTimeMs] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form State
  const [usernamesText, setUsernamesText] = useState("");
  const [reposText, setReposText] = useState("");
  const [daysInput, setDaysInput] = useState("7");
  const [rosterName, setRosterName] = useState("");

  // Rosters State
  const [rosters, setRosters] = useState<RosterResponse[]>([]);
  const [isSavingRoster, setIsSavingRoster] = useState(false);
  const [isSlackModalOpen, setIsSlackModalOpen] = useState(false);

  useEffect(() => {
    fetchRosters();
  }, []);

  const fetchRosters = async () => {
    try {
      const saved = await listRosters();
      setRosters(saved);
    } catch (e) {
      console.error(e);
    }
  };

  const handleSaveRoster = async () => {
    if (!rosterName.trim() || !usernamesText.trim()) return;
    setIsSavingRoster(true);
    try {
      const users = usernamesText.split(",").map(u => u.trim()).filter(Boolean);
      await createRoster({ name: rosterName, usernames: users });
      await fetchRosters();
      setRosterName("");
    } catch (e: unknown) {
      if (e instanceof Error) {
        setError(e.message || "Failed to save roster");
      } else {
        setError("Failed to save roster");
      }
    } finally {
      setIsSavingRoster(false);
    }
  };

  const handleLoadRoster = (r: RosterResponse) => {
    setUsernamesText(r.usernames.join(", "));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setData(null);
    setGenerationTimeMs(null);

    const users = usernamesText.split(",").map(u => u.trim()).filter(Boolean);
    const repos = reposText.split(",").map(r => r.trim()).filter(Boolean);
    const days = parseInt(daysInput, 10);

    if (users.length === 0 || repos.length === 0 || isNaN(days)) {
      setError("Please provide valid usernames, repos, and days.");
      setIsLoading(false);
      return;
    }

    try {
      const start = performance.now();
      const res = await generateTeamSummary({ usernames: users, repos, days });
      setData(res);
      setGenerationTimeMs(performance.now() - start);
      
      // Save to local storage for Presentation Mode
      if (typeof window !== "undefined") {
        localStorage.setItem("gitpulse_team_presentation", JSON.stringify(res));
      }
    } catch (e: unknown) {
      if (e instanceof Error) {
        setError(e.message || "Failed to generate team standup");
      } else {
        setError("Failed to generate team standup");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background relative overflow-hidden flex flex-col items-center py-12 px-4 sm:px-6 lg:px-8">
      {/* Background ambient light effects */}
      <div className="absolute top-0 inset-x-0 h-40 bg-gradient-to-b from-primary/10 to-transparent w-full pointer-events-none" />
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-primary/5 blur-[120px] pointer-events-none" />

      <main className="w-full max-w-7xl relative z-10 flex flex-col gap-8 pb-20">
        <div className="text-center space-y-4">
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight">
            Team <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-blue-500">Standups</span>
          </h1>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            Generate combined engineering summaries for your entire team.
          </p>
        </div>

        <div className="flex flex-col md:flex-row gap-8 items-start">
          <div className="w-full md:w-[35%] shrink-0 space-y-6 sticky top-24">
            <Card className="border-border bg-card/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-xl flex items-center gap-2"><Users className="w-5 h-5"/> Team Configuration</CardTitle>
                <CardDescription>Setup your team and repos to check.</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <label className="text-sm font-medium">GitHub Usernames (comma separated)</label>
                    </div>
                    <Input
                      placeholder="alice, bob, charlie"
                      value={usernamesText}
                      onChange={(e) => setUsernamesText(e.target.value)}
                      required
                    />
                    
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button variant="link" size="sm" className="px-0 h-auto text-xs">Load Saved Roster</Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>Saved Team Rosters</DialogTitle>
                          <DialogDescription>Select a team roster to load.</DialogDescription>
                        </DialogHeader>
                        <div className="space-y-2 mt-4">
                          {rosters.length === 0 ? (
                            <p className="text-sm text-muted-foreground">No saved rosters yet.</p>
                          ) : (
                            rosters.map(r => (
                              <div key={r.id} className="flex items-center justify-between p-2 border rounded-md">
                                <div>
                                  <p className="font-medium text-sm">{r.name}</p>
                                  <p className="text-xs text-muted-foreground">{r.usernames.join(", ")}</p>
                                </div>
                                <Button size="sm" onClick={() => handleLoadRoster(r)}>Load</Button>
                              </div>
                            ))
                          )}
                        </div>
                      </DialogContent>
                    </Dialog>
                  </div>

                  <div className="space-y-2 border p-3 rounded-md bg-muted/20">
                    <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Save Current Users as Roster</label>
                    <div className="flex gap-2">
                      <Input
                        placeholder="Roster Name (e.g. Frontend Team)"
                        value={rosterName}
                        onChange={(e) => setRosterName(e.target.value)}
                        className="h-8 text-sm"
                      />
                      <Button type="button" size="sm" onClick={handleSaveRoster} disabled={!rosterName.trim() || !usernamesText.trim() || isSavingRoster} className="h-8">
                        <Save className="w-3 h-3 mr-1" /> Save
                      </Button>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium">Repositories (comma separated text)</label>
                    <Input
                      placeholder="repo1, repo2"
                      value={reposText}
                      onChange={(e) => setReposText(e.target.value)}
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium">Lookback Period (Days)</label>
                    <Input
                      type="number"
                      min="1"
                      max="90"
                      value={daysInput}
                      onChange={(e) => setDaysInput(e.target.value)}
                      required
                    />
                  </div>

                  <Button type="submit" className="w-full" disabled={isLoading}>
                    {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    {isLoading ? "Generating..." : "Generate Team Standup"}
                  </Button>
                </form>

                {error && (
                  <Alert variant="destructive" className="mt-4">
                    <AlertCircle className="h-4 w-4" />
                    <AlertTitle>Error</AlertTitle>
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}
              </CardContent>
            </Card>
          </div>

          <div className="w-full md:w-[65%]">
            {(data || isLoading) && (
              <div className="space-y-4">
                <div className="flex gap-2 justify-end mb-2">
                  <Button variant="outline" size="sm" className="gap-2" onClick={() => setIsSlackModalOpen(true)} disabled={isLoading || !data}>
                    <Send className="w-4 h-4"/> Send to Slack
                  </Button>
                  <Link href="/present" target="_blank" className="flex items-center gap-2">
                    <Button variant="outline" size="sm" className="bg-primary/10 hover:bg-primary/20 text-primary border-primary/20">
                      <Presentation className="w-4 h-4 mr-2"/> Presentation Mode
                    </Button>
                  </Link>
                </div>
                
                {/* For team standups, we map the TeamSummariseResponse to what Results expects, or we can just use Results carefully */}
                <Results 
                  data={data ? {
                    display: data.display,
                    summary: data.summary,
                    repos: data.repos,
                    username: data.contributors.join(", "),
                    days: data.days,
                    generated_at: data.generated_at
                  } : null} 
                  isLoading={isLoading} 
                  generationTimeMs={generationTimeMs} 
                />
              </div>
            )}
          </div>
        </div>
      </main>

      <SlackDeliveryModal 
        isOpen={isSlackModalOpen} 
        onClose={() => setIsSlackModalOpen(false)} 
        summaryText={data?.summary || ""}
      />
    </div>
  );
}
