import React from "react";
import ReactMarkdown from "react-markdown";
import { fetchPublicSummary } from "@/lib/api";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { GitCommit, Calendar, User, Globe } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export default async function PublicSummaryPage({ params }: { params: { id: string } }) {
  let summary = null;
  let error = null;

  try {
    summary = await fetchPublicSummary(params.id);
  } catch {

    error = "This summary is not public or does not exist.";
  }

  if (error || !summary) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] p-6 text-center">
        <Globe className="h-16 w-16 text-muted-foreground/20 mb-4" />
        <h1 className="text-2xl font-bold mb-2">Summary Not Found</h1>
        <p className="text-muted-foreground mb-8 max-w-md">{error}</p>
        <Link href="/">
          <Button>Create Your Own Summary</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="container max-w-4xl py-12 px-4 sm:px-6">
      <div className="mb-8 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-primary mb-2">GitPulse Summary</h1>
          <p className="text-muted-foreground">Shared public report via gitpulse.ai</p>
        </div>
        <Link href="/">
          <Button variant="outline" size="sm">Try GitPulse</Button>
        </Link>
      </div>

      <Card className="border-border bg-card/60 backdrop-blur-sm overflow-hidden mb-8">
        <CardHeader className="bg-primary/5 border-b border-primary/10">
          <div className="flex flex-wrap items-center gap-4 text-sm">
            <div className="flex items-center gap-1.5 text-foreground font-medium">
              <User className="h-4 w-4 text-primary" />
              {summary.username}
            </div>
            <Separator orientation="vertical" className="h-4 hidden sm:block" />
            <div className="flex items-center gap-1.5 text-muted-foreground">
              <Calendar className="h-4 w-4" />
              {new Date(summary.generated_at).toLocaleDateString()}
            </div>
            <Separator orientation="vertical" className="h-4 hidden sm:block" />
            <div className="flex items-center gap-1.5 text-muted-foreground">
              <GitCommit className="h-4 w-4" />
              {summary.days} day lookback
            </div>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            {summary.repos.map((repo: string) => (
              <Badge key={repo} variant="secondary" className="bg-primary/10 text-primary border-primary/20">
                {repo}
              </Badge>
            ))}
          </div>
        </CardHeader>
        <CardContent className="pt-8 prose prose-invert prose-p:text-muted-foreground prose-headings:text-foreground prose-a:text-primary max-w-none">
          <ReactMarkdown>{summary.summary}</ReactMarkdown>
        </CardContent>
      </Card>

      <div className="text-center text-sm text-muted-foreground">
        <p>Built with GitPulse — AI-powered daily standup summaries.</p>
      </div>
    </div>
  );
}
