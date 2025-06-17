import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';
import Button from './Button';

interface ThemeToggleProps {
  size?: 'sm' | 'md' | 'lg';
  variant?: 'primary' | 'secondary' | 'accent' | 'ghost' | 'outline' | 'destructive';
  className?: string;
}

const ThemeToggle: React.FC<ThemeToggleProps> = ({ 
  size = 'sm', 
  variant = 'outline',
  className = '' 
}) => {
  const { theme, toggleTheme } = useTheme();

  return (
    <Button 
      variant={variant} 
      size={size} 
      onClick={toggleTheme}
      className={className}
      aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
    >
      {theme === 'dark' ? (
        <>
          <Sun className="h-4 w-4 mr-1" />
          Light
        </>
      ) : (
        <>
          <Moon className="h-4 w-4 mr-1" />
          Dark
        </>
      )}
    </Button>
  );
};

export default ThemeToggle;