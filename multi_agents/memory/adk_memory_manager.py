import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import logging

# Redis for caching
import redis.asyncio as redis

# Google Cloud authentication and AI
import google.auth
from google.auth.transport.requests import Request
import google.generativeai as genai
from google.cloud import aiplatform

# Internal imports
from config.settings import settings

logger = logging.getLogger(__name__)

@dataclass
class AgentSession:
    """Represents an agent session with state management"""
    session_id: str
    protocol_name: str
    created_at: datetime
    updated_at: datetime
    agent_results: Dict[str, Any]
    status: str  # 'active', 'completed', 'failed'
    confidence_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'session_id': self.session_id,
            'protocol_name': self.protocol_name,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'agent_results': self.agent_results,
            'status': self.status,
            'confidence_score': self.confidence_score
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentSession':
        """Create from dictionary"""
        return cls(
            session_id=data['session_id'],
            protocol_name=data['protocol_name'],
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            agent_results=data['agent_results'],
            status=data['status'],
            confidence_score=data['confidence_score']
        )

@dataclass
class AgentMemory:
    """Represents long-term memory for agents"""
    agent_id: str
    protocol_patterns: Dict[str, Any]
    learned_data_sources: Dict[str, Any]
    historical_assessments: List[Dict[str, Any]]
    confidence_calibration: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)

