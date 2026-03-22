import Link from "next/link";
import { Github } from "lucide-react";
import packageJson from "../package.json";

export function Footer() {
  return (
    <footer className="w-full border-t border-border bg-background py-6 md:py-0">
      <div className="container mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 px-4 sm:px-6 lg:px-8 md:h-16 md:flex-row">
        <p className="text-center text-sm leading-loose text-muted-foreground md:text-left">
          &copy; 2026 Deepak Sharma.{" "}
          <Link
            href="https://github.com/deepusharma/gitpulse/blob/master/LICENSE"
            target="_blank"
            rel="noreferrer"
            className="font-medium underline underline-offset-4 hover:text-foreground"
          >
            MIT License
          </Link>
          .
        </p>
        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <span>v{packageJson.version}</span>
          <Link
            href="https://github.com/deepusharma/gitpulse"
            target="_blank"
            rel="noreferrer"
            className="hover:text-foreground transition-colors"
          >
            <span className="sr-only">GitHub</span>
            <Github className="h-4 w-4" />
          </Link>
        </div>
      </div>
    </footer>
  );
}
