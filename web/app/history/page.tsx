"use client";

import React, { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { fetchHistory, HistoryResponse } from "@/lib/api";
import { Card, CardTitle, CardDescription } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import ReactMarkdown from "react-markdown";
import { Database, Clock, CalendarDays } from "lucide-react";

function HistoryAccordionItem({ item }: { item: any }) {
  const [expanded, setExpanded] = useState(false);
  const dateStr = new Date(item.generated_at).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short"
  });

  return (
    <div className="mb-4 last:mb-0 bg-muted/30 rounded-md border border-sidebar-border overflow-hidden backdrop-blur-sm">
      <button 
        onClick={() => setExpanded(!expanded)} 
        className="w-full text-left p-4 hover:bg-muted/50 transition-colors flex items-center justify-between"
      >
        <div className="flex flex-col md:flex-row md:items-center gap-3 md:gap-8 flex-1">
          <div className="flex items-center gap-3 font-medium text-foreground">
             <span className="text-muted-foreground w-4 text-xs flex justify-center">{expanded ? '▼' : '▶'}</span>
             <Clock className="w-4 h-4 text-primary" />
             {dateStr}
          </div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
             <Database className="w-4 h-4" />
             <span className="truncate max-w-[200px] md:max-w-[300px]">{item.repos.join(", ")}</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
             <CalendarDays className="w-4 h-4" />
             {item.days} days
          </div>
        </div>
      </button>
      <div 
        className={`grid transition-[grid-template-rows,opacity] duration-300 ease-in-out ${
          expanded ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0"
        }`}
      >
        <div className="overflow-hidden">
          <div className="p-5 pt-2 border-t border-sidebar-border mt-2 bg-black/10">
            <div className="prose prose-invert prose-p:text-muted-foreground prose-headings:text-foreground prose-a:text-primary max-w-none prose-sm sm:prose-base">
              <ReactMarkdown>{item.summary}</ReactMarkdown>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function HistoryPage() {
  const { data: session, status } = useSession();
  const [history, setHistory] = useState<HistoryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (status === "unauthenticated") {
      setLoading(false);
      return;
    }
    
    if (status === "authenticated" && session?.user?.name) {
      // By default NextAuth Github provider passes the GitHub username or full name inside session.user.name.
      // Easiest is to parse from email or name.
      const githubUsername = session.user.name;
      
      fetchHistory(githubUsername)
        .then(data => {
          setHistory(data);
          setLoading(false);
        })
        .catch(err => {
          console.error(err);
          setError("Failed to load summary history. Ensure the API is running and connected to Neon.");
          setLoading(false);
        });
    }
  }, [session, status]);

  if (status === "loading") {
    return (
      <div className="min-h-screen p-8 max-w-4xl mx-auto flex flex-col gap-6 mt-12">
        <Skeleton className="h-12 w-[200px]" />
        <Skeleton className="h-[300px] w-full" />
      </div>
    );
  }

  if (status === "unauthenticated") {
    return (
      <div className="min-h-screen flex items-center justify-center p-8 bg-background relative overflow-hidden">
        <div className="absolute top-0 inset-x-0 h-40 bg-gradient-to-b from-primary/10 to-transparent w-full pointer-events-none" />
        <Card className="w-full max-w-md border-border bg-card/60 backdrop-blur-sm shadow-lg text-center p-8 z-10">
          <CardTitle className="text-3xl mb-4">Authentication Required</CardTitle>
          <CardDescription className="text-base text-muted-foreground mb-6">
            You must be logged in via GitHub to view your summary history.
          </CardDescription>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background relative overflow-hidden py-12 px-4 sm:px-6 lg:px-8">
      {/* Background ambient light effects */}
      <div className="absolute top-0 inset-x-0 h-40 bg-gradient-to-b from-primary/10 to-transparent w-full pointer-events-none" />
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-primary/5 blur-[120px] pointer-events-none" />
      
      <main className="w-full max-w-5xl relative z-10 mx-auto flex flex-col gap-8 min-h-[calc(100vh-12rem)]">
        <section className="mt-4 sm:mt-8 pb-4 border-b border-border/50 flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4">
            <div>
                <h1 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl mb-2 flex items-center gap-3">
                  <Clock className="w-8 h-8 text-primary" />
                  History
                </h1>
                <p className="text-lg text-muted-foreground max-w-2xl">
                    View your previously generated standup summaries.
                </p>
            </div>
            {history && (
                <Badge variant="outline" className="px-4 py-1.5 text-sm font-medium border-primary/20 bg-primary/5">
                    Total Summaries: {history.total}
                </Badge>
            )}
        </section>

        {loading ? (
          <div className="space-y-4">
            <Skeleton className="h-20 w-full rounded-xl" />
            <Skeleton className="h-20 w-full rounded-xl" />
            <Skeleton className="h-20 w-full rounded-xl" />
          </div>
        ) : error ? (
          <div className="text-red-400 bg-red-500/10 p-6 rounded-xl border border-red-500/20 shadow-sm">
            <div className="font-bold mb-1">Error Loading History</div>
            {error}
          </div>
        ) : history?.summaries.length === 0 ? (
          <div className="text-center py-20 bg-muted/20 rounded-xl border border-dashed border-sidebar-border shadow-sm backdrop-blur-sm">
            <Clock className="w-12 h-12 mx-auto text-muted-foreground mb-4 opacity-50" />
            <h3 className="text-xl font-semibold mb-2">No history found</h3>
            <p className="text-muted-foreground max-w-md mx-auto">
              You haven't generated any summaries yet. Head back to the main generator directly to pull your recent commits!
            </p>
          </div>
        ) : (
          <div className="flex flex-col pb-20">
            {history?.summaries.map((item) => (
              <HistoryAccordionItem key={item.id} item={item} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
