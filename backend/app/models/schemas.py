"""
Pydantic models for request/response validation
"""
from typing import Optional, TypedDict, Literal
from pydantic import BaseModel, Field
from datetime import datetime


# Request Models
class ChatRequest(BaseModel):
    """Chat request model"""
    query: str = Field(..., max_length=500, description="Customer query text")
    session_id: Optional[str] = Field(None, description="Session identifier for conversation context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What payment methods do you support?",
                "session_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


# Response Models
class ChatResponse(BaseModel):
    """Chat response model"""
    response: str = Field(..., description="AI-generated response")
    category: str = Field(..., description="Query category (Technical, Billing, General)")
    sentiment: str = Field(..., description="Query sentiment (Positive, Neutral, Negative)")
    session_id: str = Field(..., description="Session identifier")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "We support credit cards, PayPal, and bank transfers...",
                "category": "Billing",
                "sentiment": "Neutral",
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2025-10-15T12:34:56.789Z"
            }
        }


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    vectordb: str = Field(..., description="Vector database status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Check timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "vectordb": "connected",
                "timestamp": "2025-10-15T12:34:56.789Z"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Internal server error",
                "detail": "OpenAI API connection failed",
                "timestamp": "2025-10-15T12:34:56.789Z"
            }
        }


# LangGraph State Model (TypedDict for LangGraph compatibility)
class CustomerSupportState(TypedDict):
    """State model for LangGraph workflow"""
    customer_query: str
    query_category: str
    query_sentiment: str
    final_response: str
