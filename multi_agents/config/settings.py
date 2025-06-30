import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings  # ← Fixed import
from pydantic import Field, field_validator  # ← Updated validator import for Pydantic v2
import logging

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """
    Application settings with Vertex AI and ADK configuration.
    Handles authentication and model configuration for ChainGuard AI.
    """
    
    # ========= Google Cloud / Vertex AI Configuration =========
    
    # Service Account Configuration
    GOOGLE_APPLICATION_CREDENTIALS: str = Field(
        default="chainguardai-1728b786facc.json",
        description="Path to Google Cloud service account JSON file"
    )
    
    # Vertex AI Project Configuration  
    VERTEX_AI_PROJECT_ID: str = Field(
        default="chainguardai",
        description="Google Cloud Project ID for Vertex AI"
    )
    
    VERTEX_AI_LOCATION: str = Field(
        default="us-central1",
        description="Vertex AI location/region"
    )
    
    # ========= Gemini Model Configuration =========
    
    # Gemini 2.5 Flash for fast operations (Data Hunter, quick analysis)
    GEMINI_MODEL_NAME: str = Field(
        default="gemini-2.5-flash-preview-04-17",
        description="Primary Gemini model for fast operations"
    )
    
    # Gemini 2.0 Flash for complex reasoning (Risk Synthesizer, deep analysis)
    GEMINI_PRO_MODEL: str = Field(
        default="gemini-2.0-flash-001",
        description="Gemini Pro model for complex reasoning tasks"
    )
    
    # Model configuration parameters
    GEMINI_TEMPERATURE: float = Field(
        default=0.1,
        ge=0.0, le=2.0,
        description="Temperature for model responses (0.0-2.0)"
    )
    
    GEMINI_MAX_TOKENS: int = Field(
        default=8192,
        gt=0,
        description="Maximum tokens for model responses"
    )
    
    GEMINI_TOP_P: float = Field(
        default=0.95,
        ge=0.0, le=1.0,
        description="Top-p sampling parameter"
    )
    
    # ========= External API Configuration =========
    
    # GitHub API
    GITHUB_TOKEN: Optional[str] = Field(
        default=None,
        description="GitHub personal access token for API access"
    )
    
    # DeFi Data Sources
    DEFILLAMA_API_KEY: Optional[str] = Field(
        default="",
        description="DeFiLlama API key (optional, has free tier)"
    )
    
    COINGECKO_API_KEY: Optional[str] = Field(
        default="",
        description="CoinGecko API key (optional, has free tier)"
    )
    
    ETHERSCAN_API_KEY: Optional[str] = Field(
        default="",
        description="Etherscan API key for contract verification"
    )
    
    # The Graph API
    THE_GRAPH_API_KEY: Optional[str] = Field(
        default="",
        description="The Graph API key for subgraph queries"
    )
    
    # ========= Redis Configuration =========
    
    REDIS_URL: str = Field(
        default="redis://localhost:6379",
        description="Redis connection URL for caching"
    )
    
    REDIS_CACHE_TTL: int = Field(
        default=600,  # 10 minutes
        gt=0,
        description="Redis cache TTL in seconds"
    )
    
    REDIS_MAX_CONNECTIONS: int = Field(
        default=20,
        gt=0,
        description="Maximum Redis connections in pool"
    )
    
    # ========= Application Configuration =========
    
    # Environment
    ENVIRONMENT: str = Field(
        default="development",
        description="Application environment (development, staging, production)"
    )
    
    # Logging
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level"
    )
    
    # API Configuration
    API_PREFIX: str = Field(
        default="/api/v1",
        description="API prefix for all endpoints"
    )
    
    # Request timeout settings
    HTTP_TIMEOUT: int = Field(
        default=30,
        gt=0,
        description="HTTP request timeout in seconds"
    )
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = Field(
        default=60,
        gt=0,
        description="API rate limit per minute per IP"
    )
    
    # ========= Agent Configuration =========
    
    # Agent execution timeouts
    AGENT_TIMEOUT_SECONDS: int = Field(
        default=120,
        gt=0,
        description="Maximum execution time per agent"
    )
    
    # Maximum concurrent agent executions
    MAX_CONCURRENT_AGENTS: int = Field(
        default=4,
        gt=0,
        description="Maximum concurrent agent executions"
    )
    
    # Data validation settings
    DATA_QUALITY_THRESHOLD: float = Field(
        default=0.7,
        ge=0.0, le=1.0,
        description="Minimum data quality threshold for analysis"
    )
    
    # ========= Validators (Updated for Pydantic v2) =========
    
    @field_validator('GOOGLE_APPLICATION_CREDENTIALS')
    @classmethod
    def validate_service_account(cls, v):
        """Validate service account file exists and is valid JSON"""
        if not v:
            raise ValueError("Google Application Credentials must be provided")
        
        # Convert to absolute path
        if not os.path.isabs(v):
            # Look in project root first
            project_root = Path(__file__).parent.parent
            credential_path = project_root / v
            if credential_path.exists():
                v = str(credential_path)
            else:
                raise ValueError(f"Service account file not found: {v}")
        
        # Validate JSON structure
        try:
            with open(v, 'r') as f:
                credentials = json.load(f)
            
            required_fields = ['type', 'project_id', 'private_key', 'client_email']
            for field in required_fields:
                if field not in credentials:
                    raise ValueError(f"Invalid service account file: missing {field}")
            
            if credentials['type'] != 'service_account':
                raise ValueError("Credentials file must be for a service account")
                
        except json.JSONDecodeError:
            raise ValueError("Service account file must be valid JSON")
        except FileNotFoundError:
            raise ValueError(f"Service account file not found: {v}")
        
        return v
    
    @field_validator('VERTEX_AI_PROJECT_ID')
    @classmethod
    def validate_project_id(cls, v):
        """Validate project ID format"""
        if not v or not v.strip():
            raise ValueError("Vertex AI Project ID cannot be empty")
        return v.strip()
    
    @field_validator('REDIS_URL')
    @classmethod
    def validate_redis_url(cls, v):
        """Validate Redis URL format"""
        if not v.startswith(('redis://', 'rediss://')):
            raise ValueError("Redis URL must start with redis:// or rediss://")
        return v
    
    # ========= Configuration Properties =========
    
    @property
    def service_account_info(self) -> Dict[str, Any]:
        """Get service account information"""
        try:
            with open(self.GOOGLE_APPLICATION_CREDENTIALS, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load service account: {e}")
            return {}
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT.lower() == 'production'
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.ENVIRONMENT.lower() == 'development'
    
    def get_model_config(self, model_type: str = "flash") -> Dict[str, Any]:
        """Get model configuration for specified model type"""
        base_config = {
            "temperature": self.GEMINI_TEMPERATURE,
            "max_output_tokens": self.GEMINI_MAX_TOKENS,
            "top_p": self.GEMINI_TOP_P,
        }
        
        if model_type.lower() == "pro":
            base_config["model_name"] = self.GEMINI_PRO_MODEL
        else:
            base_config["model_name"] = self.GEMINI_MODEL_NAME
        
        return base_config
    
    def setup_authentication(self):
        """Setup Google Cloud authentication"""
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.GOOGLE_APPLICATION_CREDENTIALS
        logger.info(f"Google Cloud authentication configured with service account: {self.GOOGLE_APPLICATION_CREDENTIALS}")
    
    # Pydantic v2 configuration
    model_config = {
        'env_file': '.env',
        'env_file_encoding': 'utf-8',
        'case_sensitive': True,
        'validate_assignment': True,
        'extra': 'forbid'
    }

# Global settings instance
settings = Settings()

# Initialize authentication on import
try:
    settings.setup_authentication()
    logger.info("✅ ChainGuard AI settings loaded successfully")
    logger.info(f"   📁 Project ID: {settings.VERTEX_AI_PROJECT_ID}")
    logger.info(f"   🌎 Location: {settings.VERTEX_AI_LOCATION}")
    logger.info(f"   🤖 Primary Model: {settings.GEMINI_MODEL_NAME}")
    logger.info(f"   🧠 Pro Model: {settings.GEMINI_PRO_MODEL}")
    logger.info(f"   🏗️ Environment: {settings.ENVIRONMENT}")
except Exception as e:
    logger.error(f"❌ Failed to initialize ChainGuard AI settings: {e}")
    raise

# Export for easy importing
__all__ = ['settings', 'Settings']