import asyncio
import aiohttp
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# Internal imports
from config.settings import settings

logger = logging.getLogger(__name__)

@dataclass
class ToolResult:
    """Standardized result from ADK tool execution"""
    tool_name: str
    success: bool
    data: Dict[str, Any]
    reliability_score: float  # 0.0-1.0
    execution_time: float
    timestamp: datetime
    errors: List[str]
    source_urls: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'tool_name': self.tool_name,
            'success': self.success,
            'data': self.data,
            'reliability_score': self.reliability_score,
            'execution_time': self.execution_time,
            'timestamp': self.timestamp.isoformat(),
            'errors': self.errors,
            'source_urls': self.source_urls
        }

class BaseADKTool(ABC):
    """
    Base class for all ChainGuard AI ADK tools.
    Provides common HTTP functionality, error handling, and standardized interfaces.
    """
    
    def __init__(self, tool_name: str):
        self.tool_name = tool_name
        self.session: Optional[aiohttp.ClientSession] = None
        self.timeout = aiohttp.ClientTimeout(total=settings.HTTP_TIMEOUT)
        
        # Protocol configuration mappings
        self.protocol_config = self._load_protocol_config()
        
        logger.info(f"🔧 Initialized ADK tool: {tool_name}")
    
    def _load_protocol_config(self) -> Dict[str, Dict[str, str]]:
        """Load protocol configuration for API mappings"""
        return {
            "Aave V3": {
                "github": "aave-dao/aave-v3-origin",  # ← Changed from aave/aave-v3-core
                "defillama": "aave-v3", 
                "coingecko": "aave",
                "contract": "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2"
            },
            "Aave V4": {
                "github": "aave/aave-v3-core",
                "defillama": "aave-v3",
                "coingecko": "aave", 
                "contract": "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2"
            },
            "Lido (stETH)": {
                "github": "lidofinance/lido-dao",
                "defillama": "lido",
                "coingecko": "lido-dao",
                "contract": "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84"
            },
            "EigenLayer": {
                "github": "Layr-Labs/eigenlayer-contracts", 
                "defillama": "eigenlayer",
                "coingecko": "eigenlayer",
                "contract": "0x858646372CC42E1A627fcE94aa7A7033e7CF075A"
            },
            "Ethena (USDe)": {
                "github": "ethena-labs/ethena",
                "defillama": "ethena", 
                "coingecko": "ethena-usde",
                "contract": "0x4c9EDD5852cd905f086C759E8383e09bff1E68B3"
            },
            "Pendle Finance": {
                "github": "pendle-finance/pendle-core-v2",
                "defillama": "pendle",
                "coingecko": "pendle", 
                "contract": "0x888888888889758F76e7103c6CbF23ABbF58F946"
            },
            "Uniswap V4": {
                "github": "Uniswap/v4-core",
                "defillama": "uniswap-v3",
                "coingecko": "uniswap",
                "contract": "0x1F98431c8aD98523631AE4a59f267346ea31F984"
            }
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        if not self.session:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            self.session = None
    
    # ========= Abstract Methods =========
    
    @abstractmethod
    async def execute(self, protocol_name: str, parameters: Optional[Dict[str, Any]] = None) -> ToolResult:
        """
        Main execution method that each tool must implement.
        
        Args:
            protocol_name: Name of the protocol to analyze
            parameters: Additional parameters for the tool
            
        Returns:
            ToolResult with analysis data
        """
        pass
    
    @abstractmethod
    def get_protocol_identifiers(self, protocol_name: str) -> Dict[str, str]:
        """
        Get protocol-specific identifiers (repo names, API slugs, etc.)
        
        Args:
            protocol_name: Name of the protocol
            
        Returns:
            Dictionary of identifiers for this tool
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the tool's data sources.
        
        Returns:
            Health status information
        """
        pass
    
    # ========= Common HTTP Methods =========
    
    async def http_get(
        self, 
        url: str, 
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform HTTP GET request with error handling.
        
        Args:
            url: Request URL
            headers: HTTP headers
            params: Query parameters
            
        Returns:
            Response data as dictionary
            
        Raises:
            aiohttp.ClientError: On HTTP errors
        """
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        try:
            async with self.session.get(url, headers=headers, params=params) as response:
                response.raise_for_status()
                
                # Handle different content types
                content_type = response.content_type.lower()
                if 'application/json' in content_type:
                    return await response.json()
                else:
                    text_data = await response.text()
                    try:
                        return json.loads(text_data)
                    except json.JSONDecodeError:
                        return {"raw_text": text_data}
                        
        except aiohttp.ClientError as e:
            logger.error(f"HTTP GET failed for {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in HTTP GET for {url}: {e}")
            raise aiohttp.ClientError(f"Request failed: {e}")
    
    async def http_post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Perform HTTP POST request with error handling.
        
        Args:
            url: Request URL
            data: Form data
            json_data: JSON data
            headers: HTTP headers
            
        Returns:
            Response data as dictionary
        """
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        try:
            async with self.session.post(url, data=data, json=json_data, headers=headers) as response:
                response.raise_for_status()
                return await response.json()
                
        except aiohttp.ClientError as e:
            logger.error(f"HTTP POST failed for {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in HTTP POST for {url}: {e}")
            raise aiohttp.ClientError(f"Request failed: {e}")
    
    # ========= Utility Methods =========
    
    def get_protocol_config(self, protocol_name: str) -> Optional[Dict[str, str]]:
        """Get configuration for a protocol"""
        return self.protocol_config.get(protocol_name)
    
    def calculate_reliability_score(
        self,
        data_completeness: float,
        response_time: float,
        api_success_rate: float = 1.0
    ) -> float:
        """
        Calculate reliability score for tool result.
        
        Args:
            data_completeness: How complete the data is (0.0-1.0)
            response_time: Response time in seconds
            api_success_rate: Success rate of API calls (0.0-1.0)
            
        Returns:
            Reliability score (0.0-1.0)
        """
        # Penalize slow responses
        time_factor = max(0.1, 1.0 - (response_time / 30.0))  # 30s = very slow
        
        # Combine factors
        reliability = (
            data_completeness * 0.5 + 
            api_success_rate * 0.3 + 
            time_factor * 0.2
        )
        
        return max(0.0, min(1.0, reliability))
    
    def validate_protocol_name(self, protocol_name: str) -> bool:
        """Validate that protocol is supported"""
        return protocol_name in self.protocol_config
    
    def log_tool_activity(self, activity: str, details: Optional[Dict[str, Any]] = None):
        """Log tool activity for debugging"""
        log_msg = f"[{self.tool_name}] {activity}"
        if details:
            log_msg += f" - {details}"
        logger.info(log_msg)
    
    async def execute_with_timeout(
        self,
        protocol_name: str,
        parameters: Optional[Dict[str, Any]] = None,
        timeout_seconds: int = 30
    ) -> ToolResult:
        """
        Execute tool with timeout protection.
        
        Args:
            protocol_name: Protocol to analyze
            parameters: Tool parameters
            timeout_seconds: Execution timeout
            
        Returns:
            ToolResult with analysis data
        """
        start_time = datetime.utcnow()
        
        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                self.execute(protocol_name, parameters),
                timeout=timeout_seconds
            )
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            result.execution_time = execution_time
            
            self.log_tool_activity(
                f"Completed analysis for {protocol_name}",
                {"execution_time": execution_time, "success": result.success}
            )
            
            return result
            
        except asyncio.TimeoutError:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            error_msg = f"Tool {self.tool_name} timed out after {timeout_seconds}s"
            
            self.log_tool_activity(f"Timeout for {protocol_name}", {"timeout": timeout_seconds})
            
            return ToolResult(
                tool_name=self.tool_name,
                success=False,
                data={},
                reliability_score=0.0,
                execution_time=execution_time,
                timestamp=datetime.utcnow(),
                errors=[error_msg],
                source_urls=[]
            )
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            error_msg = f"Tool {self.tool_name} failed: {str(e)}"
            
            logger.error(error_msg, exc_info=True)
            
            return ToolResult(
                tool_name=self.tool_name,
                success=False,
                data={},
                reliability_score=0.0,
                execution_time=execution_time,
                timestamp=datetime.utcnow(),
                errors=[error_msg],
                source_urls=[]
            )

# Tool registry for dynamic loading
TOOL_REGISTRY = {}

def register_tool(tool_class):
    """Decorator to register tool classes"""
    TOOL_REGISTRY[tool_class.__name__] = tool_class
    return tool_class