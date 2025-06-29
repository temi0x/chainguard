import requests
import json
import time
from typing import Dict, Any

# Configuration
LOCAL_URL = "http://localhost:8000"

def test_api() -> None:
    """Test the ChainGuard AI Q&A API locally"""
    
    print(f"🧪 Testing ChainGuard AI Q&A API")
    print(f"🌐 Local URL: {LOCAL_URL}")
    print(f"🏠 Local development mode")
    print("=" * 60)
    
    # Test 1: Health Check
    print("\n1️⃣ Testing Health Check...")
    try:
        response = requests.get(f"{LOCAL_URL}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ Health Check: {health_data['status']}")
            print(f"   🤖 Model: {health_data.get('model', 'N/A')}")
            print(f"   📁 Project: {health_data.get('project', 'N/A')}")
            print(f"   🏠 Mode: {health_data.get('mode', 'N/A')}")
            
            # Check individual components
            checks = health_data.get('checks', {})
            for check_name, check_status in checks.items():
                status_icon = "✅" if check_status else "❌"
                print(f"   {status_icon} {check_name}: {check_status}")
        else:
            print(f"   ❌ Health Check Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection Error: Make sure the API is running!")
        print(f"   💡 Start the API with: python main.py")
        return
    except Exception as e:
        print(f"   ❌ Health Check Error: {e}")
        return
    
    # Test 2: Root Endpoint
    print("\n2️⃣ Testing Root Endpoint...")
    try:
        response = requests.get(f"{LOCAL_URL}/", timeout=10)
        if response.status_code == 200:
            root_data = response.json()
            print(f"   ✅ Root endpoint working")
            print(f"   📋 Service: {root_data.get('service', 'N/A')}")
            print(f"   🔢 Version: {root_data.get('version', 'N/A')}")
            print(f"   🏠 Mode: {root_data.get('mode', 'N/A')}")
        else:
            print(f"   ❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Root endpoint error: {e}")
    
    # Test 3: Ask Questions
    print("\n3️⃣ Testing Q&A Functionality...")
    
    test_questions = [
        "What is ChainGuard AI?",
        "How does the multi-agent system work?",
        "Who are the team members?",
        "What problems does ChainGuard AI solve?",
        "How does ChainGuard integrate with Chainlink?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n   🤔 Question {i}: {question}")
        
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{LOCAL_URL}/ask",
                json={"question": question},
                headers={"Content-Type": "application/json"},
                timeout=30  # Generous timeout for AI responses
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('answer', 'No answer')
                confidence = data.get('confidence', 0)
                
                print(f"   ✅ Response received ({response_time:.2f}s)")
                print(f"   🎯 Confidence: {confidence}")
                print(f"   💬 Answer: {answer[:200]}...")
                
            else:
                print(f"   ❌ Request failed: {response.status_code}")
                print(f"   📄 Response: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Request timed out (>30s)")
        except Exception as e:
            print(f"   ❌ Request error: {e}")
        
        # Small delay between requests
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("🎉 Testing completed!")
    print(f"📖 API Documentation: {LOCAL_URL}/docs")
    print(f"🏥 Health Check: {LOCAL_URL}/health")

def interactive_test() -> None:
    """Interactive testing - ask your own questions"""
    
    print(f"🗣️ Interactive ChainGuard AI Q&A")
    print(f"🌐 Using: {LOCAL_URL}")
    print("💡 Type 'quit' to exit")
    print("=" * 50)
    
    # Quick health check first
    try:
        response = requests.get(f"{LOCAL_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ API not healthy. Please start the server first: python main.py")
            return
    except:
        print("❌ API not reachable. Please start the server first: python main.py")
        return
    
    while True:
        try:
            question = input("\n🤔 Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not question:
                print("❌ Please enter a question")
                continue
            
            print("🤖 Thinking...")
            start_time = time.time()
            
            response = requests.post(
                f"{LOCAL_URL}/ask",
                json={"question": question},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('answer', 'No answer')
                confidence = data.get('confidence', 0)
                
                print(f"\n✅ Response ({response_time:.2f}s, confidence: {confidence})")
                print(f"💬 {answer}")
                
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def quick_test():
    """Quick single question test"""
    question = "What is ChainGuard AI?"
    
    print(f"⚡ Quick Test")
    print(f"🤔 Question: {question}")
    print("-" * 40)
    
    try:
        response = requests.post(
            f"{LOCAL_URL}/ask",
            json={"question": question},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get('answer', 'No answer')
            confidence = data.get('confidence', 0)
            
            print(f"✅ Success (confidence: {confidence})")
            print(f"💬 {answer}")
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Is the API running? Start with: python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    import sys
    
    print("🧪 ChainGuard AI Q&A API - Local Testing")
    print("=" * 50)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "interactive":
            interactive_test()
        elif sys.argv[1] == "quick":
            quick_test()
        else:
            print("Usage:")
            print("  python test_api.py          # Full test suite")
            print("  python test_api.py quick    # Quick single test")
            print("  python test_api.py interactive  # Interactive mode")
    else:
        # Run full tests
        test_api()
        
        # Ask if user wants interactive mode
        try:
            choice = input("\n🤔 Want to try interactive mode? (y/n): ").lower()
            if choice in ['y', 'yes']:
                interactive_test()
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")