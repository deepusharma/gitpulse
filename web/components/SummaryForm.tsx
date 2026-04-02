"use client";

import React, { useState, useEffect } from "react";
import { generateSummary, SummariseResponse, ApiError, validateUser, fetchUserRepos } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Checkbox } from "@/components/ui/checkbox";
import { Loader2, AlertCircle, ChevronDown, ChevronUp, Check, RotateCcw } from "lucide-react";
import { useSession } from "next-auth/react";
import { MultiSelect } from "@/components/ui/multi-select";
import { cn } from "@/lib/utils";

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
  const [usernameValid, setUsernameValid] = useState<boolean | null>(null);
  const [isValidating, setIsValidating] = useState(false);
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null);
  
  const [availableRepos, setAvailableRepos] = useState<string[]>([]);
  const [selectedRepos, setSelectedRepos] = useState<string[]>([]);
  const [isLoadingRepos, setIsLoadingRepos] = useState(false);

  const [daysInput, setDaysInput] = useState("7");
  const [forceRefresh, setForceRefresh] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<ErrorState | null>(null);
  const [showTrace, setShowTrace] = useState(false);

  const { data: session } = useSession();

  useEffect(() => {
    if (session?.user?.name && !username) {
      setUsername(session.user.name);
    }
  }, [session, username]);

  // Debounced username validation
  useEffect(() => {
    if (!username.trim()) {
      setUsernameValid(null);
      setAvatarUrl(null);
      setAvailableRepos([]);
      return;
    }

    const timer = setTimeout(async () => {
      setIsValidating(true);
      try {
        const result = await validateUser(username.trim());
        setUsernameValid(result.valid);
        if (result.valid) {
          setAvatarUrl(result.avatar_url || null);
          // Fetch repos immediately
          setIsLoadingRepos(true);
          const repoData = await fetchUserRepos(username.trim());
          setAvailableRepos(repoData.repos);
          setIsLoadingRepos(false);
        } else {
          setAvailableRepos([]);
        }
      } catch (err) {
        console.error("Validation error:", err);
      } finally {
        setIsValidating(false);
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [username]);

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
    if (!username.trim() || selectedRepos.length === 0) {
      setError({ message: "Username and at least one Repository are required." });
      return;
    }

    setIsSubmitting(true);
    setIsLoading(true);
    setError(null);
    setShowTrace(false);
    onClear();

    try {
      const startTime = performance.now();
      const response = await generateSummary({
        username: username.trim(),
        repos: selectedRepos,
        days: parsedDays(),
      }, forceRefresh);
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
            <label htmlFor="username" className="text-sm font-medium flex justify-between items-center">
              GitHub Username
              {isValidating && <Loader2 className="h-3 w-3 animate-spin text-muted-foreground" />}
            </label>
            <div className="relative">
              <Input
                id="username"
                placeholder="e.g. deepusharma"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                disabled={isSubmitting}
                required
                className={cn(
                  "pr-10",
                  usernameValid === true && "border-green-500/50 focus-visible:ring-green-500/20",
                  usernameValid === false && "border-red-500/50 focus-visible:ring-red-500/20"
                )}
              />
              <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-2">
                {avatarUrl && (
                  <img src={avatarUrl} alt={username} className="h-6 w-6 rounded-full border border-border" />
                )}
                {usernameValid === true && <Check className="h-4 w-4 text-green-500" />}
                {usernameValid === false && <AlertCircle className="h-4 w-4 text-red-500" />}
              </div>
            </div>
          </div>

          <div className="space-y-2">
            <label htmlFor="repos" className="text-sm font-medium flex justify-between items-center">
              Repositories
              {isLoadingRepos && <Loader2 className="h-3 w-3 animate-spin text-muted-foreground" />}
            </label>
            <MultiSelect
              options={availableRepos}
              selected={selectedRepos}
              onChange={setSelectedRepos}
              placeholder={usernameValid ? "Select repositories..." : "Enter valid username first"}
              disabled={isSubmitting || !usernameValid}
            />
          </div>

          <div className="flex flex-col sm:flex-row gap-4">
            <div className="space-y-2 flex-1">
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
                className="w-full"
              />
            </div>
            
            <div className="space-y-2 flex flex-col justify-end">
              <div 
                className="flex items-center space-x-2 bg-muted/30 p-2 rounded-md border border-input cursor-pointer hover:bg-muted/50 transition-colors h-[40px]"
                onClick={() => setForceRefresh(!forceRefresh)}
              >
                <Checkbox 
                  id="refresh" 
                  checked={forceRefresh} 
                  onCheckedChange={(checked) => setForceRefresh(!!checked)}
                  disabled={isSubmitting}
                />
                <label
                  htmlFor="refresh"
                  className="text-xs font-medium leading-none cursor-pointer flex items-center gap-1"
                >
                  <RotateCcw className={cn("h-3 w-3", forceRefresh && "animate-spin-once")} />
                  Force fresh sync
                </label>
              </div>
            </div>
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
