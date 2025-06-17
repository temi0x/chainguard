import React from 'react';
import { getRiskScoreColor } from '../../utils/helpers';

interface GaugeProps {
  value: number; // 0-100
  size?: 'sm' | 'md' | 'lg';
  showValue?: boolean;
  label?: string;
  className?: string;
}

const Gauge: React.FC<GaugeProps> = ({
  value,
  size = 'md',
  showValue = true,
  label,
  className = '',
}) => {
  // Convert 0-100 scale to 0-1 for calculations
  const normalizedValue = value / 100;
  
  // Calculate stroke width based on size
  const strokeWidth = size === 'sm' ? 8 : size === 'md' ? 12 : 16;
  
  // Calculate size of SVG
  const svgSize = size === 'sm' ? 120 : size === 'md' ? 160 : 200;
  
  // Calculate radius 
  const radius = (svgSize - strokeWidth) / 2;
  
  // Calculate circumference
  const circumference = 2 * Math.PI * radius;
  
  // Calculate offset
  const offset = circumference - normalizedValue * circumference;
  
  // Calculate the center of the SVG
  const center = svgSize / 2;
  
  // Calculate the arc start/end angle (we use 3/4 of a circle)
  const startAngle = -135;
  const endAngle = 135;
  
  // Calculate the path for the arc
  const arcPath = `
    M ${center + radius * Math.cos((startAngle * Math.PI) / 180)} ${center + radius * Math.sin((startAngle * Math.PI) / 180)}
    A ${radius} ${radius} 0 ${endAngle - startAngle > 180 ? 1 : 0} 1 
    ${center + radius * Math.cos((endAngle * Math.PI) / 180)} ${center + radius * Math.sin((endAngle * Math.PI) / 180)}
  `;
  
  const percentComplete = 1 - offset / circumference;
  const arcLength = (endAngle - startAngle) * (Math.PI / 180) * radius;
  const progressPath = `
    M ${center + radius * Math.cos((startAngle * Math.PI) / 180)} ${center + radius * Math.sin((startAngle * Math.PI) / 180)}
    A ${radius} ${radius} 0 ${percentComplete * (endAngle - startAngle) > 180 ? 1 : 0} 1 
    ${center + radius * Math.cos(((startAngle + percentComplete * (endAngle - startAngle)) * Math.PI) / 180)} 
    ${center + radius * Math.sin(((startAngle + percentComplete * (endAngle - startAngle)) * Math.PI) / 180)}
  `;
  
  // Text size based on gauge size
  const textSize = size === 'sm' ? 'text-2xl' : size === 'md' ? 'text-3xl' : 'text-4xl';
  const labelSize = size === 'sm' ? 'text-xs' : size === 'md' ? 'text-sm' : 'text-base';
  
  // Color based on value
  const valueColor = getRiskScoreColor(value);
  
  return (
    <div className={`relative flex items-center justify-center ${className}`}>
      <svg width={svgSize} height={svgSize} viewBox={`0 0 ${svgSize} ${svgSize}`}>
        {/* Background arc */}
        <path
          d={arcPath}
          fill="none"
          stroke="rgba(255, 255, 255, 0.1)"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
        
        {/* Foreground arc (progress) */}
        <path
          d={progressPath}
          fill="none"
          className={`${valueColor}`}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          style={{ 
            transition: 'all 1s ease-in-out',
            filter: 'drop-shadow(0 0 6px currentColor)' 
          }}
        />
        
        {/* Value indicator */}
        {showValue && (
          <text
            x="50%"
            y="50%"
            textAnchor="middle"
            dominantBaseline="middle"
            className={`${textSize} font-bold ${valueColor}`}
            style={{ filter: 'drop-shadow(0 0 2px rgba(0, 0, 0, 0.5))' }}
          >
            {value}
          </text>
        )}
        
        {/* Label */}
        {label && (
          <text
            x="50%"
            y={center + 20}
            textAnchor="middle"
            dominantBaseline="middle"
            className={`${labelSize} text-muted-foreground`}
          >
            {label}
          </text>
        )}
      </svg>
    </div>
  );
};

export default Gauge;