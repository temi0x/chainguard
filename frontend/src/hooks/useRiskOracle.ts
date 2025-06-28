import { useState, useCallback } from 'react';
import { useAccount, useReadContract, useWriteContract } from 'wagmi';
import { CONTRACT_CONFIG } from '../contracts/config';

export interface RiskAssessment {
    riskScore: bigint;
    confidence: bigint;
    lastUpdated: bigint;
    explanation: string;
    componentScores: readonly [bigint, bigint, bigint, bigint];
}

export interface RiskScore {
    riskScore: bigint;
    confidence: bigint;
    lastUpdated: bigint;
}

export const useRiskOracle = () => {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const { address, isConnected } = useAccount();

    // Contract write for requesting risk assessment
    const {
        data: requestData,
        writeContract,
        isPending: isRequestPending,
        error: requestError,
    } = useWriteContract();

    // Function to request risk assessment
    const requestAssessment = useCallback(
        async (protocolName: string) => {
            if (!isConnected) {
                setError('Please connect your wallet first');
                return null;
            }

            try {
                setIsLoading(true);
                setError(null);

                const result = await writeContract({
                    ...CONTRACT_CONFIG.riskOracle,
                    functionName: 'requestRiskAssessment',
                    args: [protocolName],
                });

                return result;
            } catch (err) {
                const errorMessage = err instanceof Error ? err.message : 'Failed to request risk assessment';
                setError(errorMessage);
                return null;
            } finally {
                setIsLoading(false);
            }
        },
        [isConnected, writeContract]
    );

    // Helper function to format risk score
    const formatRiskScore = useCallback((riskScore: bigint): number => {
        // Convert from basis points (0-10000) to percentage (0-100)
        return Number(riskScore) / 100;
    }, []);

    // Helper function to format confidence
    const formatConfidence = useCallback((confidence: bigint): number => {
        // Convert from basis points (0-10000) to percentage (0-100)
        return Number(confidence) / 100;
    }, []);

    return {
        // State
        isLoading: isLoading || isRequestPending,
        error: error || (requestError?.message ?? null),
        isTransactionSuccess: !!requestData,

        // Functions
        requestAssessment,
        formatRiskScore,
        formatConfidence,

        // Contract state
        isConnected,
        address,
    };
};

// Separate hook for reading risk scores
export const useRiskScore = (protocolName: string) => {
    const { data, isLoading, error } = useReadContract({
        ...CONTRACT_CONFIG.riskOracle,
        functionName: 'getRiskScore',
        args: [protocolName],
        query: {
            enabled: !!protocolName,
        },
    });

    return {
        data: data ? {
            riskScore: data[0],
            confidence: data[1],
            lastUpdated: data[2],
        } : null,
        isLoading,
        error,
    };
};

// Separate hook for reading risk breakdown
export const useRiskBreakdown = (protocolName: string) => {
    const { data, isLoading, error } = useReadContract({
        ...CONTRACT_CONFIG.riskOracle,
        functionName: 'getRiskBreakdown',
        args: [protocolName],
        query: {
            enabled: !!protocolName,
        },
    });

    return {
        data: data ? {
            riskScore: data[0],
            confidence: data[1],
            componentScores: data[2],
            explanation: data[3],
        } : null,
        isLoading,
        error,
    };
}; 