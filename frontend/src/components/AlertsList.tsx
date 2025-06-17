import React from 'react';
import { Bell, BellOff, ExternalLink } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/Card';
import { Alert } from '../types';
import { formatRelativeTime, getAlertSeverityColor } from '../utils/helpers';

interface AlertsListProps {
  alerts: Alert[];
  onAlertClick?: (alert: Alert) => void;
}

const AlertsList: React.FC<AlertsListProps> = ({ 
  alerts,
  onAlertClick = () => {},
}) => {
  return (
    <Card className="w-full">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-xl font-bold flex items-center gap-2">
          <Bell className="h-5 w-5 text-primary" />
          Alerts & Notifications
        </CardTitle>
        <div className="text-sm text-muted-foreground">
          {alerts.length} {alerts.length === 1 ? 'alert' : 'alerts'}
        </div>
      </CardHeader>
      <CardContent>
        {alerts.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <BellOff className="h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-muted-foreground">No active alerts at this time</p>
          </div>
        ) : (
          <div className="space-y-3">
            {alerts.map((alert) => (
              <div 
                key={alert.id}
                className={`
                  flex items-start gap-3 p-3 rounded-md border border-border 
                  ${alert.read ? 'bg-muted/20' : 'bg-muted/40'} 
                  transition-colors duration-200 hover:bg-muted/50 cursor-pointer
                `}
                onClick={() => onAlertClick(alert)}
              >
                <div className={`w-2 h-2 mt-2 rounded-full ${alert.read ? 'bg-muted' : 'bg-primary animate-pulse'}`} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <div className="font-medium truncate">{alert.protocolName}</div>
                    <div className="text-xs text-muted-foreground whitespace-nowrap">
                      {formatRelativeTime(alert.timestamp)}
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground mb-2">{alert.message}</p>
                  <div className="flex items-center justify-between">
                    <span 
                      className={`text-xs px-2 py-0.5 rounded-full ${getAlertSeverityColor(alert.severity)}`}
                    >
                      {alert.severity}
                    </span>
                    <button className="text-xs text-primary flex items-center gap-1 hover:underline">
                      <span>View Details</span>
                      <ExternalLink className="h-3 w-3" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default AlertsList;