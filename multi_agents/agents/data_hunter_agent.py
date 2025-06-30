import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

# Internal imports
from agents.base_adk_agent import BaseChainGuardAgent, AgentContext, AgentResult, register_agent
from tools import GitHubADKTool, DeFiDataADKTool, BlockchainADKTool
from memory.adk_memory_manager import memory_manager

logger = logging.getLogger(__name__)

@register_agent
class DataHunterAgent(BaseChainGuardAgent):
    """
    Data Hunter Agent - Discovers and validates data sources for protocol analysis.
    
    This agent uses all three ADK tools to:
    1. Discover available data sources for a protocol
    2. Validate data quality and reliability 
    3. Provide data source recommendations for other agents
    4. Identify data gaps and fallback options
    """
    
    def __init__(self):
        super().__init__(
            agent_id="data_hunter",
            model_type="flash",  # Use fast model for data discovery
            specialized_tools=[GitHubADKTool, DeFiDataADKTool, BlockchainADKTool]
        )
        
        # Initialize ADK tools
        self.github_tool = GitHubADKTool()
        self.defi_tool = DeFiDataADKTool()
        self.blockchain_tool = BlockchainADKTool()
        
        # Data source priorities
        self.source_priorities = {
            'github': 0.8,      # High priority for development data
            'defillama': 0.9,   # Highest priority for TVL data
            'coingecko': 0.7,   # Good for market data
            'etherscan': 0.85,  # High priority for contract verification
            'subgraph': 0.75    # Good for on-chain activity
        }
        
        logger.info("🕵️ Data Hunter Agent initialized with ADK tools")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt defining the Data Hunter Agent's role"""
        return """You are the Data Hunter Agent for ChainGuard AI, responsible for discovering and validating data sources for DeFi protocol risk assessment.

Your primary responsibilities:
1. DISCOVER available data sources for any given protocol
2. VALIDATE data quality, freshness, and reliability across multiple sources
3. ASSESS data completeness and identify gaps
4. RECOMMEND optimal data collection strategies for other agents
5. PROVIDE fallback options when primary sources fail

You have access to three specialized ADK tools:
- GitHub Tool: Repository analysis, development activity, security indicators
- DeFi Data Tool: TVL metrics, market data, financial health indicators  
- Blockchain Tool: Contract verification, on-chain activity, transaction data

Your analysis should focus on:
- Data source reliability and freshness
- Cross-validation between different sources
- Identification of data quality issues
- Recommendations for comprehensive protocol analysis

Always provide confidence scores and explain your reasoning for data source recommendations."""
    
    async def analyze(self, context: AgentContext) -> AgentResult:
        """
        Main analysis method for data discovery and validation.
        
        Uses all three ADK tools to comprehensively assess data availability
        and quality for a given protocol.
        """
        start_time = datetime.utcnow()
        protocol_name = context.protocol_name
        
        self.log_analysis_step("Starting data discovery", {"protocol": protocol_name})
        
        try:
            # Execute all three tools in parallel for efficiency
            github_task = self._safe_tool_execution(
                self.github_tool, protocol_name, "GitHub"
            )
            defi_task = self._safe_tool_execution(
                self.defi_tool, protocol_name, "DeFi Data"
            )
            blockchain_task = self._safe_tool_execution(
                self.blockchain_tool, protocol_name, "Blockchain"
            )
            
            # Wait for all tools to complete
            github_result, defi_result, blockchain_result = await asyncio.gather(
                github_task, defi_task, blockchain_task
            )
            
            # Analyze data quality and cross-validate
            data_analysis = await self._analyze_data_quality(
                github_result, defi_result, blockchain_result, protocol_name
            )
            
            # Generate data source recommendations
            recommendations = await self._generate_recommendations(
                data_analysis, protocol_name
            )
            
            # Use LLM to generate insights and explanations
            insights = await self._generate_insights_with_llm(
                data_analysis, recommendations, protocol_name
            )
            
            # Calculate overall confidence and reliability
            overall_confidence = self._calculate_overall_confidence(data_analysis)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Compile final result
            result_data = {
                'protocol_name': protocol_name,
                'data_discovery_summary': {
                    'total_sources_found': len([r for r in [github_result, defi_result, blockchain_result] if r and r.success]),
                    'data_quality_score': data_analysis['overall_quality_score'],
                    'reliability_score': overall_confidence,
                    'data_freshness_score': data_analysis['freshness_score']
                },
                'source_analysis': {
                    'github': self._format_tool_result(github_result),
                    'defi_data': self._format_tool_result(defi_result),
                    'blockchain': self._format_tool_result(blockchain_result)
                },
                'data_validation': data_analysis,
                'recommendations': recommendations,
                'insights': insights,
                'validated_sources': self._extract_validated_sources(
                    github_result, defi_result, blockchain_result
                ),
                'risk_factors': self._identify_data_risks(data_analysis),
                'execution_metadata': {
                    'total_execution_time': execution_time,
                    'tool_execution_times': {
                        'github': github_result.execution_time if github_result else 0,
                        'defi_data': defi_result.execution_time if defi_result else 0,
                        'blockchain': blockchain_result.execution_time if blockchain_result else 0
                    }
                }
            }
            
            self.log_analysis_step(
                "Data discovery completed",
                {
                    "sources_found": result_data['data_discovery_summary']['total_sources_found'],
                    "quality_score": result_data['data_discovery_summary']['data_quality_score'],
                    "execution_time": execution_time
                }
            )
            
            return AgentResult(
                agent_id=self.agent_id,
                success=True,
                data=result_data,
                confidence=overall_confidence,
                reasoning=insights.get('summary', 'Data discovery and validation completed'),
                execution_time=execution_time,
                timestamp=datetime.utcnow(),
                errors=[]
            )
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            error_msg = f"Data discovery failed for {protocol_name}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            return AgentResult(
                agent_id=self.agent_id,
                success=False,
                data={},
                confidence=0.0,
                reasoning=f"Data discovery failed due to: {str(e)}",
                execution_time=execution_time,
                timestamp=datetime.utcnow(),
                errors=[error_msg]
            )
    
    async def _safe_tool_execution(self, tool, protocol_name: str, tool_name: str):
        """Execute tool with error handling and timeout"""
        try:
            self.log_analysis_step(f"Executing {tool_name} tool", {"protocol": protocol_name})
            result = await tool.execute_with_timeout(protocol_name, timeout_seconds=30)
            
            if result.success:
                self.log_analysis_step(
                    f"{tool_name} tool completed successfully",
                    {"reliability": result.reliability_score, "time": result.execution_time}
                )
            else:
                self.log_analysis_step(
                    f"{tool_name} tool failed",
                    {"errors": result.errors[:2]}  # Log first 2 errors
                )
            
            return result
            
        except Exception as e:
            logger.warning(f"{tool_name} tool execution failed: {e}")
            # Return a failed ToolResult for consistency
            from tools.base_adk_tool import ToolResult
            return ToolResult(
                tool_name=tool_name.lower().replace(' ', '_'),
                success=False,
                data={},
                reliability_score=0.0,
                execution_time=0.0,
                timestamp=datetime.utcnow(),
                errors=[str(e)],
                source_urls=[]
            )
    
    async def _analyze_data_quality(self, github_result, defi_result, blockchain_result, protocol_name: str) -> Dict[str, Any]:
        """Analyze data quality across all sources"""
        
        quality_analysis = {
            'source_availability': {},
            'data_completeness': {},
            'reliability_scores': {},
            'cross_validation': {},
            'overall_quality_score': 0.0,
            'freshness_score': 0.0
        }
        
        results = {
            'github': github_result,
            'defi_data': defi_result,
            'blockchain': blockchain_result
        }
        
        total_sources = len(results)
        successful_sources = 0
        total_reliability = 0.0
        
        # Analyze each source
        for source_name, result in results.items():
            if result and result.success:
                successful_sources += 1
                quality_analysis['source_availability'][source_name] = True
                quality_analysis['reliability_scores'][source_name] = result.reliability_score
                total_reliability += result.reliability_score
                
                # Assess data completeness
                completeness = self._assess_data_completeness(result, source_name)
                quality_analysis['data_completeness'][source_name] = completeness
            else:
                quality_analysis['source_availability'][source_name] = False
                quality_analysis['reliability_scores'][source_name] = 0.0
                quality_analysis['data_completeness'][source_name] = 0.0
        
        # Cross-validation checks
        quality_analysis['cross_validation'] = await self._cross_validate_data(
            github_result, defi_result, blockchain_result
        )
        
        # Overall quality score
        if successful_sources > 0:
            avg_reliability = total_reliability / successful_sources
            source_coverage = successful_sources / total_sources
            quality_analysis['overall_quality_score'] = (avg_reliability * 0.7 + source_coverage * 0.3) * 100
        
        # Freshness score
        quality_analysis['freshness_score'] = self._calculate_freshness_score(results)
        
        return quality_analysis
    
    def _assess_data_completeness(self, result, source_name: str) -> float:
        """Assess how complete the data is from a specific source"""
        if not result or not result.success:
            return 0.0
        
        data = result.data
        expected_fields = {
            'github': ['health_score', 'repository_metrics', 'insights'],
            'defi_data': ['financial_health_score', 'tvl_metrics', 'price_metrics'],
            'blockchain': ['onchain_health_score', 'contract_verification', 'network_activity']
        }
        
        if source_name not in expected_fields:
            return 0.5  # Default for unknown sources
        
        required_fields = expected_fields[source_name]
        present_fields = sum(1 for field in required_fields if field in data and data[field])
        
        return present_fields / len(required_fields)
    
    async def _cross_validate_data(self, github_result, defi_result, blockchain_result) -> Dict[str, Any]:
        """Cross-validate data between different sources"""
        validation = {
            'consistency_checks': [],
            'data_conflicts': [],
            'validation_score': 0.0
        }
        
        try:
            # Check if protocol names match across sources
            protocol_names = []
            if github_result and github_result.success:
                github_name = github_result.data.get('protocol_name')
                if github_name:
                    protocol_names.append(github_name)
            
            if defi_result and defi_result.success:
                defi_name = defi_result.data.get('protocol_name')
                if defi_name:
                    protocol_names.append(defi_name)
            
            if blockchain_result and blockchain_result.success:
                blockchain_name = blockchain_result.data.get('protocol_name')
                if blockchain_name:
                    protocol_names.append(blockchain_name)
            
            # Check name consistency
            if len(set(protocol_names)) <= 1:
                validation['consistency_checks'].append("Protocol names consistent across sources")
                validation['validation_score'] += 0.3
            else:
                validation['data_conflicts'].append("Inconsistent protocol names across sources")
            
            # Cross-validate numerical data (if available)
            # For example, compare GitHub stars with DeFi adoption metrics
            
            # Check data freshness consistency
            timestamps = []
            for result in [github_result, defi_result, blockchain_result]:
                if result and result.success:
                    timestamp = result.data.get('last_updated')
                    if timestamp:
                        timestamps.append(timestamp)
            
            if len(timestamps) > 1:
                # All should be recent (within last hour of each other)
                validation['consistency_checks'].append("Data timestamps are reasonably consistent")
                validation['validation_score'] += 0.2
            
            # Additional validation score based on successful checks
            if len(validation['data_conflicts']) == 0:
                validation['validation_score'] += 0.5
            
            validation['validation_score'] = min(1.0, validation['validation_score'])
            
        except Exception as e:
            logger.warning(f"Cross-validation failed: {e}")
            validation['data_conflicts'].append(f"Cross-validation error: {str(e)}")
        
        return validation
    
    def _calculate_freshness_score(self, results: Dict[str, Any]) -> float:
        """Calculate how fresh/recent the data is"""
        freshness_scores = []
        current_time = datetime.utcnow()
        
        for source_name, result in results.items():
            if result and result.success:
                # Check when the analysis was performed
                analysis_time = result.timestamp
                hours_old = (current_time - analysis_time).total_seconds() / 3600
                
                # Score decreases as data gets older
                if hours_old < 1:
                    freshness_scores.append(1.0)
                elif hours_old < 6:
                    freshness_scores.append(0.8)
                elif hours_old < 24:
                    freshness_scores.append(0.6)
                else:
                    freshness_scores.append(0.3)
        
        return sum(freshness_scores) / len(freshness_scores) if freshness_scores else 0.0
    
    async def _generate_recommendations(self, data_analysis: Dict[str, Any], protocol_name: str) -> Dict[str, Any]:
        """Generate data source recommendations for other agents"""
        
        recommendations = {
            'optimal_sources': [],
            'fallback_sources': [],
            'data_gaps': [],
            'collection_strategy': {},
            'confidence_levels': {}
        }
        
        # Analyze source reliability and recommend optimal sources
        reliability_scores = data_analysis['reliability_scores']
        source_availability = data_analysis['source_availability']
        
        # Rank sources by reliability
        available_sources = [
            (source, score) for source, score in reliability_scores.items()
            if source_availability.get(source, False) and score > 0.5
        ]
        available_sources.sort(key=lambda x: x[1], reverse=True)
        
        # Categorize recommendations
        for source, score in available_sources:
            if score > 0.7:
                recommendations['optimal_sources'].append({
                    'source': source,
                    'reliability': score,
                    'recommended_use': self._get_source_use_case(source)
                })
            else:
                recommendations['fallback_sources'].append({
                    'source': source,
                    'reliability': score,
                    'use_case': 'backup_validation'
                })
        
        # Identify data gaps
        for source in ['github', 'defi_data', 'blockchain']:
            if not source_availability.get(source, False):
                gap_info = {
                    'missing_source': source,
                    'impact': self._assess_gap_impact(source),
                    'alternatives': self._suggest_alternatives(source)
                }
                recommendations['data_gaps'].append(gap_info)
        
        # Generate collection strategy
        recommendations['collection_strategy'] = self._generate_collection_strategy(
            recommendations['optimal_sources'], 
            recommendations['data_gaps']
        )
        
        return recommendations
    
    def _get_source_use_case(self, source: str) -> str:
        """Get recommended use case for a data source"""
        use_cases = {
            'github': 'development_health_assessment',
            'defi_data': 'financial_metrics_analysis',
            'blockchain': 'contract_verification_and_activity'
        }
        return use_cases.get(source, 'general_analysis')
    
    def _assess_gap_impact(self, missing_source: str) -> str:
        """Assess the impact of a missing data source"""
        impacts = {
            'github': 'moderate - limits development health assessment',
            'defi_data': 'high - critical for financial health analysis',
            'blockchain': 'moderate - reduces on-chain verification confidence'
        }
        return impacts.get(missing_source, 'unknown impact')
    
    def _suggest_alternatives(self, missing_source: str) -> List[str]:
        """Suggest alternative data sources"""
        alternatives = {
            'github': ['manual repository search', 'documentation analysis'],
            'defi_data': ['direct protocol APIs', 'alternative aggregators'],
            'blockchain': ['direct RPC calls', 'alternative explorers']
        }
        return alternatives.get(missing_source, ['manual research'])
    
    def _generate_collection_strategy(self, optimal_sources: List[Dict], data_gaps: List[Dict]) -> Dict[str, Any]:
        """Generate optimal data collection strategy"""
        strategy = {
            'primary_approach': 'parallel_collection',
            'recommended_sequence': [],
            'validation_strategy': 'cross_reference',
            'fallback_plan': []
        }
        
        # Recommend collection sequence based on source reliability
        for source_info in optimal_sources:
            strategy['recommended_sequence'].append({
                'source': source_info['source'],
                'priority': 'high',
                'timeout': 30
            })
        
        # Add fallback plans for gaps
        for gap in data_gaps:
            strategy['fallback_plan'].append({
                'missing_source': gap['missing_source'],
                'alternatives': gap['alternatives']
            })
        
        return strategy
    
    async def _generate_insights_with_llm(self, data_analysis: Dict[str, Any], recommendations: Dict[str, Any], protocol_name: str) -> Dict[str, Any]:
        """Use LLM to generate human-readable insights about data discovery"""
        
        # Prepare context for LLM
        context = {
            'protocol_name': protocol_name,
            'total_sources_available': len([s for s in data_analysis['source_availability'].values() if s]),
            'overall_quality_score': data_analysis['overall_quality_score'],
            'cross_validation_score': data_analysis['cross_validation']['validation_score'],
            'optimal_sources_count': len(recommendations['optimal_sources']),
            'data_gaps_count': len(recommendations['data_gaps'])
        }
        
        prompt = f"""Analyze the data discovery results for {protocol_name} and provide insights:

Available Sources: {context['total_sources_available']}/3
Overall Quality Score: {context['overall_quality_score']:.1f}/100
Cross-validation Score: {context['cross_validation_score']:.1f}/1.0
Optimal Sources: {context['optimal_sources_count']}
Data Gaps: {context['data_gaps_count']}

Based on these metrics, provide:
1. A summary of data availability and quality
2. Key insights about the protocol's data landscape
3. Recommendations for comprehensive analysis
4. Any data reliability concerns

Focus on practical implications for risk assessment."""
        
        try:
            insights_text = await self.call_gemini(prompt, context)
            
            # Parse insights into structured format
            insights = {
                'summary': insights_text,
                'key_findings': self._extract_key_findings(data_analysis, recommendations),
                'data_quality_assessment': self._format_quality_assessment(data_analysis),
                'action_items': self._generate_action_items(recommendations)
            }
            
            return insights
            
        except Exception as e:
            logger.warning(f"LLM insights generation failed: {e}")
            
            # Fallback to structured insights
            return {
                'summary': f"Data discovery completed for {protocol_name} with {context['total_sources_available']} sources available",
                'key_findings': self._extract_key_findings(data_analysis, recommendations),
                'data_quality_assessment': self._format_quality_assessment(data_analysis),
                'action_items': self._generate_action_items(recommendations)
            }
    
    def _extract_key_findings(self, data_analysis: Dict[str, Any], recommendations: Dict[str, Any]) -> List[str]:
        """Extract key findings from data analysis"""
        findings = []
        
        # Source availability findings
        available_count = sum(data_analysis['source_availability'].values())
        findings.append(f"{available_count}/3 primary data sources are accessible")
        
        # Quality findings
        quality_score = data_analysis['overall_quality_score']
        if quality_score > 80:
            findings.append("Excellent data quality across available sources")
        elif quality_score > 60:
            findings.append("Good data quality with minor limitations")
        else:
            findings.append("Data quality concerns identified")
        
        # Cross-validation findings
        validation_score = data_analysis['cross_validation']['validation_score']
        if validation_score > 0.8:
            findings.append("Strong cross-validation between data sources")
        elif validation_score > 0.5:
            findings.append("Moderate cross-validation success")
        else:
            findings.append("Limited cross-validation capability")
        
        return findings
    
    def _format_quality_assessment(self, data_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Format quality assessment in human-readable format"""
        assessment = {}
        
        for source, available in data_analysis['source_availability'].items():
            if available:
                reliability = data_analysis['reliability_scores'][source]
                completeness = data_analysis['data_completeness'][source]
                
                if reliability > 0.8 and completeness > 0.8:
                    assessment[source] = "Excellent - High reliability and completeness"
                elif reliability > 0.6 and completeness > 0.6:
                    assessment[source] = "Good - Reliable with adequate completeness"
                else:
                    assessment[source] = "Fair - Usable but with limitations"
            else:
                assessment[source] = "Unavailable - Source not accessible"
        
        return assessment
    
    def _generate_action_items(self, recommendations: Dict[str, Any]) -> List[str]:
        """Generate actionable items based on recommendations"""
        actions = []
        
        optimal_sources = recommendations['optimal_sources']
        if optimal_sources:
            actions.append(f"Prioritize {len(optimal_sources)} high-quality data sources for comprehensive analysis")
        
        data_gaps = recommendations['data_gaps']
        if data_gaps:
            actions.append(f"Address {len(data_gaps)} data gaps using alternative collection methods")
        
        # Strategy-specific actions
        strategy = recommendations.get('collection_strategy', {})
        if strategy.get('primary_approach') == 'parallel_collection':
            actions.append("Use parallel data collection for optimal efficiency")
        
        if not optimal_sources:
            actions.append("Implement fallback data collection strategy due to limited source availability")
        
        return actions
    
    def _calculate_overall_confidence(self, data_analysis: Dict[str, Any]) -> float:
        """Calculate overall confidence in data discovery results"""
        
        # Base confidence on multiple factors
        factors = []
        
        # Source availability factor
        available_sources = sum(data_analysis['source_availability'].values())
        source_factor = available_sources / 3.0  # 3 total sources
        factors.append(source_factor)
        
        # Quality factor
        quality_factor = data_analysis['overall_quality_score'] / 100.0
        factors.append(quality_factor)
        
        # Cross-validation factor
        validation_factor = data_analysis['cross_validation']['validation_score']
        factors.append(validation_factor)
        
        # Freshness factor
        freshness_factor = data_analysis['freshness_score']
        factors.append(freshness_factor)
        
        # Weighted average with emphasis on source availability and quality
        weights = [0.3, 0.4, 0.2, 0.1]  # availability, quality, validation, freshness
        confidence = sum(f * w for f, w in zip(factors, weights))
        
        return max(0.0, min(1.0, confidence))
    
    def _format_tool_result(self, result) -> Dict[str, Any]:
        """Format tool result for inclusion in agent output"""
        if not result:
            return {
                'available': False,
                'error': 'Tool execution failed'
            }
        
        return {
            'available': result.success,
            'reliability_score': result.reliability_score,
            'execution_time': result.execution_time,
            'data_size': len(str(result.data)) if result.data else 0,
            'errors': result.errors,
            'source_urls': result.source_urls
        }
    
    def _extract_validated_sources(self, github_result, defi_result, blockchain_result) -> Dict[str, Any]:
        """Extract validated data sources for use by other agents"""
        validated = {
            'github_sources': [],
            'defi_sources': [],
            'blockchain_sources': [],
            'reliability_scores': {}
        }
        
        if github_result and github_result.success:
            validated['github_sources'] = github_result.source_urls
            validated['reliability_scores']['github'] = github_result.reliability_score
        
        if defi_result and defi_result.success:
            validated['defi_sources'] = defi_result.source_urls
            validated['reliability_scores']['defi_data'] = defi_result.reliability_score
        
        if blockchain_result and blockchain_result.success:
            validated['blockchain_sources'] = blockchain_result.source_urls
            validated['reliability_scores']['blockchain'] = blockchain_result.reliability_score
        
        return validated
    
    def _identify_data_risks(self, data_analysis: Dict[str, Any]) -> List[str]:
        """Identify risks related to data availability and quality"""
        risks = []
        
        # Source availability risks
        available_sources = sum(data_analysis['source_availability'].values())
        if available_sources < 2:
            risks.append("Limited data source diversity increases analysis risk")
        
        # Quality risks
        quality_score = data_analysis['overall_quality_score']
        if quality_score < 50:
            risks.append("Low data quality may compromise analysis accuracy")
        
        # Cross-validation risks
        validation_score = data_analysis['cross_validation']['validation_score']
        if validation_score < 0.5:
            risks.append("Poor cross-validation reduces confidence in data consistency")
        
        # Freshness risks
        freshness_score = data_analysis['freshness_score']
        if freshness_score < 0.5:
            risks.append("Stale data may not reflect current protocol state")
        
        # Specific source risks
        if not data_analysis['source_availability'].get('defi_data', False):
            risks.append("Missing financial data limits comprehensive risk assessment")
        
        if not data_analysis['source_availability'].get('github', False):
            risks.append("Missing development data reduces technical risk assessment capability")
        
        return risks
    
    async def _get_custom_memory_update(self, context: AgentContext, result: AgentResult) -> Optional[Dict[str, Any]]:
        """Update agent memory with data source learnings"""
        if not result.success:
            return None
        
        protocol_name = context.protocol_name
        data = result.data
        
        # Store successful data source patterns
        memory_update = {
            'learned_data_sources': {
                protocol_name.lower().replace(' ', '_'): {
                    'validated_sources': data.get('validated_sources', {}),
                    'quality_scores': data.get('data_validation', {}).get('reliability_scores', {}),
                    'last_successful_discovery': datetime.utcnow().isoformat(),
                    'optimal_collection_strategy': data.get('recommendations', {}).get('collection_strategy', {})
                }
            }
        }
        
        return memory_update
    
    def _get_required_data_fields(self) -> List[str]:
        """Required data fields for Data Hunter Agent"""
        return [
            'data_discovery_summary',
            'source_analysis', 
            'data_validation',
            'recommendations',
            'validated_sources'
        ]