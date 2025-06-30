# tools/__init__.py
"""
ChainGuard AI ADK Tools Package

This package contains all ADK tools for data collection and analysis:
- BaseADKTool: Foundation class for all tools
- GitHubADKTool: Repository and development analysis  
- DeFiDataADKTool: Financial metrics and market data
- BlockchainADKTool: On-chain data and contract verification
"""

from .base_adk_tool import BaseADKTool, ToolResult, TOOL_REGISTRY, register_tool
from .github_adk_tool import GitHubADKTool
from .defi_data_adk_tool import DeFiDataADKTool
from .blockchain_adk_tool import BlockchainADKTool

# Export all tools and utilities
__all__ = [
    # Base classes
    'BaseADKTool',
    'ToolResult',
    'register_tool',
    
    # Tool implementations
    'GitHubADKTool', 
    'DeFiDataADKTool',
    'BlockchainADKTool',
    
    # Tool registry
    'TOOL_REGISTRY',
    'get_all_tools',
    'get_tool_by_name',
    'create_tool_instance'
]

def get_all_tools():
    """Get all registered tool classes"""
    return TOOL_REGISTRY

def get_tool_by_name(tool_name: str):
    """Get tool class by name"""
    for class_name, tool_class in TOOL_REGISTRY.items():
        if hasattr(tool_class, 'tool_name') or tool_name.lower() in class_name.lower():
            return tool_class
    return None

def create_tool_instance(tool_name: str):
    """Create an instance of a tool by name"""
    tool_class = get_tool_by_name(tool_name)
    if tool_class:
        return tool_class()
    raise ValueError(f"Tool '{tool_name}' not found in registry")

# Tool metadata for easy reference
TOOL_METADATA = {
    'github': {
        'class': GitHubADKTool,
        'description': 'Repository analysis and development health assessment',
        'data_sources': ['GitHub API'],
        'metrics': ['stars', 'forks', 'commits', 'issues', 'security_indicators']
    },
    'defi_data': {
        'class': DeFiDataADKTool, 
        'description': 'Financial metrics and market data analysis',
        'data_sources': ['DeFiLlama API', 'CoinGecko API'],
        'metrics': ['tvl', 'price', 'market_cap', 'volume', 'chain_distribution']
    },
    'blockchain': {
        'class': BlockchainADKTool,
        'description': 'On-chain data and contract verification',
        'data_sources': ['Etherscan API', 'The Graph Subgraphs'],
        'metrics': ['contract_verification', 'transaction_activity', 'token_metrics']
    }
}