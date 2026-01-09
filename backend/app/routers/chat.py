from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
import logging
from typing import Optional
import uuid

from app.settings import settings

router = APIRouter()
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str


class ChatResponse(BaseModel):
    """Chat response model."""
    answer: str
    trace_id: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: Request, chat_request: ChatRequest):
    """
    Chat endpoint that processes user messages.
    
    Currently returns a stub response. 
    Integration with OpenAI API is prepared but not required for local development.
    
    To enable OpenAI integration:
    1. Set OPENAI_API_KEY environment variable
    2. Uncomment the OpenAI integration section below
    3. Remove the stub response
    """
    trace_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    
    logger.info(
        f"Chat request received",
        extra={
            "trace_id": trace_id,
            "message_length": len(chat_request.message)
        }
    )
    
    # Validate input
    if not chat_request.message or len(chat_request.message.strip()) == 0:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # STUB RESPONSE - Safe for local development
    # This allows the application to run without OpenAI API key
    stub_answer = f"Echo: {chat_request.message} (This is a stub response. Configure OPENAI_API_KEY to enable AI responses.)"
    
    logger.info(
        f"Returning stub response",
        extra={"trace_id": trace_id}
    )
    
    return ChatResponse(
        answer=stub_answer,
        trace_id=trace_id
    )
    
    # ============================================================================
    # OPENAI INTEGRATION SECTION (Uncomment when ready to use)
    # ============================================================================
    # 
    # if not settings.openai_api_key:
    #     logger.warning("OpenAI API key not configured, returning stub response")
    #     return ChatResponse(
    #         answer="OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.",
    #         trace_id=trace_id
    #     )
    # 
    # try:
    #     import openai
    #     
    #     # Configure OpenAI client
    #     client = openai.OpenAI(api_key=settings.openai_api_key)
    #     
    #     logger.info(f"Calling OpenAI API", extra={"trace_id": trace_id})
    #     
    #     # Call OpenAI API
    #     response = client.chat.completions.create(
    #         model=settings.openai_model,
    #         messages=[
    #             {"role": "system", "content": "You are a helpful assistant."},
    #             {"role": "user", "content": chat_request.message}
    #         ],
    #         max_tokens=settings.openai_max_tokens,
    #         temperature=settings.openai_temperature
    #     )
    #     
    #     answer = response.choices[0].message.content
    #     
    #     logger.info(
    #         f"OpenAI response received",
    #         extra={
    #             "trace_id": trace_id,
    #             "model": settings.openai_model,
    #             "tokens_used": response.usage.total_tokens
    #         }
    #     )
    #     
    #     return ChatResponse(
    #         answer=answer,
    #         trace_id=trace_id
    #     )
    #     
    # except Exception as e:
    #     logger.error(
    #         f"Error calling OpenAI API: {str(e)}",
    #         extra={"trace_id": trace_id},
    #         exc_info=True
    #     )
    #     raise HTTPException(
    #         status_code=500,
    #         detail=f"Error processing chat request: {str(e)}"
    #     )
    # ============================================================================

# Made with Bob
