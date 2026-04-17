"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  BookMarked,
  Plus,
  Trash2,
  X,
  AlertCircle,
  Loader2,
  FileText,
} from "lucide-react";
import { listPromptTemplates, createPromptTemplate, deletePromptTemplate } from "@/lib/api";
import type { PromptTemplate } from "@/lib/types";

/**
 * Templates management page — Create, list, and delete saved prompt templates.
 * Protected behind NextAuth session guard.
 */
export default function TemplatesPage() {
  const { data: session, status } = useSession();
  const router = useRouter();

  const [templates, setTemplates] = useState<PromptTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // New-template form state
  const [showForm, setShowForm] = useState(false);
  const [newName, setNewName] = useState("");
  const [newContent, setNewContent] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const username = session?.user?.username ?? "";

  // Redirect unauthenticated users
  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/");
    }
  }, [status, router]);

  // Load templates when session is available
  useEffect(() => {
    if (!username) return;

    setLoading(true);
    listPromptTemplates(username)
      .then(setTemplates)
      .catch((err: unknown) => {
        const e = err as Error;
        setError(e.message || "Failed to load templates");
      })
      .finally(() => setLoading(false));
  }, [username]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim() || !newContent.trim()) {
      setFormError("Both name and content are required.");
      return;
    }
    setSubmitting(true);
    setFormError(null);

    try {
      const created = await createPromptTemplate({
        username,
        name: newName.trim(),
        content: newContent.trim(),
      });
      setTemplates((prev) => [created, ...prev]);
      setNewName("");
      setNewContent("");
      setShowForm(false);
    } catch (err: unknown) {
      const e = err as Error;
      setFormError(e.message || "Failed to create template");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: string) => {
    // Optimistic removal
    setTemplates((prev) => prev.filter((t) => t.id !== id));
    try {
      await deletePromptTemplate(id);
    } catch {
      // If deletion fails, re-fetch to restore state
      if (username) {
        const fresh = await listPromptTemplates(username).catch(() => []);
        setTemplates(fresh);
      }
    }
  };

  if (status === "loading") {
    return (
      <div className="flex items-center justify-center py-32">
        <Loader2 className="h-6 w-6 animate-spin text-emerald-500" />
      </div>
    );
  }

  return (
    <div className="py-8 relative">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_#10b981_0%,_transparent_25%)] opacity-10 pointer-events-none" />
      <main className="container mx-auto px-4 max-w-4xl relative z-10 space-y-8 pb-20">
        {/* Page header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <BookMarked className="h-6 w-6 text-emerald-400" />
              <h1 className="text-4xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 via-teal-500 to-blue-600">
                Templates
              </h1>
            </div>
            <p className="text-zinc-400 mt-2 text-lg">
              Save and reuse custom prompt instructions for your standups.
            </p>
          </div>

          {!showForm && (
            <button
              id="new-template-btn"
              onClick={() => setShowForm(true)}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium transition-colors self-start md:self-auto"
            >
              <Plus className="h-4 w-4" />
              New Template
            </button>
          )}
        </div>

        {/* Global error */}
        {error && (
          <Alert variant="destructive" className="border-red-500/50 bg-red-500/10 text-red-200">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Inline create form */}
        {showForm && (
          <Card className="bg-black/40 border-emerald-500/30">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
              <CardTitle className="text-sm font-semibold">New Template</CardTitle>
              <button
                id="close-template-form-btn"
                onClick={() => {
                  setShowForm(false);
                  setFormError(null);
                  setNewName("");
                  setNewContent("");
                }}
                aria-label="Close form"
                className="text-zinc-500 hover:text-zinc-200 transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCreate} className="space-y-4">
                {formError && (
                  <p className="text-sm text-red-400">{formError}</p>
                )}
                <div className="space-y-1">
                  <label
                    htmlFor="template-name"
                    className="text-xs text-zinc-400 font-medium"
                  >
                    Template Name
                  </label>
                  <Input
                    id="template-name"
                    placeholder="e.g. Weekly Standup — Formal"
                    value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                    className="bg-black/40 border-zinc-800 text-sm h-10"
                  />
                </div>
                <div className="space-y-1">
                  <label
                    htmlFor="template-content"
                    className="text-xs text-zinc-400 font-medium"
                  >
                    Instructions / Prompt Content
                  </label>
                  <textarea
                    id="template-content"
                    placeholder="Write your custom instructions here…"
                    value={newContent}
                    onChange={(e) => setNewContent(e.target.value)}
                    rows={5}
                    className="w-full rounded-md border border-zinc-800 bg-black/40 px-3 py-2 text-sm text-zinc-100 placeholder-zinc-600 focus:outline-none focus:ring-2 focus:ring-emerald-600 resize-none"
                  />
                </div>
                <div className="flex gap-3 justify-end">
                  <button
                    type="button"
                    onClick={() => {
                      setShowForm(false);
                      setFormError(null);
                    }}
                    className="px-4 py-2 rounded-lg border border-zinc-700 text-sm text-zinc-400 hover:text-zinc-200 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    id="submit-template-btn"
                    type="submit"
                    disabled={submitting}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium transition-colors disabled:opacity-50"
                  >
                    {submitting && <Loader2 className="h-4 w-4 animate-spin" />}
                    Save Template
                  </button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Loading state */}
        {loading && (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="h-6 w-6 animate-spin text-emerald-500" />
          </div>
        )}

        {/* Empty state */}
        {!loading && templates.length === 0 && !showForm && (
          <div className="flex flex-col items-center justify-center py-20 text-center space-y-4">
            <div className="p-4 rounded-full bg-zinc-900 border border-zinc-800">
              <FileText className="h-8 w-8 text-zinc-600" />
            </div>
            <div>
              <p className="text-zinc-300 font-medium">No saved templates yet.</p>
              <p className="text-zinc-500 text-sm mt-1">
                Create one to reuse your custom instructions across standups.
              </p>
            </div>
            <button
              id="empty-new-template-btn"
              onClick={() => setShowForm(true)}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium transition-colors"
            >
              <Plus className="h-4 w-4" />
              New Template
            </button>
          </div>
        )}

        {/* Template list */}
        {!loading && templates.length > 0 && (
          <div className="space-y-3">
            {templates.map((t) => (
              <Card
                key={t.id}
                className="bg-black/40 border-zinc-800 hover:border-zinc-700 transition-colors"
              >
                <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-2">
                  <div className="space-y-0.5">
                    <CardTitle className="text-sm font-semibold text-zinc-100">
                      {t.name}
                    </CardTitle>
                    <CardDescription className="text-[10px] text-zinc-600">
                      {new Date(t.created_at).toLocaleDateString(undefined, {
                        dateStyle: "medium",
                      })}
                    </CardDescription>
                  </div>
                  <button
                    id={`delete-template-${t.id}`}
                    onClick={() => handleDelete(t.id)}
                    aria-label={`Delete template ${t.name}`}
                    className="text-zinc-600 hover:text-rose-400 transition-colors mt-0.5"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </CardHeader>
                <CardContent>
                  <p className="text-xs text-zinc-500 line-clamp-2 leading-relaxed">
                    {t.content}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
