# ChainGuard Risk Oracle Deployment Guide

This guide will walk you through deploying the ChainGuard Risk Oracle smart contract to the Avalanche blockchain.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Set Up Environment Variables

```bash
# Copy the example environment file
cp env.example .env

# Edit .env with your values
nano .env
```

### 3. Deploy to Fuji Testnet (Recommended for testing)

```bash
# Interactive deployment helper
npx hardhat run scripts/deploy-helper.ts

# Or direct deployment
npx hardhat run scripts/deploy.ts --network fuji
```

### 4. Deploy to Avalanche Mainnet

```bash
npx hardhat run scripts/deploy.ts --network avalanche
```

## 📋 Prerequisites

### Required

- **Node.js 18+** and npm
- **AVAX tokens** for gas fees (testnet faucet available)
- **Private key** for deployment account
- **Chainlink Functions subscription** (for production)

### Optional

- **SnowTrace API key** for contract verification
- **Custom RPC URL** for better performance

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Your private key (without 0x prefix)
PRIVATE_KEY=your_private_key_here

# Chainlink Functions Configuration
FUNCTIONS_ROUTER_ADDRESS=0x0000000000000000000000000000000000000000
DON_ID=0x0000000000000000000000000000000000000000000000000000000000000000
SUBSCRIPTION_ID=0

# Optional: Custom RPC URLs
AVALANCHE_RPC_URL=https://api.avax.network/ext/bc/C/rpc
FUJI_RPC_URL=https://api.avax-test.network/ext/bc/C/rpc

# Optional: SnowTrace API key for verification
SNOWTRACE_API_KEY=your_snowtrace_api_key_here
```

### Network Configuration

The deployment supports three networks:

| Network | Chain ID | RPC URL | Block Explorer |
|---------|----------|---------|----------------|
| Fuji Testnet | 43113 | <https://api.avax-test.network/ext/bc/C/rpc> | <https://testnet.snowtrace.io> |
| Avalanche Mainnet | 43114 | <https://api.avax.network/ext/bc/C/rpc> | <https://snowtrace.io> |
| Local Hardhat | 31337 | <http://localhost:8545> | N/A |

## 🚀 Deployment Methods

### Method 1: Interactive Helper (Recommended)

The interactive helper guides you through the deployment process:

```bash
npx hardhat run scripts/deploy-helper.ts
```

This will:

- Prompt for missing configuration
- Let you choose the network
- Confirm deployment settings
- Run deployment
- Optionally verify the contract

### Method 2: Direct Deployment

Deploy directly with environment variables:

```bash
# Testnet
npx hardhat run scripts/deploy.ts --network fuji

# Mainnet
npx hardhat run scripts/deploy.ts --network avalanche

# Local
npx hardhat run scripts/deploy.ts --network hardhat
```

### Method 3: Manual Deployment

For advanced users, you can deploy manually:

```bash
# Compile contracts
npx hardhat compile

# Deploy with specific parameters
npx hardhat run scripts/deploy.ts --network fuji
```

## 🔍 Contract Verification

### Automatic Verification

The deployment script can automatically verify your contract:

```bash
# During interactive deployment, choose 'y' when prompted
# Or run verification separately:
npx hardhat run scripts/verify.ts --network fuji
```

### Manual Verification

If automatic verification fails, you can verify manually on SnowTrace:

1. Go to [SnowTrace](https://snowtrace.io) (or testnet.snowtrace.io for Fuji)
2. Search for your contract address
3. Click "Contract" tab
4. Click "Verify and Publish"
5. Fill in the verification form with:
   - Contract address
   - Compiler version: 0.8.19
   - Constructor arguments (from deployment output)

## 📊 Deployment Output

After successful deployment, you'll see:

```
🚀 Starting ChainGuard Risk Oracle deployment...

📋 Deploying contracts with account: 0x...
💰 Account balance: 1.234 AVAX

