#!/usr/bin/env python3
"""
The Graph API Discovery Script - Smart Version
Find working subgraphs and query structures with intelligent ID handling
"""

import asyncio
import aiohttp
import json

class TheGraphDiscovery:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = None
        self.discovered_ids = {}  # Store IDs we find for testing singular fields
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def discover_schema(self, subgraph_id: str):
        """Discover the schema of a subgraph"""
        print(f"\n🔍 Discovering schema for {subgraph_id[:12]}...")
        
        url = f"https://gateway.thegraph.com/api/{self.api_key}/subgraphs/id/{subgraph_id}"
        
        # Schema introspection query
        query = {
            "query": """
            {
              __schema {
                queryType {
                  fields {
                    name
                    description
                    type {
                      name
                      kind
                    }
                  }
                }
              }
            }
            """
        }
        
        try:
            async with self.session.post(url, json=query) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'data' in data and '__schema' in data['data']:
                        fields = data['data']['__schema']['queryType']['fields']
                        print(f"✅ Schema discovered! Available fields:")
                        
                        # Look for common DeFi fields and categorize them SMARTLY
                        plural_fields = []
                        singular_fields = []
                        
                        for field in fields:
                            name = field.get('name')
                            if name and any(keyword in name.lower() for keyword in 
                                   ['protocol', 'market', 'pool', 'reserve', 'vault', 'token']):
                                
                                # IMPROVED: Better plural/singular detection
                                is_plural = (
                                    (name.endswith('s') and not name.endswith('Data') and not name.endswith('Status'))  # tokens, pools, etc.
                                    or name.endswith('Datas')  # tokenDayDatas, etc.
                                    or name.endswith('ies')    # companies, etc.
                                )
                                
                                if is_plural:
                                    plural_fields.append(name)
                                    print(f"   📊 {name} (plural)")
                                else:
                                    singular_fields.append(name)
                                    print(f"   🔍 {name} (singular)")
                        
                        return plural_fields, singular_fields
                    else:
                        print(f"❌ Schema query failed: {data}")
                        return [], []
                else:
                    print(f"❌ HTTP {response.status}: {await response.text()}")
                    return [], []
        except Exception as e:
            print(f"❌ Error: {e}")
            return [], []
    
    async def test_plural_field(self, subgraph_id: str, field_name: str):
        """Test plural fields and collect IDs for singular field testing"""
        print(f"\n🧪 Testing plural field '{field_name}'...")
        
        url = f"https://gateway.thegraph.com/api/{self.api_key}/subgraphs/id/{subgraph_id}"
        
        # Test query for plural fields
        query = {
            "query": f"""
            {{
              {field_name}(first: 3) {{
                id
              }}
            }}
            """
        }
        
        try:
            async with self.session.post(url, json=query) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'data' in data and data['data'] is not None and field_name in data['data']:
                        result = data['data'][field_name]
                        if result:
                            print(f"   ✅ {field_name} works! Found {len(result)} items")
                            
                            # Collect IDs for testing singular fields
                            ids_found = []
                            for item in result:
                                if item is not None and isinstance(item, dict) and 'id' in item:
                                    item_id = item['id']
                                    ids_found.append(item_id)
                                    print(f"   📝 Sample ID: {item_id}")
                            
                            # Store IDs for singular field testing
                            if ids_found:
                                self.discovered_ids[field_name] = ids_found
                            
                            return True
                        else:
                            print(f"   ⚠️ {field_name} exists but returned empty")
                            return False
                    else:
                        errors = data.get('errors', [])
                        if errors and len(errors) > 0:
                            error_msg = errors[0].get('message', 'Unknown error')
                            print(f"   ❌ {field_name} failed: {error_msg}")
                        else:
                            print(f"   ❌ {field_name} failed: No data returned")
                        return False
                else:
                    print(f"   ❌ HTTP {response.status}")
                    return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    async def test_singular_field_with_id(self, subgraph_id: str, field_name: str, test_id: str):
        """Test singular fields using discovered IDs"""
        print(f"\n🔍 Testing singular field '{field_name}' with ID...")
        
        url = f"https://gateway.thegraph.com/api/{self.api_key}/subgraphs/id/{subgraph_id}"
        
        # Test query for singular field with ID
        query = {
            "query": f"""
            {{
              {field_name}(id: "{test_id}") {{
                id
              }}
            }}
            """
        }
        
        try:
            async with self.session.post(url, json=query) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'data' in data and data['data'] is not None and field_name in data['data']:
                        result = data['data'][field_name]
                        if result:
                            print(f"   ✅ {field_name}(id: \"{test_id[:20]}...\") works!")
                            print(f"   📝 Retrieved ID: {result.get('id', 'N/A')}")
                            return True
                        else:
                            print(f"   ⚠️ {field_name} with ID '{test_id[:20]}...' returned null")
                            return False
                    else:
                        errors = data.get('errors', [])
                        if errors and len(errors) > 0:
                            error_msg = errors[0].get('message', 'Unknown error')
                            print(f"   ❌ {field_name} failed: {error_msg}")
                        else:
                            print(f"   ❌ {field_name} failed: No data returned")
                        return False
                else:
                    print(f"   ❌ HTTP {response.status}")
                    return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    async def find_tvl_data(self, subgraph_id: str, working_field: str):
        """Find TVL or similar financial data in a working field"""
        print(f"\n💰 Looking for TVL data in '{working_field}'...")
        
        url = f"https://gateway.thegraph.com/api/{self.api_key}/subgraphs/id/{subgraph_id}"
        
        # Try different TVL field variations
        tvl_variants = [
            "totalValueLockedUSD",
            "totalValueLocked", 
            "tvlUSD",
            "tvl",
            "totalSupplyUSD",
            "totalDepositsUSD",
            "liquidityUSD",
            "totalLiquidity",
            "totalSupply",
            "balance",
            "amount",
            "volume",
            "volumeUSD"
        ]
        
        for tvl_field in tvl_variants:
            query = {
                "query": f"""
                {{
                  {working_field}(first: 1) {{
                    id
                    {tvl_field}
                  }}
                }}
                """
            }
            
            try:
                async with self.session.post(url, json=query) as response:
                    if response.status == 200:
                        data = await response.json()
                        if ('data' in data and data['data'] is not None and 
                            working_field in data['data'] and data['data'][working_field]):
                            
                            items = data['data'][working_field]
                            if items and len(items) > 0:
                                item = items[0]
                                if item is not None and isinstance(item, dict) and tvl_field in item and item[tvl_field] is not None:
                                    value = item[tvl_field]
                                    print(f"   ✅ Found {tvl_field}: {value}")
                                    return tvl_field
                        
            except Exception as e:
                continue
        
        print(f"   ⚠️ No TVL data found in {working_field}")
        return None

