import { Protocol, RiskBreakdown, AgentInsight, Alert } from '../types';

export const mockProtocols: Protocol[] = [
  {
    id: 'aave-v3',
    name: 'Aave',
    symbol: 'AAVE',
    logo: 'https://cryptologos.cc/logos/aave-aave-logo.png',
    category: 'Lending',
    tvl: 5740000000,
    riskScore: 15,
    riskCategory: 'Low',
    lastUpdated: new Date(Date.now() - 3600000).toISOString(),
    confidenceLevel: 92,
  },
  {
    id: 'uniswap-v3',
    name: 'Uniswap',
    symbol: 'UNI',
    logo: 'https://cryptologos.cc/logos/uniswap-uni-logo.png',
    category: 'DEX',
    tvl: 3750000000,
    riskScore: 22,
    riskCategory: 'Low',
    lastUpdated: new Date(Date.now() - 7200000).toISOString(),
    confidenceLevel: 89,
  },
  {
    id: 'curve-finance',
    name: 'Curve Finance',
    symbol: 'CRV',
    logo: 'https://cryptologos.cc/logos/curve-dao-token-crv-logo.png',
    category: 'DEX',
    tvl: 1620000000,
    riskScore: 30,
    riskCategory: 'Medium',
    lastUpdated: new Date(Date.now() - 1800000).toISOString(),
    confidenceLevel: 85,
  },
  {
    id: 'compound-v3',
    name: 'Compound',
    symbol: 'COMP',
    logo: 'https://cryptologos.cc/logos/compound-comp-logo.png',
    category: 'Lending',
    tvl: 750000000,
    riskScore: 25,
    riskCategory: 'Low',
    lastUpdated: new Date(Date.now() - 5400000).toISOString(),
    confidenceLevel: 88,
  },
  {
    id: 'venus',
    name: 'Venus',
    symbol: 'XVS',
    logo: 'https://cryptologos.cc/logos/venus-xvs-logo.png',
    category: 'Lending',
    tvl: 520000000,
    riskScore: 65,
    riskCategory: 'High',
    lastUpdated: new Date(Date.now() - 3600000).toISOString(),
    confidenceLevel: 78,
  },
];

export const mockRiskBreakdowns: Record<string, RiskBreakdown> = {
  'aave-v3': {
    security: {
      score: 12,
      factors: ['Multiple security audits', 'Bug bounty program', 'Time-locked admin controls'],
      explanation: 'Aave has undergone multiple security audits by leading firms and maintains a robust bug bounty program. The protocol has a proven track record with no major exploits.',
    },
    financial: {
      score: 18,
      factors: ['Healthy reserve factors', 'Liquidation thresholds', 'Diverse asset base'],
      explanation: 'Aave maintains conservative financial parameters with appropriate liquidation thresholds and reserve factors to ensure solvency even during market stress.',
    },
    governance: {
      score: 15,
      factors: ['Active governance participation', 'Transparent proposal process', 'Multi-sig admin controls'],
      explanation: 'The Aave governance process is transparent and active with a diverse set of participants. Major protocol changes require thorough discussion and community vote.',
    },
    sentiment: {
      score: 14,
      factors: ['Positive developer sentiment', 'Growing user base', 'Strong institutional backing'],
      explanation: 'Aave enjoys strong community support and positive sentiment across social media channels. Developer activity remains consistently high.',
    },
  },
  'curve-finance': {
    security: {
      score: 28,
      factors: ['Recent audit findings', 'Centralized admin keys', 'Complex staking contracts'],
      explanation: 'Curve has had recent security audit findings that, while addressed, indicate increasing complexity in the codebase. The DAO structure creates some centralization risks.',
    },
    financial: {
      score: 35,
      factors: ['Declining TVL trend', 'High pool concentration', 'Fee volatility'],
      explanation: 'Curve has experienced some TVL decline and concentration in a few major pools. Fee distribution mechanisms create potential incentive misalignments.',
    },
    governance: {
      score: 22,
      factors: ['Active voting participation', 'Some proposal controversies', 'veCRV lock-in dynamics'],
      explanation: 'The veCRV governance model creates some friction and potential vote concentration issues, though participation remains healthy.',
    },
    sentiment: {
      score: 32,
      factors: ['Mixed social sentiment', 'Recent negative press', 'Strong core community'],
      explanation: 'Sentiment has been mixed with some concerns about competitive positioning, though the core community remains supportive.',
    },
  },
};

