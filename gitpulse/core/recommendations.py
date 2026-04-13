"""
Proactive AI recommendations module.

Analyses aggregated developer activity metrics and uses the Groq LLM to produce
3–5 actionable, human-readable recommendations for the developer.

Usage example::

    metrics = {
        "commits": 12,
        "prs": 2,
        "issues": 1,
        "avg_cycle_time_hrs": 18.5,
        "stale_prs": 3,
        "commit_streak_days": 4,
        "prev_commits": 20,
    }
    nudges = await get_recommendations(metrics)
    print(nudges)
"""

import logging

from gitpulse.core.summarise import summarise

logger = logging.getLogger(__name__)


def build_recommendations_prompt(metrics: dict) -> str:
    """Build a Groq prompt that requests proactive developer recommendations.

    Args:
        metrics: A dict containing the following keys (all optional but recommended):
            - commits (int): Total commits in the current period.
            - prs (int): Total PRs merged in the current period.
            - issues (int): Total issues closed in the current period.
            - avg_cycle_time_hrs (float): Average time from PR open to merge (hours).
            - stale_prs (int): Number of PRs open for more than 7 days.
            - commit_streak_days (int): Consecutive days with at least one commit.
            - prev_commits (int): Total commits in the previous equivalent period.

    Returns:
        A formatted prompt string ready to be passed to ``summarise()``.
    """
    commits = metrics.get("commits", 0)
    prs = metrics.get("prs", 0)
    issues = metrics.get("issues", 0)
    avg_cycle_time_hrs = metrics.get("avg_cycle_time_hrs", 0.0)
    stale_prs = metrics.get("stale_prs", 0)
    commit_streak_days = metrics.get("commit_streak_days", 0)
    prev_commits = metrics.get("prev_commits", 0)

    delta_str = ""
    if prev_commits > 0:
        delta = round(((commits - prev_commits) / prev_commits) * 100, 1)
        direction = "up" if delta >= 0 else "down"
        delta_str = f"Commit volume is {direction} {abs(delta)}% compared to the previous period."
    elif commits == 0:
        delta_str = "No commits recorded in the current period."

    prompt = f"""You are a senior engineering coach reviewing a developer's recent GitHub activity metrics.

Activity metrics for the current period:
- Commits: {commits}
- PRs merged: {prs}
- Issues closed: {issues}
- Average PR cycle time: {avg_cycle_time_hrs:.1f} hours
- Stale PRs (open > 7 days): {stale_prs}
- Commit streak: {commit_streak_days} consecutive days
- Previous period commits: {prev_commits}
{delta_str}

Based on these metrics, identify any worrying patterns and provide exactly 3–5 concise, actionable recommendations to help this developer improve their velocity, code review cadence, or work habits.

Rules:
- Be specific and constructive — no generic advice.
- Keep each recommendation to one or two sentences.
- Format as a numbered list.
- No preamble or sign-off.
"""
    return prompt


async def get_recommendations(metrics: dict) -> str:
    """Generate proactive AI recommendations from developer activity metrics.

    Calls ``build_recommendations_prompt`` to construct the LLM prompt, then
    delegates to ``summarise`` which calls the Groq API.

    Args:
        metrics: Activity metrics dict — see ``build_recommendations_prompt`` for
            the expected keys.

    Returns:
        A numbered-list string of 3–5 actionable recommendations produced by
        the Groq LLM.

    Raises:
        EnvironmentError: If ``GROQ_API_KEY`` is not set.
        groq.AuthenticationError: If the API key is invalid.
    """
    logger.info("get_recommendations: building prompt from metrics: %s", metrics)
    prompt = build_recommendations_prompt(metrics)
    recommendations = await summarise(prompt)
    logger.info("get_recommendations: received %d chars from LLM", len(recommendations))
    return recommendations
