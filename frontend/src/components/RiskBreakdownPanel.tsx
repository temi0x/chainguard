import React, { useState } from 'react';
import { Activity, ChevronDown, ChevronUp, Shield, Coins, Users, MessageSquare } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/Card';
import { RiskBreakdown } from '../types';

interface RiskBreakdownPanelProps {
  riskBreakdown: RiskBreakdown;
}

const RiskBreakdownPanel: React.FC<RiskBreakdownPanelProps> = ({ riskBreakdown }) => {
  const [expandedSection, setExpandedSection] = useState<string | null>('security');
  
  const toggleSection = (section: string) => {
    if (expandedSection === section) {
      setExpandedSection(null);
    } else {
      setExpandedSection(section);
    }
  };
  
  const sections = [
    {
      id: 'security',
      title: 'Security Analysis',
      icon: <Shield className="h-5 w-5 text-success" />,
      score: riskBreakdown.security.score,
      factors: riskBreakdown.security.factors,
      explanation: riskBreakdown.security.explanation,
      color: 'bg-success',
    },
    {
      id: 'financial',
      title: 'Financial Health',
      icon: <Coins className="h-5 w-5 text-secondary" />,
      score: riskBreakdown.financial.score,
      factors: riskBreakdown.financial.factors,
      explanation: riskBreakdown.financial.explanation,
      color: 'bg-secondary',
    },
    {
      id: 'governance',
      title: 'Governance Health',
      icon: <Users className="h-5 w-5 text-primary" />,
      score: riskBreakdown.governance.score,
      factors: riskBreakdown.governance.factors,
      explanation: riskBreakdown.governance.explanation,
      color: 'bg-primary',
    },
    {
      id: 'sentiment',
      title: 'Community Sentiment',
      icon: <MessageSquare className="h-5 w-5 text-accent" />,
      score: riskBreakdown.sentiment.score,
      factors: riskBreakdown.sentiment.factors,
      explanation: riskBreakdown.sentiment.explanation,
      color: 'bg-accent',
    },
  ];
  
  return (
    <Card className="w-full">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-xl font-bold flex items-center gap-2">
          <Activity className="h-5 w-5 text-primary" />
          Risk Breakdown
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {sections.map((section) => (
            <div 
              key={section.id}
              className="rounded-lg border border-border overflow-hidden transition-all duration-300"
            >
              <div 
                className="flex items-center justify-between p-4 bg-muted/10 cursor-pointer"
                onClick={() => toggleSection(section.id)}
              >
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-muted">
                    {section.icon}
                  </div>
                  <div>
                    <h3 className="font-medium">{section.title}</h3>
                    <div className="text-sm text-muted-foreground">
                      Risk Score: <span className="font-medium">{section.score}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-32 h-2 bg-muted rounded-full overflow-hidden">
                    <div 
                      className={`h-full ${section.color}`}
                      style={{ width: `${section.score}%` }}
                    />
                  </div>
                  {expandedSection === section.id ? (
                    <ChevronUp className="h-4 w-4 text-muted-foreground" />
                  ) : (
                    <ChevronDown className="h-4 w-4 text-muted-foreground" />
                  )}
                </div>
              </div>
              
              {expandedSection === section.id && (
                <div className="p-4 bg-card border-t border-border">
                  <div className="space-y-4">
                    <div>
                      <h4 className="text-sm font-medium mb-2">Risk Factors</h4>
                      <div className="flex flex-wrap gap-2">
                        {section.factors.map((factor, idx) => (
                          <span
                            key={idx}
                            className="inline-flex items-center rounded-full bg-muted/20 px-2.5 py-0.5 text-xs font-medium"
                          >
                            {factor}
                          </span>
                        ))}
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="text-sm font-medium mb-2">Analysis</h4>
                      <p className="text-sm text-muted-foreground">{section.explanation}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default RiskBreakdownPanel;