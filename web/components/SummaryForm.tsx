"use client";

import React, { useState } from "react";
import { generateSummary, SummariseResponse, ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Loader2, AlertCircle, ChevronDown, ChevronUp } from "lucide-react";
import { useSession } from "next-auth/react";

interface SummaryFormProps {
  onSuccess: (data: SummariseResponse, generationTimeMs: number) => void;
  onClear: () => void;
  setIsLoading: (loading: boolean) => void;
}

interface ErrorState {
  message: string;
  traceback?: string | null;
}

export function SummaryForm({ onSuccess, onClear, setIsLoading }: SummaryFormProps) {
  const [username, setUsername] = useState("");
  const [repos, setRepos] = useState("");
  // Store days as a string so typing works naturally; parse on submit
  const [daysInput, setDaysInput] = useState("7");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<ErrorState | null>(null);
  const [showTrace, setShowTrace] = useState(false);

  const { data: session } = useSession();

  React.useEffect(() => {
    if (session?.user?.username && !username) {
      setUsername(session.user.username);
    }
  }, [session, username]);

  const handleDaysChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    // Allow free typing — only allow digits
    const raw = e.target.value.replace(/^0+(?=\d)/, ""); // strip leading zeros
    if (raw === "" || /^\d+$/.test(raw)) {
      setDaysInput(raw);
    }
  };

  const parsedDays = () => {
    const n = parseInt(daysInput, 10);
    return isNaN(n) || n < 1 ? 7 : Math.min(n, 90);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !repos.trim()) {
      setError({ message: "Username and Repositories are required." });
      return;
    }

    setIsSubmitting(true);
    setIsLoading(true);
    setError(null);
    setShowTrace(false);
    onClear();

    try {
      const reposArray = repos
        .split(",")
        .map((r) => r.trim())
        .filter((r) => r.length > 0);

      const startTime = performance.now();
      const response = await generateSummary({
        username: username.trim(),
        repos: reposArray,
        days: parsedDays(),
      });
      const endTime = performance.now();
      onSuccess(response, endTime - startTime);
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        setError({ message: err.message, traceback: err.traceback });
      } else if (err instanceof Error) {
        setError({ message: err.message });
      } else {
        setError({ message: "An unexpected error occurred." });
      }
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
            <label htmlFor="days" className="text-sm font-medium">
              Lookback Period (Days)
            </label>
            <Input
              id="days"
              inputMode="numeric"
              pattern="[0-9]*"
              placeholder="7"
              value={daysInput}
              onChange={handleDaysChange}
              onBlur={() => setDaysInput(String(parsedDays()))}
              disabled={isSubmitting}
              className="w-24"
            />
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle className="flex items-center justify-between">
                <span>Error</span>
                {error.traceback && (
                  <button
                    type="button"
                    onClick={() => setShowTrace((v) => !v)}
                    className="flex items-center gap-1 text-xs font-normal underline underline-offset-2 opacity-80 hover:opacity-100"
                  >
                    {showTrace ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
                    {showTrace ? "Hide details" : "Show details"}
                  </button>
                )}
              </AlertTitle>
              <AlertDescription className="space-y-2">
                <p>{error.message}</p>
                {error.traceback && showTrace && (
                  <pre className="mt-2 max-h-40 overflow-auto rounded bg-black/40 p-2 text-xs text-red-200 whitespace-pre-wrap">
                    {error.traceback}
                  </pre>
                )}
              </AlertDescription>
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