async def main():
    """Main discovery function with smart ID handling"""
    api_key = "062651607a7ca538bfebb9729b7c759c"
    
    # Test the subgraph that's working
    working_subgraph = "A3Np3RQbaBA6oKJgiwDJeo5T3zrYfGHPWFYayMwtNDum"
    
    print("🔍 The Graph API Discovery Tool - Smart Version")
    print("Testing your Uniswap V2 subgraph with intelligent ID handling")
    print("=" * 60)
    
    async with TheGraphDiscovery(api_key) as discovery:
        # Step 1: Discover schema and categorize fields
        plural_fields, singular_fields = await discovery.discover_schema(working_subgraph)
        
        if not plural_fields and not singular_fields:
            print("\n❌ Could not discover schema. Trying common field names...")
            # Fallback
            plural_fields = ["tokens", "tokenDayDatas", "markets", "reserves", "pools"]
            singular_fields = ["token", "tokenDayData", "market", "reserve", "pool"]
        
        # Step 2: Test plural fields first (to get IDs)
        print(f"\n📊 Testing plural fields (these usually work without IDs)...")
        working_plural_fields = []
        
        for field in plural_fields:
            if await discovery.test_plural_field(working_subgraph, field):
                working_plural_fields.append(field)
        
        # Step 3: Test singular fields using discovered IDs
        print(f"\n🔍 Testing singular fields (using discovered IDs)...")
        working_singular_fields = []
        
        for singular_field in singular_fields:
            # Find related plural field that might have IDs
            test_id = None
            
            # IMPROVED: Better ID matching logic
            for plural_field, ids in discovery.discovered_ids.items():
                # Direct match: token -> tokens, tokenDayData -> tokenDayDatas
                if (singular_field + 's' == plural_field or 
                    singular_field + 'Datas' == plural_field or
                    singular_field.replace('Data', 'Datas') == plural_field):
                    test_id = ids[0] if ids else None
                    print(f"   🔗 Using ID from related field '{plural_field}': {test_id[:20]}...")
                    break
            
            if test_id:
                if await discovery.test_singular_field_with_id(working_subgraph, singular_field, test_id):
                    working_singular_fields.append(singular_field)
            else:
                print(f"\n🔍 Testing singular field '{singular_field}'...")
                print(f"   ⚠️ No related IDs found - skipping (would need specific ID)")
        
        # Step 4: Find TVL data in working fields
        all_working_fields = working_plural_fields + working_singular_fields
        
        if all_working_fields:
            print(f"\n🎉 Found {len(all_working_fields)} working fields!")
            print(f"   📊 Plural fields: {working_plural_fields}")
            print(f"   🔍 Singular fields: {working_singular_fields}")
            
            # Look for TVL data in plural fields (they're more useful for data extraction)
            tvl_found = False
            for field in working_plural_fields:
                tvl_field = await discovery.find_tvl_data(working_subgraph, field)
                if tvl_field:
                    print(f"\n🎯 WORKING QUERY:")
                    print(f"""
curl -X POST \\
     -H "Content-Type: application/json" \\
     -d '{{"query":"{{ {field}(first: 5) {{ id {tvl_field} }} }}"}}' \\
     "https://gateway.thegraph.com/api/{api_key}/subgraphs/id/{working_subgraph}"
                    """)
                    tvl_found = True
                    break
            
            if not tvl_found:
                print(f"\n⚠️ Working fields found but no TVL data discovered.")
                print(f"You can still use these fields for other data:")
                for field in all_working_fields:
                    print(f"   - {field}")
        else:
            print("\n❌ No working fields found. The subgraph may not be compatible.")
    
    print("\n" + "=" * 60)
    if all_working_fields:
        print("✅ Discovery complete! Your subgraph is working perfectly.")
        print(f"📈 Summary: {len(working_plural_fields)} plural fields, {len(working_singular_fields)} singular fields")
    else:
        print("❌ Discovery failed. Try a different subgraph.")

if __name__ == "__main__":
    asyncio.run(main())