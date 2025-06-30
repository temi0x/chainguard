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
class GitHubADKTool(BaseADKTool):
    """
    GitHub ADK Tool for repository analysis and development health assessment.
    Provides insights into code quality, security practices, and development activity.
    """
    
    def __init__(self):
        super().__init__("github_analysis")
        self.base_url = "https://api.github.com"
        self.github_token = settings.GITHUB_TOKEN
        
        if not self.github_token:
            logger.warning("GitHub token not provided - API rate limits will be restrictive")
    
    def get_protocol_identifiers(self, protocol_name: str) -> Dict[str, str]:
        """Get GitHub repository identifier for protocol"""
        config = self.get_protocol_config(protocol_name)
        if config and 'github' in config:
            repo_path = config['github']
            owner, repo = repo_path.split('/')
            return {
                'owner': owner,
                'repo': repo,
                'full_name': repo_path
            }
        return {}
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for GitHub API"""
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'ChainGuard-AI/1.0'
        }
        
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'
        
        return headers
    
    async def execute(self, protocol_name: str, parameters: Optional[Dict[str, Any]] = None) -> ToolResult:
        """
        Execute GitHub analysis for a protocol.
        
        Args:
            protocol_name: Name of the protocol to analyze
            parameters: Additional parameters (unused for now)
            
        Returns:
            ToolResult with GitHub analysis data
        """
        start_time = datetime.utcnow()
        errors = []
        source_urls = []
        
        self.log_tool_activity(f"Starting GitHub analysis for {protocol_name}")
        
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
        
        # Get repository identifiers
        repo_ids = self.get_protocol_identifiers(protocol_name)
        if not repo_ids:
            return ToolResult(
                tool_name=self.tool_name,
                success=False,
                data={},
                reliability_score=0.0,
                execution_time=0.0,
                timestamp=start_time,
                errors=[f"No GitHub repository found for '{protocol_name}'"],
                source_urls=[]
            )
        
        try:
            async with self:  # Use context manager for session
                # Collect all repository data
                repo_data = await self._get_repository_info(repo_ids, source_urls, errors)
                commits_data = await self._get_recent_commits(repo_ids, source_urls, errors)
                issues_data = await self._get_issues_analysis(repo_ids, source_urls, errors)
                
                # Calculate analysis metrics
                analysis_result = self._analyze_repository_health(
                    repo_data, commits_data, issues_data, protocol_name
                )
                
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                
                # Calculate reliability score
                data_completeness = self._calculate_data_completeness(repo_data, commits_data, issues_data)
                reliability = self.calculate_reliability_score(
                    data_completeness=data_completeness,
                    response_time=execution_time,
                    api_success_rate=1.0 - (len(errors) / 3.0)  # 3 API calls expected
                )
                
                self.log_tool_activity(
                    f"GitHub analysis completed for {protocol_name}",
                    {
                        "health_score": analysis_result.get('health_score', 0),
                        "reliability": reliability,
                        "execution_time": execution_time
                    }
                )
                
                return ToolResult(
                    tool_name=self.tool_name,
                    success=len(errors) < 3,  # Success if at least one API call worked
                    data=analysis_result,
                    reliability_score=reliability,
                    execution_time=execution_time,
                    timestamp=datetime.utcnow(),
                    errors=errors,
                    source_urls=source_urls
                )
                
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            error_msg = f"GitHub analysis failed for {protocol_name}: {str(e)}"
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
    
    async def _get_repository_info(self, repo_ids: Dict[str, str], source_urls: List[str], errors: List[str]) -> Dict[str, Any]:
        """Get basic repository information"""
        url = f"{self.base_url}/repos/{repo_ids['full_name']}"
        source_urls.append(url)
        
        try:
            headers = self._get_auth_headers()
            data = await self.http_get(url, headers=headers)
            
            # Extract relevant information
            return {
                'name': data.get('name'),
                'full_name': data.get('full_name'),
                'description': data.get('description'),
                'stars': data.get('stargazers_count', 0),
                'forks': data.get('forks_count', 0),
                'watchers': data.get('watchers_count', 0),
                'open_issues': data.get('open_issues_count', 0),
                'size': data.get('size', 0),
                'created_at': data.get('created_at'),
                'updated_at': data.get('updated_at'),
                'pushed_at': data.get('pushed_at'),
                'language': data.get('language'),
                'has_wiki': data.get('has_wiki', False),
                'has_pages': data.get('has_pages', False),
                'has_downloads': data.get('has_downloads', False),
                'archived': data.get('archived', False),
                'disabled': data.get('disabled', False),
                'default_branch': data.get('default_branch', 'main'),
                'license': data.get('license', {}).get('name') if data.get('license') else None
            }
            
        except Exception as e:
            error_msg = f"Failed to get repository info: {str(e)}"
            errors.append(error_msg)
            logger.warning(error_msg)
            return {}
    
    async def _get_recent_commits(self, repo_ids: Dict[str, str], source_urls: List[str], errors: List[str]) -> Dict[str, Any]:
        """Get recent commit activity"""
        url = f"{self.base_url}/repos/{repo_ids['full_name']}/commits"
        source_urls.append(url)
        
        try:
            headers = self._get_auth_headers()
            params = {
                'per_page': 30,
                'since': (datetime.utcnow() - timedelta(days=30)).isoformat()
            }
            
            commits = await self.http_get(url, headers=headers, params=params)
            
            if not isinstance(commits, list):
                commits = []
            
            # Analyze commit patterns
            commit_analysis = {
                'total_commits_30d': len(commits),
                'commits': [],
                'unique_authors': set(),
                'security_related_commits': 0,
                'avg_commits_per_week': 0
            }
            
            for commit in commits:
                try:
                    commit_data = commit.get('commit', {})
                    author = commit_data.get('author', {})
                    message = commit_data.get('message', '').lower()
                    
                    commit_info = {
                        'sha': commit.get('sha', '')[:8],
                        'message': commit_data.get('message', ''),
                        'author': author.get('name', 'Unknown'),
                        'date': author.get('date'),
                        'additions': commit.get('stats', {}).get('additions', 0),
                        'deletions': commit.get('stats', {}).get('deletions', 0)
                    }
                    
                    commit_analysis['commits'].append(commit_info)
                    commit_analysis['unique_authors'].add(author.get('name', 'Unknown'))
                    
                    # Check for security-related commits
                    security_keywords = ['security', 'vulnerability', 'exploit', 'patch', 'fix', 'audit']
                    if any(keyword in message for keyword in security_keywords):
                        commit_analysis['security_related_commits'] += 1
                        
                except Exception:
                    continue
            
            # Calculate weekly average
            if len(commits) > 0:
                commit_analysis['avg_commits_per_week'] = len(commits) / 4.3  # ~30 days / 7 days
            
            # Convert set to count
            commit_analysis['unique_authors'] = len(commit_analysis['unique_authors'])
            
            return commit_analysis
            
        except Exception as e:
            error_msg = f"Failed to get commit data: {str(e)}"
            errors.append(error_msg)
            logger.warning(error_msg)
            return {'total_commits_30d': 0, 'unique_authors': 0, 'security_related_commits': 0}
    
    async def _get_issues_analysis(self, repo_ids: Dict[str, str], source_urls: List[str], errors: List[str]) -> Dict[str, Any]:
        """Get issues analysis"""
        url = f"{self.base_url}/repos/{repo_ids['full_name']}/issues"
        source_urls.append(url)
        
        try:
            headers = self._get_auth_headers()
            params = {
                'state': 'open',
                'per_page': 20,
                'sort': 'created',
                'direction': 'desc'
            }
            
            issues = await self.http_get(url, headers=headers, params=params)
            
            if not isinstance(issues, list):
                issues = []
            
            # Analyze issues
            issues_analysis = {
                'total_open_issues': len(issues),
                'security_issues': 0,
                'bug_issues': 0,
                'enhancement_issues': 0,
                'recent_activity': False
            }
            
            for issue in issues:
                try:
                    title = issue.get('title', '').lower()
                    labels = [label.get('name', '').lower() for label in issue.get('labels', [])]
                    created_at = issue.get('created_at')
                    
                    # Categorize issues
                    security_indicators = ['security', 'vulnerability', 'exploit', 'cve']
                    bug_indicators = ['bug', 'error', 'fix', 'broken']
                    enhancement_indicators = ['enhancement', 'feature', 'improvement']
                    
                    if any(indicator in title or indicator in str(labels) for indicator in security_indicators):
                        issues_analysis['security_issues'] += 1
                    elif any(indicator in title or indicator in str(labels) for indicator in bug_indicators):
                        issues_analysis['bug_issues'] += 1
                    elif any(indicator in title or indicator in str(labels) for indicator in enhancement_indicators):
                        issues_analysis['enhancement_issues'] += 1
                    
                    # Check for recent activity (within 7 days)
                    if created_at:
                        created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        if (datetime.utcnow().replace(tzinfo=created_date.tzinfo) - created_date).days <= 7:
                            issues_analysis['recent_activity'] = True
                            
                except Exception:
                    continue
            
            return issues_analysis
            
        except Exception as e:
            error_msg = f"Failed to get issues data: {str(e)}"
            errors.append(error_msg)
            logger.warning(error_msg)
            return {'total_open_issues': 0, 'security_issues': 0, 'bug_issues': 0}
    
    def _analyze_repository_health(
        self, 
        repo_data: Dict[str, Any], 
        commits_data: Dict[str, Any], 
        issues_data: Dict[str, Any],
        protocol_name: str
    ) -> Dict[str, Any]:
        """Analyze overall repository health and generate insights"""
        
        # Initialize health components
        health_components = {
            'community_engagement': 0.0,
            'development_activity': 0.0, 
            'maintenance_quality': 0.0,
            'security_awareness': 0.0
        }
        
        # Community Engagement Score (0-100)
        if repo_data:
            stars = repo_data.get('stars', 0)
            forks = repo_data.get('forks', 0)
            watchers = repo_data.get('watchers', 0)
            
            # Score based on community metrics (logarithmic scale)
            import math
            stars_score = min(100, math.log10(max(1, stars)) * 20)  # Max score at 10k stars
            forks_score = min(100, math.log10(max(1, forks)) * 25)   # Max score at 1k forks
            watchers_score = min(100, math.log10(max(1, watchers)) * 30)  # Max score at 100 watchers
            
            health_components['community_engagement'] = (stars_score + forks_score + watchers_score) / 3
        
        # Development Activity Score (0-100)
        if commits_data:
            commits_30d = commits_data.get('total_commits_30d', 0)
            unique_authors = commits_data.get('unique_authors', 0)
            
            # Activity scoring
            commit_score = min(100, commits_30d * 3)  # 33+ commits = max score
            author_diversity = min(100, unique_authors * 20)  # 5+ authors = max score
            
            health_components['development_activity'] = (commit_score + author_diversity) / 2
        
        # Maintenance Quality Score (0-100)
        if repo_data:
            has_license = bool(repo_data.get('license'))
            has_wiki = repo_data.get('has_wiki', False)
            has_description = bool(repo_data.get('description'))
            not_archived = not repo_data.get('archived', False)
            recent_update = False
            
            # Check if updated recently (within 30 days)
            if repo_data.get('pushed_at'):
                try:
                    last_push = datetime.fromisoformat(repo_data['pushed_at'].replace('Z', '+00:00'))
                    days_since_update = (datetime.utcnow().replace(tzinfo=last_push.tzinfo) - last_push).days
                    recent_update = days_since_update <= 30
                except:
                    pass
            
            maintenance_factors = [has_license, has_wiki, has_description, not_archived, recent_update]
            health_components['maintenance_quality'] = (sum(maintenance_factors) / len(maintenance_factors)) * 100
        
        # Security Awareness Score (0-100)
        security_score = 50.0  # Base score
        
        if commits_data:
            security_commits = commits_data.get('security_related_commits', 0)
            total_commits = commits_data.get('total_commits_30d', 1)
            security_ratio = security_commits / max(1, total_commits)
            
            # Bonus for security-related commits
            security_score += min(30, security_ratio * 300)  # Max 30 point bonus
        
        if issues_data:
            security_issues = issues_data.get('security_issues', 0)
            total_issues = issues_data.get('total_open_issues', 1)
            
            # Small penalty for many open security issues
            if security_issues > 0:
                security_score -= min(20, (security_issues / max(1, total_issues)) * 100)
        
        health_components['security_awareness'] = max(0, min(100, security_score))
        
        # Calculate overall health score
        overall_health = sum(health_components.values()) / len(health_components)
        
        # Generate insights and recommendations
        insights = self._generate_insights(repo_data, commits_data, issues_data, health_components)
        
        return {
            'protocol_name': protocol_name,
            'health_score': round(overall_health, 2),
            'health_components': {k: round(v, 2) for k, v in health_components.items()},
            'repository_metrics': {
                'stars': repo_data.get('stars', 0),
                'forks': repo_data.get('forks', 0),
                'commits_30d': commits_data.get('total_commits_30d', 0),
                'unique_authors': commits_data.get('unique_authors', 0),
                'open_issues': issues_data.get('total_open_issues', 0),
                'security_commits': commits_data.get('security_related_commits', 0)
            },
            'risk_factors': self._identify_risk_factors(repo_data, commits_data, issues_data),
            'insights': insights,
            'last_updated': repo_data.get('pushed_at', 'Unknown')
        }
    
    def _generate_insights(
        self, 
        repo_data: Dict[str, Any], 
        commits_data: Dict[str, Any], 
        issues_data: Dict[str, Any],
        health_components: Dict[str, float]
    ) -> List[str]:
        """Generate human-readable insights from the analysis"""
        insights = []
        
        # Community insights
        if health_components['community_engagement'] > 80:
            insights.append("Strong community engagement with high star and fork counts")
        elif health_components['community_engagement'] < 40:
            insights.append("Limited community engagement - may indicate newer or niche protocol")
        
        # Development insights
        if health_components['development_activity'] > 70:
            insights.append("Active development with regular commits and multiple contributors")
        elif health_components['development_activity'] < 30:
            insights.append("Limited development activity - potential maintenance concerns")
        
        # Security insights
        security_commits = commits_data.get('security_related_commits', 0)
        if security_commits > 0:
            insights.append(f"Security-conscious development with {security_commits} security-related commits")
        
        security_issues = issues_data.get('security_issues', 0)
        if security_issues > 0:
            insights.append(f"⚠️ {security_issues} open security-related issues require attention")
        
        # Maintenance insights
        if repo_data.get('archived'):
            insights.append("⚠️ Repository is archived - no active maintenance")
        elif health_components['maintenance_quality'] > 80:
            insights.append("Well-maintained repository with proper documentation and licensing")
        
        return insights
    
    def _identify_risk_factors(
        self, 
        repo_data: Dict[str, Any], 
        commits_data: Dict[str, Any], 
        issues_data: Dict[str, Any]
    ) -> List[str]:
        """Identify potential risk factors from GitHub analysis"""
        risk_factors = []
        
        # Development risks
        if commits_data.get('total_commits_30d', 0) == 0:
            risk_factors.append("No recent development activity")
        
        if commits_data.get('unique_authors', 0) <= 1:
            risk_factors.append("Single developer dependency")
        
        # Repository risks
        if repo_data.get('archived'):
            risk_factors.append("Repository is archived")
        
        if not repo_data.get('license'):
            risk_factors.append("No license specified")
        
        # Security risks
        if issues_data.get('security_issues', 0) > 0:
            risk_factors.append("Open security issues")
        
        # Community risks
        if repo_data.get('stars', 0) < 100:
            risk_factors.append("Limited community adoption")
        
        return risk_factors
    
    def _calculate_data_completeness(
        self, 
        repo_data: Dict[str, Any], 
        commits_data: Dict[str, Any], 
        issues_data: Dict[str, Any]
    ) -> float:
        """Calculate how complete the collected data is"""
        completeness_factors = [
            bool(repo_data),
            bool(commits_data),
            bool(issues_data)
        ]
        
        return sum(completeness_factors) / len(completeness_factors)
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on GitHub API"""
        try:
            headers = self._get_auth_headers()
            
            # Test API connectivity with rate limit info
            async with self:
                url = f"{self.base_url}/rate_limit"
                data = await self.http_get(url, headers=headers)
                
                rate_limit = data.get('rate', {})
                return {
                    'status': 'healthy',
                    'api_accessible': True,
                    'rate_limit_remaining': rate_limit.get('remaining', 0),
                    'rate_limit_total': rate_limit.get('limit', 0),
                    'reset_time': rate_limit.get('reset'),
                    'authenticated': bool(self.github_token)
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'api_accessible': False,
                'error': str(e),
                'authenticated': bool(self.github_token)
            }