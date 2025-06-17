import React, { useState } from 'react';
import { Send, MessageSquare, Loader2 } from 'lucide-react';
import Modal from './ui/Modal';
import Button from './ui/Button';

interface NaturalLanguageModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (query: string) => void;
}

const NaturalLanguageModal: React.FC<NaturalLanguageModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
}) => {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    setResponse(null);

    // Simulate AI response
    setTimeout(() => {
      const mockResponse = generateMockResponse(query);
      setResponse(mockResponse);
      setIsLoading(false);
      onSubmit(query);
    }, 2000);
  };

  const generateMockResponse = (query: string): string => {
    const lowerQuery = query.toLowerCase();
    
    if (lowerQuery.includes('safe') || lowerQuery.includes('secure')) {
      return "Based on our AI analysis, Aave and Compound are currently among the safest DeFi protocols with risk scores of 15 and 25 respectively. They have strong security audits, healthy financial metrics, and active governance.";
    }
    
    if (lowerQuery.includes('high yield') || lowerQuery.includes('apy')) {
      return "For higher yields, you might consider Curve Finance (risk score: 30) which offers competitive APYs on stablecoin pools. However, be aware of the medium risk level due to recent governance changes.";
    }
    
    if (lowerQuery.includes('compare')) {
      return "I can help you compare protocols! Aave (risk: 15) offers better security, while Curve (risk: 30) provides higher yields. Would you like a detailed side-by-side comparison?";
    }
    
    return "I've analyzed your query and found several relevant protocols. Aave and Uniswap show strong fundamentals with low risk scores. Would you like me to provide more specific recommendations based on your risk tolerance?";
  };

  const handleClose = () => {
    setQuery('');
    setResponse(null);
    setIsLoading(false);
    onClose();
  };

  const exampleQueries = [
    "Which protocols are safest for a $10k investment?",
    "Compare Aave vs Compound for lending",
    "What are the highest yield opportunities with medium risk?",
    "Is Curve Finance safe for stablecoin farming?",
  ];

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Ask ChainGuard AI" className="max-w-3xl">
      <div className="space-y-6">
        <div className="flex items-start gap-3 p-4 bg-muted/10 rounded-lg border border-border">
          <MessageSquare className="h-5 w-5 text-primary mt-0.5" />
          <div>
            <h3 className="font-medium mb-1">Natural Language Query</h3>
            <p className="text-sm text-muted-foreground">
              Ask me anything about DeFi protocols, risk assessments, or investment strategies. 
              I'll analyze the data and provide personalized recommendations.
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
              className="w-full h-24 px-3 py-2 bg-background border border-border rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              disabled={isLoading}
            />
          </div>

          <div className="flex justify-between items-center">
            <div className="text-xs text-muted-foreground">
              {query.length}/500 characters
            </div>
            <Button 
              type="submit" 
              disabled={!query.trim() || isLoading}
              className="min-w-[100px]"
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

        {response && (
          <div className="p-4 bg-primary/5 border border-primary/20 rounded-lg">
            <div className="flex items-start gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10">
                <MessageSquare className="h-4 w-4 text-primary" />
              </div>
              <div className="flex-1">
                <h4 className="font-medium mb-2">ChainGuard AI Response</h4>
                <p className="text-sm text-muted-foreground leading-relaxed">{response}</p>
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
                className="text-left p-3 text-sm bg-muted/5 hover:bg-muted/10 border border-border rounded-md transition-colors"
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