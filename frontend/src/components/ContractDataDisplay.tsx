import React from "react";
import { useAccount } from "wagmi";
import { useRiskScore, useRiskBreakdown } from "../hooks/useRiskOracle";
import { Card, CardHeader, CardTitle, CardContent } from "./ui/Card";
import { Badge } from "./ui/Badge";
import {
  Loader2,
  TrendingUp,
  Shield,
  Activity,
  AlertTriangle,
} from "lucide-react";

interface ContractDataDisplayProps {
  protocolName?: string;
}

const ContractDataDisplay: React.FC<ContractDataDisplayProps> = ({
  protocolName = "aave-v3",
}) => {
  const { isConnected } = useAccount();
  const {
    data: riskScoreData,
    isLoading: isRiskScoreLoading,
    error: riskScoreError,
  } = useRiskScore(protocolName);
  const {
    data: riskBreakdownData,
    isLoading: isRiskBreakdownLoading,
    error: riskBreakdownError,
  } = useRiskBreakdown(protocolName);

  if (!isConnected) {
    return null;
  }

  const formatScore = (score: bigint | undefined) => {
    if (!score) return "N/A";
    return Number(score).toString();
  };

  const formatTimestamp = (timestamp: bigint | undefined) => {
    if (!timestamp) return "N/A";
    return new Date(Number(timestamp) * 1000).toLocaleString();
  };

  const getRiskCategory = (score: number) => {
    if (score <= 30) return { label: "Low", color: "success" };
    if (score <= 70) return { label: "Medium", color: "warning" };
    return { label: "High", color: "destructive" };
  };

  const isLoading = isRiskScoreLoading || isRiskBreakdownLoading;
  const hasError = riskScoreError || riskBreakdownError;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Smart Contract Data</h2>
        {isLoading && (
          <div className="flex items-center gap-2 text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            Loading contract data...
          </div>
        )}
      </div>

      {hasError && (
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-destructive">
              <AlertTriangle className="h-5 w-5" />
              <p>
                Error loading contract data:{" "}
                {hasError?.message || "Unknown error"}
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Risk Score Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Overall Risk Score
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isRiskScoreLoading ? (
              <div className="flex items-center justify-center h-20">
                <Loader2 className="h-6 w-6 animate-spin" />
              </div>
            ) : riskScoreData ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-3xl font-bold">
                    {formatScore(riskScoreData.riskScore)}
                  </span>
                  <Badge
                    variant={
                      getRiskCategory(Number(riskScoreData.riskScore))
                        .color as any
                    }
                  >
                    {getRiskCategory(Number(riskScoreData.riskScore)).label}
                  </Badge>
                </div>
                <div className="space-y-1 text-sm text-muted-foreground">
                  <p>Confidence: {formatScore(riskScoreData.confidence)}%</p>
                  <p>
                    Last Updated: {formatTimestamp(riskScoreData.lastUpdated)}
                  </p>
                </div>
              </div>
            ) : (
              <p className="text-muted-foreground">No data available</p>
            )}
          </CardContent>
        </Card>

        {/* Risk Breakdown Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              Risk Components
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isRiskBreakdownLoading ? (
              <div className="flex items-center justify-center h-20">
                <Loader2 className="h-6 w-6 animate-spin" />
              </div>
            ) : riskBreakdownData ? (
              <div className="space-y-3">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Security:</span>
                    <span className="font-medium">
                      {formatScore(riskBreakdownData.componentScores[0])}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Financial:</span>
                    <span className="font-medium">
                      {formatScore(riskBreakdownData.componentScores[1])}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Governance:</span>
                    <span className="font-medium">
                      {formatScore(riskBreakdownData.componentScores[2])}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Sentiment:</span>
                    <span className="font-medium">
                      {formatScore(riskBreakdownData.componentScores[3])}
                    </span>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-muted-foreground">
                No breakdown data available
              </p>
            )}
          </CardContent>
        </Card>

        {/* Protocol Info Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Protocol Info
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Protocol:</span>
                  <span className="font-medium capitalize">
                    {protocolName.replace("-", " ")}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Network:</span>
                  <span className="font-medium">Avalanche</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Status:</span>
                  <Badge variant="success">Active</Badge>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ContractDataDisplay;
