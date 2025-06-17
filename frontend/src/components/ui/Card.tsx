import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  isGlass?: boolean;
  isHoverable?: boolean;
}

export const Card = ({ children, className = '', isGlass = false, isHoverable = false }: CardProps) => {
  const baseClasses = 'rounded-lg border border-border bg-card text-card-foreground shadow-sm';
  const glassClasses = isGlass ? 'glass' : '';
  const hoverClasses = isHoverable ? 'transition-all duration-300 hover:shadow-lg hover:translate-y-[-2px]' : '';
  
  return (
    <div className={`${baseClasses} ${glassClasses} ${hoverClasses} ${className}`}>
      {children}
    </div>
  );
};

interface CardHeaderProps {
  children: React.ReactNode;
  className?: string;
}

export const CardHeader = ({ children, className = '' }: CardHeaderProps) => {
  return <div className={`flex flex-col space-y-1.5 p-6 ${className}`}>{children}</div>;
};

interface CardTitleProps {
  children: React.ReactNode;
  className?: string;
}

export const CardTitle = ({ children, className = '' }: CardTitleProps) => {
  return <h3 className={`text-lg font-semibold leading-none tracking-tight ${className}`}>{children}</h3>;
};

interface CardDescriptionProps {
  children: React.ReactNode;
  className?: string;
}

export const CardDescription = ({ children, className = '' }: CardDescriptionProps) => {
  return <p className={`text-sm text-muted-foreground ${className}`}>{children}</p>;
};

interface CardContentProps {
  children: React.ReactNode;
  className?: string;
}

export const CardContent = ({ children, className = '' }: CardContentProps) => {
  return <div className={`p-6 pt-0 ${className}`}>{children}</div>;
};

interface CardFooterProps {
  children: React.ReactNode;
  className?: string;
}

export const CardFooter = ({ children, className = '' }: CardFooterProps) => {
  return <div className={`flex items-center p-6 pt-0 ${className}`}>{children}</div>;
};