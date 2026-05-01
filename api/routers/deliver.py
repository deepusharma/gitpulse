from fastapi import APIRouter, HTTPException, Depends
import httpx
import logging
import os
import resend

from api.models import SlackDeliverRequest, EmailDeliverRequest, GistDeliverRequest, GistDeliverResponse
from api.dependencies import get_token_override

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/deliver", tags=["deliver"])

@router.post("/slack")
async def deliver_slack(req: SlackDeliverRequest):
    if not req.webhook_url.startswith("https://hooks.slack.com/"):
        raise HTTPException(status_code=400, detail="Invalid Slack webhook URL")
    
    payload = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": req.summary
                }
            }
        ]
    }
    if req.channel:
        payload["channel"] = req.channel

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(req.webhook_url, json=payload)
            if resp.status_code != 200:
                logger.error("Slack rejected payload: %s %s", resp.status_code, resp.text)
                raise HTTPException(status_code=502, detail="Slack delivery rejected")
        except Exception as e:
            logger.error("Slack webhook error: %s", e)
            raise HTTPException(status_code=500, detail="Failed to reach Slack")
    return {"ok": True}

@router.post("/email")
async def deliver_email(req: EmailDeliverRequest):
    api_key = os.getenv("RESEND_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="RESEND_API_KEY is not configured on the server")
    
    resend.api_key = api_key
    
    # Convert simple markdown to basic HTML or just use plain text with pre tag
    html_content = f"<h2>GitPulse Standup Summary</h2><pre style='white-space: pre-wrap; font-family: sans-serif;'>{req.summary}</pre>"
    
    try:
        r = resend.Emails.send({
            "from": "GitPulse <onboarding@resend.dev>",
            "to": req.to,
            "subject": "Your GitPulse Standup Summary",
            "html": html_content
        })
        return {"ok": True, "id": r.get("id")}
    except Exception as e:
        logger.error("Resend error: %s", e)
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

@router.post("/gist", response_model=GistDeliverResponse)
async def deliver_gist(
    req: GistDeliverRequest,
    x_github_token: str = Depends(get_token_override)
):
    if not x_github_token:
        raise HTTPException(status_code=401, detail="GitHub token required for Gist delivery")
        
    payload = {
        "description": "GitPulse Standup Summary",
        "public": req.is_public,
        "files": {
            "standup.md": {
                "content": req.summary
            }
        }
    }
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                "https://api.github.com/gists",
                headers={
                    "Authorization": f"Bearer {x_github_token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28"
                },
                json=payload
            )
            if resp.status_code != 201:
                logger.error("GitHub Gist creation failed: %s %s", resp.status_code, resp.text)
                raise HTTPException(status_code=resp.status_code, detail="Failed to create Gist")
            
            data = resp.json()
            return GistDeliverResponse(url=data["html_url"])
        except httpx.RequestError as e:
            logger.error("Gist webhook error: %s", e)
            raise HTTPException(status_code=500, detail="Failed to reach GitHub API")
