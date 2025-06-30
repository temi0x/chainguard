import asyncio
import json
import math
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

# Internal imports
from agents.base_adk_agent import BaseChainGuardAgent, AgentContext, AgentResult, register_agent
from tools import DeFiDataADKTool
from memory.adk_memory_manager import memory_manager

logger = logging.getLogger(__name__)

@register_agent
class MarketIntelligenceAgent(BaseChainGuardAgent):
    """
    Market Intelligence Agent - Financial risk assessment and market analysis.
    
    This agent specializes in:
    1. TVL stability and trend analysis
    2. Market performance and volatility assessment
    3. Liquidity health evaluation
    4. Yield sustainability analysis
    5. Financial risk factor identification
    """
    
    def __init__(self):
        super().__init__(
            agent_id="market_intelligence",
            model_type="pro",  # Use pro model for complex financial analysis
            specialized_tools=[DeFiDataADKTool]
        )
        
        # Risk weighting for different financial factors
        self.financial_weights = {
            'tvl_stability': 0.25,
            'market_performance': 0.20,
            'liquidity_health': 0.20,
            'yield_sustainability': 0.15,
            'market_correlation': 0.10,
            'adoption_metrics': 0.10
        }
        
        # Market risk thresholds
        self.risk_thresholds = {
            'tvl_decline_critical': -50,  # > 50% decline is critical
            'tvl_decline_high': -30,      # > 30% decline is high risk
            'volume_ratio_low': 0.5,      # < 0.5% volume/mcap is low liquidity
            'volatility_high': 30,        # > 30% price change in 24h is high volatility
        }
        
        logger.info("💰 Market Intelligence Agent initialized for financial analysis")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt defining the Market Intelligence Agent's role"""
        return """You are the Market Intelligence Agent for ChainGuard AI, specializing in financial risk assessment and market analysis for DeFi protocols.

Your expertise includes:
1. TVL ANALYSIS - Evaluating total value locked trends, stability, and growth patterns
2. MARKET PERFORMANCE - Assessing price stability, trading volume, and market metrics
3. LIQUIDITY HEALTH - Analyzing liquidity depth, trading activity, and market efficiency
4. YIELD SUSTAINABILITY - Evaluating revenue models, yield sources, and long-term viability
5. FINANCIAL RISK IDENTIFICATION - Identifying market-related risks and vulnerabilities

Your analysis should focus on:
- TVL trends and stability indicators
- Market cap, trading volume, and liquidity metrics
- Price volatility and correlation analysis
- Revenue generation and yield sustainability
- Market adoption and ecosystem growth
- Financial stress indicators and risk factors

Always provide quantitative analysis with clear risk implications and market context."""
    
    async def analyze(self, context: AgentContext) -> AgentResult:
        """
        Main analysis method for financial risk assessment.
        
        Uses DeFi market data to assess financial health and stability.
        """
        start_time = datetime.utcnow()
        protocol_name = context.protocol_name
        
        self.log_analysis_step("Starting financial analysis", {"protocol": protocol_name})
        
        try:
            # Get data from Data Hunter Agent results
            previous_results = context.previous_results
            defi_data = self._extract_defi_data(previous_results)
            
            if not defi_data:
                # If no previous results, collect our own data
                defi_data = await self._collect_financial_data(protocol_name)
            
            # Perform comprehensive financial analysis
            financial_analysis = await self._analyze_financial_metrics(defi_data, protocol_name)
            
            # Assess market performance and stability
            market_analysis = await self._analyze_market_performance(defi_data, protocol_name)
            
            # Evaluate liquidity and trading health
            liquidity_analysis = await self._analyze_liquidity_health(defi_data, protocol_name)
            
            # Assess yield sustainability
            sustainability_analysis = await self._analyze_yield_sustainability(defi_data, protocol_name)
            
            # Identify financial risks
            financial_risks = await self._identify_financial_risks(
                financial_analysis, market_analysis, liquidity_analysis, sustainability_analysis
            )
            
            # Generate market insights with LLM
            market_insights = await self._generate_market_insights(
                financial_analysis, market_analysis, liquidity_analysis, 
                sustainability_analysis, financial_risks, protocol_name
            )
            
            # Calculate overall financial risk score
            overall_financial_score = self._calculate_financial_score(
                financial_analysis, market_analysis, liquidity_analysis, sustainability_analysis
            )
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Calculate confidence based on data availability and analysis completeness
            confidence = self._calculate_analysis_confidence(defi_data, financial_analysis)
            
            # Compile comprehensive result
            result_data = {
                'protocol_name': protocol_name,
                'financial_risk_score': overall_financial_score,
                'financial_analysis': financial_analysis,
                'market_analysis': market_analysis,
                'liquidity_analysis': liquidity_analysis,
                'sustainability_analysis': sustainability_analysis,
                'financial_risks': financial_risks,
                'market_insights': market_insights,
                'risk_factors': self._categorize_financial_risks(financial_risks),
                'recommendations': self._generate_financial_recommendations(
                    financial_analysis, market_analysis, liquidity_analysis
                ),
                'data_sources_used': {
                    'defi_data_available': bool(defi_data),
                    'tvl_data_available': bool(defi_data.get('tvl_metrics')),
                    'price_data_available': bool(defi_data.get('price_metrics'))
                },
                'analysis_metadata': {
                    'analysis_depth': 'comprehensive',
                    'confidence_level': confidence,
                    'execution_time': execution_time,
                    'model_used': self.model_type
                }
            }
            
            self.log_analysis_step(
                "Financial analysis completed",
                {
                    "financial_score": overall_financial_score,
                    "confidence": confidence,
                    "risks_identified": len(financial_risks),
                    "execution_time": execution_time
                }
            )
            
            return AgentResult(
                agent_id=self.agent_id,
                success=True,
                data=result_data,
                confidence=confidence,
                reasoning=market_insights.get('summary', 'Comprehensive financial analysis completed'),
                execution_time=execution_time,
                timestamp=datetime.utcnow(),
                errors=[]
            )
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            error_msg = f"Financial analysis failed for {protocol_name}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            return AgentResult(
                agent_id=self.agent_id,
                success=False,
                data={},
                confidence=0.0,
                reasoning=f"Financial analysis failed due to: {str(e)}",
                execution_time=execution_time,
                timestamp=datetime.utcnow(),
                errors=[error_msg]
            )
    
    def _extract_defi_data(self, previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract DeFi data from Data Hunter Agent results"""
        try:
            data_hunter_result = previous_results.get('data_hunter', {})
            if isinstance(data_hunter_result, dict) and 'result' in data_hunter_result:
                defi_source = data_hunter_result['result'].get('source_analysis', {}).get('defi_data', {})
                validated_sources = data_hunter_result['result'].get('validated_sources', {})
                return {
                    'source_analysis': defi_source,
                    'defi_sources': validated_sources.get('defi_sources', [])
                }
        except Exception as e:
            logger.warning(f"Could not extract DeFi data from previous results: {e}")
        
        return {}
    
    async def _collect_financial_data(self, protocol_name: str) -> Dict[str, Any]:
        """Collect financial data if not available from previous agents"""
        defi_tool = DeFiDataADKTool()
        
        try:
            defi_result = await defi_tool.execute_with_timeout(protocol_name, timeout_seconds=30)
            if defi_result.success:
                return defi_result.data
        except Exception as e:
            logger.warning(f"Failed to collect DeFi data: {e}")
        
        return {}
    
    async def _analyze_financial_metrics(self, defi_data: Dict[str, Any], protocol_name: str) -> Dict[str, Any]:
        """Analyze core financial metrics"""
        
        financial_metrics = {
            'tvl_analysis': self._analyze_tvl_metrics(defi_data),
            'growth_analysis': self._analyze_growth_patterns(defi_data),
            'stability_analysis': self._analyze_financial_stability(defi_data),
            'scale_analysis': self._analyze_protocol_scale(defi_data)
        }
        
        # Calculate overall financial health score
        scores = [analysis.get('score', 0) for analysis in financial_metrics.values()]
        overall_score = sum(scores) / len(scores) if scores else 0
        
        return {
            'overall_score': overall_score,
            'components': financial_metrics
        }
    
    def _analyze_tvl_metrics(self, defi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze TVL trends and stability"""
        score = 50  # Base score
        details = []
        risks = []
        
        tvl_metrics = defi_data.get('tvl_metrics', {})
        current_tvl = tvl_metrics.get('current_tvl_usd', 0)
        tvl_change_30d = tvl_metrics.get('tvl_change_30d_percent', 0)
        
        # TVL size scoring (logarithmic scale)
        if current_tvl > 0:
            tvl_size_score = min(50, math.log10(current_tvl / 1_000_000) * 15)  # $1B = max bonus
            score += tvl_size_score
            
            if current_tvl > 1_000_000_000:  # $1B+
                details.append(f"Large-scale protocol with ${current_tvl/1_000_000_000:.1f}B TVL")
            elif current_tvl > 100_000_000:  # $100M+
                details.append(f"Medium-scale protocol with ${current_tvl/1_000_000:.0f}M TVL")
            else:
                details.append(f"Small-scale protocol with ${current_tvl/1_000_000:.1f}M TVL")
                if current_tvl < 10_000_000:  # Less than $10M
                    risks.append("Low TVL indicates limited adoption")
                    score -= 15
        
        # TVL trend analysis
        if tvl_change_30d > 20:
            score += 15
            details.append(f"Strong TVL growth of {tvl_change_30d:.1f}% in 30 days")
        elif tvl_change_30d > 0:
            score += 5
            details.append(f"Positive TVL growth of {tvl_change_30d:.1f}% in 30 days")
        elif tvl_change_30d > self.risk_thresholds['tvl_decline_high']:
            score -= 10
            details.append(f"TVL decline of {tvl_change_30d:.1f}% in 30 days")
        elif tvl_change_30d > self.risk_thresholds['tvl_decline_critical']:
            score -= 25
            risks.append(f"Significant TVL decline of {tvl_change_30d:.1f}% in 30 days")
        else:
            score -= 40
            risks.append(f"Critical TVL decline of {tvl_change_30d:.1f}% in 30 days")
        
        return {
            'score': min(100, max(0, score)),
            'details': details,
            'risks': risks,
            'current_tvl': current_tvl,
            'tvl_trend': 'growth' if tvl_change_30d > 5 else 'stable' if tvl_change_30d > -5 else 'decline'
        }
    
    def _analyze_growth_patterns(self, defi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze growth patterns and trends"""
        score = 60  # Base score
        details = []
        risks = []
        
        # Chain distribution analysis
        chain_distribution = defi_data.get('chain_distribution', {})
        chains = chain_distribution.get('chains', {})
        chain_count = chain_distribution.get('chain_count', 0)
        
        if chain_count > 5:
            score += 20
            details.append(f"Multi-chain presence across {chain_count} networks")
        elif chain_count > 1:
            score += 10
            details.append(f"Multi-chain deployment on {chain_count} networks")
        else:
            risks.append("Single-chain dependency")
            score -= 10
        
        # TVL distribution analysis
        if chains:
            # Check for concentration risk
            total_tvl = chain_distribution.get('total_tvl', 0)
            if total_tvl > 0:
                # Find the largest chain's share
                max_chain_tvl = max(v for k, v in chains.items() if not k.endswith('_percentage'))
                concentration = (max_chain_tvl / total_tvl) * 100 if total_tvl > 0 else 0
                
                if concentration > 80:
                    risks.append("High chain concentration risk")
                    score -= 15
                elif concentration > 60:
                    details.append("Moderate chain concentration")
                    score -= 5
                else:
                    details.append("Well-distributed across chains")
                    score += 10
        
        return {
            'score': min(100, max(0, score)),
            'details': details,
            'risks': risks,
            'chain_diversification': 'high' if chain_count > 3 else 'medium' if chain_count > 1 else 'low'
        }
    
    def _analyze_financial_stability(self, defi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze financial stability indicators"""
        score = 60  # Base score
        details = []
        risks = []
        
        tvl_metrics = defi_data.get('tvl_metrics', {})
        historical_tvl = tvl_metrics.get('historical_tvl', [])
        
        # Volatility analysis
        if len(historical_tvl) >= 5:
            tvl_values = [entry.get('tvl_usd', 0) for entry in historical_tvl]
            if tvl_values:
                # Calculate simple volatility (standard deviation / mean)
                mean_tvl = sum(tvl_values) / len(tvl_values)
                if mean_tvl > 0:
                    variance = sum((x - mean_tvl) ** 2 for x in tvl_values) / len(tvl_values)
                    volatility = (variance ** 0.5) / mean_tvl
                    
                    if volatility < 0.1:  # Less than 10% volatility
                        score += 20
                        details.append("Low TVL volatility indicates stability")
                    elif volatility < 0.3:  # Less than 30% volatility
                        score += 10
                        details.append("Moderate TVL volatility")
                    else:
                        score -= 15
                        risks.append("High TVL volatility")
        
        # Market cap to TVL ratio analysis
        mcap_tvl_ratio = tvl_metrics.get('mcap_tvl_ratio')
        if mcap_tvl_ratio:
            if 0.5 <= mcap_tvl_ratio <= 2.0:
                score += 10
                details.append("Healthy market cap to TVL ratio")
            elif mcap_tvl_ratio > 5.0:
                score -= 10
                risks.append("High market cap relative to TVL")
            elif mcap_tvl_ratio < 0.2:
                score -= 5
                details.append("Low market cap relative to TVL")
        
        return {
            'score': min(100, max(0, score)),
            'details': details,
            'risks': risks,
            'stability_level': 'high' if score > 75 else 'medium' if score > 50 else 'low'
        }
    
    def _analyze_protocol_scale(self, defi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze protocol scale and market position"""
        score = 50  # Base score
        details = []
        risks = []
        
        tvl_metrics = defi_data.get('tvl_metrics', {})
        current_tvl = tvl_metrics.get('current_tvl_usd', 0)
        tvl_rank = tvl_metrics.get('tvl_rank')
        
        # Scale assessment based on TVL
        if current_tvl > 5_000_000_000:  # $5B+
            score += 30
            details.append("Top-tier protocol by TVL")
        elif current_tvl > 1_000_000_000:  # $1B+
            score += 20
            details.append("Large-scale protocol")
        elif current_tvl > 100_000_000:  # $100M+
            score += 10
            details.append("Medium-scale protocol")
        elif current_tvl > 10_000_000:  # $10M+
            details.append("Small-scale protocol")
        else:
            risks.append("Very small protocol scale")
            score -= 20
        
        # Ranking assessment
        if tvl_rank:
            if tvl_rank <= 10:
                score += 20
                details.append(f"Top 10 protocol by TVL (rank #{tvl_rank})")
            elif tvl_rank <= 50:
                score += 10
                details.append(f"Top 50 protocol by TVL (rank #{tvl_rank})")
            elif tvl_rank <= 100:
                details.append(f"Top 100 protocol by TVL (rank #{tvl_rank})")
            else:
                details.append(f"Ranked #{tvl_rank} by TVL")
        
        return {
            'score': min(100, max(0, score)),
            'details': details,
            'risks': risks,
            'scale_tier': 'large' if current_tvl > 1_000_000_000 else 'medium' if current_tvl > 100_000_000 else 'small'
        }
    
    async def _analyze_market_performance(self, defi_data: Dict[str, Any], protocol_name: str) -> Dict[str, Any]:
        """Analyze market performance metrics"""
        
        market_analysis = {
            'price_performance': self._analyze_price_metrics(defi_data),
            'trading_activity': self._analyze_trading_metrics(defi_data),
            'market_position': self._analyze_market_position(defi_data),
            'volatility_assessment': self._analyze_price_volatility(defi_data)
        }
        
        # Calculate overall market score
        scores = [analysis.get('score', 0) for analysis in market_analysis.values()]
        overall_score = sum(scores) / len(scores) if scores else 0
        
        return {
            'overall_score': overall_score,
            'components': market_analysis
        }
    
    def _analyze_price_metrics(self, defi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze token price performance"""
        score = 60  # Base score
        details = []
        risks = []
        
        price_metrics = defi_data.get('price_metrics', {})
        current_price = price_metrics.get('current_price_usd', 0)
        price_change_24h = price_metrics.get('price_change_24h_percent', 0)
        
        # Price level assessment
        if current_price > 0:
            details.append(f"Current token price: ${current_price:.2f}")
            
            # 24h price change analysis
            if abs(price_change_24h) < 5:
                score += 10
                details.append("Stable price action (24h)")
            elif abs(price_change_24h) < 15:
                details.append(f"Moderate price movement: {price_change_24h:.1f}% (24h)")
            elif abs(price_change_24h) > self.risk_thresholds['volatility_high']:
                score -= 15
                risks.append(f"High price volatility: {price_change_24h:.1f}% (24h)")
            
            # Longer-term performance
            market_data = defi_data.get('market_data', {})
            price_change_7d = market_data.get('price_change_7d_percent', 0)
            price_change_30d = market_data.get('price_change_30d_percent', 0)
            
            if price_change_7d and price_change_30d:
                if price_change_30d > 20:
                    score += 15
                    details.append(f"Strong 30-day performance: {price_change_30d:.1f}%")
                elif price_change_30d < -30:
                    score -= 10
                    risks.append(f"Poor 30-day performance: {price_change_30d:.1f}%")
        
        return {
            'score': min(100, max(0, score)),
            'details': details,
            'risks': risks,
            'price_trend': 'bullish' if price_change_24h > 5 else 'bearish' if price_change_24h < -5 else 'stable'
        }
    
    def _analyze_trading_metrics(self, defi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trading volume and liquidity"""
        score = 50  # Base score
        details = []
        risks = []
        
        price_metrics = defi_data.get('price_metrics', {})
        volume_24h = price_metrics.get('volume_24h_usd', 0)
        market_cap = price_metrics.get('market_cap_usd', 0)
        
        # Volume analysis
        if volume_24h > 0:
            if volume_24h > 10_000_000:  # $10M+ daily volume
                score += 20
                details.append(f"High trading volume: ${volume_24h/1_000_000:.1f}M")
            elif volume_24h > 1_000_000:  # $1M+ daily volume
                score += 10
                details.append(f"Good trading volume: ${volume_24h/1_000_000:.1f}M")
            elif volume_24h < 100_000:  # Less than $100k daily volume
                score -= 15
                risks.append("Low trading volume")
        
        # Volume to market cap ratio
        if market_cap > 0 and volume_24h > 0:
            volume_ratio = (volume_24h / market_cap) * 100
            
            if 1 <= volume_ratio <= 15:
                score += 15
                details.append(f"Healthy volume/mcap ratio: {volume_ratio:.1f}%")
            elif volume_ratio > 50:
                score -= 10
                risks.append("Extremely high trading turnover")
            elif volume_ratio < self.risk_thresholds['volume_ratio_low']:
                score -= 10
                risks.append("Low trading activity relative to market cap")
        
        return {
            'score': min(100, max(0, score)),
            'details': details,
            'risks': risks,
            'liquidity_level': 'high' if volume_24h > 10_000_000 else 'medium' if volume_24h > 1_000_000 else 'low'
        }
    
    def _analyze_market_position(self, defi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market position and ranking"""
        score = 60  # Base score
        details = []
        risks = []
        
        market_data = defi_data.get('market_data', {})
        market_cap_rank = market_data.get('market_cap_rank')
        market_cap = defi_data.get('price_metrics', {}).get('market_cap_usd', 0)
        
        # Market cap ranking
        if market_cap_rank:
            if market_cap_rank <= 20:
                score += 25
                details.append(f"Top 20 cryptocurrency by market cap (rank #{market_cap_rank})")
            elif market_cap_rank <= 100:
                score += 15
                details.append(f"Top 100 cryptocurrency by market cap (rank #{market_cap_rank})")
            elif market_cap_rank <= 500:
                score += 5
                details.append(f"Top 500 cryptocurrency by market cap (rank #{market_cap_rank})")
            else:
                details.append(f"Market cap rank: #{market_cap_rank}")
        
        # Market cap size
        if market_cap > 0:
            if market_cap > 10_000_000_000:  # $10B+
                score += 20
                details.append("Large-cap cryptocurrency")
            elif market_cap > 1_000_000_000:  # $1B+
                score += 10
                details.append("Mid-cap cryptocurrency")
            elif market_cap < 100_000_000:  # Less than $100M
                risks.append("Small market capitalization")
                score -= 10
        
        return {
            'score': min(100, max(0, score)),
            'details': details,
            'risks': risks,
            'market_tier': 'large' if market_cap > 1_000_000_000 else 'medium' if market_cap > 100_000_000 else 'small'
        }
    
    def _analyze_price_volatility(self, defi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze price volatility and stability"""
        score = 70  # Base score
        details = []
        risks = []
        
        price_metrics = defi_data.get('price_metrics', {})
        market_data = defi_data.get('market_data', {})
        
        # Short-term volatility
        price_change_24h = price_metrics.get('price_change_24h_percent', 0)
        if abs(price_change_24h) < 5:
            score += 15
            details.append("Low 24h price volatility")
        elif abs(price_change_24h) > 20:
            score -= 20
            risks.append("High 24h price volatility")
        
        # Medium-term volatility
        price_change_7d = market_data.get('price_change_7d_percent', 0)
        if price_change_7d and abs(price_change_7d) > 40:
            score -= 15
            risks.append("High 7-day price volatility")
        
        # All-time highs and lows
        ath = market_data.get('all_time_high')
        atl = market_data.get('all_time_low')
        current_price = price_metrics.get('current_price_usd', 0)
        
        if ath and current_price > 0:
            distance_from_ath = ((ath - current_price) / ath) * 100
            if distance_from_ath < 20:
                details.append("Near all-time high")
                score += 5
            elif distance_from_ath > 80:
                details.append("Far from all-time high")
                score -= 5
        
        return {
            'score': min(100, max(0, score)),
            'details': details,
            'risks': risks,
            'volatility_level': 'low' if abs(price_change_24h) < 5 else 'high' if abs(price_change_24h) > 20 else 'medium'
        }
    
    async def _analyze_liquidity_health(self, defi_data: Dict[str, Any], protocol_name: str) -> Dict[str, Any]:
        """Analyze liquidity health and trading efficiency"""
        
        liquidity_analysis = {
            'trading_liquidity': self._assess_trading_liquidity(defi_data),
            'market_depth': self._assess_market_depth(defi_data),
            'liquidity_stability': self._assess_liquidity_stability(defi_data)
        }
        
        # Calculate overall liquidity score
        scores = [analysis.get('score', 0) for analysis in liquidity_analysis.values()]
        overall_score = sum(scores) / len(scores) if scores else 0
        
        return {
            'overall_score': overall_score,
            'components': liquidity_analysis
        }
    
    def _assess_trading_liquidity(self, defi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess trading liquidity quality"""
        score = 60  # Base score
        details = []
        risks = []
        
        market_data = defi_data.get('market_data', {})
        liquidity_score_cg = market_data.get('liquidity_score', 0)
        
        if liquidity_score_cg:
            normalized_score = liquidity_score_cg * 100  # CoinGecko score is 0-1
            score = normalized_score
            
            if normalized_score > 80:
                details.append("Excellent liquidity depth")
            elif normalized_score > 60:
                details.append("Good liquidity depth")
            elif normalized_score < 40:
                risks.append("Poor liquidity depth")
        
        return {
            'score': min(100, max(0, score)),
            'details': details,
            'risks': risks
        }
    
    def _assess_market_depth(self, defi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess market depth and order book quality"""
        score = 60  # Base score
        details = []
        risks = []
        
        # Use volume metrics as proxy for market depth
        price_metrics = defi_data.get('price_metrics', {})
        volume_24h = price_metrics.get('volume_24h_usd', 0)
        market_cap = price_metrics.get('market_cap_usd', 0)
        
        if market_cap > 0 and volume_24h > 0:
            volume_ratio = (volume_24h / market_cap) * 100
            
            if 2 <= volume_ratio <= 20:
                score += 20
                details.append("Healthy market depth indicators")
            elif volume_ratio < 1:
                score -= 15
                risks.append("Low market depth")
            elif volume_ratio > 50:
                score -= 10
                risks.append("Potentially thin order book")
        
        return {
            'score': min(100, max(0, score)),
            'details': details,
            'risks': risks
        }
    
    def _assess_liquidity_stability(self, defi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess liquidity stability over time"""
        score = 70  # Base score
        details = []
        risks = []
        
        # Assess based on TVL stability as proxy for liquidity stability
        tvl_metrics = defi_data.get('tvl_metrics', {})
        tvl_change_30d = tvl_metrics.get('tvl_change_30d_percent', 0)
        
        if abs(tvl_change_30d) < 20:
            score += 15
            details.append("Stable liquidity over 30 days")
        elif tvl_change_30d < -50:
            score -= 25
            risks.append("Significant liquidity outflow")
        
        return {
            'score': min(100, max(0, score)),
            'details': details,
            'risks': risks
        }
    
    async def _analyze_yield_sustainability(self, defi_data: Dict[str, Any], protocol_name: str) -> Dict[str, Any]:
        """Analyze yield sustainability and revenue model"""
        
        sustainability_analysis = {
            'revenue_model': self._assess_revenue_model(defi_data),
            'yield_sources': self._assess_yield_sources(defi_data),
            'economic_sustainability': self._assess_economic_sustainability(defi_data)
        }
        
        # Calculate overall sustainability score
        scores = [analysis.get('score', 0) for analysis in sustainability_analysis.values()]
        overall_score = sum(scores) / len(scores) if scores else 0
        
        return {
            'overall_score': overall_score,
            'components': sustainability_analysis
        }
    
    def _assess_revenue_model(self, defi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess protocol revenue model sustainability"""
        score = 60  # Base score
        details = []
        risks = []
        
        # Category-based assessment
        category = defi_data.get('category', '').lower()
        
        if 'lending' in category:
            score += 10
            details.append("Lending protocol - sustainable fee model")
        elif 'dex' in category or 'exchange' in category:
            score += 15
            details.append("DEX protocol - trading fee revenue")
        elif 'yield' in category or 'farming' in category:
            score -= 5
            details.append("Yield farming - sustainability depends on incentives")
        
        # TVL growth as indicator of sustainable model
        tvl_metrics = defi_data.get('tvl_metrics', {})
        tvl_change_30d = tvl_metrics.get('tvl_change_30d_percent', 0)
        
        if tvl_change_30d > 10:
            score += 15
            details.append("Growing TVL indicates healthy revenue model")
        elif tvl_change_30d < -20:
            score -= 10
            risks.append("Declining TVL may indicate revenue model issues")
        
        return {
            'score': min(100, max(0, score)),
            'details': details,
            'risks': risks
        }
    
    def _assess_yield_sources(self, defi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess yield source diversification and sustainability"""
        score = 65  # Base score
        details = []
        risks = []
        
        # Chain diversification as proxy for yield source diversification
        chain_distribution = defi_data.get('chain_distribution', {})
        chain_count = chain_distribution.get('chain_count', 0)
        
        if chain_count > 3:
            score += 15
            details.append("Multi-chain deployment diversifies yield sources")
        elif chain_count == 1:
            score -= 10
            risks.append("Single-chain dependency for yield generation")
        
        # Protocol maturity
        tvl_metrics = defi_data.get('tvl_metrics', {})
        current_tvl = tvl_metrics.get('current_tvl_usd', 0)
        
        if current_tvl > 1_000_000_000:  # $1B+ indicates mature yield sources
            score += 10
            details.append("Large TVL indicates mature yield generation")
        elif current_tvl < 50_000_000:  # Less than $50M
            score -= 5
            details.append("Small TVL - yield sustainability unproven")
        
        return {
            'score': min(100, max(0, score)),
            'details': details,
            'risks': risks
        }
    
    def _assess_economic_sustainability(self, defi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall economic sustainability"""
        score = 60  # Base score
        details = []
        risks = []
        
        # Market cap to TVL ratio
        tvl_metrics = defi_data.get('tvl_metrics', {})
        mcap_tvl_ratio = tvl_metrics.get('mcap_tvl_ratio')
        
        if mcap_tvl_ratio:
            if 0.3 <= mcap_tvl_ratio <= 3.0:
                score += 15
                details.append("Healthy market cap to TVL ratio")
            elif mcap_tvl_ratio > 10:
                score -= 10
                risks.append("Very high market cap relative to TVL")
            elif mcap_tvl_ratio < 0.1:
                score -= 5
                details.append("Very low market cap relative to TVL")
        
        # Protocol age and stability (inferred from data quality)
        if defi_data.get('tvl_metrics') and defi_data.get('price_metrics'):
            score += 10
            details.append("Comprehensive market data suggests established protocol")
        
        return {
            'score': min(100, max(0, score)),
            'details': details,
            'risks': risks
        }
    
    async def _identify_financial_risks(self, financial_analysis: Dict[str, Any], market_analysis: Dict[str, Any], liquidity_analysis: Dict[str, Any], sustainability_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify specific financial risk factors"""
        
        risks = []
        
        # Extract risks from financial analysis
        for component, analysis in financial_analysis.get('components', {}).items():
            for risk in analysis.get('risks', []):
                risks.append({
                    'category': 'financial',
                    'subcategory': component,
                    'description': risk,
                    'severity': self._assess_financial_risk_severity(risk, analysis.get('score', 0)),
                    'impact': 'high' if analysis.get('score', 0) < 40 else 'medium' if analysis.get('score', 0) < 70 else 'low'
                })
        
        # Extract risks from market analysis
        for component, analysis in market_analysis.get('components', {}).items():
            for risk in analysis.get('risks', []):
                risks.append({
                    'category': 'market',
                    'subcategory': component,
                    'description': risk,
                    'severity': self._assess_financial_risk_severity(risk, analysis.get('score', 0)),
                    'impact': 'high' if analysis.get('score', 0) < 40 else 'medium' if analysis.get('score', 0) < 70 else 'low'
                })
        
        # Extract risks from liquidity analysis
        for component, analysis in liquidity_analysis.get('components', {}).items():
            for risk in analysis.get('risks', []):
                risks.append({
                    'category': 'liquidity',
                    'subcategory': component,
                    'description': risk,
                    'severity': self._assess_financial_risk_severity(risk, analysis.get('score', 0)),
                    'impact': 'high' if analysis.get('score', 0) < 40 else 'medium' if analysis.get('score', 0) < 70 else 'low'
                })
        
        # Extract risks from sustainability analysis
        for component, analysis in sustainability_analysis.get('components', {}).items():
            for risk in analysis.get('risks', []):
                risks.append({
                    'category': 'sustainability',
                    'subcategory': component,
                    'description': risk,
                    'severity': self._assess_financial_risk_severity(risk, analysis.get('score', 0)),
                    'impact': 'high' if analysis.get('score', 0) < 40 else 'medium' if analysis.get('score', 0) < 70 else 'low'
                })
        
        return risks
    
    def _assess_financial_risk_severity(self, risk_description: str, score: float) -> str:
        """Assess financial risk severity"""
        critical_keywords = ['critical', 'significant', 'high', 'extremely']
        high_keywords = ['decline', 'low', 'poor', 'small']
        
        risk_lower = risk_description.lower()
        
        if any(keyword in risk_lower for keyword in critical_keywords) or score < 20:
            return 'critical'
        elif any(keyword in risk_lower for keyword in high_keywords) or score < 40:
            return 'high'
        elif score < 60:
            return 'medium'
        else:
            return 'low'
    
    async def _generate_market_insights(self, financial_analysis: Dict[str, Any], market_analysis: Dict[str, Any], liquidity_analysis: Dict[str, Any], sustainability_analysis: Dict[str, Any], financial_risks: List[Dict[str, Any]], protocol_name: str) -> Dict[str, Any]:
        """Generate market insights using LLM"""
        
        # Prepare context for LLM
        context = {
            'protocol_name': protocol_name,
            'financial_score': financial_analysis.get('overall_score', 0),
            'market_score': market_analysis.get('overall_score', 0),
            'liquidity_score': liquidity_analysis.get('overall_score', 0),
            'sustainability_score': sustainability_analysis.get('overall_score', 0),
            'high_risk_count': len([r for r in financial_risks if r.get('severity') in ['high', 'critical']]),
            'total_risks': len(financial_risks)
        }
        
        prompt = f"""Analyze the financial assessment for {protocol_name} and provide expert market insights:

Financial Health Score: {context['financial_score']:.1f}/100
Market Performance Score: {context['market_score']:.1f}/100
Liquidity Health Score: {context['liquidity_score']:.1f}/100
Sustainability Score: {context['sustainability_score']:.1f}/100
High Risk Issues: {context['high_risk_count']}
Total Risk Factors: {context['total_risks']}

Based on this financial analysis, provide:
1. Overall financial health assessment
2. Key market strengths and vulnerabilities
3. Liquidity and trading considerations
4. Sustainability outlook and concerns
5. Investment risk implications
6. Comparison to typical DeFi market standards

Focus on practical financial implications for users and investors."""
        
        try:
            insights_text = await self.call_gemini(prompt, context)
            
            # Parse insights into structured format
            insights = {
                'summary': insights_text,
                'key_findings': self._extract_financial_findings(financial_analysis, market_analysis, liquidity_analysis),
                'critical_risks': [r for r in financial_risks if r.get('severity') == 'critical'],
                'financial_rating': self._determine_financial_rating(financial_analysis.get('overall_score', 0))
            }
            
            return insights
            
        except Exception as e:
            logger.warning(f"LLM insights generation failed: {e}")
            
            # Fallback to structured insights
            return {
                'summary': f"Financial analysis completed for {protocol_name}",
                'key_findings': self._extract_financial_findings(financial_analysis, market_analysis, liquidity_analysis),
                'critical_risks': [r for r in financial_risks if r.get('severity') == 'critical'],
                'financial_rating': self._determine_financial_rating(financial_analysis.get('overall_score', 0))
            }
    
    def _extract_financial_findings(self, financial_analysis: Dict[str, Any], market_analysis: Dict[str, Any], liquidity_analysis: Dict[str, Any]) -> List[str]:
        """Extract key financial findings"""
        findings = []
        
        financial_score = financial_analysis.get('overall_score', 0)
        if financial_score > 80:
            findings.append("Strong financial fundamentals")
        elif financial_score < 40:
            findings.append("Significant financial concerns")
        
        # TVL analysis
        tvl_component = financial_analysis.get('components', {}).get('tvl_analysis', {})
        tvl_trend = tvl_component.get('tvl_trend', 'unknown')
        if tvl_trend == 'growth':
            findings.append("Positive TVL growth trend")
        elif tvl_trend == 'decline':
            findings.append("TVL declining - monitor closely")
        
        # Market performance
        market_score = market_analysis.get('overall_score', 0)
        if market_score > 75:
            findings.append("Strong market performance")
        elif market_score < 45:
            findings.append("Market performance concerns")
        
        # Liquidity health
        liquidity_score = liquidity_analysis.get('overall_score', 0)
        if liquidity_score > 75:
            findings.append("Good liquidity and trading depth")
        elif liquidity_score < 50:
            findings.append("Liquidity concerns identified")
        
        return findings
    
    def _determine_financial_rating(self, financial_score: float) -> str:
        """Determine financial rating based on score"""
        if financial_score >= 85:
            return "EXCELLENT"
        elif financial_score >= 70:
            return "GOOD"
        elif financial_score >= 55:
            return "MODERATE"
        elif financial_score >= 40:
            return "POOR"
        else:
            return "CRITICAL"
    
    def _calculate_financial_score(self, financial_analysis: Dict[str, Any], market_analysis: Dict[str, Any], liquidity_analysis: Dict[str, Any], sustainability_analysis: Dict[str, Any]) -> float:
        """Calculate overall financial risk score"""
        
        # Weight different components
        weights = {
            'financial': 0.35,
            'market': 0.25,
            'liquidity': 0.25,
            'sustainability': 0.15
        }
        
        financial_score = financial_analysis.get('overall_score', 0)
        market_score = market_analysis.get('overall_score', 0)
        liquidity_score = liquidity_analysis.get('overall_score', 0)
        sustainability_score = sustainability_analysis.get('overall_score', 0)
        
        overall_score = (
            financial_score * weights['financial'] +
            market_score * weights['market'] +
            liquidity_score * weights['liquidity'] +
            sustainability_score * weights['sustainability']
        )
        
        return round(overall_score, 2)
    
    def _calculate_analysis_confidence(self, defi_data: Dict[str, Any], financial_analysis: Dict[str, Any]) -> float:
        """Calculate confidence in the financial analysis"""
        
        confidence_factors = []
        
        # Data availability confidence
        if defi_data.get('tvl_metrics'):
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.3)
        
        if defi_data.get('price_metrics'):
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.4)
        
        if defi_data.get('market_data'):
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.5)
        
        # Analysis completeness
        components = financial_analysis.get('components', {})
        completeness = len(components) / 4.0  # We have 4 financial components
        confidence_factors.append(completeness)
        
        # Average confidence with minimum threshold
        base_confidence = sum(confidence_factors) / len(confidence_factors)
        
        return max(0.4, min(1.0, base_confidence))  # Ensure confidence is between 0.4 and 1.0
    
    def _categorize_financial_risks(self, financial_risks: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Categorize financial risks by severity"""
        categorized = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
        for risk in financial_risks:
            severity = risk.get('severity', 'medium')
            description = risk.get('description', '')
            categorized[severity].append(description)
        
        return categorized
    
    def _generate_financial_recommendations(self, financial_analysis: Dict[str, Any], market_analysis: Dict[str, Any], liquidity_analysis: Dict[str, Any]) -> List[str]:
        """Generate financial recommendations"""
        recommendations = []
        
        # Financial recommendations
        tvl_analysis = financial_analysis.get('components', {}).get('tvl_analysis', {})
        if tvl_analysis.get('tvl_trend') == 'decline':
            recommendations.append("Monitor TVL trends closely for further decline")
        
        # Market recommendations
        market_components = market_analysis.get('components', {})
        trading_activity = market_components.get('trading_activity', {})
        if trading_activity.get('liquidity_level') == 'low':
            recommendations.append("Exercise caution due to low trading liquidity")
        
        # Liquidity recommendations
        liquidity_score = liquidity_analysis.get('overall_score', 0)
        if liquidity_score < 50:
            recommendations.append("Consider potential liquidity constraints for large positions")
        
        return recommendations
    
    async def _get_custom_memory_update(self, context: AgentContext, result: AgentResult) -> Optional[Dict[str, Any]]:
        """Update agent memory with financial analysis learnings"""
        if not result.success:
            return None
        
        protocol_name = context.protocol_name
        data = result.data
        
        memory_update = {
            'financial_assessments': {
                protocol_name.lower().replace(' ', '_'): {
                    'financial_score': data.get('financial_risk_score', 0),
                    'financial_rating': data.get('market_insights', {}).get('financial_rating', 'UNKNOWN'),
                    'tvl_trend': data.get('financial_analysis', {}).get('components', {}).get('tvl_analysis', {}).get('tvl_trend', 'unknown'),
                    'analysis_timestamp': datetime.utcnow().isoformat(),
                    'confidence_level': result.confidence
                }
            }
        }
        
        return memory_update
    
    def _get_required_data_fields(self) -> List[str]:
        """Required data fields for Market Intelligence Agent"""
        return [
            'financial_risk_score',
            'financial_analysis',
            'market_analysis',
            'liquidity_analysis',
            'market_insights'
        ]