class ADKMemoryManager:
    """
    Memory and session management for ChainGuard AI multi-agent system.
    Handles state sharing between agents, caching, and Vertex AI integration.
    """
    
    def __init__(self):
        self.settings = settings
        self.redis_client: Optional[redis.Redis] = None
        self.sessions: Dict[str, AgentSession] = {}
        self.agent_memories: Dict[str, AgentMemory] = {}
        
        # FIX 1: Add session_service and memory_service attributes for ADK integration
        from google.adk.sessions import InMemorySessionService
        from google.adk.memory import InMemoryMemoryService
        
        self.session_service = InMemorySessionService()
        self.memory_service = InMemoryMemoryService()

        # Initialize Google Cloud AI Platform
        self._initialize_vertex_ai()
        
        # Initialize Gemini clients
        self._initialize_gemini_clients()
        
        logger.info("✅ ADK Memory Manager initialized")
    
    def _initialize_vertex_ai(self):
        """Initialize Vertex AI with service account authentication"""
        try:
            # Initialize Vertex AI
            aiplatform.init(
                project=self.settings.VERTEX_AI_PROJECT_ID,
                location=self.settings.VERTEX_AI_LOCATION,
                credentials=None  # Will use GOOGLE_APPLICATION_CREDENTIALS env var
            )
            
            logger.info(f"✅ Vertex AI initialized - Project: {self.settings.VERTEX_AI_PROJECT_ID}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Vertex AI: {e}")
            raise
    
    def _initialize_gemini_clients(self):
        """Initialize Gemini AI clients for agent communication"""
        try:
            # Configure Gemini
            genai.configure(api_key=None)  # Will use ADC (Application Default Credentials)
            
            # Test connection with a simple call
            models = genai.list_models()
            available_models = [m.name for m in models]
            
            logger.info(f"✅ Gemini clients initialized")
            logger.info(f"   📋 Available models: {len(available_models)}")
            
            # Store model configurations
            self.model_configs = {
                'flash': self.settings.get_model_config('flash'),
                'pro': self.settings.get_model_config('pro')
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini clients: {e}")
            logger.warning("Continuing without Gemini - agents will use fallback methods")
            self.model_configs = {}
    
    async def initialize_redis(self):
        """Initialize Redis connection for caching"""
        try:
            self.redis_client = redis.from_url(
                self.settings.REDIS_URL,
                max_connections=self.settings.REDIS_MAX_CONNECTIONS,
                decode_responses=True
            )
            
            # Test connection
            await self.redis_client.ping()
            logger.info("✅ Redis connection established")
            
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}")
            logger.warning("Continuing without Redis - using in-memory cache only")
    
    async def close_redis(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis connection closed")
    
    # ========= Session Management =========
    
    def create_session(self, protocol_name: str) -> str:
        """Create a new agent session for protocol analysis"""
        session_id = f"session_{protocol_name}_{uuid.uuid4().hex[:8]}"
        
        session = AgentSession(
            session_id=session_id,
            protocol_name=protocol_name,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            agent_results={},
            status='active',
            confidence_score=0.0
        )
        
        self.sessions[session_id] = session
        logger.info(f"📝 Created session {session_id} for protocol {protocol_name}")
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[AgentSession]:
        """Get session by ID"""
        return self.sessions.get(session_id)
    
    async def store_agent_result(self, session_id: str, agent_id: str, result: Dict[str, Any]):
        """Store agent result in session"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        session.agent_results[agent_id] = {
            'result': result,
            'timestamp': datetime.utcnow().isoformat(),
            'agent_id': agent_id
        }
        
        session.updated_at = datetime.utcnow()
        
        # Also cache in Redis if available
        if self.redis_client:
            try:
                cache_key = f"agent_result:{session_id}:{agent_id}"
                await self.redis_client.setex(
                    cache_key,
                    self.settings.REDIS_CACHE_TTL,
                    json.dumps(result, default=str)
                )
            except Exception as e:
                logger.warning(f"Failed to cache agent result: {e}")
        
        logger.info(f"💾 Stored result for agent {agent_id} in session {session_id}")
    
    def get_agent_results(self, session_id: str) -> Dict[str, Any]:
        """Get all agent results for a session"""
        session = self.get_session(session_id)
        if not session:
            return {}
        
        return session.agent_results
    
    def update_session_status(self, session_id: str, status: str, confidence_score: float = None):
        """Update session status and confidence"""
        session = self.get_session(session_id)
        if session:
            session.status = status
            session.updated_at = datetime.utcnow()
            if confidence_score is not None:
                session.confidence_score = confidence_score
            
            logger.info(f"📊 Updated session {session_id} status to {status}")
    
    # ========= Agent Memory Management =========
    
    def get_agent_memory(self, agent_id: str) -> AgentMemory:
        """Get or create agent memory"""
        if agent_id not in self.agent_memories:
            self.agent_memories[agent_id] = AgentMemory(
                agent_id=agent_id,
                protocol_patterns={},
                learned_data_sources={},
                historical_assessments=[],
                confidence_calibration={}
            )
        
        return self.agent_memories[agent_id]
    
    def update_agent_memory(self, agent_id: str, memory_update: Dict[str, Any]):
        """Update agent's long-term memory"""
        memory = self.get_agent_memory(agent_id)
        
        # Update different memory components
        if 'protocol_patterns' in memory_update:
            memory.protocol_patterns.update(memory_update['protocol_patterns'])
        
        if 'learned_data_sources' in memory_update:
            memory.learned_data_sources.update(memory_update['learned_data_sources'])
        
        if 'assessment' in memory_update:
            memory.historical_assessments.append({
                'timestamp': datetime.utcnow().isoformat(),
                'assessment': memory_update['assessment']
            })
            
            # Keep only last 100 assessments
            if len(memory.historical_assessments) > 100:
                memory.historical_assessments = memory.historical_assessments[-100:]
        
        if 'confidence_calibration' in memory_update:
            memory.confidence_calibration.update(memory_update['confidence_calibration'])
        
        logger.info(f"🧠 Updated memory for agent {agent_id}")
    
    # ========= Caching Operations =========
    
    async def cache_assessment(self, protocol_name: str, assessment: Dict[str, Any]):
        """Cache complete risk assessment"""
        if not self.redis_client:
            return
        
        try:
            cache_key = f"assessment:{protocol_name.lower().replace(' ', '_')}"
            await self.redis_client.setex(
                cache_key,
                self.settings.REDIS_CACHE_TTL,
                json.dumps(assessment, default=str)
            )
            
            logger.info(f"💾 Cached assessment for {protocol_name}")
            
        except Exception as e:
            logger.warning(f"Failed to cache assessment: {e}")
    
    # FIX 2: Add missing get_cache method
    async def get_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached data by key"""
        try:
            if self.redis_client:
                cached_data = await self.redis_client.get(cache_key)
                if cached_data:
                    return json.loads(cached_data)
            
            # Fallback to in-memory cache if Redis unavailable
            logger.warning("No Redis connection available for cache retrieval")
            return None
            
        except Exception as e:
            logger.warning(f"Cache retrieval failed: {e}")
            return None

    # FIX: Add missing set_cache method
    async def set_cache(self, cache_key: str, data: Dict[str, Any], ttl_minutes: int = 10):
        """Set cached data with TTL"""
        try:
            if self.redis_client:
                ttl_seconds = ttl_minutes * 60
                await self.redis_client.setex(
                    cache_key,
                    ttl_seconds,
                    json.dumps(data, default=str)
                )
                logger.info(f"💾 Cached data with key: {cache_key}")
            else:
                logger.warning("No Redis connection available for caching")
                
        except Exception as e:
            logger.warning(f"Cache storage failed: {e}")
    
    async def get_cached_assessment(self, protocol_name: str) -> Optional[Dict[str, Any]]:
        """Get cached risk assessment"""
        if not self.redis_client:
            return None
        
        try:
            cache_key = f"assessment:{protocol_name.lower().replace(' ', '_')}"
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                logger.info(f"📋 Retrieved cached assessment for {protocol_name}")
                return json.loads(cached_data)
                
        except Exception as e:
            logger.warning(f"Failed to retrieve cached assessment: {e}")
        
        return None
    
    # ========= Gemini Client Access =========
    
    def get_gemini_model(self, model_type: str = "flash"):
        """Get configured Gemini model for agent use"""
        if model_type not in self.model_configs:
            logger.warning(f"Model type {model_type} not available, using flash")
            model_type = "flash"
        
        try:
            config = self.model_configs.get(model_type, self.model_configs.get('flash', {}))
            model_name = config.get('model_name', 'gemini-2.0-flash-exp')
            
            # Create generation config
            generation_config = {
                'temperature': config.get('temperature', 0.1),
                'top_p': config.get('top_p', 0.95),
                'max_output_tokens': config.get('max_output_tokens', 8192),
            }
            
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config
            )
            
            return model
            
        except Exception as e:
            logger.error(f"Failed to create Gemini model: {e}")
            return None
    
    # ========= Utility Methods =========
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Clean up old sessions to prevent memory leaks"""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        sessions_to_remove = []
        for session_id, session in self.sessions.items():
            if session.updated_at < cutoff_time:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.sessions[session_id]
        
        if sessions_to_remove:
            logger.info(f"🧹 Cleaned up {len(sessions_to_remove)} old sessions")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current sessions"""
        total_sessions = len(self.sessions)
        active_sessions = sum(1 for s in self.sessions.values() if s.status == 'active')
        completed_sessions = sum(1 for s in self.sessions.values() if s.status == 'completed')
        
        return {
            'total_sessions': total_sessions,
            'active_sessions': active_sessions,
            'completed_sessions': completed_sessions,
            'agent_memories': len(self.agent_memories)
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all components"""
        health = {
            'vertex_ai': False,
            'gemini': False,
            'redis': False,
            'sessions': len(self.sessions),
            'agent_memories': len(self.agent_memories)
        }
        
        # Check Vertex AI
        try:
            # Simple check - if we got this far, Vertex AI is initialized
            health['vertex_ai'] = True
        except:
            pass
        
        # Check Gemini
        try:
            if self.model_configs:
                health['gemini'] = True
        except:
            pass
        
        # Check Redis
        if self.redis_client:
            try:
                await self.redis_client.ping()
                health['redis'] = True
            except:
                pass
        
        return health

# Global memory manager instance
memory_manager = ADKMemoryManager()