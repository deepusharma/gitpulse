"use client";

import React from "react";
import ReactMarkdown from "react-markdown";
import { SummariseResponse } from "@/lib/api";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import { Copy, Check, GitCommit, FileText, Database, Clock } from "lucide-react";

function CollapsibleSection({ title, content }: { title: string; content: string }) {
  const [expanded, setExpanded] = React.useState(true);
  
  return (
    <div className="mb-6 last:mb-0">
      <button 
        onClick={() => setExpanded(!expanded)} 
        className="flex items-center gap-2 w-full text-left font-bold text-lg text-foreground mb-2 hover:text-primary transition-colors"
      >
        <span className="text-xs">{expanded ? '▼' : '▶'}</span>
        {title}
      </button>
      <div 
        className={`grid transition-[grid-template-rows,opacity] duration-300 ease-in-out ${
          expanded ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0"
        }`}
      >
        <div className="overflow-hidden">
          <div className="prose prose-invert prose-p:text-muted-foreground prose-headings:text-foreground prose-a:text-primary max-w-none prose-sm sm:prose-base">
            <ReactMarkdown>{content}</ReactMarkdown>
          </div>
        </div>
      </div>
    </div>
  );
}

interface ResultsProps {
  data: SummariseResponse | null;
  isLoading: boolean;
  generationTimeMs?: number | null;
}

