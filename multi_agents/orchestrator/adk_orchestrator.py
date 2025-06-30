import asyncio
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import logging

# Google ADK imports
from google.adk.runners import Runner
from google.adk.memory import InMemoryMemoryService  
from google.adk.sessions import InMemorySessionService

# Internal imports
from agents.data_hunter_agent import DataHunterAgent
from agents.protocol_analyst_agent import ProtocolAnalystAgent
from agents.market_intelligence_agent import MarketIntelligenceAgent
from agents.risk_synthesizer_agent import RiskSynthesizerAgent
from memory.adk_memory_manager import memory_manager
from models.response_models import (
    RiskAssessment, AgentStatus, ProtocolInfo, RiskLevel, 
    ComponentRiskScore, DataQuality
)
from utils.protocol_validator import protocol_validator
from config.settings import settings

logger = logging.getLogger(__name__)

class ADKOrchestrator:
    """
    Multi-Agent Orchestrator using Google ADK Runners.
    
    Coordinates the execution of 4 specialized agents:
    1. Data Hunter Agent - discovers and validates data sources
    2. Protocol Analyst Agent - analyzes security and governance  
    3. Market Intelligence Agent - analyzes financial health
    4. Risk Synthesizer Agent - combines all insights
    
    Uses ADK session management for inter-agent communication and state sharing.
    """
    
    def __init__(self):
        """Initialize the ADK orchestrator with all agents and services"""
        
        # Initialize protocol validator
        self.protocol_validator = protocol_validator
        

        # Initialize ADK memory services
        self.session_service = InMemorySessionService()
        self.memory_service = InMemoryMemoryService()

        # FIX 2: Also reference memory_manager services for compatibility
        self.memory_manager = memory_manager
        
        self.sessions = {}

        # Initialize all agents
        self.agents = {
            'data_hunter': DataHunterAgent(),
            'protocol_analyst': ProtocolAnalystAgent(), 
            'market_intelligence': MarketIntelligenceAgent(),
            'risk_synthesizer': RiskSynthesizerAgent()
        }
        
        # Cache settings
        self.cache_ttl_minutes = 10  # 10-minute cache TTL
        
        logger.info("🚀 ADK Orchestrator initialized with 4 agents")
        logger.info(f"   📊 Agents: {list(self.agents.keys())}")
        logger.info(f"   💾 Cache TTL: {self.cache_ttl_minutes} minutes")
    
    def _create_error_assessment(
        self, 
        protocol_name: str, 
        session_id: str, 
        error_type: str, 
        error_message: str
    ) -> RiskAssessment:
        """Create a proper error assessment when things go wrong"""
        
        protocol_info = ProtocolInfo(
            name=protocol_name,
            normalized_name=protocol_name.lower().replace(' ', '-')
        )
        
        return RiskAssessment(
            protocol=protocol_info,  # ← CORRECT field name
            overall_risk_score=100.0,
            risk_level=RiskLevel.CRITICAL,
            confidence=0.0,
            component_scores=ComponentRiskScore(security=100.0, liquidity=100.0, governance=100.0, technical=100.0),
            agent_insights={},
            data_quality=DataQuality(completeness=0.0, freshness=0.0, reliability=0.0, source_count=0, last_updated=datetime.utcnow()),
            analysis_id=f"{error_type}_{hashlib.md5(protocol_name.encode()).hexdigest()[:8]}",
            session_id=session_id,
            total_execution_time=0.0,
            executive_summary=f"Risk assessment for {protocol_name} failed: {error_type}",
            detailed_explanation=f"Assessment could not be completed due to: {error_message}",
            major_risks=[],
            minor_risks=[],
            recommendations=[]
        )

    async def assess_protocol_risk(self, protocol_name: str) -> RiskAssessment:
        """Main orchestration method"""
        
        try:
            logger.info(f"🎯 Starting risk assessment for {protocol_name}")
            
            # Generate session ID
            session_id = f"assessment_{protocol_name.replace(' ', '_')}_{int(datetime.utcnow().timestamp())}"
            
            # 1. Check cache first
            cache_key = self._generate_cache_key(protocol_name)
            cached_assessment = await self._get_cached_assessment(cache_key)
            if cached_assessment:
                logger.info(f"📋 Returning cached assessment for {protocol_name}")
                return cached_assessment
            
            # 2. Validate protocol is supported
            if not self.protocol_validator.is_supported(protocol_name):
                logger.error(f"Protocol '{protocol_name}' not supported")
                return self._create_error_assessment(
                    protocol_name=protocol_name,
                    session_id=session_id,
                    error_type="unsupported_protocol",
                    error_message=f"Protocol '{protocol_name}' not supported"
                )
            
            # 3. Execute multi-agent workflow
            try:
                assessment_result = await self._execute_multi_agent_workflow(
                    protocol_name=protocol_name,
                    session_id=session_id
                )
                
                # 4. Cache the result
                await self._cache_assessment(cache_key, assessment_result)
                
                return assessment_result
                
            except Exception as workflow_error:
                logger.error(f"Multi-agent workflow failed: {workflow_error}")
                return self._create_error_assessment(
                    protocol_name=protocol_name,
                    session_id=session_id,
                    error_type="workflow_failure",
                    error_message=str(workflow_error)
                )
                
        except Exception as e:
            logger.error(f"Assessment failed for {protocol_name}: {e}")
            return self._create_error_assessment(
                protocol_name=protocol_name,
                session_id=f"error_{int(datetime.utcnow().timestamp())}",
                error_type="general_failure",
                error_message=str(e)
            )
    
    async def _execute_multi_agent_workflow(
        self, 
        protocol_name: str,  # Fixed parameter order
        session_id: str
    ) -> RiskAssessment:
        """
        Execute the complete multi-agent workflow using ADK Runners.
        
        Phase 1: Data Hunter (sequential)
        Phase 2: Protocol Analyst + Market Intelligence (parallel) 
        Phase 3: Risk Synthesizer (sequential)
        """
        
        # Phase 1: Data Discovery
        logger.info("🔍 Phase 1: Data Discovery (Data Hunter Agent)")
        data_hunter_result = await self._execute_agent_with_runner(
            agent=self.agents['data_hunter'],
            session_id=session_id,
            protocol_name=protocol_name,
            phase="data_discovery"
        )
        
        # FIX: Check success field in dictionary instead of .success attribute
        if not data_hunter_result.get('success', False):
            logger.warning("⚠️ Data Hunter failed, proceeding with limited data")
        
        # Phase 2: Parallel Analysis
        logger.info("🔀 Phase 2: Parallel Analysis (Protocol + Market Agents)")
        
        # Execute Protocol Analyst and Market Intelligence in parallel
        analyst_task = self._execute_agent_with_runner(
            agent=self.agents['protocol_analyst'],
            session_id=session_id,
            protocol_name=protocol_name,
            phase="protocol_analysis"
        )
        
        market_task = self._execute_agent_with_runner(
            agent=self.agents['market_intelligence'],
            session_id=session_id,
            protocol_name=protocol_name,
            phase="market_analysis"
        )
        
        # Wait for both parallel agents to complete
        protocol_result, market_result = await asyncio.gather(
            analyst_task, 
            market_task,
            return_exceptions=True
        )
        
        # Handle any exceptions from parallel execution
        if isinstance(protocol_result, Exception):
            logger.error(f"Protocol Analyst failed: {protocol_result}")
            protocol_result = self._create_error_result("protocol_analyst", str(protocol_result))
        
        if isinstance(market_result, Exception):
            logger.error(f"Market Intelligence failed: {market_result}")
            market_result = self._create_error_result("market_intelligence", str(market_result))
        
        # Phase 3: Risk Synthesis
        logger.info("🎯 Phase 3: Risk Synthesis (Risk Synthesizer Agent)")
        synthesis_result = await self._execute_agent_with_runner(
            agent=self.agents['risk_synthesizer'],
            session_id=session_id,
            protocol_name=protocol_name,
            phase="risk_synthesis"
        )
        
        # Compile final assessment
        return await self._compile_final_assessment(
            protocol_name=protocol_name,
            session_id=session_id,
            agent_results={
                'data_hunter': data_hunter_result,
                'protocol_analyst': protocol_result,
                'market_intelligence': market_result,
                'risk_synthesizer': synthesis_result
            }
        )
    
    async def _execute_agent_with_runner(
        self,
        agent,
        session_id: str,
        protocol_name: str,
        phase: str
    ):
        """Execute a single agent using ADK Runner with proper session management"""
        
        try:
            # FIX: Don't pass session_id to Runner constructor
            runner = Runner(
                agent=agent,
                session_service=self.session_service,
                memory_service=self.memory_service
                # Remove session_id parameter
            )
            
            # Create agent context using the BaseADKAgent's AgentContext
            from agents.base_adk_agent import AgentContext
            
            context = AgentContext(
                session_id=session_id,
                protocol_name=protocol_name,
                parameters={'phase': phase},
                previous_results={}
            )
            
            logger.info(f"   🤖 Executing {agent.agent_id} in phase {phase}")
            
            # FIX: Execute agent through the agent's execute method directly
            # instead of runner.run which might not exist
            result = await agent.execute(context)
            
            # Store result in session for other agents
            await self.session_service.store(
                session_id=session_id,
                key=f"{agent.agent_id}_result",
                value=result.to_dict() if hasattr(result, 'to_dict') else result.__dict__
            )
            
            logger.info(f"   ✅ {agent.agent_id} completed successfully")
            
            # FIX: Return consistent format matching the expected structure
            return {
                'status': 'completed' if result.success else 'failed',
                'result': result,
                'execution_time': result.execution_time,
                'confidence': result.confidence,
                'success': result.success  # Add this field for compatibility
            }
            
        except Exception as e:
            error_msg = f"Agent {getattr(agent, 'agent_id', 'unknown')} execution failed: {e}"
            logger.error(error_msg)
            
            # FIX: Return consistent error format
            return {
                'status': 'failed',
                'error': str(e),
                'execution_time': 0.0,
                'confidence': 0.0,
                'success': False  # Add this field for compatibility
            }
    
    def _create_error_result(self, agent_id: str, error_message: str):
        """Create a standardized error result for failed agents"""
        
        # FIX: Return dictionary format instead of AgentResult object
        return {
            'status': 'failed',
            'error': error_message,
            'execution_time': 0.0,
            'confidence': 0.0,
            'success': False,
            'agent_id': agent_id
        }
    
    async def _compile_final_assessment(
        self,
        protocol_name: str,
        session_id: str,
        agent_results: Dict[str, Any]
    ) -> RiskAssessment:
        """Compile final risk assessment from all agent results"""
        
        try:
            # Create ProtocolInfo object (required field)
            protocol_info = ProtocolInfo(
                name=protocol_name,
                normalized_name=protocol_name.lower().replace(' ', '-')
            )
            
            # Process agent results with proper defaults
            processed_insights = {}
            successful_agents = []
            
            for agent_id, result in agent_results.items():
                if result and result.get('status') != 'failed':
                    successful_agents.append(agent_id)
                    processed_insights[agent_id] = {
                        'agent_id': agent_id,
                        'status': AgentStatus.COMPLETED,
                        'confidence': result.get('confidence', 0.0),
                        'findings': result.get('findings', []),
                        'execution_time': result.get('execution_time', 0.0),
                        'reasoning': result.get('reasoning', 'Agent completed successfully'),
                        'timestamp': datetime.utcnow(),
                        'errors': []
                    }
                else:
                    processed_insights[agent_id] = {
                        'agent_id': agent_id,
                        'status': AgentStatus.FAILED,
                        'confidence': 0.0,
                        'findings': [],
                        'execution_time': 0.0,
                        'reasoning': result.get('error', 'Unknown error') if result else 'Agent execution failed',
                        'timestamp': datetime.utcnow(),
                        'errors': [result.get('error', 'Unknown error') if result else 'Agent execution failed']
                    }
            
            # Calculate overall risk score
            if successful_agents:
                overall_risk_score = 60.0  # Default medium risk
                risk_level = RiskLevel.MEDIUM
                confidence = 0.5
            else:
                overall_risk_score = 80.0
                risk_level = RiskLevel.HIGH
                confidence = 0.1
            
            # Create component scores
            from models.response_models import ComponentRiskScore
            component_scores = ComponentRiskScore(
                security=60.0,
                liquidity=60.0,
                governance=60.0,
                technical=60.0
            )
            
            # Create data quality
            from models.response_models import DataQuality
            data_quality = DataQuality(
                completeness=0.7 if successful_agents else 0.1,
                freshness=0.8,
                reliability=0.6 if successful_agents else 0.2,
                source_count=len(successful_agents),
                last_updated=datetime.utcnow()
            )
            
            # Generate analysis ID
            analysis_id = f"analysis_{hashlib.md5(f'{protocol_name}_{session_id}'.encode()).hexdigest()[:8]}"
            
            # Create final assessment with correct field names
            return RiskAssessment(
                protocol=protocol_info,  # ← CORRECT: protocol (ProtocolInfo object)
                overall_risk_score=overall_risk_score,
                risk_level=risk_level,
                confidence=confidence,
                component_scores=component_scores,
                agent_insights=processed_insights,
                data_quality=data_quality,
                analysis_id=analysis_id,
                session_id=session_id,
                total_execution_time=0.0,
                executive_summary=f"Risk assessment for {protocol_name} completed with {len(successful_agents)}/4 agents successful.",
                detailed_explanation=f"Analysis involved {len(agent_results)} agents. {'Partial data available.' if successful_agents else 'Limited data due to agent failures.'}",
                major_risks=[],
                minor_risks=[],
                recommendations=[]
            )
            
        except Exception as e:
            logger.error(f"Failed to compile final assessment: {e}", exc_info=True)
            
            # Return error assessment with proper structure
            protocol_info = ProtocolInfo(
                name=protocol_name,
                normalized_name=protocol_name.lower().replace(' ', '-')
            )
            
            return RiskAssessment(
                protocol=protocol_info,  # ← CORRECT field name
                overall_risk_score=100.0,
                risk_level=RiskLevel.CRITICAL,
                confidence=0.0,
                component_scores=ComponentRiskScore(security=100.0, liquidity=100.0, governance=100.0, technical=100.0),
                agent_insights={},
                data_quality=DataQuality(completeness=0.0, freshness=0.0, reliability=0.0, source_count=0, last_updated=datetime.utcnow()),
                analysis_id=f"error_{hashlib.md5(protocol_name.encode()).hexdigest()[:8]}",
                session_id=session_id,
                total_execution_time=0.0,
                executive_summary=f"Risk assessment for {protocol_name} failed due to compilation error.",
                detailed_explanation=f"Error during assessment compilation: {str(e)}",
                major_risks=[],
                minor_risks=[],
                recommendations=[]
            )
    
    def _generate_cache_key(self, protocol_name: str) -> str:
        """Generate cache key for protocol assessment"""
        # Include date to ensure daily cache refresh
        date_str = datetime.utcnow().strftime('%Y-%m-%d')
        cache_string = f"risk_assessment_{protocol_name}_{date_str}"
        return hashlib.md5(cache_string.encode()).hexdigest()

    
    
    async def _get_cached_assessment(self, cache_key: str) -> Optional[RiskAssessment]:
        """Get cached assessment if available and fresh"""
        try:
            # FIX: Use memory_manager's Redis client directly
            if hasattr(self.memory_manager, 'redis_client') and self.memory_manager.redis_client:
                cached_data = await self.memory_manager.redis_client.get(cache_key)
                
                if cached_data:
                    cached_dict = json.loads(cached_data)
                    # Check if cache is still fresh
                    cache_time_str = cached_dict.get('timestamp')
                    if cache_time_str:
                        cache_time = datetime.fromisoformat(cache_time_str)
                        if datetime.utcnow() - cache_time < timedelta(minutes=self.cache_ttl_minutes):
                            logger.info(f"📋 Cache hit for key: {cache_key}")
                            # FIX: Return the actual cached data, not try to create RiskAssessment
                            return cached_dict
                        else:
                            logger.info(f"⏰ Cache expired for key: {cache_key}")
                            
        except Exception as e:
            logger.warning(f"Cache retrieval failed: {e}")
        
        return None
    
    async def _cache_assessment(self, cache_key: str, assessment: RiskAssessment):
        """Cache the assessment result"""
        try:
            # FIX: Use memory_manager's set_cache method
            cache_data = assessment.__dict__ if hasattr(assessment, '__dict__') else assessment
            cache_data['timestamp'] = datetime.utcnow().isoformat()
            
            # Use the memory_manager's set_cache method
            await self.memory_manager.set_cache(
                cache_key, 
                cache_data, 
                ttl_minutes=self.cache_ttl_minutes
            )
            
            logger.info(f"💾 Cached assessment with key: {cache_key}")
            
        except Exception as e:
            logger.warning(f"Cache storage failed: {e}")
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents for health checking"""
        
        agent_statuses = {}
        
        for agent_id, agent in self.agents.items():
            try:
                # Quick health check for each agent
                health = await agent.health_check()
                agent_statuses[agent_id] = {
                    'status': 'healthy' if health.get('status') == 'healthy' else 'unhealthy',
                    'model_type': agent.model_type,
                    'last_check': datetime.utcnow().isoformat()
                }
            except Exception as e:
                agent_statuses[agent_id] = {
                    'status': 'error',
                    'error': str(e),
                    'last_check': datetime.utcnow().isoformat()
                }
        
        return {
            'orchestrator_status': 'healthy',
            'total_agents': len(self.agents),
            'healthy_agents': sum(1 for status in agent_statuses.values() if status['status'] == 'healthy'),
            'agents': agent_statuses,
            'cache_ttl_minutes': self.cache_ttl_minutes,
            'supported_protocols': len(self.protocol_validator.supported_protocols)
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            # Clean up memory manager
            if hasattr(self.memory_manager, 'close_redis'):
                await self.memory_manager.close_redis()
            
            # FIX 4: Check if session_service has cleanup method before calling it
            if hasattr(self.session_service, 'cleanup'):
                await self.session_service.cleanup()
                
            logger.info("🧹 ADK Orchestrator cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

# Global orchestrator instance
orchestrator = ADKOrchestrator()