import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import AgentInsightsPanel from '../components/AgentInsightsPanel';
import ProtocolSearch from '../components/ui/ProtocolSearch';
import Button from '../components/ui/Button';
import { Protocol } from '../types';
import { mockProtocols, mockAgentInsights } from '../data/mockData';
import { BrainCircuit, BarChart, Search, Filter } from 'lucide-react';

const InsightsPage: React.FC = () => {
  const { protocolId } = useParams<{ protocolId: string }>();
  const navigate = useNavigate();
  const [protocol, setProtocol] = useState<Protocol | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [viewMode, setViewMode] = useState<'timeline' | 'agent'>('timeline');
  
  useEffect(() => {
    if (protocolId) {
      setIsLoading(true);
      setTimeout(() => {
        const foundProtocol = mockProtocols.find(p => p.id === protocolId);
        setProtocol(foundProtocol || null);
        setIsLoading(false);
      }, 1500);
    }
  }, [protocolId]);
  
  const handleProtocolSelect = (selected: Protocol) => {
    navigate(`/insights/${selected.id}`);
  };
  
  const getInsightsForProtocol = () => {
    if (!protocol || !mockAgentInsights[protocol.id]) {
      return [];
    }
    
    return mockAgentInsights[protocol.id];
  };
  
  return (
    <div className="container mx-auto px-4 py-24">
      <div className="flex flex-col items-center justify-center mb-8">
        <h1 className="text-3xl font-bold mb-6">Agent Insights</h1>
        <div className="flex flex-col sm:flex-row items-center gap-4">
          <ProtocolSearch onSelect={handleProtocolSelect} />
          <div className="flex bg-muted/10 rounded-lg p-1">
            <Button
              variant={viewMode === 'timeline' ? 'secondary' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('timeline')}
              className="rounded-r-none"
            >
              <BarChart className="h-4 w-4 mr-2" />
              Timeline
            </Button>
            <Button
              variant={viewMode === 'agent' ? 'secondary' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('agent')}
              className="rounded-l-none"
            >
              <BrainCircuit className="h-4 w-4 mr-2" />
              By Agent
            </Button>
          </div>
        </div>
      </div>
      
      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-16">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mb-4"></div>
          <p className="text-lg">Loading agent insights...</p>
        </div>
      ) : protocol ? (
        <div className="space-y-8">
          <Card className="w-full">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <div className="flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-full overflow-hidden bg-muted">
                  <img 
                    src={protocol.logo} 
                    alt={protocol.name} 
                    className="h-full w-full object-cover"
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = 'none';
                      (e.target as HTMLImageElement).parentElement!.textContent = protocol.symbol[0];
                    }} 
                  />
                </div>
                <div>
                  <CardTitle className="text-xl font-bold">{protocol.name}</CardTitle>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <span>{protocol.symbol}</span>
                    <span>•</span>
                    <span>{protocol.category}</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm">
                  <Filter className="h-4 w-4 mr-2" />
                  Filter
                </Button>
              </div>
            </CardHeader>
            <CardContent className="pt-4">
              <div className="flex items-center justify-between mb-6 pb-4 border-b border-border">
                <div>
                  <h3 className="text-lg font-medium">Agent Activity</h3>
                  <p className="text-sm text-muted-foreground">
                    Showing {getInsightsForProtocol().length} insights from {protocol.name}
                  </p>
                </div>
              </div>
              
              <AgentInsightsPanel insights={getInsightsForProtocol()} />
            </CardContent>
          </Card>
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <div className="w-24 h-24 rounded-full bg-muted/30 flex items-center justify-center mb-6">
            <Search className="h-12 w-12 text-muted-foreground" />
          </div>
          <h2 className="text-2xl font-bold mb-2">Select a Protocol</h2>
          <p className="text-muted-foreground max-w-md">
            Search for a DeFi protocol to view detailed agent insights and reasoning
          </p>
        </div>
      )}
    </div>
  );
};

export default InsightsPage;