export interface Protocol {
  id: string;
  name: string;
  symbol: string;
  logo: string;
  category: string;
  tvl: number; // Total Value Locked in USD
  riskScore: number; // 0-100
  riskCategory: 'Low' | 'Medium' | 'High';
  lastUpdated: string; // ISO date string
  confidenceLevel: number; // 0-100
}

export interface RiskBreakdown {
  security: {
    score: number;
    factors: string[];
    explanation: string;
  };
  financial: {
    score: number;
    factors: string[];
    explanation: string;
  };
  governance: {
    score: number;
    factors: string[];
    explanation: string;
  };
  sentiment: {
    score: number;
    factors: string[];
    explanation: string;
  };
}

export interface AgentInsight {
  agentName: string;
  agentType: 'Security' | 'Financial' | 'Governance' | 'Sentiment';
  timestamp: string;
  findings: string[];
  confidence: number;
  reasoning: string;
}

export interface Alert {
  id: string;
  protocolId: string;
  protocolName: string;
  type: 'TVL Drop' | 'Governance Event' | 'Exploit' | 'Price Change';
  severity: 'Low' | 'Medium' | 'High' | 'Critical';
  message: string;
  timestamp: string;
  read: boolean;
}