📝 Deployment Configuration:
   Functions Router: 0x...
   DON ID: 0x...
   Subscription ID: 123
   Gas Limit: 300000

🔨 Deploying ChainGuard Risk Oracle...
⏳ Waiting for deployment confirmation...
✅ ChainGuard Risk Oracle deployed to: 0x...

🔍 Verifying deployment...
✅ Contract verification successful

📄 Deployment information saved to: deployments/fuji.json

🎉 Deployment completed successfully!

📋 Next Steps:
1. Update the contract address in frontend/src/contracts/config.ts
2. Configure Chainlink Functions secrets
3. Test the contract integration

🔗 Contract on SnowTrace:
   https://testnet.snowtrace.io/address/0x...
```

## 🔗 Chainlink Functions Setup

### 1. Create Subscription

1. Go to [Chainlink Functions](https://functions.chain.link/)
2. Create a new subscription
3. Fund it with LINK tokens

### 2. Get Configuration

From your subscription, get:

- **Functions Router Address**
- **DON ID**
- **Subscription ID**

### 3. Set Secrets

In your Chainlink Functions subscription, set:

- `chainguardApiKey`: Your ChainGuard AI service API key

### 4. Update Contract

Update your deployment configuration with the Chainlink values.

## 🧪 Testing

### 1. Test Deployment

```bash
# Run tests
npx hardhat test

# Test on local network
npx hardhat node
npx hardhat run scripts/deploy.ts --network hardhat
```

### 2. Test Contract Functions

After deployment, test the contract:

```bash
# Request a risk assessment
npx hardhat console --network fuji
> const contract = await ethers.getContractAt("ChainGuardRiskOracle", "DEPLOYED_ADDRESS")
> await contract.requestRiskAssessment("aave-v3")
```

## 🚨 Troubleshooting

### Common Issues

#### "Insufficient funds"

- Ensure your account has enough AVAX for gas fees
- Get testnet AVAX from [Avalanche Faucet](https://faucet.avax.network/)

#### "Contract deployment failed"

- Check your private key format (no 0x prefix)
- Verify RPC URL is accessible
- Ensure gas limit is sufficient

#### "Verification failed"

- Check constructor arguments match deployment
- Verify compiler version is 0.8.19
- Ensure SnowTrace API key is valid

#### "Chainlink Functions not found"

- Verify Functions Router address is correct
- Check if Chainlink Functions are available on Avalanche
- Ensure subscription is properly configured

### Debug Mode

Enable debug logging:

```bash
DEBUG=hardhat:* npx hardhat run scripts/deploy.ts --network fuji
```

### Gas Optimization

If deployment fails due to gas, try:

```bash
# Increase gas limit
GAS_LIMIT=500000 npx hardhat run scripts/deploy.ts --network fuji

# Or set gas price
GAS_PRICE=30000000000 npx hardhat run scripts/deploy.ts --network fuji
```

## 📁 Deployment Files

After deployment, these files are created:

- `deployments/fuji.json` - Fuji testnet deployment info
- `deployments/avalanche.json` - Mainnet deployment info
- `artifacts/` - Compiled contract artifacts

## 🔄 Updating Frontend

After deployment, update your frontend configuration:

```typescript
// frontend/src/contracts/config.ts
export const CONTRACT_ADDRESSES = {
  riskOracle: 'YOUR_DEPLOYED_CONTRACT_ADDRESS' as const,
};
```

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify your configuration matches the examples
3. Check the deployment logs for specific error messages
4. Ensure you're using the correct network and addresses

## 🎯 Production Checklist

Before going to production:

- [ ] Contract deployed to Avalanche mainnet
- [ ] Contract verified on SnowTrace
- [ ] Chainlink Functions subscription configured
- [ ] API secrets set in Chainlink Functions
- [ ] Frontend updated with contract address
- [ ] Gas fees tested and optimized
- [ ] Error handling implemented
- [ ] Monitoring set up
