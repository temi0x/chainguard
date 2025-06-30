import React, { useState } from "react";
import { Send, MessageSquare, Loader2, AlertCircle } from "lucide-react";
import Modal from "./ui/Modal";
import Button from "./ui/Button";

interface NaturalLanguageModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (query: string) => void;
}

interface ApiResponse {
  answer: string;
  confidence: number;
  timestamp: string;
  model_used: string;
}

interface ApiError {
  message: string;
  status?: number;
}

const NaturalLanguageModal: React.FC<NaturalLanguageModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
}) => {
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<ApiResponse | null>(null);
  const [error, setError] = useState<ApiError | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || query.length > 1000) return;

    setIsLoading(true);
    setResponse(null);
    setError(null);

    try {
      const apiToken = import.meta.env.VITE_NL_API_TOKEN;
      const baseURL = import.meta.env.VITE_NL_API_BASE_URL || "";
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
      };

      if (apiToken) {
        headers["Authorization"] = `Bearer ${apiToken}`;
      }

      const apiResponse = await fetch(`${baseURL}/ask`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          question: query.trim(),
        }),
      });

      if (!apiResponse.ok) {
        const errorData = await apiResponse.json().catch(() => ({}));
        throw new Error(
          errorData.message ||
            `HTTP ${apiResponse.status}: ${apiResponse.statusText}`
        );
      }

      const data: ApiResponse = await apiResponse.json();
      setResponse(data);
      onSubmit(query);
    } catch (err) {
      console.error("API Error:", err);
      setError({
        message:
          err instanceof Error
            ? err.message
            : "Failed to get response from ChainGuard AI",
        status:
          err instanceof Error && "status" in err
            ? (err as any).status
            : undefined,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    setQuery("");
    setResponse(null);
    setError(null);
    setIsLoading(false);
    onClose();
  };

  const formatConfidence = (confidence: number): string => {
    return `${(confidence * 100).toFixed(1)}%`;
  };

  const formatTimestamp = (timestamp: string): string => {
    try {
      return new Date(timestamp).toLocaleString();
    } catch {
      return timestamp;
    }
  };

  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 0.8) return "text-green-600";
    if (confidence >= 0.6) return "text-yellow-600";
    return "text-red-600";
  };

  const exampleQueries = [
    "Which protocols are safest for a $10k investment?",
    "Compare Aave vs Compound for lending",
    "What are the highest yield opportunities with medium risk?",
    "Is Curve Finance safe for stablecoin farming?",
    "What is ChainGuard AI used for?",
    "How does the risk assessment algorithm work?",
  ];

  const isQueryValid = query.trim() && query.length <= 1000;

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Ask ChainGuard AI"
      className="max-w-3xl"
    >
      <div className="space-y-6">
        <div className="flex items-start gap-3 p-4 bg-muted/10 rounded-lg border border-border">
          <MessageSquare className="h-5 w-5 text-primary mt-0.5" />
          <div>
            <h3 className="font-medium mb-1">Natural Language Query</h3>
            <p className="text-sm text-muted-foreground">
              Ask me anything about DeFi protocols, risk assessments, or
              investment strategies. I'll analyze the data and provide
              personalized recommendations powered by{" "}
              {response?.model_used || "advanced AI models"}.
            </p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="query" className="block text-sm font-medium mb-2">
              Your Question
            </label>
            <textarea
              id="query"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., Which protocols are safest for a $10k investment?"
              className={`w-full h-24 px-3 py-2 bg-background border rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent ${
                query.length > 1000 ? "border-red-500" : "border-border"
              }`}
              disabled={isLoading}
              maxLength={1000}
            />
          </div>

          <div className="flex justify-between items-center">
            <div
              className={`text-xs ${
                query.length > 1000 ? "text-red-500" : "text-muted-foreground"
              }`}
            >
              {query.length}/1000 characters
              {query.length > 1000 && " (Too long)"}
            </div>
            <Button
              type="submit"
              disabled={!isQueryValid || isLoading}
              className="min-w-[120px]"
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Send className="h-4 w-4 mr-2" />
                  Ask AI
                </>
              )}
            </Button>
          </div>
        </form>

        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-red-500 mt-0.5" />
              <div>
                <h4 className="font-medium text-red-800 mb-1">Error</h4>
                <p className="text-sm text-red-700">{error.message}</p>
                {error.status && (
                  <p className="text-xs text-red-600 mt-1">
                    Status: {error.status}
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {response && (
          <div className="p-4 bg-primary/5 border border-primary/20 rounded-lg">
            <div className="flex items-start gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10">
                <MessageSquare className="h-4 w-4 text-primary" />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium">ChainGuard AI Response</h4>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <span
                      className={`font-medium ${getConfidenceColor(
                        response.confidence
                      )}`}
                    >
                      {formatConfidence(response.confidence)} confidence
                    </span>
                    <span>•</span>
                    <span>{response.model_used}</span>
                  </div>
                </div>
                <div className="max-h-64 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
                  <p className="text-sm text-muted-foreground leading-relaxed mb-2">
                    {response.answer}
                  </p>
                </div>
                <div className="text-xs text-muted-foreground mt-2 pt-2 border-t border-primary/10">
                  {formatTimestamp(response.timestamp)}
                </div>
              </div>
            </div>
          </div>
        )}

        <div>
          <h4 className="font-medium mb-3">Example Questions</h4>
          <div className="grid grid-cols-1 gap-2">
            {exampleQueries.map((example, index) => (
              <button
                key={index}
                onClick={() => setQuery(example)}
                className="text-left p-3 text-sm bg-muted/5 hover:bg-muted/10 border border-border rounded-md transition-colors disabled:opacity-50"
                disabled={isLoading}
              >
                "{example}"
              </button>
            ))}
          </div>
        </div>
      </div>
    </Modal>
  );
};

export default NaturalLanguageModal;
