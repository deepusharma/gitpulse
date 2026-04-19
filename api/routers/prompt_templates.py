from fastapi import APIRouter, HTTPException
import logging
from typing import List

from api.models import PromptTemplateCreate, PromptTemplateResponse
from api.db import get_db_pool

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/prompt-templates", tags=["prompt-templates"])

@router.post("", response_model=PromptTemplateResponse, status_code=201)
async def create_prompt_template(req: PromptTemplateCreate):
    db_pool = get_db_pool()
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database integration disabled")
    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                '''
                INSERT INTO prompt_templates (username, name, content)
                VALUES ($1, $2, $3)
                RETURNING id, username, name, content, created_at
                ''',
                req.username,
                req.name,
                req.content,
            )
            return PromptTemplateResponse(
                id=str(row["id"]),
                username=row["username"],
                name=row["name"],
                content=row["content"],
                created_at=row["created_at"].strftime("%Y-%m-%dT%H:%M:%SZ"),
            )
    except Exception as exc:
        logger.error("Failed to create prompt template: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create prompt template")

@router.get("", response_model=List[PromptTemplateResponse])
async def list_prompt_templates(username: str):
    db_pool = get_db_pool()
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database integration disabled")
    try:
        async with db_pool.acquire() as conn:
            rows = await conn.fetch(
                '''
                SELECT id, username, name, content, created_at
                FROM prompt_templates
                WHERE username = $1
                ORDER BY created_at DESC
                ''',
                username,
            )
            return [
                PromptTemplateResponse(
                    id=str(r["id"]),
                    username=r["username"],
                    name=r["name"],
                    content=r["content"],
                    created_at=r["created_at"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                )
                for r in rows
            ]
    except Exception as exc:
        logger.error("Failed to list prompt templates: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list prompt templates")

@router.delete("/{template_id}", status_code=204)
async def delete_prompt_template(template_id: str):
    db_pool = get_db_pool()
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database integration disabled")
    try:
        async with db_pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM prompt_templates WHERE id::text = $1",
                template_id,
            )
            if result == "DELETE 0":
                raise HTTPException(status_code=404, detail="Template not found")
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to delete prompt template: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete prompt template")
