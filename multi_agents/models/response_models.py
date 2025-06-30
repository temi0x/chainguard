from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, field_validator
from enum import Enum

class RiskLevel(str, Enum):
    """Risk level categories"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AgentStatus(str, Enum):
    """Agent execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

class DataSourceType(str, Enum):
    """Types of data sources"""
    GITHUB = "github"
    SUBGRAPH = "subgraph"
    API = "api"
    SMART_CONTRACT = "smart_contract"
    SOCIAL = "social"
    AUDIT = "audit"

# ========= Base Models =========

class BaseResponse(BaseModel):
    """Base response model with common fields"""
    success: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    message: Optional[str] = None
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }

class ErrorDetail(BaseModel):
    """Error detail information"""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseResponse):
    """Error response model"""
    success: bool = False
    error: ErrorDetail
    suggestion: Optional[str] = None

# ========= Data Source Models =========

class DataSource(BaseModel):
    """Data source information"""
    type: DataSourceType
    url: str
    reliability_score: float = Field(ge=0.0, le=1.0)
    last_validated: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator('reliability_score')
    @classmethod
    def validate_reliability(cls, v):
        return round(v, 3)

class DataQuality(BaseModel):
    """Data quality assessment"""
    overall_score: float = Field(ge=0.0, le=1.0)
    completeness: float = Field(ge=0.0, le=1.0)
    freshness: float = Field(ge=0.0, le=1.0)
    accuracy: float = Field(ge=0.0, le=1.0)
    sources_validated: int
    missing_data_points: List[str] = Field(default_factory=list)
    
    @field_validator('overall_score', 'completeness', 'freshness', 'accuracy')
    @classmethod
    def round_scores(cls, v):
        return round(v, 3)

# ========= Agent Result Models =========

class AgentInsight(BaseModel):
    """Individual agent analysis result"""
    agent_id: str
    status: AgentStatus
    confidence: float = Field(ge=0.0, le=1.0)
    risk_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    key_findings: List[str] = Field(default_factory=list)
    reasoning: str
    data_sources_used: List[DataSource] = Field(default_factory=list)
    execution_time: float
    warnings: List[str] = Field(default_factory=list)
    
    @field_validator('confidence')
    @classmethod
    def round_confidence(cls, v):
        return round(v, 3)
    
    @field_validator('risk_score')
    @classmethod
    def round_risk_score(cls, v):
        return round(v, 2) if v is not None else None

class ComponentRiskScore(BaseModel):
    """Risk score breakdown by component"""
    security: float = Field(ge=0.0, le=100.0)
    financial: float = Field(ge=0.0, le=100.0)
    governance: float = Field(ge=0.0, le=100.0)
    social: float = Field(ge=0.0, le=100.0)
    technical: float = Field(ge=0.0, le=100.0)
    
    @field_validator('security', 'financial', 'governance', 'social', 'technical')
    @classmethod
    def round_scores(cls, v):
        return round(v, 2)

class RiskFactorDetail(BaseModel):
    """Detailed risk factor information"""
    category: str
    severity: RiskLevel
    impact_score: float = Field(ge=0.0, le=10.0)
    likelihood: float = Field(ge=0.0, le=1.0)
    description: str
    mitigation_suggestions: List[str] = Field(default_factory=list)
    
    @field_validator('impact_score')
    @classmethod
    def round_impact(cls, v):
        return round(v, 2)
    
    @field_validator('likelihood')
    @classmethod
    def round_likelihood(cls, v):
        return round(v, 3)

# ========= Main Assessment Models =========

class ProtocolInfo(BaseModel):
    """Basic protocol information"""
    name: str
    normalized_name: str
    category: Optional[str] = None
    website: Optional[str] = None
    documentation: Optional[str] = None
    chains: List[str] = Field(default_factory=list)

class RiskAssessment(BaseModel):
    """Complete risk assessment for a protocol"""
    protocol: ProtocolInfo
    
    # Overall assessment
    overall_risk_score: float = Field(ge=0.0, le=100.0)
    risk_level: RiskLevel
    confidence: float = Field(ge=0.0, le=1.0)
    
    # Component breakdown
    component_scores: ComponentRiskScore
    
    # Risk factors
    major_risks: List[RiskFactorDetail] = Field(default_factory=list)
    minor_risks: List[RiskFactorDetail] = Field(default_factory=list)
    
    # Agent insights
    agent_insights: Dict[str, AgentInsight] = Field(default_factory=dict)
    
    # Data quality
    data_quality: DataQuality
    
    # Analysis metadata
    analysis_id: str
    session_id: str
    assessment_time: datetime = Field(default_factory=datetime.utcnow)
    total_execution_time: float
    
    # Natural language summary
    executive_summary: str
    detailed_explanation: str
    recommendations: List[str] = Field(default_factory=list)
    
    @field_validator('overall_risk_score')
    @classmethod
    def round_overall_score(cls, v):
        return round(v, 2)
    
    @field_validator('confidence')
    @classmethod
    def round_confidence(cls, v):
        return round(v, 3)
    
    @field_validator('risk_level', mode='before')
    @classmethod
    def determine_risk_level(cls, v, values):
        if isinstance(v, str):
            return v
        
        # Auto-determine risk level from overall score
        if hasattr(values, 'data') and 'overall_risk_score' in values.data:
            score = values.data['overall_risk_score']
            if score <= 30:
                return RiskLevel.LOW
            elif score <= 60:
                return RiskLevel.MEDIUM
            elif score <= 85:
                return RiskLevel.HIGH
            else:
                return RiskLevel.CRITICAL
        
        return RiskLevel.MEDIUM

