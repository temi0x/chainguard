import React from 'react';
import { useNavigate } from 'react-router-dom';
import LandingHero from '../components/LandingHero';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Protocol } from '../types';
import { Activity, BrainCircuit, Shield, BarChart2 } from 'lucide-react';

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  
  const handleProtocolSelect = (protocol: Protocol) => {
    navigate(`/protocol/${protocol.id}`);
  };
  
  const handleStartClick = () => {
    navigate('/dashboard');
  };
  
  const features = [
    {
      icon: <Shield className="h-8 w-8 text-success" />,
      title: 'Security Analysis',
      description: 'Deep scan of smart contracts for vulnerabilities, audit history, and best practices compliance.',
    },
    {
      icon: <Activity className="h-8 w-8 text-secondary" />,
      title: 'Financial Health',
      description: 'Assessment of TVL trends, liquidity depth, collateralization ratios, and market parameters.',
    },
    {
      icon: <BrainCircuit className="h-8 w-8 text-primary" />,
      title: 'AI Agents',
      description: 'Specialized AI agents continuously monitor protocols for emerging threats and risks.',
    },
    {
      icon: <BarChart2 className="h-8 w-8 text-accent" />,
      title: 'Comparative Analysis',
      description: 'Side-by-side comparison of multiple protocols to identify the safest option for your needs.',
    },
  ];
  
  return (
    <div className="flex flex-col min-h-screen">
      <LandingHero 
        onSelectProtocol={handleProtocolSelect}
        onStartClick={handleStartClick}
      />
      
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-4">Key Features</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            ChainGuard AI provides comprehensive risk assessment through multiple analysis vectors
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <Card key={index} className="bg-card">
              <CardHeader>
                <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-muted">
                  {feature.icon}
                </div>
                <CardTitle>{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">{feature.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
        
        <div className="mt-24 max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-6">How It Works</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="flex flex-col items-center">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 mb-4">
                <span className="text-lg font-bold">1</span>
              </div>
              <h3 className="text-lg font-medium mb-2">Search</h3>
              <p className="text-sm text-muted-foreground">
                Find any DeFi protocol using our comprehensive database
              </p>
            </div>
            <div className="flex flex-col items-center">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 mb-4">
                <span className="text-lg font-bold">2</span>
              </div>
              <h3 className="text-lg font-medium mb-2">Analyze</h3>
              <p className="text-sm text-muted-foreground">
                Our AI agents assess security, financial health, governance, and community sentiment
              </p>
            </div>
            <div className="flex flex-col items-center">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 mb-4">
                <span className="text-lg font-bold">3</span>
              </div>
              <h3 className="text-lg font-medium mb-2">Decide</h3>
              <p className="text-sm text-muted-foreground">
                Make informed investment decisions based on comprehensive risk analysis
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;