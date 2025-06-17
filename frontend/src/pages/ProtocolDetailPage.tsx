import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import RiskScorePanel from '../components/RiskScorePanel';
import RiskBreakdownPanel from '../components/RiskBreakdownPanel';
import AgentInsightsPanel from '../components/AgentInsightsPanel';
import AlertsList from '../components/AlertsList';
import Button from '../components/ui/Button';
import { Protocol } from '../types';
import { mockProtocols, mockRiskBreakdowns, mockAgentInsights, mockAlerts } from '../data/mockData';

const ProtocolDetailPage: React.FC = () => {
  const { protocolId } = useParams<{ protocolId: string }>();
  const navigate = useNavigate();
  const [protocol, setProtocol] = useState<Protocol | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    if (protocolId) {
      // Simulate API loading
      setIsLoading(true);
      setTimeout(() => {
        const foundProtocol = mockProtocols.find(p => p.id === protocolId);
        setProtocol(foundProtocol || null);
        setIsLoading(false);
      }, 1500);
    }
  }, [protocolId]);
  
  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-24">
        <div className="flex flex-col items-center justify-center py-16">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mb-4"></div>
          <p className="text-lg">Analyzing protocol risk profile...</p>
        </div>
      </div>
    );
  }
  
  if (!protocol) {
    return (
      <div className="container mx-auto px-4 py-24">
        <div className="flex flex-col items-center justify-center py-16">
          <h1 className="text-2xl font-bold mb-4">Protocol Not Found</h1>
          <p className="text-muted-foreground mb-6">The requested protocol could not be found.</p>
          <Button onClick={() => navigate('/dashboard')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </Button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto px-4 py-24">
      <div className="mb-6">
        <Button 
          variant="ghost" 
          onClick={() => navigate('/dashboard')}
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Dashboard
        </Button>
      </div>
      
      <div className="space-y-8">
        <RiskScorePanel protocol={protocol} />
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {mockRiskBreakdowns[protocol.id] && (
            <RiskBreakdownPanel riskBreakdown={mockRiskBreakdowns[protocol.id]} />
          )}
          
          {mockAgentInsights[protocol.id] && (
            <AgentInsightsPanel insights={mockAgentInsights[protocol.id]} />
          )}
        </div>
        
        <AlertsList alerts={mockAlerts.filter(alert => alert.protocolId === protocol.id)} />
      </div>
    </div>
  );
};

export default ProtocolDetailPage;