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
class DeFiDataADKTool(BaseADKTool):
    """
    DeFi Data ADK Tool for financial metrics and market data analysis.
    Integrates with DeFiLlama and CoinGecko APIs for TVL, pricing, and market data.
    """
    
    def __init__(self):
        super().__init__("defi_data_analysis")
        
        # API configurations
        self.defillama_base_url = "https://api.llama.fi"
        self.coingecko_base_url = "https://api.coingecko.com/api/v3"
        
        # API keys (optional - both have free tiers)
        self.coingecko_api_key = settings.COINGECKO_API_KEY
        self.defillama_api_key = settings.DEFILLAMA_API_KEY  # Usually not needed
        
        logger.info("🦙 DeFi Data ADK Tool initialized")
    
    def get_protocol_identifiers(self, protocol_name: str) -> Dict[str, str]:
        """Get DeFi protocol identifiers for APIs"""
        config = self.get_protocol_config(protocol_name)
        if config:
            return {
                'defillama_slug': config.get('defillama', ''),
                'coingecko_id': config.get('coingecko', ''),
                'protocol_name': protocol_name
            }
        return {}
    
    def _get_coingecko_headers(self) -> Dict[str, str]:
        """Get CoinGecko API headers"""
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'ChainGuard-AI/1.0'
        }
        
        if self.coingecko_api_key:
            headers['x-cg-demo-api-key'] = self.coingecko_api_key
        
        return headers
    
    async def execute(self, protocol_name: str, parameters: Optional[Dict[str, Any]] = None) -> ToolResult:
        """
        Execute DeFi data analysis for a protocol.
        
        Args:
            protocol_name: Name of the protocol to analyze
            parameters: Additional parameters (unused for now)
            
        Returns:
            ToolResult with DeFi data analysis
        """
        start_time = datetime.utcnow()
        errors = []
        source_urls = []
        
        self.log_tool_activity(f"Starting DeFi data analysis for {protocol_name}")
        
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
                errors=[f"No DeFi data identifiers found for '{protocol_name}'"],
                source_urls=[]
            )
        
        try:
            async with self:  # Use context manager for session
                # Collect data from multiple sources
                defillama_data = await self._get_defillama_data(protocol_ids, source_urls, errors)
                coingecko_data = await self._get_coingecko_data(protocol_ids, source_urls, errors)
                
                # Analyze and synthesize data
                analysis_result = self._analyze_defi_metrics(
                    defillama_data, coingecko_data, protocol_name
                )
                
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                
                # Calculate reliability score
                data_completeness = self._calculate_data_completeness(defillama_data, coingecko_data)
                reliability = self.calculate_reliability_score(
                    data_completeness=data_completeness,
                    response_time=execution_time,
                    api_success_rate=1.0 - (len(errors) / 2.0)  # 2 API sources
                )
                
                self.log_tool_activity(
                    f"DeFi data analysis completed for {protocol_name}",
                    {
                        "financial_health_score": analysis_result.get('financial_health_score', 0),
                        "current_tvl": analysis_result.get('tvl_metrics', {}).get('current_tvl_usd', 0),
                        "reliability": reliability,
                        "execution_time": execution_time
                    }
                )
                
                return ToolResult(
                    tool_name=self.tool_name,
                    success=len(errors) < 2,  # Success if at least one API source worked
                    data=analysis_result,
                    reliability_score=reliability,
                    execution_time=execution_time,
                    timestamp=datetime.utcnow(),
                    errors=errors,
                    source_urls=source_urls
                )
                
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            error_msg = f"DeFi data analysis failed for {protocol_name}: {str(e)}"
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
    
    async def _get_defillama_data(self, protocol_ids: Dict[str, str], source_urls: List[str], errors: List[str]) -> Dict[str, Any]:
        """Get protocol data from DeFiLlama with improved reliability and error handling"""
        defillama_slug = protocol_ids.get('defillama_slug')
        if not defillama_slug:
            errors.append("No DeFiLlama slug available")
            return {}
        
        url = f"{self.defillama_base_url}/protocol/{defillama_slug}"
        source_urls.append(url)
        
        try:
            # Enhanced headers for better API compatibility
            headers = {
                'User-Agent': 'ChainGuard-AI/3.0',
                'Accept': 'application/json',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Cache-Control': 'no-cache'
            }
            
            # Increased timeout and retry logic
            async with self.session.get(url, headers=headers, timeout=30) as response:
                if response.status == 200:
                    try:
                        data = await response.json()
                    except Exception as json_error:
                        error_msg = f"Failed to parse DeFiLlama JSON response: {str(json_error)}"
                        errors.append(error_msg)
                        logger.warning(error_msg)
                        return {}
                    
                    # Validate response structure
                    if not isinstance(data, dict):
                        error_msg = f"DeFiLlama returned invalid data format for {defillama_slug}"
                        errors.append(error_msg)
                        return {}
                    
                    # Extract and validate TVL data
                    tvl_data = data.get('tvl', [])
                    chains_data = data.get('chainTvls', {})
                    
                    # Process historical TVL data with error handling
                    processed_tvl = []
                    if isinstance(tvl_data, list) and tvl_data:
                        # Get last 30 days of data
                        recent_tvl = tvl_data[-30:] if len(tvl_data) >= 30 else tvl_data
                        
                        for entry in recent_tvl:
                            if isinstance(entry, dict) and 'date' in entry and 'totalLiquidityUSD' in entry:
                                try:
                                    processed_tvl.append({
                                        'date': entry['date'],
                                        'tvl_usd': float(entry['totalLiquidityUSD']) if entry['totalLiquidityUSD'] is not None else 0.0
                                    })
                                except (ValueError, TypeError) as e:
                                    # Skip invalid entries but continue processing
                                    logger.debug(f"Skipping invalid TVL entry: {e}")
                                    continue
                    
                    # Calculate TVL metrics with safety checks
                    current_tvl = 0.0
                    tvl_30d_ago = 0.0
                    tvl_change_30d = 0.0
                    
                    if processed_tvl:
                        try:
                            current_tvl = processed_tvl[-1]['tvl_usd']
                            tvl_30d_ago = processed_tvl[0]['tvl_usd'] if len(processed_tvl) > 20 else current_tvl
                            
                            if tvl_30d_ago > 0:
                                tvl_change_30d = ((current_tvl - tvl_30d_ago) / tvl_30d_ago) * 100
                        except (KeyError, IndexError, ZeroDivisionError) as e:
                            logger.warning(f"Error calculating TVL metrics: {e}")
                            # Continue with zero values
                    
                    # Process chain distribution data
                    chain_distribution = self._process_chain_tvl(chains_data)
                    
                    # Build comprehensive response
                    result = {
                        'protocol_name': data.get('name', protocol_ids.get('protocol_name', defillama_slug)),
                        'symbol': data.get('symbol', ''),
                        'category': data.get('category', ''),
                        'chains': data.get('chains', []),
                        'description': data.get('description', ''),
                        'url': data.get('url', ''),
                        'logo': data.get('logo', ''),
                        'tvl_metrics': {
                            'current_tvl_usd': current_tvl,
                            'tvl_change_30d_percent': round(tvl_change_30d, 2),
                            'historical_tvl': processed_tvl[-7:] if processed_tvl else [],  # Last 7 days for efficiency
                            'tvl_rank': data.get('tvl_rank'),
                            'mcap_tvl_ratio': data.get('mcap') / max(current_tvl, 1) if data.get('mcap') else None
                        },
                        'chain_distribution': chain_distribution,
                        'methodology': data.get('methodology', {}),
                        'social_links': {
                            'twitter': data.get('twitter'),
                            'discord': data.get('discord'),
                            'telegram': data.get('telegram')
                        },
                        'governance': {
                            'governance_forum': data.get('governanceID'),
                            'parentProtocol': data.get('parentProtocol')
                        },
                        'audit_links': data.get('audit_links', []),
                        'oracles': data.get('oracles', []),
                        'forkedFrom': data.get('forkedFrom', []),
                        'listedAt': data.get('listedAt'),
                        'last_updated': datetime.utcnow().isoformat(),
                        'data_source': 'defillama',
                        'api_version': 'v1'
                    }
                    
                    # Log successful data collection
                    logger.info(f"Successfully collected DeFiLlama data for {defillama_slug}: TVL ${current_tvl:,.0f}")
                    
                    return result
                    
                elif response.status == 404:
                    error_msg = f"Protocol '{defillama_slug}' not found on DeFiLlama"
                    errors.append(error_msg)
                    logger.warning(error_msg)
                    return {}
                elif response.status == 429:
                    error_msg = f"DeFiLlama rate limit exceeded for {defillama_slug}"
                    errors.append(error_msg)
                    logger.warning(error_msg)
                    return {}
                elif response.status >= 500:
                    error_msg = f"DeFiLlama server error {response.status} for {defillama_slug}"
                    errors.append(error_msg)
                    logger.warning(error_msg)
                    return {}
                else:
                    error_msg = f"DeFiLlama API returned status {response.status} for {defillama_slug}"
                    errors.append(error_msg)
                    logger.warning(error_msg)
                    return {}
                    
        except asyncio.TimeoutError:
            error_msg = f"DeFiLlama API timeout for {defillama_slug} after 30 seconds"
            errors.append(error_msg)
            logger.warning(error_msg)
            return {}
        except aiohttp.ClientError as e:
            error_msg = f"DeFiLlama network error for {defillama_slug}: {str(e)}"
            errors.append(error_msg)
            logger.warning(error_msg)
            return {}
        except Exception as e:
            error_msg = f"Unexpected error fetching DeFiLlama data for {defillama_slug}: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg, exc_info=True)
            return {}
    
    async def _get_coingecko_data(self, protocol_ids: Dict[str, str], source_urls: List[str], errors: List[str]) -> Dict[str, Any]:
        """Get token/market data from CoinGecko"""
        coingecko_id = protocol_ids.get('coingecko_id')
        if not coingecko_id:
            errors.append("No CoinGecko ID available")
            return {}
        
        # Use simple price endpoint for efficiency
        url = f"{self.coingecko_base_url}/simple/price"
        source_urls.append(url)
        
        try:
            headers = self._get_coingecko_headers()
            params = {
                'ids': coingecko_id,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_market_cap': 'true',
                'include_24hr_vol': 'true'
            }
            
            data = await self.http_get(url, headers=headers, params=params)
            
            # Extract token data
            token_data = data.get(coingecko_id, {})
            
            if not token_data:
                errors.append(f"No CoinGecko data found for {coingecko_id}")
                return {}
            
            # Get additional detailed info if available
            detailed_data = await self._get_detailed_coingecko_data(coingecko_id, source_urls, errors)
            
            return {
                'token_id': coingecko_id,
                'price_metrics': {
                    'current_price_usd': token_data.get('usd', 0),
                    'price_change_24h_percent': token_data.get('usd_24h_change', 0),
                    'market_cap_usd': token_data.get('usd_market_cap', 0),
                    'volume_24h_usd': token_data.get('usd_24h_vol', 0)
                },
                'market_data': detailed_data,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Failed to get CoinGecko data for {coingecko_id}: {str(e)}"
            errors.append(error_msg)
            logger.warning(error_msg)
            return {}
    
    async def _get_detailed_coingecko_data(self, coingecko_id: str, source_urls: List[str], errors: List[str]) -> Dict[str, Any]:
        """Get additional detailed data from CoinGecko"""
        url = f"{self.coingecko_base_url}/coins/{coingecko_id}"
        source_urls.append(url)
        
        try:
            headers = self._get_coingecko_headers()
            params = {
                'localization': 'false',
                'tickers': 'false',
                'market_data': 'true',
                'community_data': 'false',
                'developer_data': 'false'
            }
            
            data = await self.http_get(url, headers=headers, params=params)
            
            market_data = data.get('market_data', {})
            
            return {
                'market_cap_rank': market_data.get('market_cap_rank'),
                'total_supply': market_data.get('total_supply'),
                'circulating_supply': market_data.get('circulating_supply'),
                'price_change_7d_percent': market_data.get('price_change_percentage_7d'),
                'price_change_30d_percent': market_data.get('price_change_percentage_30d'),
                'all_time_high': market_data.get('ath', {}).get('usd'),
                'all_time_low': market_data.get('atl', {}).get('usd'),
                'liquidity_score': data.get('liquidity_score'),
                'public_interest_score': data.get('public_interest_score')
            }
            
        except Exception as e:
            # This is optional data, so don't add to errors list
            logger.debug(f"Could not get detailed CoinGecko data: {e}")
            return {}
    
    def _process_chain_tvl(self, chains_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process chain TVL distribution data"""
        if not chains_data:
            return {}
        
        chain_distribution = {}
        total_tvl = 0
        
        for chain, tvl_history in chains_data.items():
            if isinstance(tvl_history, list) and tvl_history:
                # Get latest TVL for this chain
                latest_entry = tvl_history[-1]
                if isinstance(latest_entry, dict) and 'totalLiquidityUSD' in latest_entry:
                    chain_tvl = latest_entry['totalLiquidityUSD']
                    chain_distribution[chain] = chain_tvl
                    total_tvl += chain_tvl
        
        # Calculate percentages
        if total_tvl > 0:
            for chain in chain_distribution:
                chain_distribution[f"{chain}_percentage"] = (chain_distribution[chain] / total_tvl) * 100
        
        return {
            'total_tvl': total_tvl,
            'chains': chain_distribution,
            'chain_count': len([k for k in chain_distribution.keys() if not k.endswith('_percentage')])
        }
    
    def _analyze_defi_metrics(
        self, 
        defillama_data: Dict[str, Any], 
        coingecko_data: Dict[str, Any],
        protocol_name: str
    ) -> Dict[str, Any]:
        """Analyze DeFi metrics and calculate financial health scores"""
        
        # Initialize financial health components
        health_components = {
            'tvl_stability': 0.0,
            'market_performance': 0.0,
            'liquidity_health': 0.0,
            'ecosystem_adoption': 0.0
        }
        
        # TVL Stability Score (0-100)
        if defillama_data and 'tvl_metrics' in defillama_data:
            tvl_metrics = defillama_data['tvl_metrics']
            current_tvl = tvl_metrics.get('current_tvl_usd', 0)
            tvl_change_30d = tvl_metrics.get('tvl_change_30d_percent', 0)
            
            # Score based on TVL size and stability
            import math
            tvl_size_score = min(100, math.log10(max(1, current_tvl / 1000000)) * 25)  # Log scale, $1B = max
            
            # Stability scoring - prefer steady growth over volatility
            if abs(tvl_change_30d) <= 20:  # Within ±20% is stable
                stability_score = 100 - abs(tvl_change_30d) * 2
            else:
                stability_score = max(0, 60 - abs(tvl_change_30d))  # Penalty for high volatility
            
            health_components['tvl_stability'] = (tvl_size_score + stability_score) / 2
        
        # Market Performance Score (0-100)
        if coingecko_data and 'price_metrics' in coingecko_data:
            price_metrics = coingecko_data['price_metrics']
            market_cap = price_metrics.get('market_cap_usd', 0)
            volume_24h = price_metrics.get('volume_24h_usd', 0)
            price_change_24h = price_metrics.get('price_change_24h_percent', 0)
            
            # Market cap scoring
            import math
            market_cap_score = min(100, math.log10(max(1, market_cap / 1000000)) * 30)  # $1B = max
            
            # Volume scoring (healthy trading activity)
            volume_score = min(100, math.log10(max(1, volume_24h / 100000)) * 40)  # $100M = max
            
            # Price stability (prefer stable over volatile)
            price_stability = max(0, 100 - abs(price_change_24h) * 5)  # Penalty for high volatility
            
            health_components['market_performance'] = (market_cap_score + volume_score + price_stability) / 3
        
        # Liquidity Health Score (0-100)
        liquidity_score = 50.0  # Base score
        
        if coingecko_data and 'market_data' in coingecko_data:
            market_data = coingecko_data['market_data']
            liquidity_score_cg = market_data.get('liquidity_score', 0)
            if liquidity_score_cg:
                liquidity_score = liquidity_score_cg * 100  # CoinGecko score is 0-1
        
        # Calculate volume to market cap ratio
        if coingecko_data and 'price_metrics' in coingecko_data:
            price_metrics = coingecko_data['price_metrics']
            market_cap = price_metrics.get('market_cap_usd', 0)
            volume_24h = price_metrics.get('volume_24h_usd', 0)
            
            if market_cap > 0 and volume_24h > 0:
                volume_ratio = (volume_24h / market_cap) * 100
                # Healthy ratio is typically 1-10%
                if 1 <= volume_ratio <= 10:
                    liquidity_score += 20
                elif volume_ratio > 10:
                    liquidity_score += 10  # Very high might indicate volatility
        
        health_components['liquidity_health'] = min(100, max(0, liquidity_score))
        
        # Ecosystem Adoption Score (0-100)
        adoption_score = 50.0  # Base score
        
        if defillama_data:
            # Multi-chain presence
            chains = defillama_data.get('chains', [])
            chain_count = len(chains) if isinstance(chains, list) else 0
            adoption_score += min(30, chain_count * 6)  # Max bonus for 5+ chains
            
            # Chain distribution (prefer diversified over concentrated)
            chain_dist = defillama_data.get('chain_distribution', {})
            if chain_dist and 'chain_count' in chain_dist:
                if chain_dist['chain_count'] > 1:
                    adoption_score += 10  # Bonus for multi-chain
        
        # Audit and security indicators
        if defillama_data and defillama_data.get('audit_links'):
            adoption_score += 10  # Bonus for having audits
        
        health_components['ecosystem_adoption'] = min(100, max(0, adoption_score))
        
        # Calculate overall financial health score
        overall_financial_health = sum(health_components.values()) / len(health_components)
        
        # Generate insights
        insights = self._generate_financial_insights(defillama_data, coingecko_data, health_components)
        
        # Compile final analysis
        return {
            'protocol_name': protocol_name,
            'financial_health_score': round(overall_financial_health, 2),
            'health_components': {k: round(v, 2) for k, v in health_components.items()},
            'tvl_metrics': defillama_data.get('tvl_metrics', {}),
            'price_metrics': coingecko_data.get('price_metrics', {}),
            'market_data': coingecko_data.get('market_data', {}),
            'chain_distribution': defillama_data.get('chain_distribution', {}),
            'risk_factors': self._identify_financial_risks(defillama_data, coingecko_data),
            'insights': insights,
            'data_sources': {
                'defillama_available': bool(defillama_data),
                'coingecko_available': bool(coingecko_data)
            },
            'last_updated': datetime.utcnow().isoformat()
        }
    
    def _generate_financial_insights(
        self, 
        defillama_data: Dict[str, Any], 
        coingecko_data: Dict[str, Any],
        health_components: Dict[str, float]
    ) -> List[str]:
        """Generate human-readable financial insights"""
        insights = []
        
        # TVL insights
        if defillama_data and 'tvl_metrics' in defillama_data:
            tvl_metrics = defillama_data['tvl_metrics']
            current_tvl = tvl_metrics.get('current_tvl_usd', 0)
            tvl_change = tvl_metrics.get('tvl_change_30d_percent', 0)
            
            if current_tvl > 1_000_000_000:  # $1B+
                insights.append(f"Large-scale protocol with ${current_tvl/1_000_000_000:.1f}B TVL")
            elif current_tvl > 100_000_000:  # $100M+
                insights.append(f"Medium-scale protocol with ${current_tvl/1_000_000:.0f}M TVL")
            else:
                insights.append(f"Small-scale protocol with ${current_tvl/1_000_000:.1f}M TVL")
            
            if tvl_change > 20:
                insights.append(f"Strong TVL growth of {tvl_change:.1f}% in 30 days")
            elif tvl_change < -20:
                insights.append(f"⚠️ Significant TVL decline of {tvl_change:.1f}% in 30 days")
            else:
                insights.append(f"Stable TVL with {tvl_change:.1f}% change in 30 days")
        
        # Market insights
        if coingecko_data and 'price_metrics' in coingecko_data:
            price_metrics = coingecko_data['price_metrics']
            market_cap = price_metrics.get('market_cap_usd', 0)
            volume_24h = price_metrics.get('volume_24h_usd', 0)
            
            if market_cap > 0 and volume_24h > 0:
                volume_ratio = (volume_24h / market_cap) * 100
                if volume_ratio > 15:
                    insights.append("High trading activity indicates strong market interest")
                elif volume_ratio < 1:
                    insights.append("Low trading volume may indicate limited liquidity")
        
        # Multi-chain insights
        if defillama_data:
            chains = defillama_data.get('chains', [])
            if isinstance(chains, list) and len(chains) > 1:
                insights.append(f"Multi-chain presence across {len(chains)} networks")
        
        # Health component insights
        if health_components['tvl_stability'] > 80:
            insights.append("Excellent TVL stability and size")
        elif health_components['tvl_stability'] < 40:
            insights.append("⚠️ TVL concerns - either small size or high volatility")
        
        return insights
    
    def _identify_financial_risks(
        self, 
        defillama_data: Dict[str, Any], 
        coingecko_data: Dict[str, Any]
    ) -> List[str]:
        """Identify financial risk factors"""
        risk_factors = []
        
        # TVL risks
        if defillama_data and 'tvl_metrics' in defillama_data:
            tvl_metrics = defillama_data['tvl_metrics']
            current_tvl = tvl_metrics.get('current_tvl_usd', 0)
            tvl_change = tvl_metrics.get('tvl_change_30d_percent', 0)
            
            if current_tvl < 10_000_000:  # Less than $10M
                risk_factors.append("Low TVL indicates limited adoption")
            
            if tvl_change < -30:
                risk_factors.append("Significant TVL decline")
        
        # Market risks
        if coingecko_data and 'price_metrics' in coingecko_data:
            price_metrics = coingecko_data['price_metrics']
            volume_24h = price_metrics.get('volume_24h_usd', 0)
            market_cap = price_metrics.get('market_cap_usd', 0)
            
            if volume_24h < 100_000:  # Less than $100k daily volume
                risk_factors.append("Low trading volume")
            
            if market_cap > 0 and volume_24h > 0:
                volume_ratio = (volume_24h / market_cap) * 100
                if volume_ratio > 50:  # Very high turnover
                    risk_factors.append("Extremely high trading volume may indicate instability")
        
        # Chain concentration risk
        if defillama_data and 'chain_distribution' in defillama_data:
            chain_dist = defillama_data['chain_distribution']
            if chain_dist and 'chain_count' in chain_dist:
                if chain_dist['chain_count'] == 1:
                    risk_factors.append("Single-chain dependency")
        
        return risk_factors
    
    def _calculate_data_completeness(
        self, 
        defillama_data: Dict[str, Any], 
        coingecko_data: Dict[str, Any]
    ) -> float:
        """Calculate completeness of collected financial data"""
        completeness_factors = [
            bool(defillama_data),
            bool(coingecko_data)
        ]
        
        # Bonus for having key metrics
        if defillama_data and 'tvl_metrics' in defillama_data:
            completeness_factors.append(True)
        
        if coingecko_data and 'price_metrics' in coingecko_data:
            completeness_factors.append(True)
        
        return sum(completeness_factors) / len(completeness_factors)
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on DeFi data APIs"""
        health_status = {
            'status': 'healthy',
            'defillama_api': False,
            'coingecko_api': False,
            'errors': []
        }
        
        try:
            async with self:
                # Test DeFiLlama API with better error handling
                try:
                    url = f"{self.defillama_base_url}/protocols"
                    headers = {
                        'User-Agent': 'ChainGuard-AI/3.0',
                        'Accept': 'application/json'
                    }
                    
                    async with self.session.get(url, headers=headers, timeout=30) as response:
                        if response.status == 200:
                            data = await response.json()
                            if isinstance(data, list) and len(data) > 0:
                                health_status['defillama_api'] = True
                            else:
                                health_status['errors'].append("DeFiLlama API: Empty response")
                        else:
                            health_status['errors'].append(f"DeFiLlama API: HTTP {response.status}")
                            
                except Exception as e:
                    health_status['errors'].append(f"DeFiLlama API: {str(e)}")
                
                # Test CoinGecko API
                try:
                    url = f"{self.coingecko_base_url}/ping"
                    headers = self._get_coingecko_headers()
                    await self.http_get(url, headers=headers)
                    health_status['coingecko_api'] = True
                except Exception as e:
                    health_status['errors'].append(f"CoinGecko API: {str(e)}")
                
                # Overall status
                if not health_status['defillama_api'] and not health_status['coingecko_api']:
                    health_status['status'] = 'unhealthy'
                elif not health_status['defillama_api'] or not health_status['coingecko_api']:
                    health_status['status'] = 'degraded'
                
        except Exception as e:
            health_status['status'] = 'unhealthy'
            health_status['errors'].append(f"General error: {str(e)}")
        
        return health_status