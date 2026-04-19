from fastapi import APIRouter, HTTPException
import httpx
import logging

from api.models import SlackDeliverRequest

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
