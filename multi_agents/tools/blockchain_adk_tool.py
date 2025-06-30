import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging

# Internal imports
from tools.base_adk_tool import BaseADKTool, ToolResult, register_tool
from config.settings import settings

logger = logging.getLogger(__name__)

@register_tool
class BlockchainADKTool(BaseADKTool):
    """
    Blockchain ADK Tool for on-chain data analysis and contract verification.
    Integrates with The Graph subgraphs and Etherscan API for blockchain data.
    """
    
    def __init__(self):
        super().__init__("blockchain_analysis")
        
        # API configurations
        self.etherscan_base_url = "https://api.etherscan.io/api"
        self.thegraph_base_url = "https://gateway.thegraph.com/api"
        
        # API keys
        self.etherscan_api_key = settings.ETHERSCAN_API_KEY
        self.thegraph_api_key = settings.THE_GRAPH_API_KEY
        
        # Your discovered working subgraph
        self.working_subgraph_id = "A3Np3RQbaBA6oKJgiwDJeo5T3zrYfGHPWFYayMwtNDum"
        
        logger.info("⛓️ Blockchain ADK Tool initialized")
    
    def get_protocol_identifiers(self, protocol_name: str) -> Dict[str, str]:
        """Get blockchain identifiers for protocol"""
        config = self.get_protocol_config(protocol_name)
        if config:
            return {
                'contract_address': config.get('contract', ''),
                'protocol_name': protocol_name
            }
        return {}
    
    def _get_etherscan_headers(self) -> Dict[str, str]:
        """Get Etherscan API headers"""
        return {
            'Accept': 'application/json',
            'User-Agent': 'ChainGuard-AI/1.0'
        }
    
    def _get_thegraph_headers(self) -> Dict[str, str]:
        """Get The Graph API headers"""
        return {
            'Content-Type': 'application/json',
            'User-Agent': 'ChainGuard-AI/1.0'
        }
    
    async def execute(self, protocol_name: str, parameters: Optional[Dict[str, Any]] = None) -> ToolResult:
        """
        Execute blockchain analysis for a protocol.
        
        Args:
            protocol_name: Name of the protocol to analyze
            parameters: Additional parameters (unused for now)
            
        Returns:
            ToolResult with blockchain analysis data
        """
        start_time = datetime.utcnow()
        errors = []
        source_urls = []
        
        self.log_tool_activity(f"Starting blockchain analysis for {protocol_name}")
        
        # Validate protocol
        if not self.validate_protocol_name(protocol_name):
            return ToolResult(
                tool_name=self.tool_name,
                success=False,
                data={},
                reliability_score=0.0,
                execution_time=0.0,
                timestamp=start_time,
                errors=[f"Protocol '{protocol_name}' not supported"],
                source_urls=[]
            )
        
        # Get protocol identifiers
        protocol_ids = self.get_protocol_identifiers(protocol_name)
        if not protocol_ids:
            return ToolResult(
                tool_name=self.tool_name,
                success=False,
                data={},
                reliability_score=0.0,
                execution_time=0.0,
                timestamp=start_time,
                errors=[f"No blockchain identifiers found for '{protocol_name}'"],
                source_urls=[]
            )
        
        try:
            async with self:  # Use context manager for session
                # Collect blockchain data from multiple sources
                etherscan_data = await self._get_etherscan_data(protocol_ids, source_urls, errors)
                subgraph_data = await self._get_subgraph_data(protocol_ids, source_urls, errors)
                
                # Analyze and synthesize blockchain data
                analysis_result = self._analyze_blockchain_metrics(
                    etherscan_data, subgraph_data, protocol_name
                )
                
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                
                # Calculate reliability score
                data_completeness = self._calculate_data_completeness(etherscan_data, subgraph_data)
                reliability = self.calculate_reliability_score(
                    data_completeness=data_completeness,
                    response_time=execution_time,
                    api_success_rate=1.0 - (len(errors) / 2.0)  # 2 data sources
                )
                
                self.log_tool_activity(
                    f"Blockchain analysis completed for {protocol_name}",
                    {
                        "onchain_health_score": analysis_result.get('onchain_health_score', 0),
                        "contract_verified": analysis_result.get('contract_verification', {}).get('is_verified', False),
                        "reliability": reliability,
                        "execution_time": execution_time
                    }
                )
                
                return ToolResult(
                    tool_name=self.tool_name,
                    success=len(errors) < 2,  # Success if at least one data source worked
                    data=analysis_result,
                    reliability_score=reliability,
                    execution_time=execution_time,
                    timestamp=datetime.utcnow(),
                    errors=errors,
                    source_urls=source_urls
                )
                
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            error_msg = f"Blockchain analysis failed for {protocol_name}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            return ToolResult(
                tool_name=self.tool_name,
                success=False,
                data={},
                reliability_score=0.0,
                execution_time=execution_time,
                timestamp=datetime.utcnow(),
                errors=[error_msg],
                source_urls=source_urls
            )
    
    async def _get_etherscan_data(self, protocol_ids: Dict[str, str], source_urls: List[str], errors: List[str]) -> Dict[str, Any]:
        """Get contract verification data from Etherscan"""
        contract_address = protocol_ids.get('contract_address')
        if not contract_address or not self.etherscan_api_key:
            error_msg = "No contract address or Etherscan API key available"
            errors.append(error_msg)
            return {}
        
        url = f"{self.etherscan_base_url}"
        source_urls.append(url)
        
        try:
            headers = self._get_etherscan_headers()
            params = {
                'module': 'contract',
                'action': 'getsourcecode',
                'address': contract_address,
                'apikey': self.etherscan_api_key
            }
            
            data = await self.http_get(url, headers=headers, params=params)
            
            if data.get('status') != '1':
                error_msg = f"Etherscan API error: {data.get('message', 'Unknown error')}"
                errors.append(error_msg)
                return {}
            
            result = data.get('result', [])
            if not result or not isinstance(result, list):
                errors.append("No contract data returned from Etherscan")
                return {}
            
            contract_info = result[0]
            
            # Process contract verification data
            source_code = contract_info.get('SourceCode', '')
            is_verified = bool(source_code.strip())
            
            return {
                'contract_address': contract_address,
                'is_verified': is_verified,
                'contract_name': contract_info.get('ContractName', ''),
                'compiler_version': contract_info.get('CompilerVersion', ''),
                'optimization_used': contract_info.get('OptimizationUsed', '0') == '1',
                'runs': contract_info.get('Runs', ''),
                'constructor_arguments': contract_info.get('ConstructorArguments', ''),
                'evm_version': contract_info.get('EVMVersion', ''),
                'library': contract_info.get('Library', ''),
                'license_type': contract_info.get('LicenseType', ''),
                'proxy': contract_info.get('Proxy', '0') == '1',
                'implementation': contract_info.get('Implementation', ''),
                'swarm_source': contract_info.get('SwarmSource', ''),
                'has_source_code': is_verified,
                'source_code_length': len(source_code) if source_code else 0
            }
            
        except Exception as e:
            error_msg = f"Failed to get Etherscan data for {contract_address}: {str(e)}"
            errors.append(error_msg)
            logger.warning(error_msg)
            return {}
    
    async def _get_subgraph_data(self, protocol_ids: Dict[str, str], source_urls: List[str], errors: List[str]) -> Dict[str, Any]:
        """Get protocol data from The Graph subgraph"""
        if not self.thegraph_api_key:
            errors.append("No The Graph API key available")
            return {}
        
        url = f"{self.thegraph_base_url}/{self.thegraph_api_key}/subgraphs/id/{self.working_subgraph_id}"
        source_urls.append(url)
        
        try:
            headers = self._get_thegraph_headers()
            
            # Use your discovered working query
            query_data = {
                "query": """
                {
                  tokens(first: 10, orderBy: txCount, orderDirection: desc) {
                    id
                    symbol
                    name
                    totalSupply
                    txCount
                    decimals
                  }
                }
                """
            }
            
            data = await self.http_post(url, json_data=query_data, headers=headers)
            
            if 'errors' in data:
                error_msg = f"Subgraph query error: {data['errors']}"
                errors.append(error_msg)
                return {}
            
            # Process subgraph data
            tokens_data = data.get('data', {}).get('tokens', [])
            
            if not tokens_data:
                errors.append("No token data returned from subgraph")
                return {}
            
            # Analyze token activity and metrics
            total_transactions = sum(int(token.get('txCount', 0)) for token in tokens_data)
            active_tokens = len([token for token in tokens_data if int(token.get('txCount', 0)) > 100])
            
            # Calculate protocol activity metrics
            protocol_activity = {
                'total_tokens': len(tokens_data),
                'active_tokens': active_tokens,
                'total_transactions': total_transactions,
                'avg_transactions_per_token': total_transactions / len(tokens_data) if tokens_data else 0,
                'top_tokens': tokens_data[:5],  # Top 5 most active tokens
                'activity_distribution': self._analyze_activity_distribution(tokens_data)
            }
            
            return {
                'subgraph_accessible': True,
                'protocol_activity': protocol_activity,
                'token_metrics': self._calculate_token_metrics(tokens_data),
                'network_health': self._assess_network_health(tokens_data),
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Failed to get subgraph data: {str(e)}"
            errors.append(error_msg)
            logger.warning(error_msg)
            return {}
    
    def _analyze_activity_distribution(self, tokens_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze distribution of activity across tokens"""
        if not tokens_data:
            return {}
        
        tx_counts = [int(token.get('txCount', 0)) for token in tokens_data]
        tx_counts.sort(reverse=True)
        
        total_tx = sum(tx_counts)
        if total_tx == 0:
            return {'concentration': 'unknown'}
        
        # Calculate concentration metrics
        top_token_share = tx_counts[0] / total_tx if tx_counts else 0
        top_3_share = sum(tx_counts[:3]) / total_tx if len(tx_counts) >= 3 else top_token_share
        
        # Determine concentration level
        if top_token_share > 0.7:
            concentration = 'highly_concentrated'
        elif top_3_share > 0.8:
            concentration = 'moderately_concentrated'
        else:
            concentration = 'well_distributed'
        
        return {
            'concentration': concentration,
            'top_token_share': round(top_token_share * 100, 2),
            'top_3_share': round(top_3_share * 100, 2),
            'active_token_ratio': len([tx for tx in tx_counts if tx > 0]) / len(tx_counts)
        }
    
    def _calculate_token_metrics(self, tokens_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate aggregate token metrics"""
        if not tokens_data:
            return {}
        
        metrics = {
            'total_unique_tokens': len(tokens_data),
            'tokens_with_activity': len([token for token in tokens_data if int(token.get('txCount', 0)) > 0]),
            'high_activity_tokens': len([token for token in tokens_data if int(token.get('txCount', 0)) > 1000]),
            'average_tx_per_token': 0,
            'median_tx_per_token': 0,
            'max_tx_count': 0
        }
        
        tx_counts = [int(token.get('txCount', 0)) for token in tokens_data]
        if tx_counts:
            metrics['average_tx_per_token'] = sum(tx_counts) / len(tx_counts)
            metrics['median_tx_per_token'] = sorted(tx_counts)[len(tx_counts) // 2]
            metrics['max_tx_count'] = max(tx_counts)
        
        return metrics
    
    def _assess_network_health(self, tokens_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess overall network health based on token activity"""
        if not tokens_data:
            return {'health_status': 'unknown'}
        
        total_tokens = len(tokens_data)
        active_tokens = len([token for token in tokens_data if int(token.get('txCount', 0)) > 0])
        high_activity_tokens = len([token for token in tokens_data if int(token.get('txCount', 0)) > 1000])
        
        # Calculate health metrics
        activity_ratio = active_tokens / total_tokens if total_tokens > 0 else 0
        high_activity_ratio = high_activity_tokens / total_tokens if total_tokens > 0 else 0
        
        # Determine health status
        if activity_ratio > 0.8 and high_activity_ratio > 0.2:
            health_status = 'excellent'
        elif activity_ratio > 0.6 and high_activity_ratio > 0.1:
            health_status = 'good'
        elif activity_ratio > 0.3:
            health_status = 'moderate'
        else:
            health_status = 'poor'
        
        return {
            'health_status': health_status,
            'activity_ratio': round(activity_ratio * 100, 2),
            'high_activity_ratio': round(high_activity_ratio * 100, 2),
            'total_ecosystem_transactions': sum(int(token.get('txCount', 0)) for token in tokens_data)
        }
    
    def _analyze_blockchain_metrics(
        self, 
        etherscan_data: Dict[str, Any], 
        subgraph_data: Dict[str, Any],
        protocol_name: str
    ) -> Dict[str, Any]:
        """Analyze blockchain metrics and calculate on-chain health scores"""
        
        # Initialize on-chain health components
        health_components = {
            'contract_verification': 0.0,
            'network_activity': 0.0,
            'ecosystem_health': 0.0,
            'transparency': 0.0
        }
        
        # Contract Verification Score (0-100)
        if etherscan_data:
            verification_score = 0.0
            
            if etherscan_data.get('is_verified'):
                verification_score += 60  # Base score for verification
                
                # Bonus points for quality indicators
                if etherscan_data.get('optimization_used'):
                    verification_score += 10
                    
                if etherscan_data.get('license_type'):
                    verification_score += 10
                    
                # Source code quality
                source_length = etherscan_data.get('source_code_length', 0)
                if source_length > 1000:  # Non-trivial contract
                    verification_score += 10
                    
                # Modern compiler
                compiler = etherscan_data.get('compiler_version', '')
                if '0.8' in compiler or '0.7' in compiler:  # Modern Solidity
                    verification_score += 10
            else:
                verification_score = 20  # Small base score for unverified contracts
            
            health_components['contract_verification'] = min(100, verification_score)
        
        # Network Activity Score (0-100)
        if subgraph_data and 'protocol_activity' in subgraph_data:
            activity_data = subgraph_data['protocol_activity']
            
            total_tx = activity_data.get('total_transactions', 0)
            active_tokens = activity_data.get('active_tokens', 0)
            total_tokens = activity_data.get('total_tokens', 1)
            
            # Activity volume scoring
            import math
            if total_tx > 0:
                activity_volume_score = min(100, math.log10(total_tx) * 20)  # 10M transactions = max
            else:
                activity_volume_score = 0
            
            # Token ecosystem activity
            token_activity_score = (active_tokens / total_tokens) * 100 if total_tokens > 0 else 0
            
            health_components['network_activity'] = (activity_volume_score + token_activity_score) / 2
        
        # Ecosystem Health Score (0-100)
        ecosystem_score = 50.0  # Base score
        
        if subgraph_data and 'network_health' in subgraph_data:
            network_health = subgraph_data['network_health']
            health_status = network_health.get('health_status', 'unknown')
            
            health_score_map = {
                'excellent': 90,
                'good': 75,
                'moderate': 50,
                'poor': 25,
                'unknown': 40
            }
            
            ecosystem_score = health_score_map.get(health_status, 40)
            
            # Bonus for high activity ratios
            activity_ratio = network_health.get('activity_ratio', 0) / 100
            ecosystem_score += activity_ratio * 10  # Up to 10 point bonus
        
        health_components['ecosystem_health'] = min(100, max(0, ecosystem_score))
        
        # Transparency Score (0-100)
        transparency_score = 50.0  # Base score
        
        if etherscan_data:
            if etherscan_data.get('is_verified'):
                transparency_score += 30
            
            if etherscan_data.get('license_type'):
                transparency_score += 10
                
            # Proxy contract detection
            if etherscan_data.get('proxy'):
                if etherscan_data.get('implementation'):
                    transparency_score += 10  # Proxy with clear implementation
                else:
                    transparency_score -= 10  # Proxy without clear implementation
        
        if subgraph_data and subgraph_data.get('subgraph_accessible'):
            transparency_score += 10  # Bonus for having accessible on-chain data
        
        health_components['transparency'] = min(100, max(0, transparency_score))
        
        # Calculate overall on-chain health score
        overall_onchain_health = sum(health_components.values()) / len(health_components)
        
        # Generate insights
        insights = self._generate_blockchain_insights(etherscan_data, subgraph_data, health_components)
        
        return {
            'protocol_name': protocol_name,
            'onchain_health_score': round(overall_onchain_health, 2),
            'health_components': {k: round(v, 2) for k, v in health_components.items()},
            'contract_verification': etherscan_data,
            'network_activity': subgraph_data.get('protocol_activity', {}),
            'token_metrics': subgraph_data.get('token_metrics', {}),
            'network_health': subgraph_data.get('network_health', {}),
            'risk_factors': self._identify_blockchain_risks(etherscan_data, subgraph_data),
            'insights': insights,
            'data_sources': {
                'etherscan_available': bool(etherscan_data),
                'subgraph_available': bool(subgraph_data)
            },
            'last_updated': datetime.utcnow().isoformat()
        }
    
    def _generate_blockchain_insights(
        self, 
        etherscan_data: Dict[str, Any], 
        subgraph_data: Dict[str, Any],
        health_components: Dict[str, float]
    ) -> List[str]:
        """Generate human-readable blockchain insights"""
        insights = []
        
        # Contract verification insights
        if etherscan_data:
            if etherscan_data.get('is_verified'):
                insights.append("✅ Smart contract is verified and transparent")
                
                if etherscan_data.get('optimization_used'):
                    insights.append("Gas-optimized contract deployment")
                    
                compiler = etherscan_data.get('compiler_version', '')
                if '0.8' in compiler:
                    insights.append("Modern Solidity compiler version used")
            else:
                insights.append("⚠️ Smart contract is not verified")
        
        # Network activity insights
        if subgraph_data and 'protocol_activity' in subgraph_data:
            activity = subgraph_data['protocol_activity']
            total_tx = activity.get('total_transactions', 0)
            
            if total_tx > 1_000_000:
                insights.append(f"High network activity with {total_tx:,} total transactions")
            elif total_tx > 100_000:
                insights.append(f"Moderate network activity with {total_tx:,} total transactions")
            elif total_tx > 0:
                insights.append(f"Limited network activity with {total_tx:,} total transactions")
            else:
                insights.append("⚠️ No network activity detected")
        
        # Ecosystem insights
        if subgraph_data and 'network_health' in subgraph_data:
            health = subgraph_data['network_health']
            health_status = health.get('health_status', 'unknown')
            
            if health_status == 'excellent':
                insights.append("Excellent ecosystem health with diverse token activity")
            elif health_status == 'good':
                insights.append("Good ecosystem health with solid token activity")
            elif health_status == 'moderate':
                insights.append("Moderate ecosystem health")
            elif health_status == 'poor':
                insights.append("⚠️ Poor ecosystem health - limited token activity")
        
        # Overall health insights
        if health_components['contract_verification'] > 80:
            insights.append("Strong smart contract transparency and verification")
        elif health_components['contract_verification'] < 40:
            insights.append("⚠️ Contract verification concerns")
        
        return insights
    
    def _identify_blockchain_risks(
        self, 
        etherscan_data: Dict[str, Any], 
        subgraph_data: Dict[str, Any]
    ) -> List[str]:
        """Identify blockchain-related risk factors"""
        risk_factors = []
        
        # Contract verification risks
        if etherscan_data:
            if not etherscan_data.get('is_verified'):
                risk_factors.append("Unverified smart contract")
            
            if etherscan_data.get('proxy') and not etherscan_data.get('implementation'):
                risk_factors.append("Proxy contract without clear implementation")
        
        # Network activity risks
        if subgraph_data and 'protocol_activity' in subgraph_data:
            activity = subgraph_data['protocol_activity']
            total_tx = activity.get('total_transactions', 0)
            
            if total_tx < 1000:
                risk_factors.append("Very low network activity")
        
        # Ecosystem concentration risks
        if subgraph_data and 'protocol_activity' in subgraph_data:
            activity = subgraph_data['protocol_activity']
            if 'activity_distribution' in activity:
                dist = activity['activity_distribution']
                if dist.get('concentration') == 'highly_concentrated':
                    risk_factors.append("Highly concentrated token activity")
        
        # Data availability risks
        if not subgraph_data or not subgraph_data.get('subgraph_accessible'):
            risk_factors.append("Limited on-chain data availability")
        
        return risk_factors
    
    def _calculate_data_completeness(
        self, 
        etherscan_data: Dict[str, Any], 
        subgraph_data: Dict[str, Any]
    ) -> float:
        """Calculate completeness of collected blockchain data"""
        completeness_factors = [
            bool(etherscan_data),
            bool(subgraph_data)
        ]
        
        # Bonus for having key data
        if etherscan_data and 'is_verified' in etherscan_data:
            completeness_factors.append(True)
        
        if subgraph_data and 'protocol_activity' in subgraph_data:
            completeness_factors.append(True)
        
        return sum(completeness_factors) / len(completeness_factors)
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on blockchain data sources"""
        health_status = {
            'status': 'healthy',
            'etherscan_api': False,
            'thegraph_api': False,
            'errors': []
        }
        
        try:
            async with self:
                # Test Etherscan API
                if self.etherscan_api_key:
                    try:
                        url = f"{self.etherscan_base_url}"
                        headers = self._get_etherscan_headers()
                        params = {
                            'module': 'stats',
                            'action': 'ethsupply',
                            'apikey': self.etherscan_api_key
                        }
                        await self.http_get(url, headers=headers, params=params)
                        health_status['etherscan_api'] = True
                    except Exception as e:
                        health_status['errors'].append(f"Etherscan API: {str(e)}")
                else:
                    health_status['errors'].append("Etherscan API key not configured")
                
                # Test The Graph API
                if self.thegraph_api_key:
                    try:
                        url = f"{self.thegraph_base_url}/{self.thegraph_api_key}/subgraphs/id/{self.working_subgraph_id}"
                        headers = self._get_thegraph_headers()
                        query = {"query": "{ tokens(first: 1) { id } }"}
                        await self.http_post(url, json_data=query, headers=headers)
                        health_status['thegraph_api'] = True
                    except Exception as e:
                        health_status['errors'].append(f"The Graph API: {str(e)}")
                else:
                    health_status['errors'].append("The Graph API key not configured")
                
                # Overall status
                if not health_status['etherscan_api'] and not health_status['thegraph_api']:
                    health_status['status'] = 'unhealthy'
                elif not health_status['etherscan_api'] or not health_status['thegraph_api']:
                    health_status['status'] = 'degraded'
                
        except Exception as e:
            health_status['status'] = 'unhealthy'
            health_status['errors'].append(f"General error: {str(e)}")
        
        return health_status