export const mockAgentInsights: Record<string, AgentInsight[]> = {
  'aave-v3': [
    {
      agentName: 'Protocol Analyst',
      agentType: 'Security',
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      findings: [
        'No critical vulnerabilities found in smart contracts',
        'Timelock mechanisms implemented correctly',
        'Oracle implementations use recommended security patterns',
        'Access controls properly implemented across all contracts',
      ],
      confidence: 94,
      reasoning: 'After analyzing the latest deployed contracts, I found the codebase follows security best practices with proper access controls and validation checks. The use of Chainlink oracles reduces manipulation risks, and timelock mechanisms prevent immediate changes to critical parameters.',
    },
    {
      agentName: 'Market Intelligence',
      agentType: 'Financial',
      timestamp: new Date(Date.now() - 3500000).toISOString(),
      findings: [
        'Healthy reserve ratios maintained across all markets',
        'Liquidation parameters configured conservatively',
        'Diversified asset exposure with appropriate risk weighting',
        'Stress test scenarios show protocol remains solvent in 70% market decline',
      ],
      confidence: 91,
      reasoning: 'Financial analysis indicates Aave maintains conservative risk parameters with appropriate collateralization ratios. Simulation of multiple market stress scenarios shows the protocol remains solvent even under extreme conditions. Reserve growth indicates healthy fee accumulation.',
    },
  ],
  'curve-finance': [
    {
      agentName: 'Protocol Analyst',
      agentType: 'Security',
      timestamp: new Date(Date.now() - 1800000).toISOString(),
      findings: [
        'Recent audit identified 3 medium severity issues',
        'Complex reentrancy controls across pools',
        'Some centralization risks in admin functions',
        'Growing complexity in newer pool designs',
      ],
      confidence: 86,
      reasoning: 'The analysis of Curve contracts revealed increasing complexity in newer pool designs which creates potential security challenges. While no critical vulnerabilities were found, several medium severity issues were identified in the most recent audit, all of which have been addressed but indicate growing complexity risks.',
    },
    {
      agentName: 'Governance Monitor',
      agentType: 'Governance',
      timestamp: new Date(Date.now() - 1700000).toISOString(),
      findings: [
        'Voting power concentration among top 5 holders increasing',
        'Recent governance proposals implemented with minimal opposition',
        'veCRV lock dynamics creating potential governance challenges',
        'Cross-protocol governance dependencies with Convex',
      ],
      confidence: 82,
      reasoning: 'Governance analysis shows increasing concentration of voting power among top veCRV holders, with Convex holding significant influence. Recent proposals have passed with minimal opposition, suggesting possible centralization concerns. The veCRV lock dynamics create complex governance incentives that may not always align with security-first approach.',
    },
  ],
};

export const mockAlerts: Alert[] = [
  {
    id: '1',
    protocolId: 'venus',
    protocolName: 'Venus',
    type: 'TVL Drop',
    severity: 'High',
    message: 'Venus protocol experienced a 25% TVL drop in the last 24 hours',
    timestamp: new Date(Date.now() - 3600000).toISOString(),
    read: false,
  },
  {
    id: '2',
    protocolId: 'curve-finance',
    protocolName: 'Curve Finance',
    type: 'Governance Event',
    severity: 'Medium',
    message: 'Critical parameter change proposal passed with 72% approval',
    timestamp: new Date(Date.now() - 7200000).toISOString(),
    read: false,
  },
  {
    id: '3',
    protocolId: 'compound-v3',
    protocolName: 'Compound',
    type: 'Price Change',
    severity: 'Low',
    message: 'COMP token price decreased by 8% in the last 12 hours',
    timestamp: new Date(Date.now() - 10800000).toISOString(),
    read: true,
  },
];