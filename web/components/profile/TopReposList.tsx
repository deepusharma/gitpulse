interface TopReposListProps {
  repos: string[];
}

export function TopReposList({ repos }: TopReposListProps) {
  if (repos.length === 0) {
    return (
      <div className="p-4 rounded-xl border border-border bg-card text-sm text-muted-foreground">
        No repository activity found.
      </div>
    );
  }

  return (
    <div className="p-4 rounded-xl border border-border bg-card">
      <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-3">
        Top Repositories
      </h2>
      <div className="flex flex-wrap gap-2">
        {repos.map((repo, idx) => (
          <a
            key={repo}
            href={`https://github.com/${repo}`}
            target="_blank"
            rel="noreferrer noopener"
            className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium border transition-colors hover:border-primary/50 hover:text-primary ${
              idx === 0
                ? "border-primary/40 bg-primary/10 text-primary"
                : "border-border bg-muted text-muted-foreground"
            }`}
          >
            <span className="font-mono text-xs opacity-60">#{idx + 1}</span>
            {repo}
          </a>
        ))}
      </div>
    </div>
  );
}
