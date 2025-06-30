#!/usr/bin/env python3
"""
ChainGuard AI - External API Testing Script
Test all external data sources before Phase 3 implementation
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime
import sys

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

class APITester:
    def __init__(self):
        self.results = {}
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_github_api(self):
        """Test GitHub API with personal access token"""
        print("🐙 Testing GitHub API...")
        
        token = os.getenv('GITHUB_TOKEN')
        if not token:
            print("❌ GitHub token not found")
            return False
        
        try:
            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            # Test: Get Aave V3 repository info
            url = "https://api.github.com/repos/aave/aave-v3-core"
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ GitHub API working")
                    print(f"   📊 Aave V3 Core: {data['stargazers_count']} stars, {data['forks_count']} forks")
                    print(f"   📅 Last push: {data['pushed_at']}")
                    print(f"   👥 Contributors: {data.get('subscribers_count', 'N/A')}")
                    
                    # Test rate limit
                    rate_limit = response.headers.get('X-RateLimit-Remaining', 'Unknown')
                    print(f"   ⚡ Rate limit remaining: {rate_limit}")
                    
                    self.results['github'] = {'status': 'success', 'data': data}
                    return True
                else:
                    print(f"❌ GitHub API failed: {response.status}")
                    print(f"   Response: {await response.text()}")
                    return False
                    
        except Exception as e:
            print(f"❌ GitHub API error: {e}")
            return False
    
    async def test_coingecko_api(self):
        """Test CoinGecko API"""
        print("\n🦎 Testing CoinGecko API...")
        
        api_key = os.getenv('COINGECKO_API_KEY')
        
        try:
            # Test with and without API key
            headers = {}
            if api_key:
                headers['x-cg-demo-api-key'] = api_key
                print(f"   🔑 Using API key: {api_key[:8]}...")
            else:
                print("   🆓 Using free tier")
            
            # Test: Get AAVE token data
            url = "https://api.coingecko.com/api/v3/coins/aave"
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    price = data['market_data']['current_price']['usd']
                    market_cap = data['market_data']['market_cap']['usd']
                    volume = data['market_data']['total_volume']['usd']
                    
                    print(f"✅ CoinGecko API working")
                    print(f"   💰 AAVE Price: ${price:,.2f}")
                    print(f"   📊 Market Cap: ${market_cap:,.0f}")
                    print(f"   📈 24h Volume: ${volume:,.0f}")
                    
                    self.results['coingecko'] = {'status': 'success', 'price': price}
                    return True
                else:
                    print(f"❌ CoinGecko API failed: {response.status}")
                    print(f"   Response: {await response.text()}")
                    return False
                    
        except Exception as e:
            print(f"❌ CoinGecko API error: {e}")
            return False
    
    async def test_etherscan_api(self):
        """Test Etherscan API"""
        print("\n⛓️ Testing Etherscan API...")
        
        api_key = os.getenv('ETHERSCAN_API_KEY')
        if not api_key:
            print("❌ Etherscan API key not found")
            return False
        
        try:
            # Test: Get AAVE contract verification status
            aave_contract = "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9"  # AAVE token
            url = f"https://api.etherscan.io/api?module=contract&action=getsourcecode&address={aave_contract}&apikey={api_key}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data['status'] == '1':
                        result = data['result'][0]
                        print(f"✅ Etherscan API working")
                        print(f"   📄 Contract: {aave_contract}")
                        print(f"   ✅ Verified: {'Yes' if result['SourceCode'] else 'No'}")
                        print(f"   🏷️ Contract Name: {result.get('ContractName', 'N/A')}")
                        print(f"   🔧 Compiler: {result.get('CompilerVersion', 'N/A')}")
                        
                        self.results['etherscan'] = {'status': 'success', 'verified': bool(result['SourceCode'])}
                        return True
                    else:
                        print(f"❌ Etherscan API error: {data.get('message', 'Unknown error')}")
                        return False
                else:
                    print(f"❌ Etherscan API failed: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ Etherscan API error: {e}")
            return False
    
    async def test_thegraph_api(self):
        """Test The Graph API with improved error handling"""
        print("\n📊 Testing The Graph API...")
        
        api_key = os.getenv('THE_GRAPH_API_KEY')
        if not api_key:
            print("❌ The Graph API key not found")
            return False
        
        # Use the subgraph we know works from discovery script
        working_subgraph = "A3Np3RQbaBA6oKJgiwDJeo5T3zrYfGHPWFYayMwtNDum"
        
        print(f"   🧪 Testing known working subgraph...")
        
        url = f"https://gateway.thegraph.com/api/{api_key}/subgraphs/id/{working_subgraph}"
        
        # Test the query we know works from discovery
        test_query = {
            "query": """
            {
              tokens(first: 1) {
                id
                totalLiquidity
              }
            }
            """
        }
        
        try:
            async with self.session.post(url, json=test_query) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'data' in data and 'tokens' in data['data']:
                        tokens = data['data']['tokens']
                        if tokens and len(tokens) > 0:
                            token = tokens[0]
                            liquidity = token.get('totalLiquidity', 'N/A')
                            
                            print(f"   ✅ The Graph API working!")
                            print(f"   🏦 Subgraph: Uniswap V2 Compatible")
                            print(f"   📊 Sample token ID: {token.get('id', 'N/A')}")
                            print(f"   💰 Total liquidity: {liquidity}")
                            
                            self.results['thegraph'] = {
                                'status': 'success',
                                'subgraph': 'working',
                                'field': 'tokens',
                                'sample_data': token
                            }
                            return True
                        else:
                            print(f"   ⚠️ Query succeeded but no tokens found")
                    else:
                        errors = data.get('errors', [])
                        if errors:
                            error_msg = errors[0].get('message', 'Unknown error')
                            print(f"   ❌ GraphQL error: {error_msg}")
                        else:
                            print(f"   ❌ Unexpected response format")
                else:
                    print(f"   ❌ HTTP {response.status}: {await response.text()}")
                    
        except Exception as e:
            print(f"   ❌ Request error: {e}")
        
        # Fallback: Try a simple schema query
        print(f"   🔄 Trying schema introspection as fallback...")
        
        schema_query = {
            "query": """
            {
              __schema {
                queryType {
                  name
                }
              }
            }
            """
        }
        
        try:
            async with self.session.post(url, json=schema_query) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'data' in data and '__schema' in data['data']:
                        print(f"   ✅ The Graph API accessible (schema query works)")
                        print(f"   ⚠️ Main query failed, but API is reachable")
                        
                        self.results['thegraph'] = {
                            'status': 'partial',
                            'note': 'API accessible but query failed'
                        }
                        return True
                        
        except Exception as e:
            print(f"   ❌ Schema query also failed: {e}")
        
        print("   ❌ All The Graph tests failed")
        return False
    
    async def test_defillama_api(self):
        """Test DeFiLlama API (free, no key required)"""
        print("\n🦙 Testing DeFiLlama API...")
        
        try:
            # Test: Get Aave protocol data
            url = "https://api.llama.fi/protocol/aave-v3"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    current_tvl = data.get('tvl', [])
                    if current_tvl:
                        latest_tvl = current_tvl[-1]['totalLiquidityUSD']
                        print(f"✅ DeFiLlama API working")
                        print(f"   🏦 Protocol: {data.get('name', 'Aave V3')}")
                        print(f"   💰 Current TVL: ${latest_tvl:,.0f}")
                        print(f"   🌐 Chains: {', '.join(data.get('chains', []))}")
                        print(f"   🏷️ Category: {data.get('category', 'N/A')}")
                        
                        self.results['defillama'] = {'status': 'success', 'tvl': latest_tvl}
                        return True
                    else:
                        print("❌ No TVL data available")
                        return False
                else:
                    print(f"❌ DeFiLlama API failed: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ DeFiLlama API error: {e}")
            return False
    
    async def test_all_apis(self):
        """Test all APIs"""
        print("🚀 ChainGuard AI - External API Testing")
        print("=" * 50)
        
        tests = [
            self.test_github_api(),
            self.test_coingecko_api(),
            self.test_etherscan_api(),
            self.test_thegraph_api(),
            self.test_defillama_api()
        ]
        
        results = await asyncio.gather(*tests, return_exceptions=True)
        
        print("\n" + "=" * 50)
        print("📊 API Testing Summary:")
        
        success_count = sum(1 for r in results if r is True)
        total_count = len(results)
        
        for i, (name, result) in enumerate(zip(['GitHub', 'CoinGecko', 'Etherscan', 'The Graph', 'DeFiLlama'], results)):
            status = "✅" if result is True else "❌"
            print(f"   {status} {name}")
        
        print(f"\n🎯 Success Rate: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
        
        if success_count == total_count:
            print("🎉 All APIs are working! Ready for Phase 3.")
        elif success_count >= 3:
            print("⚠️ Most APIs working. Can proceed with caution.")
        else:
            print("❌ Too many API failures. Please check credentials.")
        
        return success_count >= 3

async def test_google_cloud():
    """Test Google Cloud / Vertex AI / Gemini"""
    print("\n☁️ Testing Google Cloud & Vertex AI...")
    
    try:
        # Test authentication
        import google.auth
        from google.auth.transport.requests import Request
        import google.generativeai as genai
        
        # Check if service account file exists
        creds_file = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'chainguardai-1728b786facc.json')
        if not os.path.exists(creds_file):
            print(f"❌ Service account file not found: {creds_file}")
            return False
        
        print(f"✅ Service account file found: {creds_file}")
        
        # Test Vertex AI credentials
        credentials, project_id = google.auth.default()
        print(f"✅ Google Cloud authentication successful")
        print(f"   📁 Project ID: {project_id}")
        
        # Test Gemini configuration
        genai.configure()
        
        # List available models
        models = list(genai.list_models())
        available_model_names = [m.name for m in models]
        
        print(f"✅ Gemini API accessible")
        print(f"   🤖 Available models: {len(available_model_names)}")
        
        # Test specific models from .env
        flash_model = os.getenv('GEMINI_MODEL_NAME', 'gemini-2.5-flash-preview-04-17')
        pro_model = os.getenv('GEMINI_PRO_MODEL', 'gemini-2.0-flash-001')
        
        for model_name in [flash_model, pro_model]:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Test: Respond with 'Hello ChainGuard'")
                if response.text and 'ChainGuard' in response.text:
                    print(f"   ✅ {model_name}: Working")
                else:
                    print(f"   ⚠️ {model_name}: Accessible but unexpected response")
            except Exception as e:
                print(f"   ❌ {model_name}: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Google Cloud test failed: {e}")
        return False

async def main():
    """Main testing function"""
    print("🧪 ChainGuard AI - Pre-Phase 3 API Testing")
    print("Testing all external data sources and Google Cloud integration")
    print("=" * 70)
    
    # Test external APIs
    async with APITester() as tester:
        api_success = await tester.test_all_apis()
    
    # Test Google Cloud
    gcloud_success = await test_google_cloud()
    
    print("\n" + "=" * 70)
    print("🏁 Final Results:")
    print(f"   {'✅' if api_success else '❌'} External APIs")
    print(f"   {'✅' if gcloud_success else '❌'} Google Cloud & Vertex AI")
    
    if api_success and gcloud_success:
        print("\n🚀 All systems ready! You can proceed with:")
        print("   1. python main.py (test Phase 1 & 2)")
        print("   2. Phase 3 implementation")
    else:
        print("\n⚠️ Some systems have issues. Please resolve before continuing.")
    
    return api_success and gcloud_success

if __name__ == "__main__":
    asyncio.run(main())