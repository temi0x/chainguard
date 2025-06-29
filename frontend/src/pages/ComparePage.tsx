import React from "react";
import { useNavigate } from "react-router-dom";
import ComparisonPanel from "../components/ComparisonPanel";
import { Protocol } from "../types";
import { mockProtocols } from "../data/mockData";

const ComparePage: React.FC = () => {
  const navigate = useNavigate();

  const handleProtocolSelect = (protocol: Protocol) => {
    navigate(`/protocol/${protocol.id}`);
  };

  return (
    <div className="container mx-auto px-4 py-24">
      <div className="flex flex-col items-center justify-center mb-8">
        <h1 className="text-3xl font-bold mb-6">Protocol Comparison</h1>
        <p className="text-muted-foreground max-w-2xl text-center">
          Compare risk profiles of multiple DeFi protocols to make informed
          investment decisions
        </p>
      </div>

      <div className="space-y-8">
        <ComparisonPanel
          protocols={mockProtocols}
          onSelectProtocol={handleProtocolSelect}
        />
      </div>
    </div>
  );
};

export default ComparePage;
