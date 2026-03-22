"use client";

import React, { useState } from "react";
import { generateSummary, SummariseResponse } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Loader2, AlertCircle } from "lucide-react";
import { useSession } from "next-auth/react";

interface SummaryFormProps {
  onSuccess: (data: SummariseResponse) => void;
  onClear: () => void;
  setIsLoading: (loading: boolean) => void;
}

export function SummaryForm({ onSuccess, onClear, setIsLoading }: SummaryFormProps) {
  const [username, setUsername] = useState("");
  const [repos, setRepos] = useState("");
  const [days, setDays] = useState(7);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const { data: session } = useSession();

  React.useEffect(() => {
    if (session?.user?.name && !username) {
      setUsername(session.user.name);
    }
  }, [session, username]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !repos.trim()) {
      setError("Username and Repositories are required.");
      return;
    }

    setIsSubmitting(true);
    setIsLoading(true);
    setError(null);
    onClear();

    try {
      const reposArray = repos
        .split(",")
        .map((r) => r.trim())
        .filter((r) => r.length > 0);
      
      const response = await generateSummary({
        username: username.trim(),
        repos: reposArray,
        days: days,
      });
      onSuccess(response);
    } catch (err: any) {
      setError(err.message || "Something went wrong.");
      setIsLoading(false);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card className="max-w-xl mx-auto border-border bg-card/50 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="text-xl">Generate Standup</CardTitle>
        <CardDescription>Enter GitHub details to build your standup.</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="username" className="text-sm font-medium">GitHub Username</label>
            <Input
              id="username"
              placeholder="e.g. deepusharma"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={isSubmitting}
              required
            />
          </div>
          <div className="space-y-2">
            <label htmlFor="repos" className="text-sm font-medium">Repositories</label>
            <Input
              id="repos"
              placeholder="e.g. gitpulse, dotfiles (comma separated)"
              value={repos}
              onChange={(e) => setRepos(e.target.value)}
              disabled={isSubmitting}
              required
            />
          </div>
          <div className="space-y-2">
            <label htmlFor="days" className="text-sm font-medium">Lookback Period (Days)</label>
            <Input
              id="days"
              type="number"
              min={1}
              max={90}
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              disabled={isSubmitting}
              required
            />
          </div>
          
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Error</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          
          <Button type="submit" className="w-full" disabled={isSubmitting}>
            {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {isSubmitting ? "Generating..." : "Generate Standup"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
