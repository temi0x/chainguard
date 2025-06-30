import asyncio
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
import logging
from dataclasses import dataclass

# Google AI imports
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Internal imports
from config.settings import settings
from memory.adk_memory_manager import memory_manager, AgentMemory

logger = logging.getLogger(__name__)

@dataclass
class AgentContext:
    """Context information passed to agents during execution"""
    session_id: str
    protocol_name: str
    parameters: Dict[str, Any]
    previous_results: Dict[str, Any]
    
    def get_parameter(self, key: str, default: Any = None) -> Any:
        """Get parameter with default value"""
        return self.parameters.get(key, default)

@dataclass
class AgentResult:
    """Standardized result from agent execution"""
    agent_id: str
    success: bool
    data: Dict[str, Any]
    confidence: float
    reasoning: str
    execution_time: float
    timestamp: datetime
    errors: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'agent_id': self.agent_id,
            'success': self.success,
            'data': self.data,
            'confidence': self.confidence,
            'reasoning': self.reasoning,
            'execution_time': self.execution_time,
            'timestamp': self.timestamp.isoformat(),
            'errors': self.errors
        }

class BaseChainGuardAgent(ABC):
    """
    Base class for all ChainGuard AI agents.
    Provides common functionality for Gemini integration, memory management,
    and standardized execution patterns.
    """
    
    def __init__(
        self,
        agent_id: str,
        model_type: str = "flash",
        specialized_tools: Optional[List] = None
    ):
        self.agent_id = agent_id
        self.model_type = model_type
        self.specialized_tools = specialized_tools or []
        
        # Get memory manager instance
        self.memory_manager = memory_manager
        
        # Initialize agent memory
        self.memory = self.memory_manager.get_agent_memory(agent_id)
        
        # Get Gemini model
        self.gemini_model = self.memory_manager.get_gemini_model(model_type)
        
        # Agent configuration
        self.timeout_seconds = settings.AGENT_TIMEOUT_SECONDS
        self.max_retries = 3
        
        logger.info(f"🤖 Initialized agent {agent_id} with {model_type} model")
    
    # ========= Abstract Methods =========
    
    @abstractmethod
    async def analyze(self, context: AgentContext) -> AgentResult:
        """
        Main analysis method that each agent must implement.
        This is where the agent-specific logic goes.
        """
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt that defines the agent's role and behavior.
        Each agent should define its specific expertise and approach.
        """
        pass
    
    # ========= Core Execution Methods =========
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute the agent with proper error handling, timing, and result management.
        This is the main entry point for agent execution.
        """
        start_time = datetime.utcnow()
        
        try:
            # Timeout protection
            result = await asyncio.wait_for(
                self._execute_with_timeout(context),
                timeout=self.timeout_seconds
            )
            
            # Store result in session
            await self.memory_manager.store_agent_result(
                context.session_id,
                self.agent_id,
                result.to_dict()
            )
            
            # Update agent memory with learnings
            await self._update_memory_from_result(context, result)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            result.execution_time = execution_time
            
            logger.info(f"✅ Agent {self.agent_id} completed in {execution_time:.2f}s")
            return result
            
        except asyncio.TimeoutError:
            error_msg = f"Agent {self.agent_id} timed out after {self.timeout_seconds}s"
            logger.error(error_msg)
            
            return AgentResult(
                agent_id=self.agent_id,
                success=False,
                data={},
                confidence=0.0,
                reasoning=f"Execution timed out after {self.timeout_seconds} seconds",
                execution_time=self.timeout_seconds,
                timestamp=datetime.utcnow(),
                errors=[error_msg]
            )
            
        except Exception as e:
            error_msg = f"Agent {self.agent_id} failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AgentResult(
                agent_id=self.agent_id,
                success=False,
                data={},
                confidence=0.0,
                reasoning=f"Execution failed: {str(e)}",
                execution_time=execution_time,
                timestamp=datetime.utcnow(),
                errors=[error_msg]
            )
    
    async def _execute_with_timeout(self, context: AgentContext) -> AgentResult:
        """Execute with retry logic"""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                return await self.analyze(context)
            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Agent {self.agent_id} attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Agent {self.agent_id} failed all {self.max_retries} attempts")
        
        raise last_error
    
    # ========= Gemini Integration Methods =========
    
    async def call_gemini(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        temperature_override: Optional[float] = None
    ) -> str:
        """
        Call Gemini model with proper prompt formatting and error handling.
        """
        if not self.gemini_model:
            raise RuntimeError(f"Gemini model not available for agent {self.agent_id}")
        
        try:
            # Build full prompt with system instructions
            system_prompt = self.get_system_prompt()
            
            full_prompt = f"""System: {system_prompt}

Context: {json.dumps(context, indent=2) if context else 'No additional context'}

User Query: {prompt}

Please provide a detailed analysis following your system instructions."""
            
            # Configure safety settings for DeFi analysis
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
            
            # Generate response
            response = await asyncio.to_thread(
                self.gemini_model.generate_content,
                full_prompt,
                safety_settings=safety_settings
            )
            
            if response.text:
                logger.debug(f"🤖 {self.agent_id} received {len(response.text)} characters from Gemini")
                return response.text.strip()
            else:
                raise RuntimeError("Empty response from Gemini")
                
        except Exception as e:
            logger.error(f"Gemini call failed for {self.agent_id}: {e}")
            raise
    
    async def structured_analysis(
        self,
        prompt: str,
        expected_fields: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Call Gemini and parse structured JSON response.
        Useful for agents that need specific data formats.
        """
        
        structured_prompt = f"""{prompt}

Please respond with a JSON object containing the following fields:
{', '.join(expected_fields)}

Ensure your response is valid JSON that can be parsed. Do not include any text outside the JSON object."""
        
        response_text = await self.call_gemini(structured_prompt, context)
        
        # Extract JSON from response (handle cases where there's extra text)
        try:
            # Try to find JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_text = response_text[start_idx:end_idx]
                parsed_response = json.loads(json_text)
                
                # Validate expected fields are present
                missing_fields = [field for field in expected_fields if field not in parsed_response]
                if missing_fields:
                    logger.warning(f"Missing fields from {self.agent_id} response: {missing_fields}")
                
                return parsed_response
            else:
                raise ValueError("No JSON object found in response")
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from {self.agent_id}: {e}")
            logger.error(f"Response text: {response_text}")
            
            # Return a fallback structure with error information
            return {
                'error': 'Failed to parse structured response',
                'raw_response': response_text,
                'confidence': 0.0
            }
    
    # ========= Memory and Learning Methods =========
    
    async def _update_memory_from_result(self, context: AgentContext, result: AgentResult):
        """Update agent memory based on execution result"""
        if not result.success:
            return
        
        memory_update = {
            'assessment': {
                'protocol': context.protocol_name,
                'result': result.data,
                'confidence': result.confidence,
                'timestamp': result.timestamp.isoformat()
            }
        }
        
        # Let specialized agents add their own memory updates
        custom_memory = await self._get_custom_memory_update(context, result)
        if custom_memory:
            memory_update.update(custom_memory)
        
        self.memory_manager.update_agent_memory(self.agent_id, memory_update)
    
    async def _get_custom_memory_update(self, context: AgentContext, result: AgentResult) -> Optional[Dict[str, Any]]:
        """Override in specialized agents to add custom memory updates"""
        return None
    
    def get_historical_patterns(self, protocol_name: str) -> List[Dict[str, Any]]:
        """Get historical analysis patterns for a protocol"""
        protocol_key = protocol_name.lower().replace(' ', '_')
        return self.memory.protocol_patterns.get(protocol_key, [])
    
    # ========= Utility Methods =========
    
    def calculate_confidence(
        self,
        data_quality_score: float,
        analysis_completeness: float,
        historical_accuracy: Optional[float] = None
    ) -> float:
        """
        Calculate confidence score based on multiple factors.
        
        Args:
            data_quality_score: Quality of input data (0.0-1.0)
            analysis_completeness: How complete the analysis is (0.0-1.0)
            historical_accuracy: Historical accuracy of this agent (0.0-1.0)
        
        Returns:
            Overall confidence score (0.0-1.0)
        """
        base_confidence = (data_quality_score * 0.4 + analysis_completeness * 0.6)
        
        if historical_accuracy is not None:
            # Weight historical accuracy if available
            base_confidence = base_confidence * 0.7 + historical_accuracy * 0.3
        
        # Apply calibration from agent memory
        agent_calibration = self.memory.confidence_calibration.get('overall', 1.0)
        calibrated_confidence = base_confidence * agent_calibration
        
        return max(0.0, min(1.0, calibrated_confidence))
    
    def validate_data_quality(self, data: Dict[str, Any]) -> float:
        """
        Assess the quality of input data.
        
        Returns:
            Data quality score (0.0-1.0)
        """
        if not data:
            return 0.0
        
        quality_factors = []
        
        # Check for required fields
        required_fields = self._get_required_data_fields()
        if required_fields:
            present_fields = sum(1 for field in required_fields if field in data and data[field] is not None)
            field_completeness = present_fields / len(required_fields)
            quality_factors.append(field_completeness)
        
        # Check data freshness (if timestamp available)
        if 'timestamp' in data or 'last_updated' in data:
            timestamp_field = data.get('timestamp') or data.get('last_updated')
            if timestamp_field:
                try:
                    if isinstance(timestamp_field, str):
                        data_time = datetime.fromisoformat(timestamp_field.replace('Z', '+00:00'))
                    else:
                        data_time = timestamp_field
                    
                    hours_old = (datetime.utcnow() - data_time.replace(tzinfo=None)).total_seconds() / 3600
                    freshness_score = max(0.0, 1.0 - (hours_old / 24))  # Degrade over 24 hours
                    quality_factors.append(freshness_score)
                except:
                    pass
        
        # Check for error indicators
        if not data.get('errors') and not data.get('error'):
            quality_factors.append(1.0)
        else:
            quality_factors.append(0.5)  # Partial penalty for errors
        
        # Return average quality score
        return sum(quality_factors) / len(quality_factors) if quality_factors else 0.5
    
    def _get_required_data_fields(self) -> List[str]:
        """Override in specialized agents to specify required data fields"""
        return []
    
    def log_analysis_step(self, step: str, details: Optional[Dict[str, Any]] = None):
        """Log analysis step for debugging and transparency"""
        log_msg = f"[{self.agent_id}] {step}"
        if details:
            log_msg += f" - {details}"
        logger.info(log_msg)
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on agent"""
        health = {
            'agent_id': self.agent_id,
            'model_type': self.model_type,
            'gemini_available': self.gemini_model is not None,
            'tools_available': len(self.specialized_tools),
            'memory_size': len(self.memory.historical_assessments),
            'status': 'healthy'
        }
        
        # Test Gemini connection
        if self.gemini_model:
            try:
                test_response = await self.call_gemini("Test: Respond with 'OK'")
                health['gemini_test'] = 'OK' in test_response
            except Exception as e:
                health['gemini_test'] = False
                health['gemini_error'] = str(e)
                health['status'] = 'degraded'
        
        return health

# Agent registry for dynamic loading
AGENT_REGISTRY = {}

def register_agent(agent_class):
    """Decorator to register agent classes"""
    AGENT_REGISTRY[agent_class.__name__] = agent_class
    return agent_class