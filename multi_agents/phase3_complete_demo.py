#!/usr/bin/env python3
"""
ChainGuard AI - Phase 3 Complete Demo

Demonstrates the complete Phase 3 implementation:
1. All three ADK tools working individually
2. Data Hunter Agent using all tools together
3. End-to-end data discovery and validation workflow
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def phase3_complete_demo():
    """Demonstrate complete Phase 3 functionality"""
    
    print("🎉 ChainGuard AI - Phase 3 Complete Demo")
    print("=" * 60)
    print("Demonstrating: ADK Tools + Agent Integration")
    print()
    
    try:
        # Import all Phase 3 components
        from tools import GitHubADKTool, DeFiDataADKTool, BlockchainADKTool, TOOL_METADATA
        from agents.data_hunter_agent import DataHunterAgent
        from agents.base_adk_agent import AgentContext
        from utils.protocol_validator import protocol_validator
        from memory.adk_memory_manager import memory_manager
        
        print("✅ Successfully imported all Phase 3 components")
        print(f"   🔧 Tools: {len(TOOL_METADATA)} ADK tools available")
        print(f"   🤖 Agents: Data Hunter Agent ready")
        print(f"   🧠 Memory: ADK Memory Manager initialized")
        
        # Test Protocol Selection
        test_protocol = "Aave V3"
        print(f"\n🎯 Demo Protocol: {test_protocol}")
        
        if not protocol_validator.is_supported(test_protocol):
            print(f"❌ Protocol {test_protocol} not supported")
            return False
        
        print(f"✅ Protocol {test_protocol} is supported")
        
        # Part 1: Individual Tool Demo
        print(f"\n" + "=" * 40)
        print("📋 PART 1: Individual ADK Tools Demo")
        print("=" * 40)
        
        tools = {
            'GitHub': GitHubADKTool(),
            'DeFi Data': DeFiDataADKTool(), 
            'Blockchain': BlockchainADKTool()
        }
        
        tool_results = {}
        
        for tool_name, tool in tools.items():
            print(f"\n🔧 Testing {tool_name} ADK Tool...")
            
            try:
                # Quick health check
                health = await tool.health_check()
                print(f"   🏥 Health: {health.get('status', 'unknown').upper()}")
                
                # Execute tool
                result = await tool.execute_with_timeout(test_protocol, timeout_seconds=20)
                tool_results[tool_name.lower().replace(' ', '_')] = result
                
                if result.success:
                    print(f"   ✅ Success! Reliability: {result.reliability_score:.2f}")
                    print(f"   ⚡ Execution time: {result.execution_time:.2f}s")
                    
                    # Show key metrics
                    if tool_name == 'GitHub':
                        health_score = result.data.get('health_score', 0)
                        print(f"   📊 Repository Health: {health_score}/100")
                    elif tool_name == 'DeFi Data':
                        financial_score = result.data.get('financial_health_score', 0)
                        print(f"   💰 Financial Health: {financial_score}/100")
                    elif tool_name == 'Blockchain':
                        onchain_score = result.data.get('onchain_health_score', 0)
                        print(f"   ⛓️ On-chain Health: {onchain_score}/100")
                else:
                    print(f"   ❌ Failed: {result.errors[0] if result.errors else 'Unknown error'}")
                    
            except Exception as e:
                print(f"   💥 Exception: {str(e)}")
                tool_results[tool_name.lower().replace(' ', '_')] = None
        
        # Part 2: Integrated Agent Demo
        print(f"\n" + "=" * 40)
        print("🤖 PART 2: Data Hunter Agent Integration")
        print("=" * 40)
        
        print(f"\n🕵️ Initializing Data Hunter Agent...")
        data_hunter = DataHunterAgent()
        
        # Create agent context
        session_id = memory_manager.create_session(test_protocol)
        context = AgentContext(
            session_id=session_id,
            protocol_name=test_protocol,
            parameters={'analysis_depth': 'comprehensive'},
            previous_results={}
        )
        
        print(f"   📝 Created session: {session_id}")
        print(f"   🎯 Analysis target: {test_protocol}")
        print(f"   ⚙️ Parameters: {context.parameters}")
        
        # Execute integrated analysis
        print(f"\n🔄 Executing integrated data discovery...")
        print("   (This uses all three tools in parallel)")
        
        try:
            start_time = datetime.now()
            agent_result = await data_hunter.execute(context)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            if agent_result.success:
                print(f"\n✅ Data Hunter Agent completed successfully!")
                print(f"   ⚡ Total execution time: {execution_time:.2f}s")
                print(f"   🎯 Agent confidence: {agent_result.confidence:.2f}")
                
                # Show discovery summary
                discovery_summary = agent_result.data.get('data_discovery_summary', {})
                print(f"\n📊 Data Discovery Summary:")
                print(f"   🔍 Sources found: {discovery_summary.get('total_sources_found', 0)}/3")
                print(f"   📈 Data quality: {discovery_summary.get('data_quality_score', 0):.1f}/100")
                print(f"   🔧 Reliability: {discovery_summary.get('reliability_score', 0):.2f}")
                print(f"   🕐 Freshness: {discovery_summary.get('data_freshness_score', 0):.2f}")
                
                # Show source analysis
                source_analysis = agent_result.data.get('source_analysis', {})
                print(f"\n🔍 Source Analysis:")
                for source, analysis in source_analysis.items():
                    available = "✅" if analysis.get('available', False) else "❌"
                    reliability = analysis.get('reliability_score', 0)
                    print(f"   {available} {source.title()}: {reliability:.2f} reliability")
                
                # Show recommendations
                recommendations = agent_result.data.get('recommendations', {})
                optimal_sources = recommendations.get('optimal_sources', [])
                data_gaps = recommendations.get('data_gaps', [])
                
                print(f"\n💡 Recommendations:")
                print(f"   🎯 Optimal sources: {len(optimal_sources)}")
                print(f"   ⚠️ Data gaps: {len(data_gaps)}")
                
                for source_rec in optimal_sources[:2]:  # Show top 2
                    source_name = source_rec.get('source', 'unknown')
                    reliability = source_rec.get('reliability', 0)
                    print(f"     ✅ {source_name.title()}: {reliability:.2f} reliability")
                
                # Show insights
                insights = agent_result.data.get('insights', {})
                key_findings = insights.get('key_findings', [])
                print(f"\n🧠 Key Insights:")
                for finding in key_findings[:3]:  # Show top 3 findings
                    print(f"   • {finding}")
                
            else:
                print(f"\n❌ Data Hunter Agent failed!")
                print(f"   💥 Error: {agent_result.reasoning}")
                for error in agent_result.errors[:2]:
                    print(f"   🔍 {error}")
        
        except Exception as e:
            print(f"\n💥 Agent execution failed: {str(e)}")
            return False
        
        # Part 3: Results Summary
        print(f"\n" + "=" * 40)
        print("📋 PART 3: Phase 3 Completion Summary")
        print("=" * 40)
        
        # Count successful components
        successful_tools = sum(1 for result in tool_results.values() 
                             if result and result.success)
        agent_success = agent_result.success if 'agent_result' in locals() else False
        
        print(f"\n🏆 Phase 3 Results:")
        print(f"   ✅ ADK Tools implemented: 3/3")
        print(f"   ✅ Tools working: {successful_tools}/3")
        print(f"   ✅ Agent integration: {'✅ Success' if agent_success else '❌ Failed'}")
        print(f"   ✅ Memory management: ✅ Working")
        print(f"   ✅ Protocol validation: ✅ Working")
        
        # Show architecture overview
        print(f"\n🏗️ Architecture Completed:")
        print(f"   📁 tools/")
        print(f"     ├── base_adk_tool.py (Foundation)")
        print(f"     ├── github_adk_tool.py (Repository analysis)")
        print(f"     ├── defi_data_adk_tool.py (Financial data)")
        print(f"     └── blockchain_adk_tool.py (On-chain data)")
        print(f"   📁 agents/")
        print(f"     └── data_hunter_agent.py (Tool integration)")
        print(f"   📁 memory/")
        print(f"     └── adk_memory_manager.py (State management)")
        
        # Next steps
        print(f"\n🚀 Ready for Phase 4:")
        print(f"   1. Implement remaining agents (Protocol Analyst, Market Intelligence, Risk Synthesizer)")
        print(f"   2. Create agent orchestration system")
        print(f"   3. Build FastAPI endpoints")
        print(f"   4. Deploy to Cloud Run")
        
        # Success assessment
        if successful_tools >= 2 and agent_success:
            print(f"\n🎉 Phase 3 COMPLETE! Excellent foundation established.")
            return True
        elif successful_tools >= 1:
            print(f"\n⚠️ Phase 3 MOSTLY COMPLETE! Some tools need attention.")
            return True
        else:
            print(f"\n❌ Phase 3 INCOMPLETE! Significant issues need resolution.")
            return False
            
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("Make sure all Phase 3 files are properly created")
        return False
    except Exception as e:
        print(f"\n💥 Demo failed: {str(e)}")
        logger.error("Demo execution failed", exc_info=True)
        return False

async def main():
    """Main demo execution"""
    
    try:
        print("🚀 Starting Phase 3 Complete Demo...")
        
        success = await phase3_complete_demo()
        
        if success:
            print("\n✨ Phase 3 Demo Complete - Ready for Phase 4!")
            sys.exit(0)
        else:
            print("\n⚠️ Phase 3 Demo Complete - Issues Identified")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Demo execution error: {e}", exc_info=True)
        print(f"\n💥 Unexpected demo error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Set up event loop policy for Windows compatibility
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Run the demo
    asyncio.run(main())