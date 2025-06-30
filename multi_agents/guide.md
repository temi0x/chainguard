# 🎯 **Complete Multi-Agent System Understanding**

## **What We're Building**
**ChainGuard AI Multi-Agent DeFi Risk Assessment System** - A real-time protocol risk analyzer built entirely on Google's Agent Development Kit (ADK) using 4 specialized AI agents to provide comprehensive risk scores with natural language explanations.

## **Core Architecture**
- **4 Google ADK Agents**: Data Hunter → Protocol Analyst + Market Intelligence (parallel) → Risk Synthesizer
- **Google ADK Framework**: Complete multi-agent system built on ADK infrastructure
- **ADK Memory Services**: Session coordination and inter-agent state sharing
- **ADK Tool Integration**: External API calls through ADK's tool calling framework
- **Redis Caching**: 10-minute TTL for completed assessments
- **No Database**: Everything in memory, real-time only
- **Cloud Run Deployment**: HTTP service with direct frontend integration

## **Technology Stack**

### **Core Framework**
- **Google ADK** (Agent Development Kit) - **ENTIRE multi-agent system framework**
- **Google Gemini 2.0** (via ADK) - LLM integration through ADK's client
- **ADK Runners** - agent execution and coordination
- **ADK Tools** - external API integration pattern

### **Memory & State Management**
- **ADK InMemorySessionService** - agent state sharing during assessment
- **ADK InMemoryMemoryService** - agent context and long-term memory
- **ADK Session Management** - workflow coordination between agents
- **Redis** - optional caching for performance (no persistence)

### **Agent Implementation**
- **ADK Agent Classes** - base agent framework from Google ADK
- **ADK Function Calling** - tool integration and external API calls
- **ADK Context Management** - session and invocation context handling
- **ADK Response Parsing** - structured output processing

### **HTTP Layer**
- **FastAPI** - minimal wrapper for HTTP endpoints
- **No Docker** - Google Cloud Run buildpacks

### **External Data Sources (via ADK Tools)**
- **GitHub API** - repository analysis
- **DeFiLlama API** - TVL and protocol metrics
- **CoinGecko API** - market data
- **Etherscan API** - contract verification
- **The Graph** - subgraph queries

## **ADK Integration Pattern**
```python
from google.adk import Agent, Runner, Tool
from google.adk.memory import InMemoryMemoryService
from google.adk.sessions import InMemorySessionService

# Each agent built using ADK's Agent class
class DataHunterAgent(Agent):
    def __init__(self):
        super().__init__(tools=[GitHubTool(), SubgraphTool()])

# Orchestration using ADK Runners
runner = Runner(
    agent=data_hunter_agent,
    session_service=InMemorySessionService(),
    memory_service=InMemoryMemoryService()
)
```

## **Deployment & Integration**
- **Target**: Google Cloud Run
- **Output**: Single endpoint URL for frontend integration
- **Response**: Comprehensive JSON (15-25KB) with detailed risk analysis

---

# 📋 **Step-by-Step Implementation Workflow**

## **Phase 1: Google ADK Setup & Project Structure**
**Duration**: 45 minutes

### **Step 1.1: Project Structure**
```
chainguard-multi-agent/
├── requirements.txt
├── .env.example
├── main.py                    # FastAPI wrapper
├── protocols.json             # Supported protocols list
├── config/
│   └── settings.py
├── agents/
│   ├── base_adk_agent.py      # ADK Agent base class
│   ├── data_hunter_agent.py   # ADK Agent implementation
│   ├── protocol_analyst_agent.py
│   ├── market_intelligence_agent.py
│   └── risk_synthesizer_agent.py
├── tools/
│   ├── github_adk_tool.py     # ADK Tool implementations
│   ├── defi_data_adk_tool.py
│   └── blockchain_adk_tool.py
├── orchestrator/
│   └── adk_orchestrator.py    # ADK Runner coordination
├── memory/
│   └── adk_memory_manager.py  # ADK Memory services
├── utils/
│   └── protocol_validator.py  # Protocol validation utilities
└── models/
    └── response_models.py
```

### **Step 1.1.1: Protocol Configuration**
```json
// protocols.json - Supported protocols for risk assessment
[
  "Aave V3/V4",
  "Lido (stETH)",
  "EigenLayer", 
  "Ethena (USDe)",
  "Pendle Finance",
  "Uniswap V4"
]
```

