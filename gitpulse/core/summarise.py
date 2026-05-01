import logging
import json
import groq
import os

logger = logging.getLogger(__name__)

# LLM Context Window Constraints
MAX_COMMITS_PER_REPO = 50
MAX_MESSAGE_LENGTH = 300

def format_activity(activity: dict) -> dict:
    """
    Receives an activity dict with commits, prs, and issues.
    Groups them by repo and cleans messages/titles.
    """
    grouped = {}

    commits = activity.get("commits", [])
    prs = activity.get("prs", [])
    issues = activity.get("issues", [])

    for commit in commits:
        repo = commit["repo"]
        grouped.setdefault(repo, {"commits": [], "prs": [], "issues": []})
        short_hash = commit["hash"][:7]
        date = commit["date"].strftime("%Y-%m-%d")
        clean_message = " | ".join(line.strip() for line in commit["message"].splitlines() if line.strip())
        if len(clean_message) > MAX_MESSAGE_LENGTH:
            clean_message = clean_message[:MAX_MESSAGE_LENGTH] + "..."
        grouped[repo]["commits"].append({
            "hash": short_hash, "date": date, "message": clean_message
        })

    for pr in prs:
        repo = pr["repo"]
        grouped.setdefault(repo, {"commits": [], "prs": [], "issues": []})
        date = pr["merged_at"].strftime("%Y-%m-%d")
        grouped[repo]["prs"].append({
            "number": pr["number"], "title": pr["title"], "date": date, "url": pr["url"]
        })

    for issue in issues:
        repo = issue["repo"]
        grouped.setdefault(repo, {"commits": [], "prs": [], "issues": []})
        date = issue["closed_at"].strftime("%Y-%m-%d")
        grouped[repo]["issues"].append({
            "number": issue["number"], "title": issue["title"], "date": date, "url": issue["url"]
        })

    return grouped

def to_prompt_str(formatted_activity: dict) -> str:    
    prompt_str = ""
    if not formatted_activity:
        return ""
        
    for repo, data in formatted_activity.items():
        prompt_str += f"### {repo}\n"
        
        commits = data.get("commits", [])
        if commits:
            prompt_str += "COMMITS:\n"
            for commit in commits[:MAX_COMMITS_PER_REPO]:
                prompt_str += f"  - {commit['hash']} | {commit['date']} | {commit['message']}\n"
            if len(commits) > MAX_COMMITS_PER_REPO:
                prompt_str += f"  - ... (truncated {len(commits) - MAX_COMMITS_PER_REPO} older commits)\n"

        prs = data.get("prs", [])
        if prs:
            prompt_str += "MERGED PULL REQUESTS:\n"
            for pr in prs:
                prompt_str += f"  - PR #{pr['number']} | {pr['date']} | {pr['title']}\n"

        issues = data.get("issues", [])
        if issues:
            prompt_str += "CLOSED ISSUES:\n"
            for issue in issues:
                prompt_str += f"  - Issue #{issue['number']} | {issue['date']} | {issue['title']}\n"
            
        prompt_str += "\n"

    return prompt_str


def to_display_str(formatted_activity: dict) -> str:    
    display_str = ""
    if not formatted_activity:
        return ""
        
    for repo, data in formatted_activity.items():
        display_str += f"### {repo}\n"
        for commit in data.get("commits", []):
            display_str += f"  - {commit['hash']} | {commit['date']}\n"
            message_lines = commit["message"].split(" | ")
            for line in message_lines:
                display_str += f"    {line}\n"
        for pr in data.get("prs", []):
            display_str += f"  - PR #{pr['number']} | {pr['date']} | {pr['title']}\n"
        for issue in data.get("issues", []):
            display_str += f"  - Issue #{issue['number']} | {issue['date']} | {issue['title']}\n"
        display_str += "\n"
    return display_str

def build_prompt(prompt_str: str, mode: str = "standup", tone: str = "professional", language: str = "English") -> str:    
    role_instructions = f"""
    You are an expert technical writer.
    Your task is to generate a concise, {tone} summary based on the github activity provided.
    
    Output must be structured into exactly four sections:
    
    WHAT I DID
    - Bullet points of features/fixes completed, Pull Requests merged, and issues closed.
    
    DETAILS
    - Technical details, PR numbers, or important context
    
    WHATS NEXT
    - What you plan to work on next
    
    BLOCKERS
    - Any obstacles or dependencies
    
    Rules:
    - No preamble (e.g., "Here is your summary")
    - No sign-off (no "Thanks", no name)
    - Only the four sections above
    - Keep it concise and maintain a {tone} tone.
    - IMPORTANT: The entire summary must be written in {language}.
    """
    
    if mode == "retro":
        role_instructions = f"""
        You are an agile iteration manager.
        Your task is to generate a 2-week Sprint Retrospective summary based on the github activity provided.
        
        Output must be structured into exactly four sections:
        
        WHAT WENT WELL
        - Major themes of PRs merged and issues closed.
        
        WHAT DIDNT GO WELL
        - Areas with high churn, bugs, or lack of progress based on commit messaging.
        
        WHAT TO IMPROVE
        - Recommendations based on the pace and commit sizes.
        
        ACTION ITEMS
        - Concrete next steps.
        
        Rules:
        - No preamble or sign-off.
        - Maintain a {tone} tone.
        - IMPORTANT: The entire summary must be written in {language}.
        """
        
    return f"{role_instructions}\n\nHere is the activity data:\n{prompt_str}"


async def summarise(prompt_str:str) -> str:
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise EnvironmentError("GROQ_API_KEY missing")

    async with groq.AsyncGroq(api_key=groq_api_key) as client:
        try:
            response = await client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt_str}],
                temperature=0.3,
            )
            return response.choices[0].message.content
        except groq.AuthenticationError as e:
            logger.error("Groq authentication failed — invalid or expired GROQ_API_KEY: %s", e)
            raise
        except Exception as e:
            logger.error("Error during Groq summarization: %s", e, exc_info=True)
            raise
