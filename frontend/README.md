# ChainGuard Risk Oracle Frontend Integration

This frontend application integrates with the ChainGuard Risk Oracle smart contract deployed on the Avalanche blockchain. It provides a user interface for requesting risk assessments and viewing protocol risk scores.

## Features

- **Wallet Integration**: Connect MetaMask or other Web3 wallets
- **Risk Assessment Requests**: Request new risk assessments for DeFi protocols
- **Real-time Data**: View current risk scores and detailed breakdowns
- **Avalanche Network**: Built specifically for Avalanche C-Chain
- **Chainlink Functions**: Integrates with Chainlink Functions for off-chain data

## Prerequisites

- Node.js 18+ and npm
- MetaMask or compatible Web3 wallet
- Avalanche C-Chain network configured in your wallet
- Deployed ChainGuard Risk Oracle contract on Avalanche

## Setup Instructions

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Contract Address

Update the contract address in `src/contracts/config.ts`:

```typescript
export const CONTRACT_ADDRESSES = {
  riskOracle: 'YOUR_DEPLOYED_CONTRACT_ADDRESS' as const,
};
```

### 3. Configure Chainlink Functions

Update the Chainlink configuration in `src/contracts/config.ts`:

```typescript
export const CHAINLINK_CONFIG = {
  functionsRouter: 'YOUR_CHAINLINK_FUNCTIONS_ROUTER_ADDRESS',
  donId: 'YOUR_DON_ID',
  subscriptionId: YOUR_SUBSCRIPTION_ID,
};
```

### 4. Environment Variables

Create a `.env` file in the root directory:

```env
VITE_REOWN_PROJECT_ID=your_reown_project_id
```

### 5. Start Development Server

```bash
npm run dev
```

## Usage

### 1. Connect Wallet

1. Navigate to `/contract` in your browser
2. Click "Connect Wallet" to connect your MetaMask or other Web3 wallet
3. Ensure your wallet is connected to Avalanche C-Chain

### 2. Request Risk Assessment

1. Enter a protocol name (e.g., "aave-v3", "uniswap-v3")
2. Click "Request Assessment"
3. Confirm the transaction in your wallet
4. Wait for the Chainlink Functions to process the request

### 3. View Risk Data

- **Current Risk Score**: View the latest risk score for a protocol
- **Risk Breakdown**: See detailed component scores (Security, Financial, Governance, Data Quality)
- **Transaction Status**: Monitor the status of your assessment requests

## Contract Integration

### Smart Contract Functions

The frontend integrates with the following contract functions:

- `requestRiskAssessment(string protocol)`: Request a new risk assessment
- `getRiskScore(string protocol)`: Get basic risk information
- `getRiskBreakdown(string protocol)`: Get detailed risk breakdown

### Events

The application listens for these contract events:

- `RiskAssessmentRequested`: Emitted when a new assessment is requested
- `RiskAssessmentUpdated`: Emitted when an assessment is completed

## Network Configuration

### Avalanche C-Chain

- **Chain ID**: 43114
- **RPC URL**: <https://api.avax.network/ext/bc/C/rpc>
- **Block Explorer**: <https://snowtrace.io>
- **Native Token**: AVAX

### Supported Wallets

- MetaMask
- Reown (formerly WalletConnect)
- Injected wallets

## Development

### Project Structure

```
src/
├── components/
│   └── ContractIntegration.tsx    # Main contract integration component
├── contracts/
│   ├── config.ts                  # Contract configuration
│   └── riskOracleABI.ts          # Contract ABI
├── hooks/
│   └── useRiskOracle.ts          # Custom hooks for contract interaction
└── config/
    └── wagmi.ts                  # Wagmi configuration
```

### Custom Hooks

- `useRiskOracle()`: Main hook for contract interactions
- `useRiskScore(protocolName)`: Hook for reading risk scores
- `useRiskBreakdown(protocolName)`: Hook for reading detailed breakdowns

### Adding New Features

1. **New Contract Functions**: Add to the ABI in `riskOracleABI.ts`
2. **New Hooks**: Create in the `hooks/` directory
3. **New Components**: Add to the `components/` directory
4. **New Routes**: Add to `App.tsx`

## Troubleshooting

### Common Issues

1. **"Contract not found"**: Ensure the contract address is correct and the contract is deployed
2. **"Network not supported"**: Make sure your wallet is connected to Avalanche C-Chain
3. **"Transaction failed"**: Check if you have enough AVAX for gas fees
4. **"Functions request failed"**: Verify Chainlink Functions configuration

### Debug Mode

Enable debug logging by setting the environment variable:

```env
VITE_DEBUG=true
```

## Deployment

### Build for Production

```bash
npm run build
```

### Deploy to Vercel

1. Connect your repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main branch

### Environment Variables for Production

- `VITE_REOWN_PROJECT_ID`: Your Reown project ID
- `VITE_CONTRACT_ADDRESS`: Your deployed contract address
- `VITE_CHAINLINK_FUNCTIONS_ROUTER`: Chainlink Functions router address

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details
