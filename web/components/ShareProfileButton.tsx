"use client";

import { useState } from "react";
import { Link2, Check } from "lucide-react";
import { useSession } from "next-auth/react";

export function ShareProfileButton() {
  const { data: session } = useSession();
  const [copied, setCopied] = useState(false);

  const username = session?.user?.name;
  if (!username) return null;

  const profileUrl = `${window.location.origin}/u/${username}`;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(profileUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard API unavailable — fallback
      const input = document.createElement("input");
      input.value = profileUrl;
      document.body.appendChild(input);
      input.select();
      document.execCommand("copy");
      document.body.removeChild(input);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <button
      id="share-profile-btn"
      onClick={handleCopy}
      title="Copy your public profile link"
      className="inline-flex items-center gap-1.5 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors px-2 py-1 rounded-md hover:bg-muted"
    >
      {copied ? (
        <>
          <Check className="h-4 w-4 text-green-500" />
          <span className="hidden sm:inline text-green-500">Copied!</span>
        </>
      ) : (
        <>
          <Link2 className="h-4 w-4" />
          <span className="hidden sm:inline">Share Profile</span>
        </>
      )}
    </button>
  );
}
