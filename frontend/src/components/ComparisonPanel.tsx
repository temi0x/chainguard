import React, { useState, useEffect } from 'react';
import { BarChart, ArrowDown, ArrowUp, BarChart2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/Card';
import Button from './ui/Button';
import ProtocolSearch from './ui/ProtocolSearch';
import RiskBadge from './ui/RiskBadge';
import { Protocol, RiskBreakdown } from '../types';
import { mockRiskBreakdowns } from '../data/mockData';
import { formatPercent } from '../utils/helpers';

interface ComparisonPanelProps {
  protocols: Protocol[];
  onSelectProtocol: (protocol: Protocol) => void;
}

const ComparisonPanel: React.FC<ComparisonPanelProps> = ({ protocols, onSelectProtocol }) => {
  const [selectedProtocols, setSelectedProtocols] = useState<Protocol[]>([]);
  const [riskBreakdowns, setRiskBreakdowns] = useState<Record<string, RiskBreakdown>>({});
  
  useEffect(() => {
    // Get risk breakdowns for selected protocols
    const breakdowns: Record<string, RiskBreakdown> = {};
    selectedProtocols.forEach(protocol => {
      if (mockRiskBreakdowns[protocol.id]) {
        breakdowns[protocol.id] = mockRiskBreakdowns[protocol.id];
      }
    });
    setRiskBreakdowns(breakdowns);
  }, [selectedProtocols]);
  
  const handleProtocolSelect = (protocol: Protocol) => {
    if (selectedProtocols.length < 3 && !selectedProtocols.find(p => p.id === protocol.id)) {
      setSelectedProtocols([...selectedProtocols, protocol]);
    }
  };
  
  const handleProtocolRemove = (protocolId: string) => {
    setSelectedProtocols(selectedProtocols.filter(p => p.id !== protocolId));
  };
  
  // Calculate the difference between two risk scores
  const getRiskDifference = (score1: number, score2: number) => {
    const diff = score1 - score2;
    const isBetter = diff < 0; // Lower risk score is better
    
    return {
      diff: Math.abs(diff),
      isBetter,
    };
  };
  
  // Generate risk category comparison text
  const getComparisonText = () => {
    if (selectedProtocols.length < 2) return null;
    
    const p1 = selectedProtocols[0];
    const p2 = selectedProtocols[1];
    const diff = getRiskDifference(p1.riskScore, p2.riskScore);
    
    let text = '';
    if (diff.diff < 5) {
      text = `${p1.name} and ${p2.name} have similar risk profiles.`;
    } else {
      const better = diff.isBetter ? p1.name : p2.name;
      const worse = diff.isBetter ? p2.name : p1.name;
      text = `${better} has a ${diff.diff} point lower risk score than ${worse}.`;
    }
    
    return text;
  };
  
  return (
    <Card className="w-full">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-xl font-bold flex items-center gap-2">
          <BarChart2 className="h-5 w-5 text-primary" />
          Comparative Analysis
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col gap-4">
          <div className="flex items-center gap-2">
            <ProtocolSearch onSelect={handleProtocolSelect} />
            <Button
              variant="outline"
              size="sm"
              disabled={selectedProtocols.length < 2}
              onClick={() => {}}
            >
              Compare
            </Button>
          </div>
          
          {selectedProtocols.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {selectedProtocols.map(protocol => (
                <div 
                  key={protocol.id}
                  className="relative flex flex-col p-4 rounded-lg border border-border bg-card/50 hover:bg-card transition-colors"
                >
                  <button 
                    className="absolute top-2 right-2 text-muted-foreground hover:text-foreground"
                    onClick={() => handleProtocolRemove(protocol.id)}
                  >
                    &times;
                  </button>
                  
                  <div className="flex items-center gap-3 mb-3">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full overflow-hidden bg-muted">
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
                      <h3 className="font-medium">{protocol.name}</h3>
                      <div className="text-sm text-muted-foreground">{protocol.symbol}</div>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-muted-foreground">Risk Score</span>
                    <span className="text-lg font-bold">{protocol.riskScore}</span>
                  </div>
                  
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-sm text-muted-foreground">Category</span>
                    <RiskBadge category={protocol.riskCategory} />
                  </div>
                  
                  {riskBreakdowns[protocol.id] && (
                    <div className="space-y-2 mt-2">
                      <h4 className="text-sm font-medium">Risk Breakdown</h4>
                      
                      <div className="grid grid-cols-2 gap-2">
                        <div className="text-xs">
                          <div className="text-muted-foreground">Security</div>
                          <div className="font-medium">{riskBreakdowns[protocol.id].security.score}</div>
                        </div>
                        <div className="text-xs">
                          <div className="text-muted-foreground">Financial</div>
                          <div className="font-medium">{riskBreakdowns[protocol.id].financial.score}</div>
                        </div>
                        <div className="text-xs">
                          <div className="text-muted-foreground">Governance</div>
                          <div className="font-medium">{riskBreakdowns[protocol.id].governance.score}</div>
                        </div>
                        <div className="text-xs">
                          <div className="text-muted-foreground">Sentiment</div>
                          <div className="font-medium">{riskBreakdowns[protocol.id].sentiment.score}</div>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  <div className="mt-auto pt-3">
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className="w-full"
                      onClick={() => onSelectProtocol(protocol)}
                    >
                      View Full Analysis
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-8 text-center bg-muted/10 rounded-lg border border-dashed border-border">
              <BarChart className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-1">Compare DeFi Protocols</h3>
              <p className="text-sm text-muted-foreground mb-4 max-w-md">
                Search and select up to 3 protocols to compare their risk profiles side by side
              </p>
            </div>
          )}
          
          {selectedProtocols.length >= 2 && (
            <div className="p-4 rounded-lg border border-border bg-muted/10 mt-4">
              <h3 className="text-lg font-medium mb-2 flex items-center gap-2">
                <BarChart className="h-5 w-5 text-primary" />
                Comparison Summary
              </h3>
              <p className="text-sm text-muted-foreground mb-3">
                {getComparisonText()}
              </p>
              
              {selectedProtocols.length === 2 && riskBreakdowns[selectedProtocols[0].id] && riskBreakdowns[selectedProtocols[1].id] && (
                <div className="space-y-3">
                  <h4 className="text-sm font-medium">Risk Factor Comparison</h4>
                  
                  {['security', 'financial', 'governance', 'sentiment'].map((category) => {
                    const p1 = selectedProtocols[0];
                    const p2 = selectedProtocols[1];
                    const score1 = riskBreakdowns[p1.id][category as keyof RiskBreakdown].score;
                    const score2 = riskBreakdowns[p2.id][category as keyof RiskBreakdown].score;
                    const { diff, isBetter } = getRiskDifference(score1, score2);
                    
                    return (
                      <div key={category} className="flex items-center text-sm">
                        <div className="w-24 capitalize">{category}</div>
                        <div className="w-12 text-center font-medium">{score1}</div>
                        <div className="w-16 text-center flex items-center justify-center">
                          {diff > 0 ? (
                            <>
                              {isBetter ? (
                                <ArrowDown className="h-4 w-4 text-success mr-1" />
                              ) : (
                                <ArrowUp className="h-4 w-4 text-destructive mr-1" />
                              )}
                              <span className={isBetter ? 'text-success' : 'text-destructive'}>{diff}</span>
                            </>
                          ) : (
                            <span className="text-muted-foreground">—</span>
                          )}
                        </div>
                        <div className="w-12 text-center font-medium">{score2}</div>
                        <div className="flex-1 h-2 bg-muted/50 rounded-full ml-2">
                          <div 
                            className="h-full rounded-full bg-gradient-to-r from-success to-destructive"
                            style={{ 
                              width: `${Math.max(score1, score2)}%`,
                              background: score1 < score2 ? 
                                `linear-gradient(to right, hsl(var(--success)) ${formatPercent(score1)}, hsl(var(--destructive)) ${formatPercent(score2)})` :
                                `linear-gradient(to right, hsl(var(--destructive)) ${formatPercent(score2)}, hsl(var(--success)) ${formatPercent(score1)})`
                            }}
                          />
                        </div>
                      </div>
                    );
                  })}
                  
                  <div className="pt-2 text-xs text-muted-foreground italic">
                    Note: Lower risk scores are better
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default ComparisonPanel;