export function Results({ data, isLoading, generationTimeMs }: ResultsProps) {
  const [isCopied, setIsCopied] = React.useState(false);

  if (!data && !isLoading) return null;

  const commitsCount = data ? (data.display.match(/^(?:-|\*) /gm) || []).length : 0;
  const wordCount = data ? data.summary.trim().split(/\s+/).length : 0;
  const hasCommits = commitsCount > 0;

  const handleCopy = () => {
    if (!data) return;
    navigator.clipboard.writeText(data.summary);
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  if (data && !hasCommits && !isLoading) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center border-border bg-card/60 backdrop-blur-sm rounded-xl border w-full col-span-1 md:col-span-2">
        <div className="bg-muted p-4 rounded-full mb-4">
          <GitCommit className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-xl font-semibold mb-2">No commit activity found</h3>
        <p className="text-muted-foreground mb-4 max-w-md">
          We couldn't find any commits for the selected repositories in the given time frame. Try increasing the lookback period or checking the repository names.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-start w-full max-w-6xl mx-auto">
      {/* Left Column: Commits Breakdown */}
      <Card className="border-border bg-card/60 backdrop-blur-sm h-full flex flex-col">
        <CardHeader className="pb-4">
          <CardTitle className="text-xl">Commit Activity</CardTitle>
          <CardDescription>
            {isLoading ? (
              <Skeleton className="h-4 w-[200px]" />
            ) : data ? (
              <span className="flex items-center gap-2">
                <span>{data.repos.length} repo(s) over {data.days} days</span>
                <Badge variant="secondary" className="font-mono">{data.repos.join(", ")}</Badge>
              </span>
            ) : null}
          </CardDescription>
        </CardHeader>
        <CardContent className="flex-1 overflow-hidden relative">
          {isLoading ? (
            <div className="space-y-4">
              <Skeleton className="h-8 w-full" />
              <Skeleton className="h-8 w-5/6" />
              <Skeleton className="h-8 w-full" />
              <Skeleton className="h-8 w-4/6" />
            </div>
          ) : data ? (
            <div className="max-h-[600px] overflow-y-auto pr-2 custom-scrollbar p-1">
              {data.display.split(/(?=(?:^|\n)### )/).map((section, idx) => {
                if (!section.trim()) return null;
                const trimmedSection = section.trim();
                const titleMatch = trimmedSection.match(/^### (.*?)(?:\n([\s\S]*))?$/);
                if (titleMatch) {
                  return (
                    <div key={idx} className="mb-4 last:mb-0 bg-muted/30 p-3 rounded-md border border-sidebar-border">
                      <CollapsibleSection title={titleMatch[1].trim()} content={titleMatch[2] || ""} />
                    </div>
                  );
                }
                return (
                  <div key={idx} className="prose prose-invert prose-p:text-muted-foreground prose-headings:text-foreground prose-a:text-primary max-w-none prose-sm sm:prose-base mb-4 bg-muted/30 p-3 rounded-md border border-sidebar-border">
                    <ReactMarkdown>{section}</ReactMarkdown>
                  </div>
                );
              })}
            </div>
          ) : null}
        </CardContent>
      </Card>

      {/* Right Column: AI Summary */}
      <Card className="border-border bg-card/60 backdrop-blur-sm h-full flex flex-col">
        <CardHeader className="pb-4 flex flex-row items-center justify-between space-y-0">
          <div>
            <CardTitle className="text-xl text-primary">Standup Summary</CardTitle>
            <CardDescription className="mt-1.5">
              {isLoading ? (
                <Skeleton className="h-4 w-[120px]" />
              ) : data ? (
                "Generated by AI"
              ) : null}
            </CardDescription>
          </div>
          {data && !isLoading && (
            <Button variant="outline" size="sm" onClick={handleCopy} className="gap-2 h-8">
              {isCopied ? <Check className="h-3.5 w-3.5 text-green-500" /> : <Copy className="h-3.5 w-3.5" />}
              {isCopied ? "Copied" : "Copy"}
            </Button>
          )}
        </CardHeader>
        <CardContent className="flex-1 relative overflow-auto">
          {isLoading ? (
            <div className="space-y-4">
              <Skeleton className="h-12 w-1/3" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-5/6" />
              <Separator />
              <Skeleton className="h-8 w-1/4" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-2/3" />
            </div>
          ) : data ? (
            <div className="max-h-[600px] overflow-y-auto pr-2 custom-scrollbar">
              {data.summary.split(/(?=\n?#{1,2} )/m).map((section, idx) => {
                if (!section.trim()) return null;
                const trimmedSection = section.trim();
                const titleMatch = trimmedSection.match(/^#{1,2}\s+(.*?)(?:\n([\s\S]*))?$/);
                if (titleMatch) {
                  const rawTitle = titleMatch[1].replace(/\*\*/g, "").trim();
                  const upperTitle = rawTitle.toUpperCase().replace(/["'\u2019]/g, "");
                  const KNOWN_SECTIONS = ["WHAT I DID", "DETAILS", "WHATS NEXT", "WHAT'S NEXT", "BLOCKERS"];
                  const isKnown = KNOWN_SECTIONS.some(s => upperTitle.includes(s.replace(/["'\u2019]/g, "")));
                  if (isKnown) {
                    return <CollapsibleSection key={idx} title={rawTitle} content={titleMatch[2] || ""} />;
                  }
                }
                return (
                  <div key={idx} className="prose prose-invert prose-p:text-muted-foreground prose-headings:text-foreground prose-a:text-primary max-w-none prose-sm sm:prose-base mb-6">
                    <ReactMarkdown>{section}</ReactMarkdown>
                  </div>
                );
              })}
            </div>
          ) : null}
        </CardContent>
        {data && !isLoading && (
          <div className="bg-muted/30 px-6 py-3 border-t flex gap-4 text-xs text-muted-foreground items-center rounded-b-xl flex-wrap">
            <span className="flex items-center gap-1.5" title="Words Generated"><FileText className="w-3.5 h-3.5" /> {wordCount} words</span>
            <span className="flex items-center gap-1.5" title="Commits Processed"><GitCommit className="w-3.5 h-3.5" /> {commitsCount} commits</span>
            <span className="flex items-center gap-1.5" title="Repositories"><Database className="w-3.5 h-3.5" /> {data.repos.length} repos</span>
            {generationTimeMs && (
              <span className="flex items-center gap-1.5" title="Generation Time"><Clock className="w-3.5 h-3.5" /> {(generationTimeMs / 1000).toFixed(2)}s</span>
            )}
          </div>
        )}
      </Card>
      
      {/* Required styles for syntax rendering */}
      <style dangerouslySetInnerHTML={{__html: `
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background-color: var(--border);
          border-radius: 4px; border: 2px solid var(--card);
        }
      `}} />
    </div>
  );
}
