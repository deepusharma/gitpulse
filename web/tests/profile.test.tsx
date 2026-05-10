import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { ProfileHeader } from "../components/profile/ProfileHeader";
import { ProfileStats } from "../components/profile/ProfileStats";
import { TopReposList } from "../components/profile/TopReposList";
import { RecentSummaryCard } from "../components/profile/RecentSummaryCard";
import { ShareProfileButton } from "../components/ShareProfileButton";

// Mock next-auth hook
vi.mock("next-auth/react", () => ({
  useSession: vi.fn(() => ({
    data: { user: { name: "deepusharma" } },
    status: "authenticated",
  })),
}));

// Mock clipboard API
Object.assign(navigator, {
  clipboard: {
    writeText: vi.fn().mockResolvedValue(undefined),
  },
});

const mockProfile = {
  username: "deepusharma",
  avatar_url: "https://example.com/avatar.png",
  bio: "Test bio",
  recent_summary: "Today I wrote some tests.",
  current_streak: 5,
  longest_streak: 10,
  top_repos: ["repo1", "repo2"],
  health_score: 85,
  total_summaries: 20,
  generated_at: "2026-05-10T00:00:00Z",
};

describe("Profile Components", () => {
  it("renders ProfileHeader correctly", () => {
    render(<ProfileHeader profile={mockProfile} />);
    expect(screen.getByText("deepusharma")).toBeInTheDocument();
    expect(screen.getByText("Test bio")).toBeInTheDocument();
    expect(screen.getByText("🔥 5d")).toBeInTheDocument(); // Streak badge
  });

  it("renders ProfileStats correctly", () => {
    render(<ProfileStats profile={mockProfile} />);
    expect(screen.getByText("5d")).toBeInTheDocument(); // current
    expect(screen.getByText("10d")).toBeInTheDocument(); // longest
    expect(screen.getByText("85/100")).toBeInTheDocument(); // health
    expect(screen.getByText("20")).toBeInTheDocument(); // summaries
  });

  it("renders TopReposList correctly with repos", () => {
    render(<TopReposList repos={mockProfile.top_repos} />);
    expect(screen.getByText("repo1")).toBeInTheDocument();
    expect(screen.getByText("repo2")).toBeInTheDocument();
    // Links should have correct href
    const repo1Link = screen.getByText("repo1").closest("a");
    expect(repo1Link).toHaveAttribute("href", "https://github.com/repo1");
  });

  it("renders TopReposList empty state", () => {
    render(<TopReposList repos={[]} />);
    expect(screen.getByText("No repository activity found.")).toBeInTheDocument();
  });

  it("renders RecentSummaryCard correctly", () => {
    render(<RecentSummaryCard summary={mockProfile.recent_summary} />);
    expect(screen.getByText("Latest Public Standup")).toBeInTheDocument();
    expect(screen.getByText("Today I wrote some tests.")).toBeInTheDocument();
  });

  it("renders RecentSummaryCard empty state", () => {
    render(<RecentSummaryCard summary={null} />);
    expect(screen.getByText("No public standups yet.")).toBeInTheDocument();
  });
});

describe("ShareProfileButton", () => {
  it("copies URL to clipboard and shows Copied! state", async () => {
    render(<ShareProfileButton />);
    const button = screen.getByRole("button");
    
    expect(screen.getByText("Share Profile")).toBeInTheDocument();
    
    fireEvent.click(button);
    
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
      expect.stringContaining("/u/deepusharma")
    );
    
    await waitFor(() => {
      expect(screen.getByText("Copied!")).toBeInTheDocument();
    });
  });
});
