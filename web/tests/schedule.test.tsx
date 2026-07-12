import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ScheduleForm } from "../components/schedule/ScheduleForm";
import * as api from "../lib/api";

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    refresh: vi.fn(),
  }),
}));

vi.mock("../lib/api", () => ({
  saveSchedule: vi.fn(),
  deleteSchedule: vi.fn(),
}));

describe("ScheduleForm", () => {
  it("renders the schedule form correctly", () => {
    render(<ScheduleForm username="testuser" initialSchedule={null} />);
    expect(screen.getByLabelText(/Enable schedule/i)).toBeDefined();
    expect(screen.getByText(/Frequency/i)).toBeDefined();
    expect(screen.getByText(/Hour \(UTC\)/i)).toBeDefined();
    expect(screen.getByText(/Channel/i)).toBeDefined();
  });

  it("hides weekly day selector when frequency is daily", () => {
    render(<ScheduleForm username="testuser" initialSchedule={{ frequency: "daily" } as any} />);
    expect(screen.queryByText(/Day of Week/i)).toBeNull();
  });

  it("shows weekly day selector when frequency is weekly", () => {
    render(<ScheduleForm username="testuser" initialSchedule={{ frequency: "weekly" } as any} />);
    expect(screen.getByText(/Day of Week/i)).toBeDefined();
  });

  it("hides slack input when email is selected", () => {
    render(<ScheduleForm username="testuser" initialSchedule={{ channel: "email" } as any} />);
    expect(screen.getByText(/Email Address/i)).toBeDefined();
    expect(screen.queryByText(/Slack Webhook URL/i)).toBeNull();
  });

  it("shows slack input when slack is selected", () => {
    render(<ScheduleForm username="testuser" initialSchedule={{ channel: "slack" } as any} />);
    expect(screen.getByText(/Slack Webhook URL/i)).toBeDefined();
    expect(screen.queryByText(/Email Address/i)).toBeNull();
  });

  it("calls API with correct payload on save", async () => {
    render(<ScheduleForm username="testuser" initialSchedule={null} />);
    
    fireEvent.change(screen.getByPlaceholderText("repo1, repo2"), { target: { value: "repo1" } });
    
    // Default channel is email, so email input is shown
    fireEvent.change(screen.getByLabelText(/Email Address/i), { target: { value: "test@example.com" } });
    
    fireEvent.submit(screen.getByRole("button", { name: /Save Schedule/i }));
    
    expect(api.saveSchedule).toHaveBeenCalledWith({
      username: "testuser",
      enabled: true,
      frequency: "daily",
      hour_utc: 12,
      day_of_week: undefined,
      channel: "email",
      email_to: "test@example.com",
      slack_webhook: undefined,
      repos: ["repo1"],
      days: 7,
    });
  });
});
