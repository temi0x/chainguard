import os
import asyncio
from typing import Dict, Any
from datetime import datetime
import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ChainGuard AI Q&A API - Local",
    description="Ask questions about ChainGuard AI DeFi Risk Assessment Platform",
    version="1.0.0"
)

# Add CORS middleware for local frontend testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration - Local Development
PROJECT_ID = "chainguardai"
LOCATION = "us-central1"
MODEL_NAME = "gemini-2.5-flash-preview-0827"
SERVICE_ACCOUNT_PATH = "./chainguardai-1728b786facc.json"

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

# Project context - based on the PDF
PROJECT_CONTEXT = """
ChainGuard AI: Autonomous DeFi Risk Assessment with LLM Agents

OVERVIEW:
ChainGuard AI is a revolutionary DeFi risk assessment platform that leverages cutting-edge Large Language Model (LLM) technology from Google's Gemini models and multi-agent artificial intelligence to provide unprecedented insights into protocol safety and investment viability.

CORE INNOVATION:
The first DeFi risk platform using a multi-agent LLM system powered by Google's Gemini models that can reason about complex protocol changes, governance decisions, and market dynamics while automatically adapting to the rapidly evolving DeFi landscape.

TEAM:
- Dayo: AI/ML Engineer (Python) - Agent Development & LLM Integration
- Charles: DevOps Engineer (Golang) - Infrastructure & Deployment  
- Temi: Full Stack & Blockchain Engineer (Golang) + UI/UX - Smart Contracts & Frontend
- Collins: Backend Engineer (Python) - API Development & Data Pipeline

KEY PROBLEMS SOLVED:
1. Static Data Sources Crisis - Deprecated endpoints, manual updates, single points of failure
2. Limited Intelligence - Binary decision making, lack of narrative understanding, no adaptability
3. Poor User Experience - Black box scoring, technical complexity, reactive monitoring

SOLUTION - INTELLIGENT AGENT NETWORK:
ChainGuard AI employs a multi-agent system where specialized AI agents collaborate to assess protocol risk:

1. Data Hunter Agent 🔍 - Ensures data reliability and discovers new sources dynamically
2. Protocol Analyst Agent 🔬 - Deep technical analysis of smart contracts and architecture  
3. Market Intelligence Agent 📊 - Analyzes financial health and sustainability
4. Risk Synthesizer Agent 🧠 - Combines all agent insights into comprehensive assessments

CHAINLINK INTEGRATION:
- Chainlink Functions: AI-to-Blockchain Bridge for decentralized computation
- Chainlink Automation: Proactive risk monitoring with intelligent triggers
- Chainlink Data Feeds: Reliable price data for financial health validation

TECHNICAL ARCHITECTURE:
- Backend: Python FastAPI, PostgreSQL, Redis, async processing
- AI/ML: Google Gemini models, multi-agent orchestration, prompt engineering
- Blockchain: Solidity smart contracts, Chainlink integration, Go utilities
- Frontend: React 18, TypeScript, Material-UI, real-time WebSocket updates
- Infrastructure: Docker, AWS/GCP, automated CI/CD, monitoring with Prometheus/Grafana

RISK SCORING METHODOLOGY:
Multi-dimensional risk calculation with weighted components:
- Protocol Security: 35% (Smart contract risks, audits, vulnerability assessment)
- Financial Health: 30% (TVL, liquidity, sustainability, revenue models)
- Governance Quality: 25% (Decentralization, governance participation, proposal quality)
- Data Quality: 10% (Data reliability, source validation, freshness)

Risk Categories:
- 0-30: LOW RISK 🟢 (Excellent to Good - established, audited protocols)
- 31-70: MEDIUM RISK 🟡 (Moderate to Concerning - exercise caution)  
- 71-100: HIGH RISK 🔴 (High to Extreme - significant risks identified)

COMPETITIVE ADVANTAGES:
1. Agent-Based Architecture - First-of-its-kind multi-agent LLM system
2. Dynamic Data Discovery - Automatically adapts to data source changes
3. Natural Language Risk Communication - Explains complex risks conversationally
4. Proactive Monitoring - Context-aware assessment beyond simple metrics

MONETIZATION:
- API Services: Free tier (10 queries/day), Pro ($99/month), Enterprise ($999/month)
- Institutional Services: DAO treasury management, protocol insurance, regulatory reporting
- Data Licensing: Risk intelligence, agent insights, market data

FUTURE ROADMAP:
- Phase 1: Production launch with 500+ protocols across multiple chains
- Phase 2: Ecosystem integration with wallets, DEX aggregators, DAO tools
- Phase 3: Advanced intelligence with cross-chain assessment and predictive modeling

The platform represents the next evolution of DeFi risk assessment, combining cutting-edge AI with blockchain infrastructure to solve critical problems in the rapidly evolving DeFi landscape.
"""

# Global model instance
model = None

def check_service_account():
    """Check if service account file exists"""
    if not os.path.exists(SERVICE_ACCOUNT_PATH):
        logger.error(f"❌ Service account file not found: {SERVICE_ACCOUNT_PATH}")
        logger.error("   Please ensure chainguardai-1728b786facc.json is in the project directory")
        raise FileNotFoundError(f"Service account file not found: {SERVICE_ACCOUNT_PATH}")
    
    logger.info(f"✅ Service account file found: {SERVICE_ACCOUNT_PATH}")

