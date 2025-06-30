# ChainGuard AI - Main.py Endpoint Payloads

## Base URL
```
https://chainguard-ai-792137755873.us-central1.run.app
```

---

## 1. Root Endpoint

### Request
```bash
curl -X GET https://chainguard-ai-792137755873.us-central1.run.app/ \
  -H "Accept: application/json"
```

### Response (Current Implementation)
```json
{
  "service": "ChainGuard AI",
  "version": "1.0.0",
  "description": "DeFi Protocol Risk Assessment using ADK Multi-Agent System",
  "system_status": "simplified_mode",
  "initialization": {
    "attempted": false,
    "successful": false,
    "timestamp": null
  },
  "endpoints": {
    "assess": "POST /assess/{protocol_name}",
    "protocols": "GET /protocols",
    "health": "GET /health",
    "agents": "GET /agents/status"
  },
  "documentation": "/docs"
}
```

**Status Code:** `200 OK`

---

## 2. Health Check Endpoint

### Request
```bash
curl -X GET https://chainguard-ai-792137755873.us-central1.run.app/health \
  -H "Accept: application/json"
```

### Response (Always Available)
```json
{
  "status": "healthy",
  "service": "chainguard-ai",
  "environment": "production",
  "timestamp": "2025-06-30T15:30:00.433601",
  "system_mode": "simplified_mode",
  "message": "Service is operational"
}
```

**Status Code:** `200 OK`

---

## 3. Protocols Endpoint

### Request
```bash
curl -X GET https://chainguard-ai-792137755873.us-central1.run.app/protocols \
  -H "Accept: application/json"
```

### Response (Fallback List - Current)
```json
{
  "supported_protocols": [
    "aave-v3",
    "compound-v3", 
    "uniswap-v3",
    "makerdao",
    "curve",
    "balancer-v2",
    "yearn-finance",
    "convex-finance",
    "lido",
    "rocket-pool",
    "frax-finance",
    "euler",
    "morpho",
    "radiant-capital",
    "benqi"
  ],
  "total_count": 15,
  "last_updated": "2025-06-30T15:30:00.834061",
  "source": "fallback_list"
}
```

**Status Code:** `200 OK`

---

## 4. System Status Endpoint

### Request
```bash
curl -X GET https://chainguard-ai-792137755873.us-central1.run.app/system/status \
  -H "Accept: application/json"
```

### Response (Before Initialization)
```json
{
  "initialization": {
    "attempted": false,
    "successful": false,
    "error": null,
    "timestamp": null
  },
  "components": {
    "orchestrator": false,
    "protocol_validator": false,
    "memory_manager": false
  },
  "memory_health": {
    "status": "not_available"
  },
  "timestamp": "2025-06-30T15:30:00.123456"
}
```

### Response (After Failed Initialization)
```json
{
  "initialization": {
    "attempted": true,
    "successful": false,
    "error": "System initialization failed: 1 validation error for Settings\nGITHUB_TOKEN\n  Field required",
    "timestamp": "2025-06-30T15:25:00.123456"
  },
  "components": {
    "orchestrator": false,
    "protocol_validator": false,
    "memory_manager": false
  },
  "memory_health": {
    "status": "not_available"
  },
  "timestamp": "2025-06-30T15:30:00.123456"
}
```

**Status Code:** `200 OK`

---

## 5. Agent Status Endpoint

### Request
```bash
curl -X GET https://chainguard-ai-792137755873.us-central1.run.app/agents/status \
  -H "Accept: application/json"
```

### Response (Current - Initialization Failed)
```json
{
  "orchestrator_status": "not_initialized",
  "total_agents": 0,
  "healthy_agents": 0,
  "adk_integration": "initialization_failed",
  "error": "System initialization failed: 1 validation error for Settings\nGITHUB_TOKEN\n  Field required [type=missing, input_value={'ENVIRONMENT': 'production', 'PORT': '8080'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.11/v/missing",
  "message": "Agent system not available. Using simplified mode."
}
```

### Response (If System Initializes Successfully)
```json
{
  "orchestrator_status": "healthy",
  "total_agents": 1,
  "healthy_agents": 1,
  "adk_integration": "phase3_compatible",
  "agents": {
    "data_hunter": {
      "agent_id": "data_hunter",
      "status": "healthy",
      "model_type": "flash",
      "specialized_tools": 3,
      "timestamp": "2025-06-30T15:30:00.123456"
    }
  }
}
```

