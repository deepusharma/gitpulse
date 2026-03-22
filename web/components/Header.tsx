import Link from "next/link";
import { Github } from "lucide-react";

export function Header() {
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
          {/* Placeholder for OAuth */}
          <div className="text-sm text-muted-foreground hidden sm:block">
            Not logged in
          </div>
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
