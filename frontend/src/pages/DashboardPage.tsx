import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAccount } from "wagmi";
import { MessageSquare } from "lucide-react";
import ProtocolsTable from "../components/ProtocolsTable";
import ProtocolSearch from "../components/ui/ProtocolSearch";
import NaturalLanguageModal from "../components/NaturalLanguageModal";
import WalletConnection from "../components/WalletConnection";
import ContractDataDisplay from "../components/ContractDataDisplay";
import Button from "../components/ui/Button";
import { Protocol } from "../types";
import { mockProtocols } from "../data/mockData";

const DashboardPage: React.FC = () => {
  const [isNLModalOpen, setIsNLModalOpen] = useState(false);
  const [selectedProtocol, setSelectedProtocol] = useState<string>("aave-v3");
  const { isConnected } = useAccount();
  const navigate = useNavigate();

  const handleProtocolSelect = (protocol: Protocol) => {
    if (!isConnected) {
      // Don't navigate if wallet is not connected
      return;
    }
    setSelectedProtocol(protocol.id);
    navigate(`/protocol/${protocol.id}`);
  };

  const handleNaturalLanguageQuery = (query: string) => {
    console.log("Natural language query:", query);
    // Here you would typically send the query to your LLM backend
  };

  // If wallet is not connected, show wallet connection UI
  if (!isConnected) {
    return (
      <div className="container mx-auto px-4 py-24">
        <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-8">
          <div className="text-center space-y-4">
            <h1 className="text-4xl font-bold">Protocol Risk Assessment</h1>
            <p className="text-xl text-muted-foreground max-w-2xl">
              Connect your wallet to access real-time protocol risk assessments
              powered by our smart contracts on Avalanche.
            </p>
          </div>
          <WalletConnection
            onWalletConnected={() => {
              // Wallet connected, component will re-render
            }}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-24 space-y-8">
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

      {/* Smart Contract Data Display */}
      <ContractDataDisplay protocolName={selectedProtocol} />

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
