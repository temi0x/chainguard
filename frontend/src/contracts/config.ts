import { riskOracleABI } from './riskOracleABI';

// Avalanche Network Configuration
export const AVALANCHE_NETWORK = {
    chainId: 43114,
    name: 'Avalanche C-Chain',
    nativeCurrency: {
        name: 'AVAX',
        symbol: 'AVAX',
        decimals: 18,
    },
    rpcUrls: {
        default: {
            http: ['https://api.avax.network/ext/bc/C/rpc'],
        },
        public: {
            http: ['https://api.avax.network/ext/bc/C/rpc'],
        },
    },
    blockExplorers: {
        default: {
            name: 'SnowTrace',
            url: 'https://snowtrace.io',
        },
    },
} as const;

// Contract addresses (replace with actual deployed addresses)
export const CONTRACT_ADDRESSES = {
    // Use environment variable or fallback to zero address
    riskOracle: import.meta.env.VITE_CONTRACT_ADDRESS || '0x0000000000000000000000000000000000000000',
} as const;

// Contract configuration
export const CONTRACT_CONFIG = {
    riskOracle: {
        address: CONTRACT_ADDRESSES.riskOracle,
        abi: riskOracleABI,
    },
} as const;

// Chainlink Functions configuration for Avalanche
export const CHAINLINK_CONFIG = {
    // Replace with actual Chainlink Functions router address on Avalanche
    functionsRouter: '0x0000000000000000000000000000000000000000' as const,
    // Replace with actual DON ID
    donId: '0x0000000000000000000000000000000000000000000000000000000000000000' as const,
    // Replace with actual subscription ID
    subscriptionId: 0n,
} as const; 