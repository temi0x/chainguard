import os
import asyncio
from typing import Dict, Any
from datetime import datetime
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import google.generativeai as genai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
MODEL_NAME = "gemini-2.5-pro"  # Default model
API_KEY = None  # Will be set from environment or service account

# Global variables
model = None

# Request/Response models
class QuestionRequest(BaseModel):
    question: str = Field(
        ..., 
        min_length=1, 
        max_length=1000, 
        description="Your question about ChainGuard AI"
    )

class QuestionResponse(BaseModel):
    answer: str
    confidence: float
    timestamp: str
    model_used: str

# Simple project context
PROJECT_CONTEXT = """
ChainGuard AI is a DeFi risk assessment platform that uses AI agents to analyze protocol safety.

Key Features:
- Multi-agent AI system for comprehensive risk analysis
- Uses Google Gemini models for intelligent reasoning
- Integrates with Chainlink for blockchain data
- Provides natural language explanations of risks

Team:
- Dayo: AI/ML Engineer (Python) - Agent Development & LLM Integration
- Charles: DevOps Engineer (Golang) - Infrastructure & Deployment  
- Temi: Full Stack & Blockchain Engineer (Golang) + UI/UX - Smart Contracts & Frontend
- Collins: Backend Engineer (Python) - API Development & Data Pipeline

The platform helps users understand DeFi protocol risks through:
1. Data Hunter Agent - Finds and validates data sources
2. Protocol Analyst Agent - Analyzes smart contracts and security
3. Market Intelligence Agent - Evaluates financial health
4. Risk Synthesizer Agent - Combines insights into clear risk assessments

Risk Scoring: 0-30 (Low Risk), 31-70 (Medium Risk), 71-100 (High Risk)

ChainGuard AI solves problems like deprecated data sources, lack of explainable AI in DeFi, and poor user experience in risk assessment.
"""

def get_api_key():
    """Get API key from environment or generate from service account"""
    
    # First try environment variable
    api_key = os.getenv('GOOGLE_AI_API_KEY') or os.getenv('GEMINI_API_KEY')
    if api_key:
        logger.info("✅ Using API key from environment variable")
        return api_key
    
    # Try to use service account to get access token
    try:
        import google.auth
        from google.auth.transport.requests import Request
        
        # Check if service account file exists
        service_account_path = "./chainguardai-1728b786facc.json"
        if os.path.exists(service_account_path):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account_path
            
            credentials, project = google.auth.default(
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
            
            # Refresh to get access token
            request = Request()
            credentials.refresh(request)
            
            if hasattr(credentials, 'token') and credentials.token:
                logger.info("✅ Using access token from service account")
                return credentials.token
        
    except Exception as e:
        logger.warning(f"⚠️ Could not get access token from service account: {e}")
    
    # If no API key found, provide instructions
    logger.error("❌ No API key found!")
    logger.error("Please set up authentication by either:")
    logger.error("1. Set GOOGLE_AI_API_KEY environment variable")
    logger.error("2. Get a free API key from: https://makersuite.google.com/app/apikey")
    logger.error("3. Export it: export GOOGLE_AI_API_KEY='your_api_key_here'")
    
    return None

async def initialize_gemini():
    """Initialize Google AI Gemini model"""
    global model, MODEL_NAME, API_KEY
    
    try:
        # Get API key
        API_KEY = get_api_key()
        if not API_KEY:
            raise Exception("No API key available - see instructions above")
        
        # Configure Google AI
        genai.configure(api_key=API_KEY)
        
        # Try different models in order of preference
        model_names_to_try = [
            "gemini-1.5-flash",
            "gemini-1.5-pro", 
            "gemini-pro",
            "gemini-1.0-pro"
        ]
        
        model_initialized = False
        
        for model_name in model_names_to_try:
            try:
                logger.info(f"🧪 Trying to initialize model: {model_name}")
                
                # Create model instance
                test_model = genai.GenerativeModel(model_name)
                
                # Test the model with a simple request
                test_response = await asyncio.to_thread(
                    test_model.generate_content,
                    "Test: Respond with 'Hello ChainGuard'",
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1,
                        max_output_tokens=50
                    )
                )
                
                if test_response.text and 'ChainGuard' in test_response.text:
                    model = test_model
                    MODEL_NAME = model_name
                    model_initialized = True
                    logger.info(f"✅ Model successfully initialized and tested: {model_name}")
                    break
                else:
                    logger.warning(f"⚠️ Model {model_name} responded but test failed")
                    
            except Exception as e:
                logger.warning(f"⚠️ Model {model_name} failed: {str(e)}")
                continue
        
        if not model_initialized:
            raise Exception("No Gemini model could be initialized")
        
        logger.info(f"✅ Google AI initialized successfully")
        logger.info(f"   🤖 Model: {MODEL_NAME}")
        logger.info(f"   🔑 Authentication: {'API Key' if len(API_KEY) < 100 else 'Access Token'}")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Google AI: {e}")
        raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup"""
    logger.info("🚀 Starting ChainGuard AI Q&A API")
    await initialize_gemini()
    logger.info("✅ API ready to serve requests!")
    yield
    logger.info("🛑 Shutting down ChainGuard AI Q&A API")

# Initialize FastAPI app
app = FastAPI(
    title="ChainGuard AI Q&A API",
    description="Ask questions about ChainGuard AI DeFi Risk Assessment Platform",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_prompt(question: str) -> str:
    """Create a simple prompt for the Gemini model"""
    return f"""You are a DeFi analyst and expert on ChainGuard AI. Answer questions about this platform clearly and helpfully.

