import React, { useState } from "react";
import { useAccount, useConnect, useDisconnect } from "wagmi";
import {
  useRiskOracle,
  useRiskScore,
  useRiskBreakdown,
} from "../hooks/useRiskOracle";
import { CONTRACT_ADDRESSES } from "../contracts/config";

const ContractIntegration: React.FC = () => {
  const [protocolName, setProtocolName] = useState("aave-v3");
  const { address, isConnected } = useAccount();
  const { connect, connectors } = useConnect();
  const { disconnect } = useDisconnect();

  const {
    requestAssessment,
    isLoading,
    error,
    isTransactionSuccess,
    formatRiskScore,
    formatConfidence,
  } = useRiskOracle();

  const { data: riskScoreData, isLoading: isRiskScoreLoading } =
    useRiskScore(protocolName);
  const { data: riskBreakdownData, isLoading: isRiskBreakdownLoading } =
    useRiskBreakdown(protocolName);

  const handleRequestAssessment = async () => {
    if (!protocolName.trim()) {
      alert("Please enter a protocol name");
      return;
    }

    await requestAssessment(protocolName);
  };

  const handleConnect = () => {
    if (connectors[0]) {
      connect({ connector: connectors[0] });
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold mb-4">
          ChainGuard Risk Oracle Integration
        </h2>

        {/* Contract Address */}
        <div className="mb-4 p-3 bg-gray-50 rounded">
          <p className="text-sm text-gray-600">Contract Address:</p>
          <p className="font-mono text-sm break-all">
            {CONTRACT_ADDRESSES.riskOracle}
          </p>
        </div>

        {/* Wallet Connection */}
        <div className="mb-6">
          {!isConnected ? (
            <button
              onClick={handleConnect}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Connect Wallet
            </button>
          ) : (
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600">
                Connected: {address?.slice(0, 6)}...{address?.slice(-4)}
              </span>
              <button
                onClick={() => disconnect()}
                className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
              >
                Disconnect
              </button>
            </div>
          )}
        </div>

        {/* Risk Assessment Request */}
        <div className="mb-6 p-4 border rounded">
          <h3 className="text-lg font-semibold mb-3">
            Request Risk Assessment
          </h3>
          <div className="flex gap-2 mb-3">
            <input
              type="text"
              value={protocolName}
              onChange={(e) => setProtocolName(e.target.value)}
              placeholder="Enter protocol name (e.g., aave-v3)"
              className="flex-1 px-3 py-2 border rounded"
            />
            <button
              onClick={handleRequestAssessment}
              disabled={!isConnected || isLoading}
              className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:bg-gray-400"
            >
              {isLoading ? "Requesting..." : "Request Assessment"}
            </button>
          </div>

          {error && <div className="text-red-600 text-sm mb-2">{error}</div>}

          {isTransactionSuccess && (
            <div className="text-green-600 text-sm mb-2">
              ✅ Risk assessment requested successfully!
            </div>
          )}
        </div>

        {/* Current Risk Score */}
        <div className="mb-6 p-4 border rounded">
          <h3 className="text-lg font-semibold mb-3">Current Risk Score</h3>
          {isRiskScoreLoading ? (
            <p className="text-gray-600">Loading risk score...</p>
          ) : riskScoreData ? (
            <div className="space-y-2">
              <p>
                <strong>Risk Score:</strong>{" "}
                {formatRiskScore(riskScoreData.riskScore)}%
              </p>
              <p>
                <strong>Confidence:</strong>{" "}
                {formatConfidence(riskScoreData.confidence)}%
              </p>
              <p>
                <strong>Last Updated:</strong>{" "}
                {new Date(
                  Number(riskScoreData.lastUpdated) * 1000
                ).toLocaleString()}
              </p>
            </div>
          ) : (
            <p className="text-gray-600">
              No risk score available for this protocol
            </p>
          )}
        </div>

        {/* Risk Breakdown */}
        <div className="p-4 border rounded">
          <h3 className="text-lg font-semibold mb-3">Risk Breakdown</h3>
          {isRiskBreakdownLoading ? (
            <p className="text-gray-600">Loading risk breakdown...</p>
          ) : riskBreakdownData ? (
            <div className="space-y-2">
              <p>
                <strong>Overall Risk Score:</strong>{" "}
                {formatRiskScore(riskBreakdownData.riskScore)}%
              </p>
              <p>
                <strong>Confidence:</strong>{" "}
                {formatConfidence(riskBreakdownData.confidence)}%
              </p>
              <div>
                <strong>Component Scores:</strong>
                <ul className="ml-4 mt-1">
                  <li>
                    Security:{" "}
                    {formatRiskScore(riskBreakdownData.componentScores[0])}%
                  </li>
                  <li>
                    Financial:{" "}
                    {formatRiskScore(riskBreakdownData.componentScores[1])}%
                  </li>
                  <li>
                    Governance:{" "}
                    {formatRiskScore(riskBreakdownData.componentScores[2])}%
                  </li>
                  <li>
                    Data Quality:{" "}
                    {formatRiskScore(riskBreakdownData.componentScores[3])}%
                  </li>
                </ul>
              </div>
              {riskBreakdownData.explanation && (
                <div>
                  <strong>Explanation:</strong>
                  <p className="mt-1 text-sm text-gray-700">
                    {riskBreakdownData.explanation}
                  </p>
                </div>
              )}
            </div>
          ) : (
            <p className="text-gray-600">
              No risk breakdown available for this protocol
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default ContractIntegration;
