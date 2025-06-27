# Mock API Documentation for On-Chain Integration Development

This document provides the expected request and response formats for the key external data sources our multi-agent system will query.

The final deployed multi-agent system on Cloud Run will handle the complex logic of calling these APIs, but your integration can be built with these mock structures for now.

---

### 1. DeFiLlama API (Financial Health)

**Purpose:** fetch core financial metrics like Total Value Locked (TVL)

**Mock Endpoint:** `GET https://api.llama.fi/protocol/{protocol_slug}`

**Request:**
- simple HTTP `GET` request. The `{protocol_slug}` is the unique ID for the protocol.
- **Example:** `GET https://api.llama.fi/protocol/aave-v2`

**Success Response (200 OK) - JSON Payload:**
```json
{
  "id": "13",
  "name": "Aave V2",
  "symbol": "AAVE",
  "chain": "Ethereum",
  "tvl": 3540123456.78,
  "chainTvls": {
    "Ethereum": 3100123456.78,
    "Polygon": 400000000.00,
    "Avalanche": 40000000.00
  },
  "slug": "aave-v2",
  "url": "https://aave.com/"
}
```

**Key Fields for On-Chain Logic:**
- `tvl` (number): The total value locked across all chains.
- `chainTvls.Ethereum` (number): The TVL on a specific chain, which might be more relevant depending on the context.

---

### 2. GitHub API (Development Activity & Security)

**Purpose:** Assess the ongoing development activity and find audit reports, which are indicators of project health and security posture.

**Mock Endpoint:** `GET https://api.github.com/repos/{owner}/{repo}/audits`
*(Note: This is a conceptual endpoint. In reality, the agent would search the repo, but this mock simplifies it.)*

**Request:**
- HTTP `GET` request to a conceptual endpoint for fetching audit info.
- **Example:** `GET https://api.github.com/repos/aave/aave-v3-core/audits`

**Success Response (200 OK) - JSON Payload:**
```json
{
  "repository": "aave/aave-v3-core",
  "last_commit_date": "2023-10-26T12:00:00Z",
  "recent_commit_count_30d": 45,
  "audits": [
    {
      "firm": "OpenZeppelin",
      "date": "2023-01-15",
      "report_url": "https://.../openzeppelin_audit.pdf",
      "summary": "No critical vulnerabilities found."
    },
    {
      "firm": "Trail of Bits",
      "date": "2023-02-20",
      "report_url": "https://.../trailofbits_audit.pdf",
      "summary": "Two high-severity issues identified and fixed."
    }
  ],
  "audit_count": 2
}
```

**Key Fields for On-Chain Logic:**
- `audit_count` (integer): A simple, quantifiable metric for security diligence.
- `recent_commit_count_30d` (integer): A measure of recent development activity.

---

### 3. The Graph (On-Chain Protocol State)

**Purpose:** To query detailed, indexed on-chain data like total borrows, supply, user positions, etc., without hitting an RPC node directly.

**Mock Endpoint:** `POST https://api.thegraph.com/subgraphs/name/aave/protocol-v3`

**Request:**
- An HTTP `POST` request with a GraphQL query in the body.

**Request Body (GraphQL Query):**
```graphql
{
  "query": "{ aaveProtocol(id: \\"1\\") { totalValueLockedUSD totalBorrowsUSD } }"
}
```

**Success Response (200 OK) - JSON Payload:**
```json
{
  "data": {
    "aaveProtocol": {
      "totalValueLockedUSD": "4512345678.90",
      "totalBorrowsUSD": "1234567890.12"
    }
  }
}
```

**Key Fields for On-Chain Logic:**
- `data.aaveProtocol.totalValueLockedUSD` (string number): The protocol's TVL according to the subgraph.
- `data.aaveProtocol.totalBorrowsUSD` (string number): The total amount borrowed, a key health indicator.

---

### 4. CoinGecko API (Market Data)

**Purpose:** To retrieve token market data such as price, trading volume, and liquidity, which are essential for assessing market risk and stability.

**Mock Endpoint:** `GET https://api.coingecko.com/api/v3/coins/{id}`

**Request:**
- A simple HTTP `GET` request. The `{id}` is CoinGecko's unique identifier for the asset.
- **Example:** `GET https://api.coingecko.com/api/v3/coins/aave`

**Success Response (200 OK) - JSON Payload:**
```json
{
  "id": "aave",
  "symbol": "aave",
  "name": "Aave",
  "market_cap_rank": 50,
  "liquidity_score": 75.8,
  "market_data": {
    "current_price": {
      "usd": 85.50
    },
    "total_volume": {
      "usd": 50123456
    },
    "market_cap": {
      "usd": 1282500000
    }
  }
}
```

**Key Fields for On-Chain Logic:**
- `liquidity_score` (number): A crucial metric for assessing how easily an asset can be traded without significant price impact.
- `market_data.total_volume.usd` (number): Represents recent trading interest and activity.
- `market_cap_rank` (integer): A proxy for how established and significant the token is in the broader market.

---

### 5. Etherscan API (Contract Verification)

**Purpose:** To directly verify smart contract integrity, most importantly checking if the source code is publicly verified on-chain.

**Mock Endpoint:** `GET https://api.etherscan.io/api?module=contract&action=getsourcecode&address={contract_address}`

**Request:**
- An HTTP `GET` request with query parameters.
- **Example:** `GET https://api.etherscan.io/api?module=contract&action=getsourcecode&address=0x87870Bca3F3fD6036b8D4ce8303D71e081e3637e`

**Success Response (200 OK) - JSON Payload:**
```json
{
  "status": "1",
  "message": "OK",
  "result": [
    {
      "SourceCode": "[... Full Solidity Source Code ...]",
      "ABI": "[... Contract ABI ...]",
      "ContractName": "AaveV3Pool",
      "CompilerVersion": "v0.8.10+commit.fc410830",
      "Proxy": "0",
      "Implementation": ""
    }
  ]
}
```

**Key Fields for On-Chain Logic:**
- `is_verified` (boolean): This is a **derived metric**. The agent determines this by checking if `result[0].SourceCode` is empty or not. For your testing, you can represent this as a simple boolean value (`true` or `false`). A verified contract is a fundamental sign of transparency and security.