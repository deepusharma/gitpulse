import React from "react";

export function Hero() {
  return (
    <div className="py-12 md:py-16 px-4 md:px-0 text-center max-w-3xl mx-auto">
      <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight mb-4 text-foreground">
        gitpulse <span className="text-primary">— Your weekly standup, done</span>
      </h1>
      <p className="text-muted-foreground text-lg mb-8 max-w-2xl mx-auto leading-relaxed">
        Generate AI-powered standup summaries directly from your GitHub commit history. 
        Just enter your username, the repositories you worked on, and let the AI do the rest.
      </p>
    </div>
  );
}