```python
# utils/protocol_validator.py
import json
from typing import List, Optional

class ProtocolValidator:
    def __init__(self, protocols_file: str = "protocols.json"):
        with open(protocols_file, 'r') as f:
            self.supported_protocols = json.load(f)
    
    def is_supported(self, protocol_name: str) -> bool:
        """Check if protocol is in supported list"""
        return protocol_name in self.supported_protocols
    
    def normalize_name(self, protocol_name: str) -> Optional[str]:
        """Normalize protocol name to match supported list"""
        protocol_lower = protocol_name.lower()
        for supported in self.supported_protocols:
            if protocol_lower in supported.lower():
                return supported
        return None
    
    def get_all_protocols(self) -> List[str]:
        """Get list of all supported protocols"""
        return self.supported_protocols
```

### **Step 1.2: ADK Dependencies Installation**
```txt
google-adk-python
google-generativeai
google-cloud-aiplatform
redis[asyncio]
fastapi
uvicorn
httpx
aiofiles
pydantic
python-dotenv
```

### **Step 1.3: ADK + Vertex AI Authentication Setup**
```python
# config/settings.py
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Vertex AI / ADK Authentication
    GOOGLE_APPLICATION_CREDENTIALS: str = "path/to/service-account.json"
    VERTEX_AI_PROJECT_ID: str = "your-project-id"
    VERTEX_AI_LOCATION: str = "us-central1"
    
    # Gemini Model Configuration
    GEMINI_MODEL_NAME: str = "gemini-2.0-flash-exp"
    GEMINI_PRO_MODEL: str = "gemini-1.5-pro"
    
    # External API Keys
    GITHUB_TOKEN: str
    DEFILLAMA_API_KEY: str = ""
    COINGECKO_API_KEY: str = ""
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"

# Initialize authentication for entire application
settings = Settings()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.GOOGLE_APPLICATION_CREDENTIALS
```

**Setup Tasks:**
- Place your service account JSON file in project root
- Configure Vertex AI project ID and location
- Set environment variables for authentication
- Initialize ADK memory services with Vertex AI credentials

---

## **Phase 2: ADK Memory Services & Base Infrastructure**
**Duration**: 1 hour

### **Step 2.1: ADK Memory Manager with Vertex AI Authentication**
```python
from google.adk.memory import InMemoryMemoryService
from google.adk.sessions import InMemorySessionService
from google.adk.llm import VertexAILLM
import vertexai
import redis.asyncio as redis

class ADKMemoryManager:
    def __init__(self, settings: Settings):
        # Initialize Vertex AI with service account
        vertexai.init(
            project=settings.VERTEX_AI_PROJECT_ID,
            location=settings.VERTEX_AI_LOCATION
        )
        
        # ADK Memory Services
        self.memory_service = InMemoryMemoryService()
        self.session_service = InMemorySessionService()
        
        # Redis Cache (optional)
        self.redis_cache = redis.from_url(settings.REDIS_URL)
        
        # ADK LLM Integration
        self.gemini_flash = VertexAILLM(
            project_id=settings.VERTEX_AI_PROJECT_ID,
            location=settings.VERTEX_AI_LOCATION,
            model_name=settings.GEMINI_MODEL_NAME
        )
        
        self.gemini_pro = VertexAILLM(
            project_id=settings.VERTEX_AI_PROJECT_ID,
            location=settings.VERTEX_AI_LOCATION,
            model_name=settings.GEMINI_PRO_MODEL
        )
```

### **Step 2.2: Base ADK Agent Class with Gemini Integration**
```python
from google.adk import Agent
from google.adk.context import InvocationContext
from google.adk.llm import VertexAILLM
from typing import List, Dict, Any

class BaseChainGuardAgent(Agent):
    def __init__(self, agent_id: str, tools: List[Tool], model_type: str = "flash"):
        # Select appropriate Gemini model based on agent needs
        if model_type == "pro":
            llm = VertexAILLM(
                project_id=settings.VERTEX_AI_PROJECT_ID,
                model_name=settings.GEMINI_PRO_MODEL  # For complex reasoning
            )
        else:
            llm = VertexAILLM(
                project_id=settings.VERTEX_AI_PROJECT_ID,
                model_name=settings.GEMINI_MODEL_NAME  # For fast execution
            )
        
        super().__init__(llm=llm, tools=tools)
        self.agent_id = agent_id
        
    async def execute_with_context(self, context: InvocationContext) -> Dict[str, Any]:
        """Execute agent with proper ADK context management"""
        # ADK handles LLM calls with Vertex AI authentication automatically
        result = await self.execute(context)
        return {
            "agent_id": self.agent_id,
            "result": result,
            "confidence": self._calculate_confidence(result),
            "timestamp": datetime.utcnow()
        }
```

### **Step 2.3: Response Models**
- Risk assessment data structures
- ADK-compatible agent result models
- JSON serialization for HTTP responses

---

## **Phase 3: ADK Tools Implementation**
**Duration**: 1.5 hours

