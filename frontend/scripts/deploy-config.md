# ChainGuard Risk Oracle Deployment Guide

## Prerequisites

1. **Avalanche Network Setup**
   - Ensure you have AVAX tokens for gas fees
   - Configure your wallet for Avalanche C-Chain (Chain ID: 43114)

2. **Chainlink Functions Setup**
   - Create a Chainlink Functions subscription
   - Get your DON ID and Functions Router address
   - Set up the `chainguardApiKey` secret

## Deployment Steps

### 1. Deploy the Smart Contract

```bash
# Navigate to the contracts directory
cd ../contracts

# Install dependencies
npm install

# Compile the contract
npx hardhat compile

# Deploy to Avalanche (replace with your actual values)
npx hardhat run scripts/deploy.js --network avalanche
```

### 2. Update Frontend Configuration

After deployment, update the following files:

#### `src/contracts/config.ts`

```typescript
export const CONTRACT_ADDRESSES = {
  riskOracle: 'YOUR_DEPLOYED_CONTRACT_ADDRESS' as const,
};

export const CHAINLINK_CONFIG = {
  functionsRouter: 'YOUR_CHAINLINK_FUNCTIONS_ROUTER_ADDRESS',
  donId: 'YOUR_DON_ID',
  subscriptionId: YOUR_SUBSCRIPTION_ID,
};
```

### 3. Environment Variables

Create a `.env` file in the frontend root:

```env
VITE_WALLET_CONNECT_PROJECT_ID=your_wallet_connect_project_id
VITE_CONTRACT_ADDRESS=your_deployed_contract_address
```

## Chainlink Functions Configuration

### 1. Create Subscription

1. Go to [Chainlink Functions](https://functions.chain.link/)
2. Create a new subscription
3. Fund it with LINK tokens

### 2. Set Secrets

Set the following secret in your Chainlink Functions subscription:

- `chainguardApiKey`: Your ChainGuard AI service API key

### 3. Update JavaScript Source

The contract constructor includes the JavaScript source code, but you may need to update the API URL to your production endpoint.

## Testing the Integration

1. **Start the Frontend**

   ```bash
   npm run dev
   ```

2. **Navigate to Contract Page**
   - Go to `http://localhost:5173/contract`

3. **Test Wallet Connection**
   - Connect your MetaMask wallet
   - Ensure it's on Avalanche C-Chain

4. **Test Risk Assessment**
   - Enter a protocol name (e.g., "aave-v3")
   - Click "Request Assessment"
   - Confirm the transaction

5. **Monitor the Process**
   - Check the transaction on SnowTrace
   - Monitor Chainlink Functions logs
   - Wait for the assessment to complete

## Troubleshooting

### Contract Deployment Issues

- Ensure you have enough AVAX for gas fees
- Verify the constructor parameters are correct
- Check that Chainlink Functions are available on Avalanche

### Frontend Integration Issues

- Verify the contract address is correct
- Ensure the ABI matches the deployed contract
- Check that your wallet is connected to Avalanche C-Chain

### Chainlink Functions Issues

- Verify your subscription is funded
- Check that the secret is properly set
- Ensure the API endpoint is accessible

## Production Checklist

- [ ] Contract deployed to Avalanche mainnet
- [ ] Contract address updated in frontend config
- [ ] Chainlink Functions subscription configured
- [ ] API secrets set in Chainlink Functions
- [ ] Frontend deployed and accessible
- [ ] Wallet connection tested
- [ ] Risk assessment flow tested
- [ ] Error handling verified
- [ ] Performance monitoring set up
