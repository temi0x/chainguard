import React from 'react';
import { getRiskCategoryColor } from '../../utils/helpers';

interface RiskBadgeProps {
  category: 'Low' | 'Medium' | 'High';
  className?: string;
}

const RiskBadge: React.FC<RiskBadgeProps> = ({ category, className = '' }) => {
  const colorClasses = getRiskCategoryColor(category);
  
  return (
    <div className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${colorClasses} ${className}`}>
      {category} Risk
    </div>
  );
};

export default RiskBadge;