**Status Code:** `200 OK`

---

## 6. Protocol Risk Assessment Endpoint

### Request
```bash
curl -X POST https://chainguard-ai-792137755873.us-central1.run.app/assess/aave-v3 \
  -H "Accept: application/json" \
  -H "Content-Type: application/json"
```

### Response (Current - Simplified Mode)
```json
{
  "protocol_name": "aave-v3",
  "overall_risk_score": 50.0,
  "risk_level": "Unknown",
  "confidence": 0.3,
  "analysis_timestamp": "2025-06-30T15:45:23.209865",
  "executive_summary": "Basic assessment for aave-v3. Full agent system temporarily unavailable.",
  "status": "simplified_mode",
  "message": "ChainGuard AI is running in simplified mode. Full analysis capabilities will be restored shortly.",
  "recommendation": "Try again in a few minutes for comprehensive analysis."
}
```

### Response (If Agent System Works)
```json
{
  "protocol_name": "aave-v3",
  "overall_risk_score": 40.0,
  "risk_level": "Medium",
  "confidence": 0.85,
  "analysis_timestamp": "2025-06-30T15:45:23.123456",
  "executive_summary": "Limited assessment completed for aave-v3. Data sources validated successfully. Additional agents pending implementation.",
  "component_scores": {
    "data_availability": 85.0,
    "source_reliability": "comprehensive"
  },
  "data_quality": "Good",
  "agents_executed": ["data_hunter"],
  "session_id": "session_a1b2c3d4_20250630_154523"
}
```

### Response (Agent System Error Fallback)
```json
{
  "protocol_name": "aave-v3",
  "overall_risk_score": 50.0,
  "risk_level": "Unknown",
  "confidence": 0.3,
  "analysis_timestamp": "2025-06-30T15:45:23.123456",
  "executive_summary": "Basic assessment for aave-v3. Full agent system temporarily unavailable.",
  "status": "simplified_mode",
  "message": "ChainGuard AI is running in simplified mode. Full analysis capabilities will be restored shortly.",
  "recommendation": "Try again in a few minutes for comprehensive analysis.",
  "error": "Full assessment failed: ModuleNotFoundError: No module named 'tools'",
  "fallback_reason": "agent_system_error"
}
```

**Status Code:** `200 OK`  
**Response Time:** <1 second for simplified, 5-15 seconds for full system

---

## Error Responses

### 400 Bad Request - Unsupported Protocol (If Validator Works)
```bash
curl -X POST https://chainguard-ai-792137755873.us-central1.run.app/assess/invalid-protocol
```

**Response:**
```json
{
  "error": {
    "error": "Protocol 'invalid-protocol' not supported",
    "supported_protocols": ["aave-v3", "compound-v3", "uniswap-v3", "makerdao", "curve", "balancer-v2", "yearn-finance", "convex-finance", "lido", "rocket-pool", "frax-finance", "euler", "morpho", "radiant-capital", "benqi"],
    "suggestion": "Check supported protocols at /protocols endpoint"
  },
  "status_code": 400,
  "timestamp": "2025-06-30T15:45:23.123456"
}
```
**Status Code:** `400 Bad Request`

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred",
  "timestamp": "2025-06-30T15:45:23.123456"
}
```
**Status Code:** `500 Internal Server Error`

---

## Key Characteristics

### Current Behavior
- **Health/Protocols**: Always work immediately
- **System Status**: Shows initialization failure details
- **Agent Status**: Shows specific error (GITHUB_TOKEN missing)
- **Assessment**: Always returns simplified response due to missing dependencies

### When System Works (After Fixing Dependencies)
- **Assessment**: Will return sophisticated DataHunterAgent results
- **Agent Status**: Will show healthy data_hunter agent
- **System Status**: Will show successful initialization

### Performance
| Endpoint | Current Response Time | Notes |
|----------|----------------------|-------|
| `/health` | <50ms | Always works |
| `/protocols` | <100ms | Fallback list |
| `/system/status` | <200ms | Shows init status |
| `/agents/status` | <500ms | Triggers init attempt |
| `/assess/*` | <1 second | Simplified mode only |

Your endpoints are well-designed with proper fallbacks - they just need the missing tool/model dependencies to unlock full functionality! 🎯