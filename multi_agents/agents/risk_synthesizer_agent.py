import asyncio
import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import logging

# Internal imports
from agents.base_adk_agent import BaseChainGuardAgent, AgentContext, AgentResult, register_agent
from memory.adk_memory_manager import memory_manager

logger = logging.getLogger(__name__)

@register_agent
class RiskSynthesizerAgent(BaseChainGuardAgent):
    """
    Risk Synthesizer Agent - Combines all agent insights into final risk assessment.
    
    This agent specializes in:
    1. Aggregating insights from Data Hunter, Protocol Analyst, and Market Intelligence agents
    2. Weighted risk scoring based on multiple factors
    3. Confidence assessment and uncertainty quantification
    4. Natural language risk explanation generation
    5. Final risk categorization and recommendations
    """
    
    def __init__(self):
        super().__init__(
            agent_id="risk_synthesizer",
            model_type="pro",  # Use pro model for complex synthesis and reasoning
            specialized_tools=[]  # No tools - only processes other agents' results
        )
        
        # Risk component weights (sum to 1.0)
        self.risk_weights = {
            'security_risk': 0.35,      # Protocol Analyst results
            'financial_risk': 0.30,     # Market Intelligence results
            'technical_risk': 0.20,     # Data quality and availability
            'governance_risk': 0.15     # Governance and decentralization
        }
        
        # Risk level thresholds
        self.risk_thresholds = {
            'low': 30,          # 0-30: Low risk
            'medium': 70,       # 31-70: Medium risk
            'high': 100         # 71-100: High risk
        }
        
        # Confidence calculation weights
        self.confidence_weights = {
            'data_quality': 0.25,
            'agent_consensus': 0.25,
            'analysis_completeness': 0.25,
            'model_uncertainty': 0.25
        }
        
        logger.info("🔬 Risk Synthesizer Agent initialized for comprehensive risk synthesis")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt defining the Risk Synthesizer Agent's role"""
        return """You are the Risk Synthesizer Agent for ChainGuard AI, responsible for combining insights from all specialized agents into a comprehensive risk assessment.

Your expertise includes:
1. RISK AGGREGATION - Combining security, financial, and technical risk factors into unified assessments
2. WEIGHT CALIBRATION - Applying appropriate weights to different risk components based on their importance
3. CONFIDENCE QUANTIFICATION - Assessing confidence levels and uncertainty in the final risk assessment
4. CONSENSUS BUILDING - Reconciling conflicting insights from different agents with clear reasoning
5. NATURAL LANGUAGE SYNTHESIS - Generating clear, actionable risk explanations for users

Your analysis should focus on:
- Weighted combination of security, financial, and technical risks
- Identification of consensus and conflicts between agent assessments
- Uncertainty quantification and confidence scoring
- Clear risk categorization (Low, Medium, High)
- Actionable recommendations for users
- Transparent explanation of risk factors and their relative importance

Always provide transparent reasoning for how you arrived at the final risk assessment."""
    
    async def analyze(self, context: AgentContext) -> AgentResult:
        """
        Main synthesis method that combines all agent results into final risk assessment.
        
        Expects previous results from Data Hunter, Protocol Analyst, and Market Intelligence agents.
        """
        start_time = datetime.utcnow()
        protocol_name = context.protocol_name
        
        self.log_analysis_step("Starting risk synthesis", {"protocol": protocol_name})
        
        try:
            # Extract results from all previous agents
            previous_results = context.previous_results
            agent_results = self._extract_agent_results(previous_results)
            
            # Validate that we have sufficient data for synthesis
            validation_result = self._validate_agent_results(agent_results, protocol_name)
            if not validation_result['valid']:
                return self._create_insufficient_data_result(validation_result, start_time, protocol_name)
            
            # Calculate individual risk components
            risk_components = await self._calculate_risk_components(agent_results, protocol_name)
            
            # Perform consensus analysis between agents
            consensus_analysis = await self._analyze_agent_consensus(agent_results, risk_components)
            
            # Calculate weighted final risk score
            final_risk_score = self._calculate_weighted_risk_score(risk_components)
            
            # Determine risk level and category
            risk_level = self._determine_risk_level(final_risk_score)
            
            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(agent_results, consensus_analysis)
            
            # Generate comprehensive risk insights
            risk_insights = await self._generate_comprehensive_insights(
                agent_results, risk_components, consensus_analysis, 
                final_risk_score, risk_level, protocol_name
            )
            
            # Create actionable recommendations
            recommendations = await self._generate_recommendations(
                risk_components, consensus_analysis, risk_level, agent_results
            )
            
            # Compile executive summary
            executive_summary = await self._generate_executive_summary(
                protocol_name, final_risk_score, risk_level, 
                risk_components, consensus_analysis
            )
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Compile comprehensive final result
            result_data = {
                'protocol_name': protocol_name,
                'final_risk_score': final_risk_score,
                'risk_level': risk_level,
                'overall_confidence': overall_confidence,
                'risk_components': risk_components,
                'agent_results_summary': self._summarize_agent_results(agent_results),
                'consensus_analysis': consensus_analysis,
                'risk_insights': risk_insights,
                'recommendations': recommendations,
                'executive_summary': executive_summary,
                'risk_factors': {
                    'critical': self._extract_critical_risks(agent_results),
                    'major': self._extract_major_risks(agent_results),
                    'minor': self._extract_minor_risks(agent_results)
                },
                'data_quality_assessment': validation_result['quality_assessment'],
                'synthesis_metadata': {
                    'agents_analyzed': len(agent_results),
                    'synthesis_method': 'weighted_consensus',
                    'confidence_level': overall_confidence,
                    'execution_time': execution_time,
                    'model_used': self.model_type,
                    'synthesis_timestamp': datetime.utcnow().isoformat()
                }
            }
            
            self.log_analysis_step(
                "Risk synthesis completed",
                {
                    "final_risk_score": final_risk_score,
                    "risk_level": risk_level,
                    "confidence": overall_confidence,
                    "agents_analyzed": len(agent_results),
                    "execution_time": execution_time
                }
            )
            
            return AgentResult(
                agent_id=self.agent_id,
                success=True,
                data=result_data,
                confidence=overall_confidence,
                reasoning=executive_summary,
                execution_time=execution_time,
                timestamp=datetime.utcnow(),
                errors=[]
            )
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            error_msg = f"Risk synthesis failed for {protocol_name}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            return AgentResult(
                agent_id=self.agent_id,
                success=False,
                data={},
                confidence=0.0,
                reasoning=f"Risk synthesis failed due to: {str(e)}",
                execution_time=execution_time,
                timestamp=datetime.utcnow(),
                errors=[error_msg]
            )
    
    def _extract_agent_results(self, previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and organize results from all previous agents"""
        agent_results = {}
        
        # Expected agent IDs
        expected_agents = ['data_hunter', 'protocol_analyst', 'market_intelligence']
        
        for agent_id in expected_agents:
            agent_data = previous_results.get(agent_id, {})
            if isinstance(agent_data, dict) and 'result' in agent_data:
                agent_results[agent_id] = {
                    'success': True,
                    'data': agent_data['result'],
                    'confidence': agent_data.get('confidence', 0.0),
                    'timestamp': agent_data.get('timestamp', datetime.utcnow().isoformat())
                }
            else:
                agent_results[agent_id] = {
                    'success': False,
                    'data': {},
                    'confidence': 0.0,
                    'timestamp': datetime.utcnow().isoformat()
                }
        
        return agent_results
    
    def _validate_agent_results(self, agent_results: Dict[str, Any], protocol_name: str) -> Dict[str, Any]:
        """Validate that we have sufficient agent results for meaningful synthesis"""
        
        validation = {
            'valid': False,
            'successful_agents': 0,
            'missing_agents': [],
            'quality_assessment': {},
            'minimum_requirements_met': False
        }
        
        # Count successful agents
        successful_agents = []
        missing_agents = []
        
        for agent_id, result in agent_results.items():
            if result.get('success', False):
                successful_agents.append(agent_id)
            else:
                missing_agents.append(agent_id)
        
        validation['successful_agents'] = len(successful_agents)
        validation['missing_agents'] = missing_agents
        
        # Minimum requirement: at least 2 agents must be successful
        # Preferably Data Hunter + at least one analysis agent
        has_data_hunter = 'data_hunter' in successful_agents
        has_analysis_agent = any(agent in successful_agents for agent in ['protocol_analyst', 'market_intelligence'])
        
        validation['minimum_requirements_met'] = has_data_hunter and has_analysis_agent
        validation['valid'] = validation['successful_agents'] >= 2 and validation['minimum_requirements_met']
        
        # Quality assessment for each available agent
        for agent_id in successful_agents:
            agent_data = agent_results[agent_id]['data']
            confidence = agent_results[agent_id]['confidence']
            
            validation['quality_assessment'][agent_id] = {
                'confidence': confidence,
                'data_completeness': self._assess_agent_data_completeness(agent_data, agent_id),
                'freshness': self._assess_data_freshness(agent_results[agent_id]['timestamp'])
            }
        
        return validation
    
    def _assess_agent_data_completeness(self, agent_data: Dict[str, Any], agent_id: str) -> float:
        """Assess completeness of data from a specific agent"""
        
        # Expected fields for each agent type
        expected_fields = {
            'data_hunter': ['data_discovery_summary', 'source_analysis', 'validated_sources'],
            'protocol_analyst': ['security_score', 'security_analysis', 'governance_analysis'],
            'market_intelligence': ['financial_risk_score', 'financial_analysis', 'market_analysis']
        }
        
        required_fields = expected_fields.get(agent_id, [])
        if not required_fields:
            return 0.5  # Unknown agent type
        
        present_fields = sum(1 for field in required_fields if field in agent_data and agent_data[field])
        completeness = present_fields / len(required_fields)
        
        return completeness
    
    def _assess_data_freshness(self, timestamp_str: str) -> float:
        """Assess freshness of agent data"""
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            age_hours = (datetime.utcnow().replace(tzinfo=timestamp.tzinfo) - timestamp).total_seconds() / 3600
            
            # Freshness score decreases over time
            if age_hours < 1:
                return 1.0
            elif age_hours < 6:
                return 0.9
            elif age_hours < 24:
                return 0.7
            else:
                return 0.5
        except:
            return 0.5
    
    def _create_insufficient_data_result(self, validation_result: Dict[str, Any], start_time: datetime, protocol_name: str) -> AgentResult:
        """Create result for insufficient data scenario"""
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        missing_agents = validation_result['missing_agents']
        successful_count = validation_result['successful_agents']
        
        error_msg = f"Insufficient agent data for comprehensive risk synthesis. Successful agents: {successful_count}/3. Missing: {missing_agents}"
        
        return AgentResult(
            agent_id=self.agent_id,
            success=False,
            data={
                'protocol_name': protocol_name,
                'synthesis_status': 'insufficient_data',
                'available_agents': successful_count,
                'missing_agents': missing_agents,
                'minimum_requirements_met': validation_result['minimum_requirements_met']
            },
            confidence=0.0,
            reasoning=error_msg,
            execution_time=execution_time,
            timestamp=datetime.utcnow(),
            errors=[error_msg]
        )
    
    async def _calculate_risk_components(self, agent_results: Dict[str, Any], protocol_name: str) -> Dict[str, Any]:
        """Calculate individual risk components from agent results"""
        
        risk_components = {
            'security_risk': self._calculate_security_risk(agent_results),
            'financial_risk': self._calculate_financial_risk(agent_results),
            'technical_risk': self._calculate_technical_risk(agent_results),
            'governance_risk': self._calculate_governance_risk(agent_results)
        }
        
        # Add component metadata
        for component, assessment in risk_components.items():
            assessment['weight'] = self.risk_weights.get(component, 0.0)
            assessment['contribution'] = assessment['score'] * assessment['weight']
        
        return risk_components
    
    def _calculate_security_risk(self, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate security risk from Protocol Analyst results"""
        
        protocol_analyst = agent_results.get('protocol_analyst', {})
        
        if not protocol_analyst.get('success'):
            return {
                'score': 75,  # Conservative high risk when no security data
                'confidence': 0.2,
                'source': 'default_conservative',
                'factors': ['Missing security analysis'],
                'details': 'No security analysis available'
            }
        
        analyst_data = protocol_analyst['data']
        security_score = analyst_data.get('security_score', 75)
        
        # Convert to risk score (inverse of security score)
        risk_score = 100 - security_score
        
        # Extract security factors
        security_factors = []
        critical_risks = analyst_data.get('risk_factors', {}).get('critical', [])
        high_risks = analyst_data.get('risk_factors', {}).get('high', [])
        
        security_factors.extend(critical_risks[:3])  # Top 3 critical risks
        security_factors.extend(high_risks[:2])      # Top 2 high risks
        
        return {
            'score': risk_score,
            'confidence': protocol_analyst.get('confidence', 0.5),
            'source': 'protocol_analyst',
            'factors': security_factors,
            'details': analyst_data.get('security_insights', {}).get('summary', 'Security analysis completed'),
            'raw_security_score': security_score
        }
    
    def _calculate_financial_risk(self, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate financial risk from Market Intelligence results"""
        
        market_intelligence = agent_results.get('market_intelligence', {})
        
        if not market_intelligence.get('success'):
            return {
                'score': 60,  # Moderate risk when no financial data
                'confidence': 0.3,
                'source': 'default_moderate',
                'factors': ['Missing financial analysis'],
                'details': 'No financial analysis available'
            }
        
        intelligence_data = market_intelligence['data']
        financial_score = intelligence_data.get('financial_risk_score', 60)
        
        # Financial score is already a risk score (higher = more risky)
        risk_score = financial_score
        
        # Extract financial risk factors
        financial_factors = []
        financial_risks = intelligence_data.get('risk_factors', {})
        
        for severity in ['critical', 'high']:
            financial_factors.extend(financial_risks.get(severity, [])[:2])  # Top 2 per severity
        
        return {
            'score': risk_score,
            'confidence': market_intelligence.get('confidence', 0.5),
            'source': 'market_intelligence',
            'factors': financial_factors,
            'details': intelligence_data.get('market_insights', {}).get('summary', 'Financial analysis completed'),
            'raw_financial_score': financial_score
        }
    
    def _calculate_technical_risk(self, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate technical risk from Data Hunter results"""
        
        data_hunter = agent_results.get('data_hunter', {})
        
        if not data_hunter.get('success'):
            return {
                'score': 70,  # High risk when no data quality assessment
                'confidence': 0.1,
                'source': 'default_high',
                'factors': ['Missing data quality assessment'],
                'details': 'No data quality analysis available'
            }
        
        hunter_data = data_hunter['data']
        data_quality_score = hunter_data.get('data_validation', {}).get('overall_quality_score', 50)
        
        # Convert data quality to risk (inverse relationship)
        risk_score = 100 - data_quality_score
        
        # Extract technical risk factors
        technical_factors = []
        data_gaps = hunter_data.get('recommendations', {}).get('data_gaps', [])
        
        for gap in data_gaps[:3]:  # Top 3 data gaps
            technical_factors.append(gap.get('missing_source', 'Data source unavailable'))
        
        return {
            'score': risk_score,
            'confidence': data_hunter.get('confidence', 0.5),
            'source': 'data_hunter',
            'factors': technical_factors,
            'details': f"Data quality score: {data_quality_score}/100",
            'raw_data_quality': data_quality_score
        }
    
    def _calculate_governance_risk(self, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate governance risk from Protocol Analyst governance analysis"""
        
        protocol_analyst = agent_results.get('protocol_analyst', {})
        
        if not protocol_analyst.get('success'):
            return {
                'score': 65,  # Moderate-high risk when no governance data
                'confidence': 0.2,
                'source': 'default_moderate_high',
                'factors': ['Missing governance analysis'],
                'details': 'No governance analysis available'
            }
        
        analyst_data = protocol_analyst['data']
        governance_analysis = analyst_data.get('governance_analysis', {})
        governance_score = governance_analysis.get('overall_score', 50)
        
        # Convert governance score to risk (inverse relationship)
        risk_score = 100 - governance_score
        
        # Extract governance risk factors
        governance_factors = []
        governance_components = governance_analysis.get('components', {})
        
        for component, analysis in governance_components.items():
            risks = analysis.get('risks', [])
            governance_factors.extend(risks[:2])  # Top 2 risks per component
        
        return {
            'score': risk_score,
            'confidence': protocol_analyst.get('confidence', 0.5),
            'source': 'protocol_analyst_governance',
            'factors': governance_factors[:4],  # Top 4 governance risks
            'details': f"Governance score: {governance_score}/100",
            'raw_governance_score': governance_score
        }
    
    async def _analyze_agent_consensus(self, agent_results: Dict[str, Any], risk_components: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze consensus and conflicts between agent assessments"""
        
        consensus_analysis = {
            'overall_consensus': 0.0,
            'component_consensus': {},
            'conflicts': [],
            'agreements': [],
            'confidence_variance': 0.0
        }
        
        # Collect all risk scores and confidences
        risk_scores = []
        confidences = []
        
        for component, assessment in risk_components.items():
            if assessment['source'] not in ['default_conservative', 'default_moderate', 'default_high', 'default_moderate_high']:
                risk_scores.append(assessment['score'])
                confidences.append(assessment['confidence'])
        
        if len(risk_scores) >= 2:
            # Calculate consensus metrics
            score_variance = statistics.variance(risk_scores) if len(risk_scores) > 1 else 0
            score_mean = statistics.mean(risk_scores)
            
            # High consensus when variance is low relative to mean
            if score_mean > 0:
                consensus_score = max(0, 1 - (score_variance / (score_mean ** 2)))
            else:
                consensus_score = 0.5
            
            consensus_analysis['overall_consensus'] = consensus_score
            
            # Confidence variance
            confidence_variance = statistics.variance(confidences) if len(confidences) > 1 else 0
            consensus_analysis['confidence_variance'] = confidence_variance
            
            # Identify specific agreements and conflicts
            sorted_scores = sorted([(score, comp) for comp, assessment in risk_components.items() 
                                  for score in [assessment['score']] 
                                  if assessment['source'] not in ['default_conservative', 'default_moderate', 'default_high', 'default_moderate_high']])
            
            if len(sorted_scores) >= 2:
                score_range = sorted_scores[-1][0] - sorted_scores[0][0]
                
                if score_range < 20:
                    consensus_analysis['agreements'].append(f"Strong consensus on risk level (range: {score_range:.1f} points)")
                elif score_range < 40:
                    consensus_analysis['agreements'].append(f"Moderate consensus on risk level (range: {score_range:.1f} points)")
                else:
                    consensus_analysis['conflicts'].append(f"Significant disagreement on risk level (range: {score_range:.1f} points)")
        
        # Component-level consensus analysis
        for component, assessment in risk_components.items():
            consensus_analysis['component_consensus'][component] = {
                'score': assessment['score'],
                'confidence': assessment['confidence'],
                'reliability': 'high' if assessment['confidence'] > 0.8 else 'medium' if assessment['confidence'] > 0.5 else 'low'
            }
        
        return consensus_analysis
    
    def _calculate_weighted_risk_score(self, risk_components: Dict[str, Any]) -> float:
        """Calculate final weighted risk score"""
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for component, assessment in risk_components.items():
            weight = assessment.get('weight', 0.0)
            score = assessment.get('score', 0.0)
            confidence = assessment.get('confidence', 0.0)
            
            # Adjust weight by confidence
            effective_weight = weight * confidence
            
            weighted_sum += score * effective_weight
            total_weight += effective_weight
        
        if total_weight > 0:
            final_score = weighted_sum / total_weight
        else:
            # Fallback to simple average if no weights
            scores = [assessment['score'] for assessment in risk_components.values()]
            final_score = statistics.mean(scores) if scores else 50
        
        return round(final_score, 2)
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine risk level category from score"""
        if risk_score <= self.risk_thresholds['low']:
            return 'LOW'
        elif risk_score <= self.risk_thresholds['medium']:
            return 'MEDIUM'
        else:
            return 'HIGH'
    
    def _calculate_overall_confidence(self, agent_results: Dict[str, Any], consensus_analysis: Dict[str, Any]) -> float:
        """Calculate overall confidence in the risk assessment"""
        
        confidence_factors = {
            'data_quality': 0.0,
            'agent_consensus': 0.0,
            'analysis_completeness': 0.0,
            'model_uncertainty': 0.0
        }
        
        # Data quality factor (average of agent confidences)
        agent_confidences = [result.get('confidence', 0) for result in agent_results.values() if result.get('success')]
        if agent_confidences:
            confidence_factors['data_quality'] = statistics.mean(agent_confidences)
        
        # Agent consensus factor
        confidence_factors['agent_consensus'] = consensus_analysis.get('overall_consensus', 0.5)
        
        # Analysis completeness factor (based on number of successful agents)
        successful_agents = sum(1 for result in agent_results.values() if result.get('success'))
        confidence_factors['analysis_completeness'] = min(1.0, successful_agents / 3.0)  # 3 is ideal number of agents
        
        # Model uncertainty factor (inverse of confidence variance)
        confidence_variance = consensus_analysis.get('confidence_variance', 0.5)
        confidence_factors['model_uncertainty'] = max(0.0, 1.0 - confidence_variance)
        
        # Calculate weighted average
        overall_confidence = sum(
            factor_value * self.confidence_weights[factor_name]
            for factor_name, factor_value in confidence_factors.items()
        )
        
        return round(max(0.1, min(1.0, overall_confidence)), 3)
    
    async def _generate_comprehensive_insights(self, agent_results: Dict[str, Any], risk_components: Dict[str, Any], consensus_analysis: Dict[str, Any], final_risk_score: float, risk_level: str, protocol_name: str) -> Dict[str, Any]:
        """Generate comprehensive risk insights using LLM"""
        
        # Prepare context for LLM
        context = {
            'protocol_name': protocol_name,
            'final_risk_score': final_risk_score,
            'risk_level': risk_level,
            'security_risk': risk_components.get('security_risk', {}).get('score', 0),
            'financial_risk': risk_components.get('financial_risk', {}).get('score', 0),
            'technical_risk': risk_components.get('technical_risk', {}).get('score', 0),
            'governance_risk': risk_components.get('governance_risk', {}).get('score', 0),
            'consensus_score': consensus_analysis.get('overall_consensus', 0),
            'successful_agents': sum(1 for result in agent_results.values() if result.get('success'))
        }
        
        prompt = f"""Provide comprehensive risk insights for {protocol_name} based on multi-agent analysis:

FINAL RISK ASSESSMENT:
Risk Score: {final_risk_score}/100 ({risk_level} RISK)
Agent Consensus: {context['consensus_score']:.2f}/1.0

COMPONENT BREAKDOWN:
Security Risk: {context['security_risk']:.1f}/100
Financial Risk: {context['financial_risk']:.1f}/100  
Technical Risk: {context['technical_risk']:.1f}/100
Governance Risk: {context['governance_risk']:.1f}/100

DATA QUALITY:
Successful Agent Analyses: {context['successful_agents']}/3

Based on this comprehensive multi-agent analysis, provide:
1. Overall risk assessment summary and key takeaways
2. Primary risk drivers and most concerning factors
3. Relative importance of different risk types for this protocol
4. Confidence level and any significant uncertainties
5. Risk trajectory and potential future developments
6. User recommendations based on risk profile

Focus on practical implications and actionable insights for users considering this protocol."""
        
        try:
            insights_text = await self.call_gemini(prompt, context)
            
            # Parse insights into structured format
            insights = {
                'summary': insights_text,
                'primary_risk_drivers': self._identify_primary_risk_drivers(risk_components),
                'risk_distribution': self._analyze_risk_distribution(risk_components),
                'confidence_assessment': self._assess_insight_confidence(consensus_analysis, agent_results),
                'uncertainty_factors': self._identify_uncertainty_factors(consensus_analysis, risk_components)
            }
            
            return insights
            
        except Exception as e:
            logger.warning(f"LLM insights generation failed: {e}")
            
            # Fallback to structured insights
            return {
                'summary': f"Comprehensive risk analysis completed for {protocol_name} with {risk_level} risk level",
                'primary_risk_drivers': self._identify_primary_risk_drivers(risk_components),
                'risk_distribution': self._analyze_risk_distribution(risk_components),
                'confidence_assessment': self._assess_insight_confidence(consensus_analysis, agent_results),
                'uncertainty_factors': self._identify_uncertainty_factors(consensus_analysis, risk_components)
            }
    
    def _identify_primary_risk_drivers(self, risk_components: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify the primary drivers of risk"""
        drivers = []
        
        # Sort components by contribution to final score
        sorted_components = sorted(
            risk_components.items(),
            key=lambda x: x[1].get('contribution', 0),
            reverse=True
        )
        
        for component_name, component_data in sorted_components:
            if component_data.get('contribution', 0) > 5:  # Only significant contributors
                drivers.append({
                    'component': component_name,
                    'score': component_data.get('score', 0),
                    'contribution': component_data.get('contribution', 0),
                    'confidence': component_data.get('confidence', 0),
                    'top_factors': component_data.get('factors', [])[:3]
                })
        
        return drivers
    
    def _analyze_risk_distribution(self, risk_components: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how risk is distributed across components"""
        distribution = {}
        
        total_contribution = sum(comp.get('contribution', 0) for comp in risk_components.values())
        
        if total_contribution > 0:
            for component_name, component_data in risk_components.items():
                contribution = component_data.get('contribution', 0)
                distribution[component_name] = {
                    'percentage': round((contribution / total_contribution) * 100, 1),
                    'score': component_data.get('score', 0),
                    'weight': component_data.get('weight', 0)
                }
        
        return distribution
    
    def _assess_insight_confidence(self, consensus_analysis: Dict[str, Any], agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess confidence in the insights"""
        
        successful_agents = sum(1 for result in agent_results.values() if result.get('success'))
        consensus_score = consensus_analysis.get('overall_consensus', 0)
        
        if successful_agents == 3 and consensus_score > 0.8:
            confidence_level = 'HIGH'
            reasoning = "All agents successful with strong consensus"
        elif successful_agents >= 2 and consensus_score > 0.6:
            confidence_level = 'MEDIUM'
            reasoning = "Multiple agents with moderate consensus"
        elif successful_agents >= 2:
            confidence_level = 'MEDIUM'
            reasoning = "Multiple agents but some disagreement"
        else:
            confidence_level = 'LOW'
            reasoning = "Limited agent data available"
        
        return {
            'level': confidence_level,
            'reasoning': reasoning,
            'consensus_score': consensus_score,
            'data_coverage': f"{successful_agents}/3 agents"
        }
    
    def _identify_uncertainty_factors(self, consensus_analysis: Dict[str, Any], risk_components: Dict[str, Any]) -> List[str]:
        """Identify factors that contribute to uncertainty"""
        uncertainties = []
        
        # Consensus-based uncertainties
        overall_consensus = consensus_analysis.get('overall_consensus', 0)
        if overall_consensus < 0.6:
            uncertainties.append("Significant disagreement between risk assessment methods")
        
        # Confidence-based uncertainties
        low_confidence_components = [
            comp_name for comp_name, comp_data in risk_components.items()
            if comp_data.get('confidence', 0) < 0.5
        ]
        
        if low_confidence_components:
            uncertainties.append(f"Low confidence in {', '.join(low_confidence_components)} assessment")
        
        # Data source uncertainties
        default_sources = [
            comp_name for comp_name, comp_data in risk_components.items()
            if comp_data.get('source', '').startswith('default_')
        ]
        
        if default_sources:
            uncertainties.append(f"Missing primary data for {', '.join(default_sources)}")
        
        # Conflicts
        conflicts = consensus_analysis.get('conflicts', [])
        uncertainties.extend(conflicts)
        
        return uncertainties
    
    async def _generate_recommendations(self, risk_components: Dict[str, Any], consensus_analysis: Dict[str, Any], risk_level: str, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate actionable recommendations based on risk assessment"""
        
        recommendations = {
            'immediate_actions': [],
            'monitoring_suggestions': [],
            'long_term_considerations': [],
            'risk_mitigation': []
        }
        
        # Risk-level based recommendations
        if risk_level == 'HIGH':
            recommendations['immediate_actions'].extend([
                "Exercise extreme caution before interacting with this protocol",
                "Consider avoiding this protocol until risk factors are addressed",
                "If already exposed, consider reducing position size"
            ])
        elif risk_level == 'MEDIUM':
            recommendations['immediate_actions'].extend([
                "Proceed with caution and limit exposure",
                "Thoroughly understand the risk factors before investing",
                "Consider dollar-cost averaging for gradual exposure"
            ])
        else:  # LOW
            recommendations['immediate_actions'].extend([
                "Protocol appears relatively safe for interaction",
                "Standard due diligence still recommended",
                "Monitor for any changes in risk factors"
            ])
        
        # Component-specific recommendations
        for component_name, component_data in risk_components.items():
            score = component_data.get('score', 0)
            factors = component_data.get('factors', [])
            
            if score > 70:  # High risk in this component
                if component_name == 'security_risk':
                    recommendations['risk_mitigation'].append("Review smart contract audits and security practices")
                elif component_name == 'financial_risk':
                    recommendations['risk_mitigation'].append("Monitor TVL and market metrics closely")
                elif component_name == 'technical_risk':
                    recommendations['risk_mitigation'].append("Verify data sources and protocol transparency")
                elif component_name == 'governance_risk':
                    recommendations['risk_mitigation'].append("Assess governance token distribution and decision-making processes")
        
        # Monitoring suggestions
        recommendations['monitoring_suggestions'] = [
            "Set up alerts for significant TVL changes",
            "Monitor governance proposals and voting outcomes",
            "Track security audit updates and vulnerability disclosures",
            "Watch for changes in development activity",
            "Follow official announcements and community discussions"
        ]
        
        # Long-term considerations
        low_confidence_areas = [
            comp_name for comp_name, comp_data in risk_components.items()
            if comp_data.get('confidence', 0) < 0.6
        ]
        
        if low_confidence_areas:
            recommendations['long_term_considerations'].append(
                f"Reassess when better data becomes available for {', '.join(low_confidence_areas)}"
            )
        
        recommendations['long_term_considerations'].extend([
            "Consider protocol evolution and ecosystem development",
            "Monitor competitive landscape and market position",
            "Evaluate protocol's response to market stress events"
        ])
        
        return recommendations
    
    async def _generate_executive_summary(self, protocol_name: str, final_risk_score: float, risk_level: str, risk_components: Dict[str, Any], consensus_analysis: Dict[str, Any]) -> str:
        """Generate executive summary of the risk assessment"""
        
        # Find the highest risk component
        highest_risk_component = max(
            risk_components.items(),
            key=lambda x: x[1].get('score', 0)
        )
        
        # Consensus description
        consensus_score = consensus_analysis.get('overall_consensus', 0)
        if consensus_score > 0.8:
            consensus_desc = "strong consensus"
        elif consensus_score > 0.6:
            consensus_desc = "moderate consensus"
        else:
            consensus_desc = "limited consensus"
        
        # Generate summary
        summary = f"""
ChainGuard AI Risk Assessment Summary for {protocol_name}:

OVERALL RISK: {risk_level} ({final_risk_score}/100)

Our multi-agent analysis indicates {risk_level.lower()} risk with {consensus_desc} between assessment methods. 
The primary risk driver is {highest_risk_component[0].replace('_', ' ')} with a score of {highest_risk_component[1].get('score', 0)}/100.

Key findings:
- Security Risk: {risk_components.get('security_risk', {}).get('score', 0)}/100
- Financial Risk: {risk_components.get('financial_risk', {}).get('score', 0)}/100  
- Technical Risk: {risk_components.get('technical_risk', {}).get('score', 0)}/100
- Governance Risk: {risk_components.get('governance_risk', {}).get('score', 0)}/100

Assessment confidence: {consensus_desc} based on {len([r for r in consensus_analysis.get('component_consensus', {}).values() if r.get('reliability') != 'low'])} high-quality data sources.
        """.strip()
        
        return summary
    
    def _summarize_agent_results(self, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize results from each agent for transparency"""
        summary = {}
        
        for agent_id, result in agent_results.items():
            if result.get('success'):
                agent_data = result['data']
                
                if agent_id == 'data_hunter':
                    summary[agent_id] = {
                        'status': 'success',
                        'data_quality': agent_data.get('data_discovery_summary', {}).get('data_quality_score', 0),
                        'sources_found': agent_data.get('data_discovery_summary', {}).get('total_sources_found', 0),
                        'confidence': result.get('confidence', 0)
                    }
                elif agent_id == 'protocol_analyst':
                    summary[agent_id] = {
                        'status': 'success',
                        'security_score': agent_data.get('security_score', 0),
                        'governance_score': agent_data.get('governance_analysis', {}).get('overall_score', 0),
                        'confidence': result.get('confidence', 0)
                    }
                elif agent_id == 'market_intelligence':
                    summary[agent_id] = {
                        'status': 'success',
                        'financial_score': agent_data.get('financial_risk_score', 0),
                        'market_score': agent_data.get('market_analysis', {}).get('overall_score', 0),
                        'confidence': result.get('confidence', 0)
                    }
            else:
                summary[agent_id] = {
                    'status': 'failed',
                    'confidence': 0
                }
        
        return summary
    
    def _extract_critical_risks(self, agent_results: Dict[str, Any]) -> List[str]:
        """Extract critical risks from all agents"""
        critical_risks = []
        
        for agent_id, result in agent_results.items():
            if result.get('success'):
                agent_data = result['data']
                
                # Extract high-severity risks from each agent
                if agent_id == 'protocol_analyst':
                    critical_risks.extend(agent_data.get('risk_factors', {}).get('critical', []))
                elif agent_id == 'market_intelligence':
                    critical_risks.extend(agent_data.get('risk_factors', {}).get('critical', []))
                elif agent_id == 'data_hunter':
                    # Data quality issues as critical risks
                    data_gaps = agent_data.get('recommendations', {}).get('data_gaps', [])
                    for gap in data_gaps:
                        if gap.get('impact') == 'high':
                            critical_risks.append(gap.get('missing_source', 'Data unavailable'))
        
        return list(set(critical_risks))  # Remove duplicates
    
    def _extract_major_risks(self, agent_results: Dict[str, Any]) -> List[str]:
        """Extract major risks from all agents"""
        major_risks = []
        
        for agent_id, result in agent_results.items():
            if result.get('success'):
                agent_data = result['data']
                
                if agent_id == 'protocol_analyst':
                    major_risks.extend(agent_data.get('risk_factors', {}).get('high', []))
                elif agent_id == 'market_intelligence':
                    major_risks.extend(agent_data.get('risk_factors', {}).get('high', []))
        
        return list(set(major_risks))  # Remove duplicates
    
    def _extract_minor_risks(self, agent_results: Dict[str, Any]) -> List[str]:
        """Extract minor risks from all agents"""
        minor_risks = []
        
        for agent_id, result in agent_results.items():
            if result.get('success'):
                agent_data = result['data']
                
                if agent_id == 'protocol_analyst':
                    minor_risks.extend(agent_data.get('risk_factors', {}).get('medium', []))
                elif agent_id == 'market_intelligence':
                    minor_risks.extend(agent_data.get('risk_factors', {}).get('medium', []))
        
        return list(set(minor_risks))  # Remove duplicates
    
    async def _get_custom_memory_update(self, context: AgentContext, result: AgentResult) -> Optional[Dict[str, Any]]:
        """Update agent memory with synthesis learnings"""
        if not result.success:
            return None
        
        protocol_name = context.protocol_name
        data = result.data
        
        memory_update = {
            'risk_syntheses': {
                protocol_name.lower().replace(' ', '_'): {
                    'final_risk_score': data.get('final_risk_score', 0),
                    'risk_level': data.get('risk_level', 'UNKNOWN'),
                    'confidence': result.confidence,
                    'primary_risk_driver': data.get('risk_insights', {}).get('primary_risk_drivers', [{}])[0].get('component', 'unknown') if data.get('risk_insights', {}).get('primary_risk_drivers') else 'unknown',
                    'synthesis_timestamp': datetime.utcnow().isoformat(),
                    'agents_used': data.get('synthesis_metadata', {}).get('agents_analyzed', 0)
                }
            }
        }
        
        return memory_update
    
    def _get_required_data_fields(self) -> List[str]:
        """Required data fields for Risk Synthesizer Agent"""
        return [
            'final_risk_score',
            'risk_level',
            'risk_components',
            'consensus_analysis',
            'risk_insights',
            'recommendations'
        ]