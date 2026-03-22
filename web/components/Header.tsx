"use client";

import Link from "next/link";
import { Github, LogIn, LogOut } from "lucide-react";
import { useSession, signIn, signOut } from "next-auth/react";

export function Header() {
  const { data: session, status } = useSession();

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-14 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-2">
          <Link href="/" className="font-bold flex items-center space-x-2">
            <span className="font-mono text-primary">&gt;</span>
            <span className="font-bold">gitpulse</span>
          </Link>
        </div>
        <div className="flex items-center gap-4">
          {status === "loading" ? (
            <div className="text-sm text-muted-foreground hidden sm:block">
              Loading...
            </div>
          ) : session ? (
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                {session.user?.image && (
                  <img src={session.user.image} alt="User avatar" className="h-6 w-6 rounded-full" />
                )}
                <span className="text-sm font-medium hidden sm:block">
                  {session.user?.name || session.user?.email || "User"}
                </span>
              </div>
              <button
                onClick={() => signOut()}
                className="text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1 text-sm font-medium"
              >
                <LogOut className="h-4 w-4" />
                <span className="hidden sm:inline">Logout</span>
              </button>
            </div>
          ) : (
            <button
              onClick={() => signIn("github")}
              className="text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1 text-sm font-medium"
            >
              <LogIn className="h-4 w-4" />
              <span className="hidden sm:inline">Login with GitHub</span>
            </button>
          )}
          <Link
            href="https://github.com/deepusharma/gitpulse"
            target="_blank"
            rel="noreferrer"
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            <Github className="h-5 w-5" />
            <span className="sr-only">GitHub</span>
          </Link>
        </div>
      </div>
    </header>
  );
}
