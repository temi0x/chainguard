import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MessageSquare } from 'lucide-react';
import ProtocolsTable from '../components/ProtocolsTable';
import ProtocolSearch from '../components/ui/ProtocolSearch';
import NaturalLanguageModal from '../components/NaturalLanguageModal';
import Button from '../components/ui/Button';
import { Protocol } from '../types';
import { mockProtocols } from '../data/mockData';

const DashboardPage: React.FC = () => {
  const [isNLModalOpen, setIsNLModalOpen] = useState(false);
  const navigate = useNavigate();
  
  const handleProtocolSelect = (protocol: Protocol) => {
    navigate(`/protocol/${protocol.id}`);
  };

  const handleNaturalLanguageQuery = (query: string) => {
    console.log('Natural language query:', query);
    // Here you would typically send the query to your LLM backend
  };
  
  return (
    <div className="container mx-auto px-4 py-24">
      <div className="flex flex-col items-center justify-center mb-8">
        <h1 className="text-3xl font-bold mb-6">Protocol Risk Assessment</h1>
        <div className="flex flex-col sm:flex-row items-center gap-4 w-full max-w-2xl">
          <ProtocolSearch onSelect={handleProtocolSelect} />
          <Button 
            variant="outline" 
            onClick={() => setIsNLModalOpen(true)}
            className="whitespace-nowrap"
          >
            <MessageSquare className="h-4 w-4 mr-2" />
            Ask AI
          </Button>
        </div>
      </div>
      
      <div className="space-y-8">
        <ProtocolsTable 
          protocols={mockProtocols}
          onSelectProtocol={handleProtocolSelect}
        />
      </div>

      <NaturalLanguageModal
        isOpen={isNLModalOpen}
        onClose={() => setIsNLModalOpen(false)}
        onSubmit={handleNaturalLanguageQuery}
      />
    </div>
  );
};

export default DashboardPage;