### **Step 3.1: ADK Tool Classes**
```python
from google.adk import Tool

class GitHubAnalysisTool(Tool):
    async def execute(self, protocol_name: str) -> Dict:
        # GitHub API integration
        pass

class DeFiLlamaDataTool(Tool):
    async def execute(self, protocol_name: str) -> Dict:
        # DeFiLlama API integration
        pass
```

### **Step 3.2: Tool Implementation Details**
- **GitHub ADK Tool**: Repository discovery, metrics extraction
- **DeFi Data ADK Tool**: DeFiLlama and CoinGecko integration
- **Blockchain ADK Tool**: Etherscan and subgraph queries
- **Error handling**: ADK tool error patterns
- **Rate limiting**: Built into ADK tool execution

---

## **Phase 4: ADK Agent Implementation**
**Duration**: 2.5 hours

### **Step 4.1: Data Hunter ADK Agent** (45 minutes)
```python
from google.adk import Agent
from google.adk.context import InvocationContext

class DataHunterAgent(BaseChainGuardAgent):
    def __init__(self, memory_manager: ADKMemoryManager):
        tools = [
            GitHubAnalysisTool(), 
            SubgraphDiscoveryTool(), 
            APIHealthTool()
        ]
        # Use Gemini Flash for fast data discovery
        super().__init__(
            agent_id="data_hunter",
            tools=tools,
            model_type="flash"
        )
        self.memory_manager = memory_manager
        
    async def execute(self, context: InvocationContext) -> Dict[str, Any]:
        protocol_name = context.parameters.get("protocol_name")
        
        # ADK automatically handles:
        # - Vertex AI authentication via service account
        # - Gemini model calls for reasoning
        # - Tool execution and result processing
        
        prompt = f"""
        You are a Data Hunter Agent for DeFi protocol analysis.
        Task: Discover and validate data sources for {protocol_name}
        
        Use available tools to:
        1. Find GitHub repositories
        2. Discover subgraph endpoints  
        3. Validate API health
        
        Return validated data sources with reliability scores.
        """
        
        # ADK handles LLM call with Vertex AI credentials
        analysis_plan = await self.llm.generate_content(prompt)
        
        # Execute tools based on LLM reasoning
        github_data = await self.tools[0].execute(protocol_name)
        subgraph_data = await self.tools[1].execute(protocol_name)
        health_data = await self.tools[2].execute([github_data, subgraph_data])
        
        # Store results in ADK session for other agents
        result = {
            "data_sources": {
                "github": github_data,
                "subgraphs": subgraph_data,
                "health_scores": health_data
            },
            "reliability_score": self._calculate_reliability(health_data),
            "reasoning": analysis_plan.text
        }
        
        # ADK session management handles state sharing
        await context.session.store(f"{self.agent_id}_result", result)
        
        return result
```

**Implementation Details:**
- **Vertex AI Integration**: Service account authentication handled automatically
- **Gemini Flash Model**: Fast reasoning for data discovery tasks
- **ADK Tool Execution**: External API calls through standardized tool pattern
- **Session State**: Results automatically available to other agents
- **Error Handling**: ADK provides robust error recovery for LLM and tool failures

### **Step 4.2: Protocol Analyst ADK Agent** (1 hour)
- **Purpose**: Security and governance analysis
- **ADK Tools**: Contract analysis, audit processing, governance evaluation
- **ADK Integration**: Tool calling, context management, result sharing

### **Step 4.3: Market Intelligence ADK Agent** (45 minutes)
- **Purpose**: Financial health analysis  
- **ADK Tools**: TVL analysis, market data processing, liquidity assessment
- **ADK Integration**: Parallel execution capability, session state access

### **Step 4.4: Risk Synthesizer ADK Agent** (20 minutes)
- **Purpose**: Combine all insights using ADK session data
- **ADK Integration**: Access previous agent results, consensus building
- **Output**: Final risk assessment with natural language explanation

---

## **Phase 5: ADK Orchestration & Workflow**
**Duration**: 1 hour

### **Step 5.1: ADK Runner Orchestration**
```python
from google.adk.runners import Runner

class ADKOrchestrator:
    def __init__(self):
        self.memory_manager = ADKMemoryManager()
        self.agents = self._initialize_adk_agents()
    
    async def assess_protocol_risk(self, protocol_name: str):
        # Create ADK session
        session_id = f"assessment_{protocol_name}_{timestamp}"
        
        # Execute agents using ADK Runners
        runner = Runner(
            agent=self.agents['data_hunter'],
            session_service=self.memory_manager.session_service,
            memory_service=self.memory_manager.memory_service,
            session_id=session_id
        )
```

### **Step 5.2: ADK Workflow Coordination**
- **Session Management**: ADK session creation and state sharing
- **Agent Execution**: Sequential and parallel agent coordination
- **Result Aggregation**: ADK session state access for synthesis
- **Caching Integration**: Redis cache with ADK workflow

