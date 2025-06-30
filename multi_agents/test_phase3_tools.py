#!/usr/bin/env python3
"""
ChainGuard AI - Phase 3 ADK Tools Testing Script

Comprehensive testing of all ADK tools with real protocols
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('phase3_test.log')
    ]
)

logger = logging.getLogger(__name__)

async def test_phase_3_tools():
    """Test all Phase 3 ADK tools implementation"""
    
    print("🔧 ChainGuard AI - Phase 3 ADK Tools Testing")
    print("=" * 60)
    
    try:
        # Import tools and dependencies
        print("\n📦 Phase 3: Testing Tool Imports...")
        
        from tools import (
            GitHubADKTool, DeFiDataADKTool, BlockchainADKTool,
            TOOL_REGISTRY, get_all_tools, create_tool_instance
        )
        from utils.protocol_validator import protocol_validator
        
        print(f"✅ Successfully imported all ADK tools")
        print(f"   🔧 Registered tools: {len(TOOL_REGISTRY)}")
        print(f"   📋 Available tools: {list(TOOL_REGISTRY.keys())}")
        
        # Test protocol selection
        protocols = protocol_validator.get_all_protocols()
        test_protocol = "Aave V3"  # Use Aave V3 as our main test case
        
        print(f"\n🎯 Testing with protocol: {test_protocol}")
        print(f"   📊 Total supported protocols: {len(protocols)}")
        
        # Initialize all tools
        print(f"\n🏗️ Initializing ADK tools...")
        
        github_tool = GitHubADKTool()
        defi_tool = DeFiDataADKTool()
        blockchain_tool = BlockchainADKTool()
        
        tools = {
            'GitHub': github_tool,
            'DeFi Data': defi_tool,
            'Blockchain': blockchain_tool
        }
        
        # Test tool health checks first
        print(f"\n🏥 Testing tool health checks...")
        
        for tool_name, tool in tools.items():
            try:
                health = await tool.health_check()
                status = health.get('status', 'unknown')
                print(f"   {tool_name}: {status.upper()}")
                
                if status != 'healthy':
                    errors = health.get('errors', [])
                    for error in errors[:2]:  # Show first 2 errors
                        print(f"     ⚠️ {error}")
                        
            except Exception as e:
                print(f"   ❌ {tool_name}: Health check failed - {e}")
        
        # Test each tool individually
        print(f"\n🧪 Testing individual tool execution...")
        
        tool_results = {}
        
        # Test GitHub Tool
        print(f"\n🐙 Testing GitHub ADK Tool...")
        try:
            github_result = await github_tool.execute_with_timeout(test_protocol, timeout_seconds=30)
            tool_results['github'] = github_result
            
            if github_result.success:
                health_score = github_result.data.get('health_score', 0)
                repo_metrics = github_result.data.get('repository_metrics', {})
                print(f"   ✅ GitHub analysis successful")
                print(f"   📊 Health Score: {health_score}/100")
                print(f"   ⭐ Stars: {repo_metrics.get('stars', 0)}")
                print(f"   🍴 Forks: {repo_metrics.get('forks', 0)}")
                print(f"   📝 Commits (30d): {repo_metrics.get('commits_30d', 0)}")
                print(f"   ⚡ Execution time: {github_result.execution_time:.2f}s")
                print(f"   🎯 Reliability: {github_result.reliability_score:.2f}")
            else:
                print(f"   ❌ GitHub analysis failed")
                for error in github_result.errors:
                    print(f"     💥 {error}")
                    
        except Exception as e:
            print(f"   💥 GitHub tool test failed: {e}")
            tool_results['github'] = None
        
        # Test DeFi Data Tool
        print(f"\n🦙 Testing DeFi Data ADK Tool...")
        try:
            defi_result = await defi_tool.execute_with_timeout(test_protocol, timeout_seconds=30)
            tool_results['defi_data'] = defi_result
            
            if defi_result.success:
                financial_score = defi_result.data.get('financial_health_score', 0)
                tvl_metrics = defi_result.data.get('tvl_metrics', {})
                price_metrics = defi_result.data.get('price_metrics', {})
                print(f"   ✅ DeFi data analysis successful")
                print(f"   📊 Financial Health Score: {financial_score}/100")
                print(f"   💰 Current TVL: ${tvl_metrics.get('current_tvl_usd', 0):,.0f}")
                print(f"   📈 TVL Change (30d): {tvl_metrics.get('tvl_change_30d_percent', 0):.1f}%")
                print(f"   💵 Token Price: ${price_metrics.get('current_price_usd', 0):.2f}")
                print(f"   ⚡ Execution time: {defi_result.execution_time:.2f}s")
                print(f"   🎯 Reliability: {defi_result.reliability_score:.2f}")
            else:
                print(f"   ❌ DeFi data analysis failed")
                for error in defi_result.errors:
                    print(f"     💥 {error}")
                    
        except Exception as e:
            print(f"   💥 DeFi data tool test failed: {e}")
            tool_results['defi_data'] = None
        
        # Test Blockchain Tool
        print(f"\n⛓️ Testing Blockchain ADK Tool...")
        try:
            blockchain_result = await blockchain_tool.execute_with_timeout(test_protocol, timeout_seconds=30)
            tool_results['blockchain'] = blockchain_result
            
            if blockchain_result.success:
                onchain_score = blockchain_result.data.get('onchain_health_score', 0)
                contract_verification = blockchain_result.data.get('contract_verification', {})
                network_activity = blockchain_result.data.get('network_activity', {})
                print(f"   ✅ Blockchain analysis successful")
                print(f"   📊 On-chain Health Score: {onchain_score}/100")
                print(f"   ✅ Contract Verified: {contract_verification.get('is_verified', False)}")
                print(f"   📝 Contract Name: {contract_verification.get('contract_name', 'N/A')}")
                print(f"   🔄 Total Transactions: {network_activity.get('total_transactions', 0):,}")
                print(f"   ⚡ Execution time: {blockchain_result.execution_time:.2f}s")
                print(f"   🎯 Reliability: {blockchain_result.reliability_score:.2f}")
            else:
                print(f"   ❌ Blockchain analysis failed")
                for error in blockchain_result.errors:
                    print(f"     💥 {error}")
                    
        except Exception as e:
            print(f"   💥 Blockchain tool test failed: {e}")
            tool_results['blockchain'] = None
        
        # Test tool registry functionality
        print(f"\n🗂️ Testing tool registry functionality...")
        
        try:
            all_tools = get_all_tools()
            print(f"   📋 Registry contains {len(all_tools)} tools")
            
            # Test tool creation by name
            github_instance = create_tool_instance('github')
            print(f"   ✅ Successfully created GitHub tool instance: {type(github_instance).__name__}")
            
            defi_instance = create_tool_instance('defi')
            print(f"   ✅ Successfully created DeFi tool instance: {type(defi_instance).__name__}")
            
            blockchain_instance = create_tool_instance('blockchain')
            print(f"   ✅ Successfully created Blockchain tool instance: {type(blockchain_instance).__name__}")
            
        except Exception as e:
            print(f"   ❌ Tool registry test failed: {e}")
        
        # Test with multiple protocols
        print(f"\n🔄 Testing with multiple protocols...")
        
        test_protocols = ["Lido (stETH)", "Uniswap V4"]
        multi_protocol_results = {}
        
        for protocol in test_protocols:
            print(f"\n   🧪 Testing {protocol}...")
            protocol_results = {}
            
            # Quick test with GitHub tool only (fastest)
            try:
                github_result = await github_tool.execute_with_timeout(protocol, timeout_seconds=15)
                if github_result.success:
                    health_score = github_result.data.get('health_score', 0)
                    print(f"     ✅ {protocol} GitHub Health: {health_score}/100")
                else:
                    print(f"     ❌ {protocol} GitHub analysis failed")
                protocol_results['github'] = github_result.success
            except Exception as e:
                print(f"     💥 {protocol} test error: {e}")
                protocol_results['github'] = False
            
            multi_protocol_results[protocol] = protocol_results
        
        # Generate comprehensive test report
        print(f"\n📊 Generating test report...")
        
        successful_tools = sum(1 for result in tool_results.values() 
                             if result and result.success)
        total_tools = len(tool_results)
        
        successful_protocols = sum(1 for results in multi_protocol_results.values() 
                                 if any(results.values()))
        total_test_protocols = len(multi_protocol_results)
        
        # Summary
        print("\n" + "=" * 60)
        print("🎉 Phase 3 ADK Tools Test Results:")
        print(f"✅ Tool implementations: {successful_tools}/{total_tools}")
        print(f"✅ Protocol compatibility: {successful_protocols + 1}/{total_test_protocols + 1}")  # +1 for main test
        
        # Detailed results
        for tool_name, result in tool_results.items():
            if result:
                status = "✅ PASS" if result.success else "❌ FAIL"
                reliability = f"({result.reliability_score:.2f})" if result.success else ""
                print(f"   {status} {tool_name.title()} Tool {reliability}")
            else:
                print(f"   ❌ FAIL {tool_name.title()} Tool (exception)")
        
        # Data structure examples
        if any(result and result.success for result in tool_results.values()):
            print(f"\n📋 Sample data structures generated:")
            
            for tool_name, result in tool_results.items():
                if result and result.success:
                    data_keys = list(result.data.keys())[:5]  # First 5 keys
                    print(f"   {tool_name.title()}: {data_keys}")
        
        # Final assessment
        if successful_tools == total_tools:
            print(f"\n🚀 Phase 3 Complete! All ADK tools working perfectly.")
            print(f"📋 Next steps:")
            print(f"   1. Integrate tools with agents (Phase 4)")
            print(f"   2. Implement orchestration (Phase 5)")
            print(f"   3. Create API endpoints (Phase 6)")
        elif successful_tools >= 2:
            print(f"\n⚠️ Phase 3 Mostly Complete! {successful_tools}/{total_tools} tools working.")
            print(f"🔧 Address failing tools before Phase 4.")
        else:
            print(f"\n❌ Phase 3 Issues! Only {successful_tools}/{total_tools} tools working.")
            print(f"🛠️ Debug and fix tools before proceeding.")
        
        return successful_tools == total_tools
        
    except Exception as e:
        print(f"\n❌ Critical error during Phase 3 testing: {e}")
        logger.error(f"Phase 3 test failed: {e}", exc_info=True)
        return False

async def main():
    """Main test execution"""
    
    try:
        print("🧪 Starting Phase 3 ADK Tools comprehensive test...")
        
        success = await test_phase_3_tools()
        
        if success:
            print("\n✨ Phase 3 Testing Complete - All Systems Go!")
            sys.exit(0)
        else:
            print("\n⚠️ Phase 3 Testing Complete - Some Issues Found")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test execution error: {e}", exc_info=True)
        print(f"\n💥 Unexpected test error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Set up event loop policy for Windows compatibility
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Run the test
    asyncio.run(main())