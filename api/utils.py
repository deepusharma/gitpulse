"""Shared utility functions for the GitPulse API.

Functions here are safe to import from any router without circular imports.
"""

from datetime import datetime, timezone


def calculate_streak(dates: list, ignore_weekends: bool = True) -> tuple[int, int]:
    """Calculate the current and longest commit streak from a list of dates.

    Args:
        dates: List of date objects representing days with at least one commit.
        ignore_weekends: If True, a Mon→Fri gap (or similar) is treated as
            consecutive so weekends do not break streaks.

    Returns:
        A tuple of (current_streak, longest_streak).
    """
    if not dates:
        return 0, 0

    sorted_dates = sorted(list(set(dates)), reverse=True)
    today = datetime.now(timezone.utc).date()

    # Build all streak lengths
    all_streaks: list[int] = []
    current_iter_streak = 1
    for i in range(len(sorted_dates) - 1):
        curr = sorted_dates[i]
        prev = sorted_dates[i + 1]
        diff = (curr - prev).days

        is_consecutive = (diff == 1) or (
            ignore_weekends
            and curr.weekday() == 0
            and prev.weekday() == 4
            and diff == 3
        )

        if is_consecutive:
            current_iter_streak += 1
        else:
            all_streaks.append(current_iter_streak)
            current_iter_streak = 1
    all_streaks.append(current_iter_streak)

    longest_streak = max(all_streaks) if all_streaks else 0

    # Current streak: most-recent run, only if it touches today or yesterday
    latest = sorted_dates[0]

    def is_recent(d1, d2) -> bool:
        if d1 == d2:
            return True
        diff = (d1 - d2).days
        if diff == 1:
            return True
        if ignore_weekends:
            if d1.weekday() == 0 and d2.weekday() == 4 and diff == 3:
                return True
            if d1.weekday() == 6 and d2.weekday() == 4 and diff == 2:
                return True
            if d1.weekday() == 5 and d2.weekday() == 4 and diff == 1:
                return True
        return False

    current_streak = all_streaks[0] if is_recent(today, latest) else 0

    return current_streak, longest_streak