---

## **Phase 6: FastAPI HTTP Wrapper**
**Duration**: 30 minutes

### **Step 6.1: Minimal API Endpoints with Protocol Validation**
```python
from fastapi import FastAPI, HTTPException
from orchestrator.adk_orchestrator import ADKOrchestrator
from utils.protocol_validator import ProtocolValidator

app = FastAPI()
adk_orchestrator = ADKOrchestrator()
protocol_validator = ProtocolValidator()

@app.post("/assess/{protocol_name}")
async def assess_protocol(protocol_name: str):
    # Validate protocol is supported
    normalized_name = protocol_validator.normalize_name(protocol_name)
    if not normalized_name:
        raise HTTPException(
            status_code=400, 
            detail=f"Protocol '{protocol_name}' not supported. Supported protocols: {protocol_validator.get_all_protocols()}"
        )
    
    result = await adk_orchestrator.assess_protocol_risk(normalized_name)
    return result.to_dict()

@app.get("/protocols")
async def get_supported_protocols():
    """Return list of supported protocols"""
    return {"supported_protocols": protocol_validator.get_all_protocols()}

@app.get("/health") 
async def health_check():
    return {"status": "healthy", "adk_version": "latest"}
```

### **Step 6.2: ADK Integration Layer**
- Request validation and ADK session initiation
- ADK orchestrator integration
- Response formatting from ADK results
- Error handling for ADK failures

---

## **Phase 7: Testing & Cloud Run Deployment**
**Duration**: 45 minutes

### **Step 7.1: ADK Agent Testing**
- Test individual ADK agents with mock tools
- Test ADK session state sharing between agents
- Test complete ADK workflow orchestration
- Validate JSON response format from ADK results

### **Step 7.2: Cloud Run Deployment with Vertex AI Authentication**
```yaml
# .env for deployment
GOOGLE_APPLICATION_CREDENTIALS=/app/service-account.json
VERTEX_AI_PROJECT_ID=your-project-id
VERTEX_AI_LOCATION=us-central1
GEMINI_MODEL_NAME=gemini-2.0-flash-exp
GEMINI_PRO_MODEL=gemini-1.5-pro
GITHUB_TOKEN=your_github_token
REDIS_URL=redis://your-redis-instance:6379
```

**Deployment Steps:**
- Include service account JSON in deployment package
- Configure environment variables for Vertex AI authentication
- Set up Cloud Run service with proper IAM permissions
- Test ADK agents with Vertex AI integration
- Verify Gemini model access through service account
- Validate complete multi-agent workflow

**Authentication Verification:**
```bash
# Test Vertex AI authentication
curl -X POST https://your-service.run.app/assess/aave-v3

# Expected: Full risk assessment JSON with all 4 agents working
# Confirms: Service account → Vertex AI → ADK → Gemini integration successful
```

---

## **📊 Expected Deliverables**

### **Final Output**
- **Cloud Run URL**: `https://your-service.run.app/assess/{protocol_name}`
- **ADK-Powered**: Complete multi-agent system built on Google ADK
- **Response Format**: Comprehensive JSON from ADK agent coordination
- **Performance**: 25-30 seconds for fresh analysis, <100ms for cached results
- **Integration Ready**: Direct frontend integration capability

### **Success Criteria**
✅ **ADK Multi-Agent System**: All 4 agents built using Google ADK framework  
✅ **Vertex AI Authentication**: Service account JSON properly integrated with ADK  
✅ **Gemini Integration**: Both Flash and Pro models accessible through ADK  
✅ **ADK Memory**: Session coordination and state sharing working  
✅ **ADK Tools**: External API integration through ADK tool pattern  
✅ **ADK Orchestration**: Runner-based agent coordination functioning  
✅ **Redis Caching**: Performance optimization layer  
✅ **Cloud Run Deployment**: ADK service with Vertex AI auth deployed successfully  
✅ **Frontend Integration**: Ready for direct website integration  

### **ADK + Vertex AI Architecture Benefits**
- **Native Google Integration**: Service account → Vertex AI → ADK → Gemini seamless flow
- **Built-in Coordination**: ADK handles agent communication automatically
- **Authenticated LLM Access**: Vertex AI credentials work throughout ADK framework
- **Tool Framework**: Standardized external API integration pattern
- **Memory Management**: ADK session and memory services handle state
- **Error Handling**: ADK provides robust error handling and recovery
- **Production Authentication**: Proper service account pattern for enterprise deployment
- **Scalability**: ADK designed for production multi-agent systems with Vertex AI

**Total Implementation Time**: ~7.5 hours

**Ready to start with Phase 1: Google ADK Setup?**