import React, { useState, useRef, useEffect } from 'react';
import { Search } from 'lucide-react';
import { mockProtocols } from '../../data/mockData';
import { Protocol } from '../../types';

interface ProtocolSearchProps {
  onSelect: (protocol: Protocol) => void;
}

const ProtocolSearch: React.FC<ProtocolSearchProps> = ({ onSelect }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const [filteredProtocols, setFilteredProtocols] = useState<Protocol[]>([]);
  const dropdownRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    // Filter protocols based on search query
    if (searchQuery.length > 0) {
      const filtered = mockProtocols.filter(protocol => 
        protocol.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        protocol.symbol.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredProtocols(filtered);
    } else {
      setFilteredProtocols([]);
    }
  }, [searchQuery]);
  
  useEffect(() => {
    // Close dropdown when clicking outside
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsFocused(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);
  
  const handleSelect = (protocol: Protocol) => {
    onSelect(protocol);
    setSearchQuery('');
    setIsFocused(false);
  };
  
  return (
    <div className="relative w-full max-w-md" ref={dropdownRef}>
      <div className={`
        flex items-center rounded-lg border bg-card px-3 py-2 text-sm ring-offset-background
        ${isFocused ? 'ring-2 ring-ring ring-offset-2' : ''}
        transition-all duration-200
      `}>
        <Search className="mr-2 h-4 w-4 text-muted-foreground" />
        <input
          type="text"
          placeholder="Search for a DeFi protocol..."
          className="flex-1 bg-transparent outline-none placeholder:text-muted-foreground"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onFocus={() => setIsFocused(true)}
        />
      </div>
      
      {isFocused && filteredProtocols.length > 0 && (
        <div className="absolute left-0 right-0 z-10 mt-1 max-h-60 overflow-auto rounded-md border border-border bg-card p-1 shadow-md animate-in fade-in-80 slide-in-from-top-5">
          <div className="text-xs font-medium text-muted-foreground px-2 py-1.5">
            Protocols
          </div>
          {filteredProtocols.map((protocol) => (
            <div
              key={protocol.id}
              className="flex items-center gap-2 rounded-sm px-2 py-1.5 text-sm hover:bg-muted/50 cursor-pointer"
              onClick={() => handleSelect(protocol)}
            >
              <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full overflow-hidden bg-muted">
                <img 
                  src={protocol.logo} 
                  alt={protocol.name} 
                  className="h-full w-full object-cover"
                  onError={(e) => {
                    // Fallback to text if image fails to load
                    (e.target as HTMLImageElement).style.display = 'none';
                    (e.target as HTMLImageElement).parentElement!.textContent = protocol.symbol[0];
                  }} 
                />
              </div>
              <div className="flex flex-col">
                <span className="font-medium">{protocol.name}</span>
                <span className="text-xs text-muted-foreground">{protocol.symbol}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ProtocolSearch;