async def initialize_vertex_ai():
    """Initialize Vertex AI and Gemini model"""
    global model
    
    try:
        # Check service account file
        check_service_account()
        
        # Set environment variable for authentication
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_PATH
        
        # Initialize Vertex AI
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        
        # Create Gemini model instance
        model = GenerativeModel(MODEL_NAME)
        
        logger.info(f"✅ Vertex AI initialized successfully")
        logger.info(f"   📁 Project: {PROJECT_ID}")
        logger.info(f"   🌎 Location: {LOCATION}")
        logger.info(f"   🤖 Model: {MODEL_NAME}")
        logger.info(f"   🔑 Service Account: {SERVICE_ACCOUNT_PATH}")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Vertex AI: {e}")
        logger.error(f"   Make sure:")
        logger.error(f"   1. Service account file exists: {SERVICE_ACCOUNT_PATH}")
        logger.error(f"   2. Vertex AI API is enabled in your project")
        logger.error(f"   3. Service account has proper permissions")
        raise

def create_prompt(question: str) -> str:
    """Create a well-structured prompt for the Gemini model"""
    return f"""You are ChainGuard AI Assistant, an expert on the ChainGuard AI DeFi Risk Assessment Platform. You have comprehensive knowledge about the project based on the following context:

{PROJECT_CONTEXT}

INSTRUCTIONS:
- Answer questions about ChainGuard AI clearly and accurately
- Use the provided context as your primary knowledge source
- If asked about technical details, refer to the specific components mentioned
- If asked about team members, mention their roles and specializations
- Be conversational but informative
- If the question is outside the scope of ChainGuard AI, politely redirect to the project
- Keep responses focused and relevant to DeFi risk assessment and the ChainGuard platform

USER QUESTION: {question}

RESPONSE (provide a helpful, accurate answer based on the ChainGuard AI project context):"""

async def get_gemini_response(question: str) -> Dict[str, Any]:
    """Get response from Gemini model"""
    global model
    
    if not model:
        raise HTTPException(status_code=500, detail="Gemini model not initialized")
    
    try:
        # Create prompt
        prompt = create_prompt(question)
        
        # Configure generation parameters
        generation_config = GenerationConfig(
            temperature=0.3,  # Balanced creativity and consistency
            top_p=0.8,
            top_k=40,
            max_output_tokens=1000,
        )
        
        # Generate response
        logger.info(f"🤖 Generating response for question: {question[:50]}...")
        
        response = await asyncio.to_thread(
            model.generate_content,
            prompt,
            generation_config=generation_config
        )
        
        if not response.text:
            raise Exception("Empty response from Gemini")
        
        # Calculate confidence score (simple heuristic)
        confidence = min(0.95, 0.7 + (len(response.text) / 2000))
        
        logger.info(f"✅ Response generated successfully (confidence: {confidence:.2f})")
        
        return {
            "answer": response.text.strip(),
            "confidence": round(confidence, 2),
            "timestamp": datetime.utcnow().isoformat(),
            "model_used": MODEL_NAME
        }
        
    except Exception as e:
        logger.error(f"❌ Gemini API error: {e}")
        raise HTTPException(status_code=500, detail=f"AI model error: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🚀 Starting ChainGuard AI Q&A API (Local)")
    await initialize_vertex_ai()
    logger.info("✅ API ready to serve requests!")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "ChainGuard AI Q&A API - Local",
        "version": "1.0.0",
        "description": "Ask questions about ChainGuard AI DeFi Risk Assessment Platform",
        "mode": "local_development",
        "endpoints": {
            "ask": "POST /ask - Ask a question about ChainGuard AI",
            "health": "GET /health - Health check",
            "docs": "GET /docs - API documentation"
        },
        "status": "ready"
    }

@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question about ChainGuard AI
    
    Submit any question about the ChainGuard AI platform, its features,
    technical architecture, team, or DeFi risk assessment capabilities.
    """
    try:
        logger.info(f"📥 Question received: {request.question[:100]}...")
        
        # Get AI response
        ai_response = await get_gemini_response(request.question)
        
        logger.info(f"📤 Response sent (confidence: {ai_response['confidence']})")
        
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
        # Check if service account file exists
        service_account_exists = os.path.exists(SERVICE_ACCOUNT_PATH)
        
        # Test Gemini model availability
        model_available = model is not None
        
        status = "healthy" if (service_account_exists and model_available) else "unhealthy"
        
        return {
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "model": MODEL_NAME,
            "project": PROJECT_ID,
            "mode": "local_development",
            "checks": {
                "service_account_file": service_account_exists,
                "gemini_model": model_available
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "reason": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"❌ Unhandled exception: {exc}")
    return {"error": "Internal server error", "detail": str(exc)}

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 ChainGuard AI Q&A API - Local Development")
    print("=" * 50)
    print("🌐 Starting server on http://localhost:8000")
    print("📖 API docs available at http://localhost:8000/docs")
    print("🏥 Health check at http://localhost:8000/health")
    print("=" * 50)
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info",
        reload=True  # Auto-reload on code changes
    )