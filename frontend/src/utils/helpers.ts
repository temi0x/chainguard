/**
 * Format number as currency
 */
export const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    notation: 'compact',
    maximumFractionDigits: 2,
  }).format(value);
};

/**
 * Format number as percentage
 */
export const formatPercent = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'percent',
    minimumFractionDigits: 0,
    maximumFractionDigits: 1,
  }).format(value / 100);
};

/**
 * Format date to relative time (e.g. "2 hours ago")
 */
export const formatRelativeTime = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const diffInMs = now.getTime() - date.getTime();
  const diffInSec = Math.floor(diffInMs / 1000);
  const diffInMin = Math.floor(diffInSec / 60);
  const diffInHour = Math.floor(diffInMin / 60);
  const diffInDay = Math.floor(diffInHour / 24);

  if (diffInSec < 60) {
    return `${diffInSec} seconds ago`;
  }
  if (diffInMin < 60) {
    return `${diffInMin} minute${diffInMin === 1 ? '' : 's'} ago`;
  }
  if (diffInHour < 24) {
    return `${diffInHour} hour${diffInHour === 1 ? '' : 's'} ago`;
  }
  if (diffInDay < 30) {
    return `${diffInDay} day${diffInDay === 1 ? '' : 's'} ago`;
  }

  return date.toLocaleDateString();
};

/**
 * Get risk category color
 */
export const getRiskCategoryColor = (category: 'Low' | 'Medium' | 'High'): string => {
  switch (category) {
    case 'Low':
      return 'text-success bg-success/10';
    case 'Medium':
      return 'text-warning bg-warning/10';
    case 'High':
      return 'text-destructive bg-destructive/10';
    default:
      return 'text-muted-foreground bg-muted/10';
  }
};

/**
 * Get risk score color
 */
export const getRiskScoreColor = (score: number): string => {
  if (score < 30) {
    return 'text-success';
  }
  if (score < 60) {
    return 'text-warning';
  }
  return 'text-destructive';
};

/**
 * Get alert severity color
 */
export const getAlertSeverityColor = (severity: 'Low' | 'Medium' | 'High' | 'Critical'): string => {
  switch (severity) {
    case 'Low':
      return 'bg-success/10 text-success';
    case 'Medium':
      return 'bg-warning/10 text-warning';
    case 'High':
      return 'bg-destructive/10 text-destructive';
    case 'Critical':
      return 'bg-destructive text-destructive-foreground';
    default:
      return 'bg-muted/10 text-muted-foreground';
  }
};

/**
 * Truncate text with ellipsis
 */
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return `${text.slice(0, maxLength)}...`;
};