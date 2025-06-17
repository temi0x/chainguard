import React from 'react';
import { Share2, Clock, AlertCircle, ExternalLink } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from './ui/Card';
import Button from './ui/Button';
import Gauge from './ui/Gauge';
import RiskBadge from './ui/RiskBadge';
import { Protocol } from '../types';
import { formatCurrency, formatRelativeTime, getRiskScoreColor } from '../utils/helpers';

interface RiskScorePanelProps {
  protocol: Protocol;
}

const RiskScorePanel: React.FC<RiskScorePanelProps> = ({ protocol }) => {
  return (
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
        <Button variant="outline" size="sm">
          <Share2 className="h-4 w-4 mr-2" />
          Share
        </Button>
      </CardHeader>
      
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="flex flex-col items-center justify-center col-span-1">
            <div className="text-center mb-2">
              <h3 className="text-lg font-medium">Risk Score</h3>
              <p className="text-sm text-muted-foreground">Lower is better</p>
            </div>
            <Gauge 
              value={protocol.riskScore} 
              size="lg"
              className="mb-3"
            />
            <RiskBadge category={protocol.riskCategory} />
          </div>
          
          <div className="col-span-2 space-y-6">
            <div>
              <h3 className="text-lg font-medium mb-1">Protocol Summary</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Based on our AI analysis, {protocol.name} presents a <span className={getRiskScoreColor(protocol.riskScore)}>{protocol.riskCategory.toLowerCase()}</span> risk profile with a score of {protocol.riskScore}/100. The protocol demonstrates strong security practices and responsible financial management.
              </p>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-muted-foreground">Total Value Locked</div>
                  <div className="text-lg font-medium">{formatCurrency(protocol.tvl)}</div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Confidence Level</div>
                  <div className="flex items-center">
                    <div className="text-lg font-medium mr-2">{protocol.confidenceLevel}%</div>
                    <div className="w-24 h-2 bg-muted rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-primary"
                        style={{ width: `${protocol.confidenceLevel}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-2 text-sm text-muted-foreground border-t border-border pt-4">
              <Clock className="h-4 w-4" />
              <span>Last updated {formatRelativeTime(protocol.lastUpdated)}</span>
              
              <div className="flex-1" />
              
              <div className="flex items-center gap-1">
                <AlertCircle className="h-4 w-4" />
                <span>Report an issue</span>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
      
      <CardFooter className="flex justify-between border-t border-border pt-4">
        <Button variant="outline" size="sm">
          <ExternalLink className="h-4 w-4 mr-2" />
          View Protocol Website
        </Button>
        <Button variant="secondary" size="sm">
          View Detailed Report
        </Button>
      </CardFooter>
    </Card>
  );
};

export default RiskScorePanel;