# ========= API Response Models =========

class AssessmentResponse(BaseResponse):
    """Main API response for risk assessment"""
    success: bool = True
    assessment: RiskAssessment
    cached: bool = False
    cache_age_seconds: Optional[int] = None

class ProtocolListResponse(BaseResponse):
    """Response for supported protocols list"""
    success: bool = True
    protocols: List[str]
    total_count: int
    
    @field_validator('total_count', mode='before')
    @classmethod
    def set_total_count(cls, v, values):
        if hasattr(values, 'data') and 'protocols' in values.data:
            return len(values.data['protocols'])
        return v or 0

class HealthCheckResponse(BaseResponse):
    """Health check response"""
    success: bool = True
    system_status: str
    components: Dict[str, Any] = Field(default_factory=dict)
    uptime_seconds: Optional[float] = None

class AgentStatusResponse(BaseResponse):
    """Individual agent status response"""
    success: bool = True
    agent_insights: Dict[str, AgentInsight]
    session_info: Dict[str, Any] = Field(default_factory=dict)

# ========= Input Models =========

class AssessmentRequest(BaseModel):
    """Request model for risk assessment"""
    protocol_name: str = Field(min_length=1, max_length=100)
    force_refresh: bool = False
    include_agent_details: bool = True
    analysis_depth: str = Field(default="standard", pattern="^(quick|standard|deep)$")  # ← Fixed: regex → pattern
    
    @field_validator('protocol_name')
    @classmethod
    def clean_protocol_name(cls, v):
        return v.strip()

class ProtocolValidationRequest(BaseModel):
    """Request model for protocol validation"""
    protocol_name: str = Field(min_length=1, max_length=100)

class ProtocolValidationResponse(BaseResponse):
    """Response for protocol validation"""
    success: bool = True
    is_supported: bool
    normalized_name: Optional[str] = None
    suggestions: List[str] = Field(default_factory=list)

# ========= Utility Models =========

class MetricTrend(BaseModel):
    """Trend information for metrics"""
    current_value: float
    previous_value: Optional[float] = None
    change_percent: Optional[float] = None
    trend_direction: Optional[str] = None  # "up", "down", "stable"
    time_period: str = "24h"
    
    @field_validator('change_percent')
    @classmethod
    def round_change(cls, v):
        return round(v, 2) if v is not None else None

class HistoricalDataPoint(BaseModel):
    """Historical data point"""
    timestamp: datetime
    value: float
    metric_name: str
    
    @field_validator('value')
    @classmethod
    def round_value(cls, v):
        return round(v, 4)

# ========= Comparison Models =========

class ProtocolComparison(BaseModel):
    """Comparison between two protocols"""
    protocol_a: str
    protocol_b: str
    comparison_metrics: Dict[str, Dict[str, float]]
    winner_by_category: Dict[str, str]
    overall_recommendation: str
    confidence: float = Field(ge=0.0, le=1.0)

class ComparisonResponse(BaseResponse):
    """Response for protocol comparison"""
    success: bool = True
    comparison: ProtocolComparison

# ========= Export all models =========

__all__ = [
    # Enums
    'RiskLevel', 'AgentStatus', 'DataSourceType',
    
    # Base models
    'BaseResponse', 'ErrorDetail', 'ErrorResponse',
    
    # Data models
    'DataSource', 'DataQuality', 'AgentInsight', 'ComponentRiskScore', 
    'RiskFactorDetail', 'ProtocolInfo', 'RiskAssessment',
    
    # API models
    'AssessmentResponse', 'ProtocolListResponse', 'HealthCheckResponse',
    'AgentStatusResponse', 'AssessmentRequest', 'ProtocolValidationRequest',
    'ProtocolValidationResponse',
    
    # Utility models
    'MetricTrend', 'HistoricalDataPoint', 'ProtocolComparison', 'ComparisonResponse'
]