import { http, createConfig } from 'wagmi';
import { avalanche } from 'wagmi/chains';
import { injected, metaMask } from 'wagmi/connectors';

// Configure chains & providers - simplified without WalletConnect for now
export const config = createConfig({
    chains: [avalanche],
    transports: {
        [avalanche.id]: http(),
    },
    connectors: [
        injected(),
        metaMask(),
    ],
}); 