Context about ChainGuard AI:
{PROJECT_CONTEXT}

User Question: {question}

Provide a clear, informative answer about ChainGuard AI based on the context above."""

async def get_gemini_response(question: str) -> Dict[str, Any]:
    """Get response from Gemini model"""
    global model
    
    if not model:
        raise HTTPException(status_code=500, detail="Gemini model not initialized")
    
    try:
        # Create prompt
        prompt = create_prompt(question)
        
        # Configure generation parameters
        generation_config = genai.types.GenerationConfig(
            temperature=0.3,
            top_p=0.8,
            top_k=40,
            max_output_tokens=800,
        )
        
        # Generate response
        logger.info(f"🤖 Generating response for: {question[:50]}...")
        
        response = await asyncio.to_thread(
            model.generate_content,
            prompt,
            generation_config=generation_config
        )
        
        if not response.text:
            raise Exception("Empty response from Gemini")
        
        # Simple confidence score
        confidence = 0.85  # Fixed confidence for simplicity
        
        logger.info(f"✅ Response generated successfully")
        
        return {
            "answer": response.text.strip(),
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat(),
            "model_used": MODEL_NAME
        }
        
    except Exception as e:
        logger.error(f"❌ Gemini API error: {e}")
        raise HTTPException(status_code=500, detail=f"AI model error: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "ChainGuard AI Q&A API",
        "version": "1.0.0",
        "description": "Ask questions about ChainGuard AI DeFi Risk Assessment Platform",
        "endpoints": {
            "ask": "POST /ask - Ask a question about ChainGuard AI",
            "health": "GET /health - Health check",
            "docs": "GET /docs - API documentation"
        },
        "status": "ready",
        "model": MODEL_NAME,
        "api_type": "Google AI (Direct)"
    }

@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Ask a question about ChainGuard AI"""
    try:
        logger.info(f"📥 Question received: {request.question[:100]}...")
        
        # Get AI response
        ai_response = await get_gemini_response(request.question)
        
        logger.info(f"📤 Response sent")
        
        return QuestionResponse(**ai_response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if API key is available
        api_key_available = API_KEY is not None
        model_available = model is not None
        
        # Test model with a simple call
        model_working = False
        if model_available:
            try:
                test_response = await asyncio.to_thread(
                    model.generate_content,
                    "Test: Respond with 'OK'",
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1,
                        max_output_tokens=10
                    )
                )
                model_working = 'OK' in (test_response.text or '')
            except:
                model_working = False
        
        status = "healthy" if (api_key_available and model_available and model_working) else "unhealthy"
        
        return {
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "model": MODEL_NAME,
            "api_type": "Google AI (Direct)",
            "checks": {
                "api_key_available": api_key_available,
                "gemini_model_available": model_available,
                "gemini_model_working": model_working
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "reason": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/setup")
async def setup_instructions():
    """Provide setup instructions if API key is missing"""
    return {
        "title": "ChainGuard AI Setup Instructions",
        "status": "API Key Required",
        "instructions": [
            "1. Get a free Google AI API key from: https://makersuite.google.com/app/apikey",
            "2. Set the environment variable: export GOOGLE_AI_API_KEY='your_api_key_here'", 
            "3. Restart the server: python main.py",
            "4. Test with: curl http://localhost:8000/health"
        ],
        "alternative": "You can also set GEMINI_API_KEY instead of GOOGLE_AI_API_KEY",
        "note": "This is much easier than setting up Vertex AI and works immediately!"
    }

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 ChainGuard AI Q&A API - Local Development")
    print("=" * 50)
    print("🌐 Starting server on http://localhost:8000")
    print("📖 API docs available at http://localhost:8000/docs")
    print("🏥 Health check at http://localhost:8000/health")
    print("🔧 Setup help at http://localhost:8000/setup")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )