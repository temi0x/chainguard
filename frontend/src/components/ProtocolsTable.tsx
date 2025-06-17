import React, { useState, useMemo } from 'react';
import { Search, ArrowUpDown, ExternalLink, TrendingUp, TrendingDown } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/Card';
import Button from './ui/Button';
import RiskBadge from './ui/RiskBadge';
import { Protocol } from '../types';
import { formatCurrency, formatRelativeTime } from '../utils/helpers';

interface ProtocolsTableProps {
  protocols: Protocol[];
  onSelectProtocol: (protocol: Protocol) => void;
}

type SortField = 'name' | 'riskScore' | 'tvl' | 'category' | 'lastUpdated';
type SortDirection = 'asc' | 'desc';

const ProtocolsTable: React.FC<ProtocolsTableProps> = ({ protocols, onSelectProtocol }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [sortField, setSortField] = useState<SortField>('riskScore');
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');

  const filteredAndSortedProtocols = useMemo(() => {
    let filtered = protocols.filter(protocol =>
      protocol.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      protocol.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
      protocol.category.toLowerCase().includes(searchQuery.toLowerCase())
    );

    filtered.sort((a, b) => {
      let aValue: any = a[sortField];
      let bValue: any = b[sortField];

      if (sortField === 'lastUpdated') {
        aValue = new Date(aValue).getTime();
        bValue = new Date(bValue).getTime();
      }

      if (typeof aValue === 'string') {
        aValue = aValue.toLowerCase();
        bValue = bValue.toLowerCase();
      }

      if (sortDirection === 'asc') {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
      }
    });

    return filtered;
  }, [protocols, searchQuery, sortField, sortDirection]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const getSortIcon = (field: SortField) => {
    if (sortField !== field) {
      return <ArrowUpDown className="h-4 w-4 text-muted-foreground" />;
    }
    return (
      <ArrowUpDown 
        className={`h-4 w-4 ${sortDirection === 'asc' ? 'rotate-180' : ''} text-primary transition-transform`} 
      />
    );
  };

  const getTVLTrend = (tvl: number) => {
    // Mock trend calculation - in real app this would come from historical data
    const trend = Math.random() > 0.5 ? 'up' : 'down';
    const percentage = (Math.random() * 10).toFixed(1);
    
    return {
      trend,
      percentage,
      icon: trend === 'up' ? TrendingUp : TrendingDown,
      color: trend === 'up' ? 'text-success' : 'text-destructive'
    };
  };

  return (
    <Card className="w-full">
      <CardHeader className="flex flex-row items-center justify-between pb-4">
        <CardTitle className="text-xl font-bold">Available Protocols</CardTitle>
        <div className="flex items-center gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search protocols..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 pr-4 py-2 bg-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent w-64"
            />
          </div>
          <div className="text-sm text-muted-foreground">
            {filteredAndSortedProtocols.length} of {protocols.length} protocols
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left p-4">
                  <button
                    onClick={() => handleSort('name')}
                    className="flex items-center gap-2 font-medium hover:text-primary transition-colors"
                  >
                    Protocol
                    {getSortIcon('name')}
                  </button>
                </th>
                <th className="text-left p-4">
                  <button
                    onClick={() => handleSort('category')}
                    className="flex items-center gap-2 font-medium hover:text-primary transition-colors"
                  >
                    Category
                    {getSortIcon('category')}
                  </button>
                </th>
                <th className="text-left p-4">
                  <button
                    onClick={() => handleSort('riskScore')}
                    className="flex items-center gap-2 font-medium hover:text-primary transition-colors"
                  >
                    Risk Score
                    {getSortIcon('riskScore')}
                  </button>
                </th>
                <th className="text-left p-4">
                  <button
                    onClick={() => handleSort('tvl')}
                    className="flex items-center gap-2 font-medium hover:text-primary transition-colors"
                  >
                    TVL
                    {getSortIcon('tvl')}
                  </button>
                </th>
                <th className="text-left p-4">Confidence</th>
                <th className="text-left p-4">
                  <button
                    onClick={() => handleSort('lastUpdated')}
                    className="flex items-center gap-2 font-medium hover:text-primary transition-colors"
                  >
                    Last Updated
                    {getSortIcon('lastUpdated')}
                  </button>
                </th>
                <th className="text-left p-4">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredAndSortedProtocols.map((protocol) => {
                const tvlTrend = getTVLTrend(protocol.tvl);
                const TrendIcon = tvlTrend.icon;
                
                return (
                  <tr 
                    key={protocol.id}
                    className="border-b border-border hover:bg-muted/5 transition-colors cursor-pointer"
                    onClick={() => onSelectProtocol(protocol)}
                  >
                    <td className="p-4">
                      <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-full overflow-hidden bg-muted">
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
                          <div className="font-medium">{protocol.name}</div>
                          <div className="text-sm text-muted-foreground">{protocol.symbol}</div>
                        </div>
                      </div>
                    </td>
                    <td className="p-4">
                      <span className="inline-flex items-center rounded-full bg-muted/20 px-2.5 py-0.5 text-xs font-medium">
                        {protocol.category}
                      </span>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <span className="text-lg font-bold">{protocol.riskScore}</span>
                        <RiskBadge category={protocol.riskCategory} />
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{formatCurrency(protocol.tvl)}</span>
                        <div className={`flex items-center gap-1 ${tvlTrend.color}`}>
                          <TrendIcon className="h-3 w-3" />
                          <span className="text-xs">{tvlTrend.percentage}%</span>
                        </div>
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium">{protocol.confidenceLevel}%</span>
                        <div className="w-16 h-2 bg-muted rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-primary"
                            style={{ width: `${protocol.confidenceLevel}%` }}
                          />
                        </div>
                      </div>
                    </td>
                    <td className="p-4">
                      <span className="text-sm text-muted-foreground">
                        {formatRelativeTime(protocol.lastUpdated)}
                      </span>
                    </td>
                    <td className="p-4">
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectProtocol(protocol);
                        }}
                      >
                        <ExternalLink className="h-4 w-4 mr-1" />
                        View
                      </Button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          
          {filteredAndSortedProtocols.length === 0 && (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Search className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-2">No protocols found</h3>
              <p className="text-sm text-muted-foreground">
                Try adjusting your search criteria
              </p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default ProtocolsTable;