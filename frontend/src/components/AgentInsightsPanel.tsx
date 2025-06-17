import React, { useState } from 'react';
import { BrainCircuit, ChevronDown, ChevronUp, Lightbulb } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/Card';
import { AgentInsight } from '../types';
import { formatRelativeTime } from '../utils/helpers';

interface AgentInsightsPanelProps {
  insights: AgentInsight[];
}

const AgentInsightsPanel: React.FC<AgentInsightsPanelProps> = ({ insights }) => {
  const [expandedInsight, setExpandedInsight] = useState<string | null>(null);
  
  const toggleInsight = (agentName: string) => {
    if (expandedInsight === agentName) {
      setExpandedInsight(null);
    } else {
      setExpandedInsight(agentName);
    }
  };
  
  const getAgentTypeColor = (type: AgentInsight['agentType']) => {
    switch (type) {
      case 'Security':
        return 'text-success bg-success/10';
      case 'Financial':
        return 'text-secondary bg-secondary/10';
      case 'Governance':
        return 'text-primary bg-primary/10';
      case 'Sentiment':
        return 'text-accent bg-accent/10';
      default:
        return 'text-muted-foreground bg-muted/10';
    }
  };
  
  return (
    <Card className="w-full">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-xl font-bold flex items-center gap-2">
          <BrainCircuit className="h-5 w-5 text-primary" />
          Agent Insights
        </CardTitle>
      </CardHeader>
      <CardContent>
        {insights.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <BrainCircuit className="h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-muted-foreground">No agent insights available</p>
          </div>
        ) : (
          <div className="space-y-4">
            {insights.map((insight, index) => (
              <div 
                key={index}
                className="rounded-lg border border-border overflow-hidden transition-all duration-300"
              >
                <div 
                  className="flex items-center justify-between p-4 bg-muted/10 cursor-pointer"
                  onClick={() => toggleInsight(insight.agentName)}
                >
                  <div className="flex items-center gap-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-muted">
                      <BrainCircuit className="h-4 w-4 text-primary" />
                    </div>
                    <div>
                      <h3 className="font-medium">{insight.agentName}</h3>
                      <div className="text-xs text-muted-foreground">
                        {formatRelativeTime(insight.timestamp)}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span 
                      className={`text-xs px-2 py-0.5 rounded-full ${getAgentTypeColor(insight.agentType)}`}
                    >
                      {insight.agentType}
                    </span>
                    {expandedInsight === insight.agentName ? (
                      <ChevronUp className="h-4 w-4 text-muted-foreground" />
                    ) : (
                      <ChevronDown className="h-4 w-4 text-muted-foreground" />
                    )}
                  </div>
                </div>
                
                {expandedInsight === insight.agentName && (
                  <div className="p-4 bg-card border-t border-border">
                    <div className="space-y-4">
                      <div>
                        <h4 className="text-sm font-medium mb-2">Key Findings</h4>
                        <ul className="space-y-2">
                          {insight.findings.map((finding, idx) => (
                            <li key={idx} className="flex items-start gap-2 text-sm">
                              <div className="mt-1 h-1.5 w-1.5 rounded-full bg-primary flex-shrink-0" />
                              <span>{finding}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                      
                      <div>
                        <h4 className="text-sm font-medium mb-2">Reasoning</h4>
                        <div className="text-sm text-muted-foreground bg-muted/5 p-3 rounded-md border border-border">
                          {insight.reasoning}
                        </div>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium">Confidence</span>
                          <span className="text-sm">{insight.confidence}%</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm text-primary">
                          <Lightbulb className="h-4 w-4" />
                          <span>AI Generated</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default AgentInsightsPanel;