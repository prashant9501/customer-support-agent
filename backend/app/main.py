"""
FastAPI application for Customer Support Agent
Main entry point for the API server
"""
import logging
import uuid
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

from app.models.schemas import ChatRequest, ChatResponse, HealthResponse, ErrorResponse
from app.workflows.support_graph import compiled_support_agent
from app.database.vectordb import initialize_vectordb, get_retriever
from app.config.settings import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("Starting Customer Support Agent API...")
    try:
        # Initialize vector database
        initialize_vectordb()
        logger.info("Vector database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize vector database: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Customer Support Agent API...")


# Initialize FastAPI app
app = FastAPI(
    title="Customer Support Agent API",
    description="AI-powered customer support system with LangGraph workflow orchestration",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
allowed_origins = settings.allowed_origins.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (frontend)
import os
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=os.path.join(frontend_path, "static")), name="static")
    logger.info(f"Mounted static files from: {frontend_path}")


@app.get("/", response_class=FileResponse)
async def serve_frontend():
    """Serve the frontend HTML page"""
    frontend_index = os.path.join(frontend_path, "index.html")
    if os.path.exists(frontend_index):
        return FileResponse(frontend_index)
    return {"message": "Frontend not found. Access API docs at /docs"}


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns:
        Health status of the service and its dependencies
    """
    try:
        # Check if retriever is accessible
        retriever = get_retriever()
        vectordb_status = "connected" if retriever else "disconnected"
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        vectordb_status = "error"
    
    return HealthResponse(
        status="healthy" if vectordb_status == "connected" else "unhealthy",
        vectordb=vectordb_status,
        timestamp=datetime.now()
    )


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Process a customer support query
    
    Args:
        request: Chat request containing query and optional session_id
        
    Returns:
        Chat response with AI-generated answer and metadata
        
    Raises:
        HTTPException: If processing fails
    """
    try:
        # Generate or use provided session ID
        session_id = request.session_id or str(uuid.uuid4())
        
        logger.info(f"Processing chat request - Session: {session_id}, Query: {request.query[:100]}...")
        
        # Validate query length
        if len(request.query) > settings.max_query_length:
            raise HTTPException(
                status_code=400,
                detail=f"Query too long. Maximum length is {settings.max_query_length} characters."
            )
        
        if not request.query.strip():
            raise HTTPException(
                status_code=400,
                detail="Query cannot be empty."
            )
        
        # Run the support agent workflow
        result = compiled_support_agent.invoke(
            {"customer_query": request.query},
            {"configurable": {"thread_id": session_id}}
        )
        
        # Extract response data
        response = ChatResponse(
            response=result.get("final_response", "I apologize, but I couldn't generate a response."),
            category=result.get("query_category", "General"),
            sentiment=result.get("query_sentiment", "Neutral"),
            session_id=session_id,
            timestamp=datetime.now()
        )
        
        logger.info(f"Chat request processed successfully - Session: {session_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for real-time chat
    
    Accepts WebSocket connections and processes messages in real-time
    """
    await websocket.accept()
    session_id = str(uuid.uuid4())
    logger.info(f"WebSocket connection established - Session: {session_id}")
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            logger.info(f"WebSocket message received - Session: {session_id}, Query: {data[:100]}...")
            
            try:
                # Validate query
                if len(data) > settings.max_query_length:
                    await websocket.send_json({
                        "error": f"Query too long. Maximum length is {settings.max_query_length} characters."
                    })
                    continue
                
                if not data.strip():
                    await websocket.send_json({
                        "error": "Query cannot be empty."
                    })
                    continue
                
                # Run support agent
                result = compiled_support_agent.invoke(
                    {"customer_query": data},
                    {"configurable": {"thread_id": session_id}}
                )
                
                # Send response
                await websocket.send_json({
                    "response": result.get("final_response", "I apologize, but I couldn't generate a response."),
                    "category": result.get("query_category", "General"),
                    "sentiment": result.get("query_sentiment", "Neutral"),
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"WebSocket response sent - Session: {session_id}")
                
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}", exc_info=True)
                await websocket.send_json({
                    "error": f"Error processing your request: {str(e)}"
                })
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected - Session: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)


@app.get("/api/status")
async def status():
    """
    API status endpoint
    
    Returns:
        Current API status and configuration info
    """
    return {
        "status": "online",
        "version": "1.0.0",
        "model": settings.llm_model,
        "max_query_length": settings.max_query_length,
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower()
    )
