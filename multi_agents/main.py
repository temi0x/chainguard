#!/usr/bin/env python3
"""
ChainGuard AI - Main Application Entry Point

Multi-Agent DeFi Protocol Risk Assessment System
Phases 1 & 2 Implementation Test
"""

import asyncio
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
        logging.FileHandler('chainguard.log')
    ]
)

logger = logging.getLogger(__name__)

async def test_phase_1_2_implementation():
    """Test implementation of Phases 1 and 2"""
    
    print("🚀 ChainGuard AI - Testing Phase 1 & 2 Implementation")
    print("=" * 60)
    
    try:
        # Test Phase 1: Configuration and Setup
        print("\n📋 Phase 1: Testing Configuration and Setup...")
        
        # Test settings import
        try:
            from config.settings import settings
            print(f"✅ Settings loaded successfully")
            print(f"   📁 Project ID: {settings.VERTEX_AI_PROJECT_ID}")
            print(f"   🌎 Location: {settings.VERTEX_AI_LOCATION}")
            print(f"   🤖 Primary Model: {settings.GEMINI_MODEL_NAME}")
            print(f"   🧠 Pro Model: {settings.GEMINI_PRO_MODEL}")
            print(f"   🔥 Temperature: {settings.GEMINI_TEMPERATURE}")
        except Exception as e:
            print(f"❌ Settings import failed: {e}")
            return False
        
        # Test protocol validator
        try:
            from utils.protocol_validator import protocol_validator
            test_protocols = ["Aave V3", "invalid_protocol", "lido", "uniswap"]
            
            print(f"\n🔍 Testing Protocol Validator:")
            for protocol in test_protocols:
                is_supported = protocol_validator.is_supported(protocol)
                normalized = protocol_validator.normalize_name(protocol)
                print(f"   {protocol}: {'✅' if is_supported else '❌'} -> {normalized}")
            
            print(f"   📊 Total supported protocols: {len(protocol_validator.get_all_protocols())}")
            
        except Exception as e:
            print(f"❌ Protocol validator test failed: {e}")
            return False
        
        # Test Phase 2: Memory Manager and Base Infrastructure
        print("\n🧠 Phase 2: Testing Memory Manager and Base Infrastructure...")
        
        # Test memory manager initialization
        try:
            from memory.adk_memory_manager import memory_manager
            
            # Initialize Redis connection (will fail gracefully if Redis not available)
            await memory_manager.initialize_redis()
            
            # Test session creation
            session_id = memory_manager.create_session("Aave V3")
            print(f"✅ Memory manager initialized")
            print(f"   📝 Created test session: {session_id}")
            
            # Test health check
            health = await memory_manager.health_check()
            print(f"   🏥 Health check: {health}")
            
        except Exception as e:
            print(f"❌ Memory manager test failed: {e}")
            return False
        
        # Test base agent class
        try:
            from agents.base_adk_agent import BaseChainGuardAgent, AgentContext, AgentResult
            
            # Create a test agent implementation
            class TestAgent(BaseChainGuardAgent):
                def __init__(self):
                    super().__init__("test_agent", "flash")
                
                def get_system_prompt(self) -> str:
                    return "You are a test agent for ChainGuard AI system validation."
                
                async def analyze(self, context: AgentContext) -> AgentResult:
                    return AgentResult(
                        agent_id=self.agent_id,
                        success=True,
                        data={"test": "successful"},
                        confidence=0.95,
                        reasoning="Test execution completed successfully",
                        execution_time=0.1,
                        timestamp=datetime.utcnow(),
                        errors=[]
                    )
            
            # Test agent instantiation
            test_agent = TestAgent()
            print(f"✅ Base agent class working")
            print(f"   🤖 Test agent ID: {test_agent.agent_id}")
            print(f"   📱 Model type: {test_agent.model_type}")
            
            # Test agent health check
            agent_health = await test_agent.health_check()
            print(f"   🏥 Agent health: {agent_health.get('status', 'unknown')}")
            
        except Exception as e:
            print(f"❌ Base agent test failed: {e}")
            return False
        
        # Test response models
        try:
            from models.response_models import RiskAssessment, ProtocolInfo, RiskLevel, AgentInsight, AgentStatus
            
            # Test model creation
            protocol_info = ProtocolInfo(
                name="Test Protocol",
                normalized_name="test_protocol"
            )
            
            agent_insight = AgentInsight(
                agent_id="test_agent",
                status=AgentStatus.COMPLETED,
                confidence=0.95,
                reasoning="Test insight generation",
                execution_time=0.1
            )
            
            print(f"✅ Response models working")
            print(f"   📊 Protocol info created: {protocol_info.name}")
            print(f"   🔍 Agent insight created: {agent_insight.agent_id}")
            
        except Exception as e:
            print(f"❌ Response models test failed: {e}")
            return False
        
        # Summary
        print("\n" + "=" * 60)
        print("🎉 Phase 1 & 2 Implementation Test Results:")
        print("✅ Configuration and settings management")
        print("✅ Protocol validation system")
        print("✅ Memory manager with session handling")
        print("✅ Base agent architecture") 
        print("✅ Response models and data structures")
        print("\n🚀 Ready to proceed with Phase 3: Tool Implementation!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Critical error during testing: {e}")
        logger.error(f"Phase 1&2 test failed: {e}", exc_info=True)
        return False
    
    finally:
        # Cleanup
        try:
            await memory_manager.close_redis()
        except:
            pass

async def main():
    """Main application entry point"""
    
    try:
        # Run phase 1 & 2 tests
        success = await test_phase_1_2_implementation()
        
        if success:
            print("\n✨ ChainGuard AI Phases 1 & 2 - Implementation Complete!")
            print("📋 Next steps:")
            print("   1. Implement Phase 3: ADK Tools")
            print("   2. Implement Phase 4: Specialized Agents")
            print("   3. Implement Phase 5: Orchestration")
            print("   4. Implement Phase 6: FastAPI endpoints")
            print("   5. Deploy to Cloud Run")
        else:
            print("\n❌ Phase 1 & 2 implementation has issues. Please check the logs.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Set up event loop policy for Windows compatibility
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Run the application
    asyncio.run(main())