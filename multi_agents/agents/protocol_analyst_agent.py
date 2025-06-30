import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

# Internal imports
from agents.base_adk_agent import BaseChainGuardAgent, AgentContext, AgentResult, register_agent
from tools import GitHubADKTool, BlockchainADKTool
from memory.adk_memory_manager import memory_manager

logger = logging.getLogger(__name__)

@register_agent
class ProtocolAnalystAgent(BaseChainGuardAgent):
    """
    Protocol Analyst Agent - Security and governance risk analysis.
    
    This agent specializes in:
    1. Smart contract security assessment
    2. Development team and governance analysis
    3. Code quality and audit evaluation
    4. Technical risk factor identification
    5. Security best practices compliance
    """
    
    def __init__(self):
        super().__init__(
            agent_id="protocol_analyst",
            model_type="pro",  # Use pro model for complex security analysis
            specialized_tools=[GitHubADKTool, BlockchainADKTool]
        )
        
        # Risk weighting for different security factors
        self.security_weights = {
            'contract_verification': 0.25,
            'development_practices': 0.20,
            'audit_quality': 0.20,
            'governance_structure': 0.15,
            'code_maturity': 0.10,
            'vulnerability_management': 0.10
        }
        
        logger.info("🔐 Protocol Analyst Agent initialized for security analysis")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt defining the Protocol Analyst Agent's role"""
        return """You are the Protocol Analyst Agent for ChainGuard AI, specializing in smart contract security and governance risk assessment.

Your expertise includes:
1. SMART CONTRACT SECURITY - Analyzing contract verification, upgrade mechanisms, admin controls
2. DEVELOPMENT PRACTICES - Evaluating code quality, testing, security practices, team competency
3. GOVERNANCE ANALYSIS - Assessing decentralization, decision-making processes, token distribution
4. AUDIT ASSESSMENT - Reviewing audit quality, vulnerability management, security disclosures
5. TECHNICAL RISK IDENTIFICATION - Identifying centralization points, upgrade risks, dependency risks

Your analysis should focus on:
- Smart contract architecture and security patterns
- Development team practices and code quality indicators
- Governance mechanisms and decentralization levels
- Audit coverage and vulnerability management
- Technical risks that could impact protocol security

Always provide detailed reasoning for your security assessments and identify specific risk factors."""
    
    async def analyze(self, context: AgentContext) -> AgentResult:
        """
        Main analysis method for protocol security and governance assessment.
        
        Uses GitHub and Blockchain data to assess technical and governance risks.
        """
        start_time = datetime.utcnow()
        protocol_name = context.protocol_name
        
        self.log_analysis_step("Starting security analysis", {"protocol": protocol_name})
        
        try:
            # Get data from Data Hunter Agent results
            previous_results = context.previous_results
            github_data = self._extract_github_data(previous_results)
            blockchain_data = self._extract_blockchain_data(previous_results)
            
            if not github_data and not blockchain_data:
                # If no previous results, we need to collect our own data
                github_data, blockchain_data = await self._collect_security_data(protocol_name)
            
            # Perform comprehensive security analysis
            security_analysis = await self._analyze_security_factors(
                github_data, blockchain_data, protocol_name
            )
            
            # Assess governance and decentralization
            governance_analysis = await self._analyze_governance_structure(
                github_data, blockchain_data, protocol_name
            )
            
            # Identify technical risks
            technical_risks = await self._identify_technical_risks(
                github_data, blockchain_data, security_analysis, governance_analysis
            )
            
            # Generate security insights with LLM
            security_insights = await self._generate_security_insights(
                security_analysis, governance_analysis, technical_risks, protocol_name
            )
            
            # Calculate overall protocol security score
            overall_security_score = self._calculate_security_score(
                security_analysis, governance_analysis
            )
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Calculate confidence based on data availability and analysis completeness
            confidence = self._calculate_analysis_confidence(github_data, blockchain_data, security_analysis)
            
            # Compile comprehensive result
            result_data = {
                'protocol_name': protocol_name,
                'security_score': overall_security_score,
                'security_analysis': security_analysis,
                'governance_analysis': governance_analysis,
                'technical_risks': technical_risks,
                'security_insights': security_insights,
                'risk_factors': self._categorize_risk_factors(technical_risks),
                'recommendations': self._generate_security_recommendations(security_analysis, governance_analysis),
                'data_sources_used': {
                    'github_available': bool(github_data),
                    'blockchain_available': bool(blockchain_data)
                },
                'analysis_metadata': {
                    'analysis_depth': 'comprehensive',
                    'confidence_level': confidence,
                    'execution_time': execution_time,
                    'model_used': self.model_type
                }
            }
            
            self.log_analysis_step(
                "Security analysis completed",
                {
                    "security_score": overall_security_score,
                    "confidence": confidence,
                    "risks_identified": len(technical_risks),
                    "execution_time": execution_time
                }
            )
            
            return AgentResult(
                agent_id=self.agent_id,
                success=True,
                data=result_data,
                confidence=confidence,
                reasoning=security_insights.get('summary', 'Comprehensive security analysis completed'),
                execution_time=execution_time,
                timestamp=datetime.utcnow(),
                errors=[]
            )
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            error_msg = f"Security analysis failed for {protocol_name}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            return AgentResult(
                agent_id=self.agent_id,
                success=False,
                data={},
                confidence=0.0,
                reasoning=f"Security analysis failed due to: {str(e)}",
                execution_time=execution_time,
                timestamp=datetime.utcnow(),
                errors=[error_msg]
            )
    
    def _extract_github_data(self, previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract GitHub data from Data Hunter Agent results"""
        try:
            data_hunter_result = previous_results.get('data_hunter', {})
            if isinstance(data_hunter_result, dict) and 'result' in data_hunter_result:
                github_source = data_hunter_result['result'].get('source_analysis', {}).get('github', {})
                validated_sources = data_hunter_result['result'].get('validated_sources', {})
                return {
                    'source_analysis': github_source,
                    'github_sources': validated_sources.get('github_sources', [])
                }
        except Exception as e:
            logger.warning(f"Could not extract GitHub data from previous results: {e}")
        
        return {}
    
    def _extract_blockchain_data(self, previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract blockchain data from Data Hunter Agent results"""
        try:
            data_hunter_result = previous_results.get('data_hunter', {})
            if isinstance(data_hunter_result, dict) and 'result' in data_hunter_result:
                blockchain_source = data_hunter_result['result'].get('source_analysis', {}).get('blockchain', {})
                validated_sources = data_hunter_result['result'].get('validated_sources', {})
                return {
                    'source_analysis': blockchain_source,
                    'blockchain_sources': validated_sources.get('blockchain_sources', [])
                }
        except Exception as e:
            logger.warning(f"Could not extract blockchain data from previous results: {e}")
        
        return {}
    
    async def _collect_security_data(self, protocol_name: str) -> tuple:
        """Collect security data if not available from previous agents"""
        github_tool = GitHubADKTool()
        blockchain_tool = BlockchainADKTool()
        
        github_data = {}
        blockchain_data = {}
        
        try:
            # Collect GitHub data
            github_result = await github_tool.execute_with_timeout(protocol_name, timeout_seconds=30)
            if github_result.success:
                github_data = github_result.data
        except Exception as e:
            logger.warning(f"Failed to collect GitHub data: {e}")
        
        try:
            # Collect blockchain data
            blockchain_result = await blockchain_tool.execute_with_timeout(protocol_name, timeout_seconds=30)
            if blockchain_result.success:
                blockchain_data = blockchain_result.data
        except Exception as e:
            logger.warning(f"Failed to collect blockchain data: {e}")
        
        return github_data, blockchain_data
    
    async def _analyze_security_factors(self, github_data: Dict[str, Any], blockchain_data: Dict[str, Any], protocol_name: str) -> Dict[str, Any]:
        """Analyze core security factors"""
        
        security_factors = {
            'contract_verification': self._assess_contract_verification(blockchain_data),
            'development_practices': self._assess_development_practices(github_data),
            'audit_quality': self._assess_audit_quality(github_data, blockchain_data),
            'code_maturity': self._assess_code_maturity(github_data),
            'vulnerability_management': self._assess_vulnerability_management(github_data)
        }
        
        # Calculate weighted scores
        factor_scores = {}
        for factor, analysis in security_factors.items():
            factor_scores[factor] = analysis.get('score', 0)
        
        return {
            'factor_details': security_factors,
            'factor_scores': factor_scores,
            'overall_technical_score': sum(factor_scores.values()) / len(factor_scores) if factor_scores else 0
        }
    
    def _assess_contract_verification(self, blockchain_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess smart contract verification and transparency"""
        score = 0
        details = []
        risks = []
        
        contract_verification = blockchain_data.get('contract_verification', {})
        
        if contract_verification.get('is_verified'):
            score += 70
            details.append("Contract is verified on Etherscan")
            
            # Bonus points for quality indicators
            if contract_verification.get('optimization_used'):
                score += 10
                details.append("Contract uses optimization")
            
            if contract_verification.get('license_type'):
                score += 10
                details.append("Contract has open source license")
            
            # Check for modern compiler
            compiler = contract_verification.get('compiler_version', '')
            if '0.8' in compiler:
                score += 10
                details.append("Uses modern Solidity compiler")
            elif '0.7' in compiler:
                score += 5
                details.append("Uses recent Solidity compiler")
        else:
            score = 20
            risks.append("Contract is not verified - transparency concern")
        
        # Check for proxy patterns
        if contract_verification.get('proxy'):
            if contract_verification.get('implementation'):
                details.append("Proxy contract with clear implementation")
            else:
                risks.append("Proxy contract without clear implementation")
                score -= 15
        
        return {
            'score': min(100, max(0, score)),
            'details': details,
            'risks': risks,
            'verification_status': contract_verification.get('is_verified', False)
        }
    
    def _assess_development_practices(self, github_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess development team practices and code quality"""
        score = 50  # Base score
        details = []
        risks = []
        
        repo_metrics = github_data.get('repository_metrics', {})
        health_components = github_data.get('health_components', {})
        
        # Development activity
        commits_30d = repo_metrics.get('commits_30d', 0)
        unique_authors = repo_metrics.get('unique_authors', 0)
        
        if commits_30d > 10:
            score += 20
            details.append(f"Active development with {commits_30d} commits in 30 days")
        elif commits_30d > 0:
            score += 10
            details.append(f"Some development activity ({commits_30d} commits)")
        else:
            risks.append("No recent development activity")
            score -= 20
        
        # Team diversity
        if unique_authors > 3:
            score += 15
            details.append(f"Diverse development team ({unique_authors} contributors)")
        elif unique_authors > 1:
            score += 5
            details.append(f"Small development team ({unique_authors} contributors)")
        else:
            risks.append("Single developer dependency")
            score -= 15
        
        # Security awareness
        security_commits = repo_metrics.get('security_commits', 0)
        if security_commits > 0:
            score += 15
            details.append(f"Security-conscious development ({security_commits} security commits)")
        
        # Community engagement
        community_score = health_components.get('community_engagement', 0)
        if community_score > 70:
            score += 10
            details.append("Strong community engagement")
        elif community_score < 30:
            risks.append("Limited community engagement")
        
        return {
            'score': min(100, max(0, score)),
            'details': details,
            'risks': risks,
            'activity_level': 'high' if commits_30d > 10 else 'medium' if commits_30d > 0 else 'low'
        }
    
    def _assess_audit_quality(self, github_data: Dict[str, Any], blockchain_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess audit coverage and quality"""
        score = 30  # Base score for unaudited protocols
        details = []
        risks = []
        
        # This would typically integrate with audit databases
        # For now, we'll use heuristics based on available data
        
        # Check for audit-related information in the data
        # This is a simplified implementation - in production, you'd integrate with audit APIs
        
        # Look for indicators of professional auditing
        security_score = blockchain_data.get('health_components', {}).get('security_awareness', 0)
        if security_score > 80:
            score += 40
            details.append("High security awareness indicators")
        
        # Check for bug bounty programs or security practices
        repo_metrics = github_data.get('repository_metrics', {})
        if repo_metrics.get('security_commits', 0) > 0:
            score += 20
            details.append("Evidence of security-focused development")
        
        # For major protocols, assume they have audits
        # This would be replaced with actual audit database integration
        protocol_name = github_data.get('protocol_name', '')
        major_protocols = ['aave', 'compound', 'uniswap', 'lido', 'makerdao']
        if any(protocol in protocol_name.lower() for protocol in major_protocols):
            score = max(score, 70)
            details.append("Major protocol - likely professionally audited")
        
        if score < 50:
            risks.append("Limited audit coverage")
        
        return {
            'score': min(100, max(0, score)),
            'details': details,
            'risks': risks,
            'audit_status': 'likely_audited' if score > 60 else 'unknown'
        }
    
    def _assess_code_maturity(self, github_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess code maturity and stability"""
        score = 50  # Base score
        details = []
        risks = []
        
        repo_metrics = github_data.get('repository_metrics', {})
        
        # Repository age and activity
        stars = repo_metrics.get('stars', 0)
        forks = repo_metrics.get('forks', 0)
        
        if stars > 1000:
            score += 25
            details.append(f"High community adoption ({stars} stars)")
        elif stars > 100:
            score += 15
            details.append(f"Good community adoption ({stars} stars)")
        else:
            risks.append("Limited community adoption")
        
        if forks > 100:
            score += 15
            details.append(f"Active forking activity ({forks} forks)")
        
        # Issue management
        open_issues = repo_metrics.get('open_issues', 0)
        if open_issues < 20:
            score += 10
            details.append("Well-maintained issue queue")
        elif open_issues > 50:
            risks.append("High number of open issues")
            score -= 5
        
        return {
            'score': min(100, max(0, score)),
            'details': details,
            'risks': risks,
            'maturity_level': 'high' if score > 75 else 'medium' if score > 50 else 'low'
        }
    
    def _assess_vulnerability_management(self, github_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess vulnerability management practices"""
        score = 60  # Base score
        details = []
        risks = []
        
        repo_metrics = github_data.get('repository_metrics', {})
        
        # Security-related commits
        security_commits = repo_metrics.get('security_commits', 0)
        if security_commits > 2:
            score += 20
            details.append(f"Regular security updates ({security_commits} commits)")
        elif security_commits > 0:
            score += 10
            details.append(f"Some security updates ({security_commits} commits)")
        
        # Open security issues (this would be detected by the GitHub tool)
        # For now, we'll use general issue metrics
        open_issues = repo_metrics.get('open_issues', 0)
        if open_issues > 0:
            # This is a simplified check - actual implementation would categorize issues
            details.append("Active issue management")
        
        # Response time and maintenance
        health_components = github_data.get('health_components', {})
        maintenance_score = health_components.get('maintenance_quality', 0)
        
        if maintenance_score > 80:
            score += 20
            details.append("Excellent maintenance practices")
        elif maintenance_score < 40:
            risks.append("Poor maintenance practices")
            score -= 15
        
        return {
            'score': min(100, max(0, score)),
            'details': details,
            'risks': risks,
            'response_quality': 'good' if score > 70 else 'moderate' if score > 50 else 'poor'
        }
    
    async def _analyze_governance_structure(self, github_data: Dict[str, Any], blockchain_data: Dict[str, Any], protocol_name: str) -> Dict[str, Any]:
        """Analyze governance and decentralization"""
        
        governance_analysis = {
            'decentralization_score': self._assess_decentralization(github_data, blockchain_data),
            'governance_quality': self._assess_governance_quality(github_data),
            'admin_controls': self._assess_admin_controls(blockchain_data),
            'upgrade_mechanisms': self._assess_upgrade_mechanisms(blockchain_data)
        }
        
        # Calculate overall governance score
        scores = [analysis.get('score', 0) for analysis in governance_analysis.values()]
        overall_score = sum(scores) / len(scores) if scores else 0
        
        return {
            'overall_score': overall_score,
            'components': governance_analysis
        }
    
    def _assess_decentralization(self, github_data: Dict[str, Any], blockchain_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall decentralization level"""
        score = 50  # Base score
        details = []
        risks = []
        
        # Development decentralization
        repo_metrics = github_data.get('repository_metrics', {})
        unique_authors = repo_metrics.get('unique_authors', 0)
        
        if unique_authors > 5:
            score += 20
            details.append(f"Decentralized development ({unique_authors} contributors)")
        elif unique_authors <= 1:
            risks.append("Centralized development (single contributor)")
            score -= 20
        
        # Contract decentralization (based on verification and proxy patterns)
        contract_verification = blockchain_data.get('contract_verification', {})
        if contract_verification.get('proxy') and not contract_verification.get('implementation'):
            risks.append("Unclear proxy implementation - potential centralization")
            score -= 15
        
        return {
            'score': min(100, max(0, score)),
            'details': details,
            'risks': risks
        }
    
    def _assess_governance_quality(self, github_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess governance quality and processes"""
        score = 60  # Base score
        details = []
        risks = []
        
        # Use community engagement as a proxy for governance quality
        health_components = github_data.get('health_components', {})
        community_score = health_components.get('community_engagement', 0)
        
        if community_score > 70:
            score += 20
            details.append("Strong community engagement")
        elif community_score < 30:
            risks.append("Weak community engagement")
            score -= 15
        
        # Check for governance-related activity
        repo_metrics = github_data.get('repository_metrics', {})
        if repo_metrics.get('open_issues', 0) > 0:
            details.append("Active community discussions")
            score += 10
        
        return {
            'score': min(100, max(0, score)),
            'details': details,
            'risks': risks
        }
    
    def _assess_admin_controls(self, blockchain_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess admin controls and centralization risks"""
        score = 70  # Base score assuming good practices
        details = []
        risks = []
        
        contract_verification = blockchain_data.get('contract_verification', {})
        
        # Check for proxy patterns which may indicate admin controls
        if contract_verification.get('proxy'):
            if contract_verification.get('implementation'):
                details.append("Transparent proxy implementation")
                score += 10
            else:
                risks.append("Opaque proxy implementation")
                score -= 20
        
        # Contract verification provides transparency
        if contract_verification.get('is_verified'):
            details.append("Contract code is transparent")
            score += 15
        else:
            risks.append("Contract code not verified")
            score -= 25
        
        return {
            'score': min(100, max(0, score)),
            'details': details,
            'risks': risks
        }
    
    def _assess_upgrade_mechanisms(self, blockchain_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess upgrade mechanisms and risks"""
        score = 60  # Base score
        details = []
        risks = []
        
        contract_verification = blockchain_data.get('contract_verification', {})
        
        # Proxy contracts often indicate upgradeable systems
        if contract_verification.get('proxy'):
            risks.append("Upgradeable contract - centralization risk")
            score -= 15
            
            if contract_verification.get('implementation'):
                details.append("Upgrade implementation is visible")
                score += 10
        else:
            details.append("Non-upgradeable contract - immutable")
            score += 20
        
        return {
            'score': min(100, max(0, score)),
            'details': details,
            'risks': risks
        }
    
    async def _identify_technical_risks(self, github_data: Dict[str, Any], blockchain_data: Dict[str, Any], security_analysis: Dict[str, Any], governance_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify specific technical risk factors"""
        
        risks = []
        
        # Extract risks from security analysis
        for factor, analysis in security_analysis.get('factor_details', {}).items():
            for risk in analysis.get('risks', []):
                risks.append({
                    'category': 'security',
                    'subcategory': factor,
                    'description': risk,
                    'severity': self._assess_risk_severity(risk, analysis.get('score', 0)),
                    'impact': 'high' if analysis.get('score', 0) < 40 else 'medium' if analysis.get('score', 0) < 70 else 'low'
                })
        
        # Extract risks from governance analysis
        for component, analysis in governance_analysis.get('components', {}).items():
            for risk in analysis.get('risks', []):
                risks.append({
                    'category': 'governance',
                    'subcategory': component,
                    'description': risk,
                    'severity': self._assess_risk_severity(risk, analysis.get('score', 0)),
                    'impact': 'high' if analysis.get('score', 0) < 40 else 'medium' if analysis.get('score', 0) < 70 else 'low'
                })
        
        return risks
    
    def _assess_risk_severity(self, risk_description: str, score: float) -> str:
        """Assess risk severity based on description and score"""
        high_severity_keywords = ['not verified', 'single developer', 'no recent', 'centralized']
        medium_severity_keywords = ['limited', 'unclear', 'poor', 'weak']
        
        risk_lower = risk_description.lower()
        
        if any(keyword in risk_lower for keyword in high_severity_keywords) or score < 30:
            return 'high'
        elif any(keyword in risk_lower for keyword in medium_severity_keywords) or score < 60:
            return 'medium'
        else:
            return 'low'
    
    async def _generate_security_insights(self, security_analysis: Dict[str, Any], governance_analysis: Dict[str, Any], technical_risks: List[Dict[str, Any]], protocol_name: str) -> Dict[str, Any]:
        """Generate security insights using LLM"""
        
        # Prepare context for LLM
        context = {
            'protocol_name': protocol_name,
            'overall_security_score': security_analysis.get('overall_technical_score', 0),
            'governance_score': governance_analysis.get('overall_score', 0),
            'high_risk_count': len([r for r in technical_risks if r.get('severity') == 'high']),
            'total_risks': len(technical_risks),
            'key_security_factors': {k: v.get('score', 0) for k, v in security_analysis.get('factor_details', {}).items()}
        }
        
        prompt = f"""Analyze the security assessment for {protocol_name} and provide expert insights:

Security Score: {context['overall_security_score']:.1f}/100
Governance Score: {context['governance_score']:.1f}/100
High Risk Issues: {context['high_risk_count']}
Total Risk Factors: {context['total_risks']}

Security Factor Scores:
{json.dumps(context['key_security_factors'], indent=2)}

Based on this analysis, provide:
1. Overall security assessment summary
2. Key strengths and weaknesses
3. Critical risk factors that need attention
4. Security recommendations for users and developers
5. Comparison to typical DeFi protocol security standards

Focus on practical security implications for users considering this protocol."""
        
        try:
            insights_text = await self.call_gemini(prompt, context)
            
            # Parse insights into structured format
            insights = {
                'summary': insights_text,
                'key_findings': self._extract_security_findings(security_analysis, governance_analysis),
                'critical_risks': [r for r in technical_risks if r.get('severity') == 'high'],
                'security_rating': self._determine_security_rating(security_analysis.get('overall_technical_score', 0))
            }
            
            return insights
            
        except Exception as e:
            logger.warning(f"LLM insights generation failed: {e}")
            
            # Fallback to structured insights
            return {
                'summary': f"Security analysis completed for {protocol_name}",
                'key_findings': self._extract_security_findings(security_analysis, governance_analysis),
                'critical_risks': [r for r in technical_risks if r.get('severity') == 'high'],
                'security_rating': self._determine_security_rating(security_analysis.get('overall_technical_score', 0))
            }
    
    def _extract_security_findings(self, security_analysis: Dict[str, Any], governance_analysis: Dict[str, Any]) -> List[str]:
        """Extract key security findings"""
        findings = []
        
        overall_score = security_analysis.get('overall_technical_score', 0)
        if overall_score > 80:
            findings.append("Strong overall security posture")
        elif overall_score < 40:
            findings.append("Significant security concerns identified")
        
        # Check individual factors
        factor_details = security_analysis.get('factor_details', {})
        
        verification = factor_details.get('contract_verification', {})
        if verification.get('verification_status'):
            findings.append("Smart contract is verified and transparent")
        else:
            findings.append("Smart contract verification concerns")
        
        dev_practices = factor_details.get('development_practices', {})
        if dev_practices.get('activity_level') == 'high':
            findings.append("Active and engaged development team")
        elif dev_practices.get('activity_level') == 'low':
            findings.append("Limited recent development activity")
        
        governance_score = governance_analysis.get('overall_score', 0)
        if governance_score > 70:
            findings.append("Good governance and decentralization")
        elif governance_score < 50:
            findings.append("Governance and decentralization concerns")
        
        return findings
    
    def _determine_security_rating(self, security_score: float) -> str:
        """Determine security rating based on score"""
        if security_score >= 80:
            return "EXCELLENT"
        elif security_score >= 65:
            return "GOOD"
        elif security_score >= 50:
            return "MODERATE"
        elif security_score >= 35:
            return "POOR"
        else:
            return "CRITICAL"
    
    def _calculate_security_score(self, security_analysis: Dict[str, Any], governance_analysis: Dict[str, Any]) -> float:
        """Calculate overall protocol security score"""
        
        # Weight security vs governance factors
        security_weight = 0.7
        governance_weight = 0.3
        
        security_score = security_analysis.get('overall_technical_score', 0)
        governance_score = governance_analysis.get('overall_score', 0)
        
        overall_score = (security_score * security_weight) + (governance_score * governance_weight)
        
        return round(overall_score, 2)
    
    def _calculate_analysis_confidence(self, github_data: Dict[str, Any], blockchain_data: Dict[str, Any], security_analysis: Dict[str, Any]) -> float:
        """Calculate confidence in the security analysis"""
        
        confidence_factors = []
        
        # Data availability confidence
        if github_data:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.3)
        
        if blockchain_data:
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.2)
        
        # Analysis completeness
        factor_details = security_analysis.get('factor_details', {})
        completeness = len(factor_details) / 5.0  # We have 5 security factors
        confidence_factors.append(completeness)
        
        # Average confidence with minimum threshold
        base_confidence = sum(confidence_factors) / len(confidence_factors)
        
        return max(0.3, min(1.0, base_confidence))  # Ensure confidence is between 0.3 and 1.0
    
    def _categorize_risk_factors(self, technical_risks: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Categorize risk factors by type and severity"""
        categorized = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
        for risk in technical_risks:
            severity = risk.get('severity', 'medium')
            description = risk.get('description', '')
            
            if severity == 'high' and risk.get('impact') == 'high':
                categorized['critical'].append(description)
            else:
                categorized[severity].append(description)
        
        return categorized
    
    def _generate_security_recommendations(self, security_analysis: Dict[str, Any], governance_analysis: Dict[str, Any]) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        # Security recommendations
        factor_details = security_analysis.get('factor_details', {})
        
        verification = factor_details.get('contract_verification', {})
        if not verification.get('verification_status'):
            recommendations.append("Verify smart contract code on Etherscan for transparency")
        
        dev_practices = factor_details.get('development_practices', {})
        if dev_practices.get('activity_level') == 'low':
            recommendations.append("Increase development activity and team engagement")
        
        audit_quality = factor_details.get('audit_quality', {})
        if audit_quality.get('score', 0) < 60:
            recommendations.append("Conduct professional security audits")
        
        # Governance recommendations
        governance_score = governance_analysis.get('overall_score', 0)
        if governance_score < 60:
            recommendations.append("Improve governance transparency and decentralization")
        
        return recommendations
    
    async def _get_custom_memory_update(self, context: AgentContext, result: AgentResult) -> Optional[Dict[str, Any]]:
        """Update agent memory with security analysis learnings"""
        if not result.success:
            return None
        
        protocol_name = context.protocol_name
        data = result.data
        
        memory_update = {
            'security_assessments': {
                protocol_name.lower().replace(' ', '_'): {
                    'security_score': data.get('security_score', 0),
                    'security_rating': data.get('security_insights', {}).get('security_rating', 'UNKNOWN'),
                    'critical_risks': len(data.get('risk_factors', {}).get('critical', [])),
                    'analysis_timestamp': datetime.utcnow().isoformat(),
                    'confidence_level': result.confidence
                }
            }
        }
        
        return memory_update
    
    def _get_required_data_fields(self) -> List[str]:
        """Required data fields for Protocol Analyst Agent"""
        return [
            'security_score',
            'security_analysis', 
            'governance_analysis',
            'technical_risks',
            'security_insights'
        ]