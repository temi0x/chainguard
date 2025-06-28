import React from "react";
import { useAccount, useConnect, useDisconnect } from "wagmi";
import { Wallet, LogOut, AlertCircle } from "lucide-react";
import Button from "./ui/Button";
import { Card, CardHeader, CardTitle, CardContent } from "./ui/Card";

interface WalletConnectionProps {
  onWalletConnected?: () => void;
}

const WalletConnection: React.FC<WalletConnectionProps> = ({
  onWalletConnected,
}) => {
  const { address, isConnected, isConnecting } = useAccount();
  const { connect, connectors, error } = useConnect();
  const { disconnect } = useDisconnect();

  React.useEffect(() => {
    if (isConnected && onWalletConnected) {
      onWalletConnected();
    }
  }, [isConnected, onWalletConnected]);

  const handleConnect = (connector: any) => {
    try {
      connect({ connector });
    } catch (err) {
      console.error("Failed to connect:", err);
    }
  };

  const formatAddress = (addr: string) => {
    return `${addr.slice(0, 6)}...${addr.slice(-4)}`;
  };

  if (isConnected && address) {
    return (
      <Card className="w-full max-w-md mx-auto">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Wallet className="h-5 w-5 text-success" />
            Wallet Connected
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="p-3 bg-success/10 rounded-lg">
            <p className="text-sm text-success">
              Connected to:{" "}
              <span className="font-mono">{formatAddress(address)}</span>
            </p>
          </div>
          <Button
            variant="outline"
            onClick={() => disconnect()}
            className="w-full"
          >
            <LogOut className="h-4 w-4 mr-2" />
            Disconnect
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Wallet className="h-5 w-5" />
          Connect Wallet
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm text-muted-foreground">
          Connect your wallet to access protocol risk assessments and interact
          with the ChainGuard smart contracts.
        </p>

        {error && (
          <div className="p-3 bg-destructive/10 rounded-lg flex items-start gap-2">
            <AlertCircle className="h-4 w-4 text-destructive mt-0.5" />
            <p className="text-sm text-destructive">{error.message}</p>
          </div>
        )}

        <div className="space-y-2">
          {connectors.map((connector) => (
            <Button
              key={connector.uid}
              onClick={() => handleConnect(connector)}
              disabled={isConnecting}
              className="w-full"
              variant="outline"
            >
              {isConnecting ? "Connecting..." : `Connect ${connector.name}`}
            </Button>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default WalletConnection;
