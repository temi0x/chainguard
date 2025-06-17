import React from 'react';
import { Shield, Search, ArrowRight } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import Button from './ui/Button';
import ProtocolSearch from './ui/ProtocolSearch';
import { Protocol } from '../types';

interface LandingHeroProps {
  onSelectProtocol: (protocol: Protocol) => void;
  onStartClick: () => void;
}

const LandingHero: React.FC<LandingHeroProps> = ({ onSelectProtocol, onStartClick }) => {
  const { theme } = useTheme();
  
  return (
    <div className="min-h-screen flex flex-col items-center justify-center relative overflow-hidden py-16 px-4">
      {/* Animated background gradient - adapts to theme */}
      <div 
        className={`absolute inset-0 pointer-events-none z-0 ${
          theme === 'dark' ? 'opacity-30' : 'opacity-20'
        }`}
        style={{
          background: theme === 'dark' 
            ? 'radial-gradient(circle at 50% 50%, rgba(139, 92, 246, 0.15), transparent 60%)'
            : 'radial-gradient(circle at 50% 50%, rgba(139, 92, 246, 0.1), transparent 60%)',
        }}
      />
      
      {/* Floating elements (decorative) - adapts to theme */}
      <div className={`absolute top-1/4 left-1/4 w-64 h-64 rounded-full animate-float ${
        theme === 'dark' ? 'bg-primary/5' : 'bg-primary/3'
      }`} style={{ animationDelay: '0s' }} />
      <div className={`absolute bottom-1/3 right-1/3 w-40 h-40 rounded-full animate-float ${
        theme === 'dark' ? 'bg-secondary/5' : 'bg-secondary/3'
      }`} style={{ animationDelay: '2s' }} />
      <div className={`absolute top-2/3 left-1/3 w-32 h-32 rounded-full animate-float ${
        theme === 'dark' ? 'bg-accent/5' : 'bg-accent/3'
      }`} style={{ animationDelay: '4s' }} />
      
      <div className="container mx-auto text-center relative z-10">
        <div className="flex items-center justify-center mb-6">
          <div className={`flex h-20 w-20 items-center justify-center rounded-full mb-6 ${
            theme === 'dark' ? 'bg-primary/10' : 'bg-primary/5'
          }`}>
            <Shield className="h-10 w-10 text-primary" />
          </div>
        </div>
        
        <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold mb-6 max-w-4xl mx-auto leading-tight">
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary via-secondary to-accent">
            AI-Powered Risk Assessment
          </span>
          <br />
          for DeFi Protocols
        </h1>
        
        <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto mb-10">
          ChainGuard AI uses advanced machine learning to analyze security, financial health, 
          governance, and community sentiment to provide comprehensive risk assessments for DeFi protocols.
        </p>
        
        <div className="flex flex-col md:flex-row items-center justify-center gap-4 mb-12">
          <ProtocolSearch onSelect={onSelectProtocol} />
          <Button onClick={onStartClick} size="lg">
            Assess Protocol
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
        
        <div className="flex flex-wrap justify-center gap-8 mb-16">
          <div className="flex flex-col items-center">
            <div className="text-4xl font-bold text-primary mb-2">100+</div>
            <div className="text-sm text-muted-foreground">Protocols Analyzed</div>
          </div>
          <div className="flex flex-col items-center">
            <div className="text-4xl font-bold text-secondary mb-2">4</div>
            <div className="text-sm text-muted-foreground">AI Agent Types</div>
          </div>
          <div className="flex flex-col items-center">
            <div className="text-4xl font-bold text-accent mb-2">92%</div>
            <div className="text-sm text-muted-foreground">Average Confidence</div>
          </div>
        </div>
        
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-bold mb-6">Trusted By</h2>
          <div className="flex flex-wrap justify-center gap-8">
            {['Coinbase', 'Chainlink', 'Aave', 'Uniswap', 'MakerDAO'].map((name, index) => (
              <div key={index} className={`flex items-center justify-center h-12 px-6 rounded-lg border border-border ${
                theme === 'dark' ? 'bg-muted/10' : 'bg-muted/20'
              }`}>
                <span className="font-medium">{name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingHero;