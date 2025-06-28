import React from "react";

type BadgeVariant =
  | "default"
  | "success"
  | "warning"
  | "destructive"
  | "secondary"
  | "outline";

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = "default",
  className = "",
}) => {
  const baseClasses =
    "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors";

  const variantClasses = {
    default: "bg-primary text-primary-foreground",
    success: "bg-success text-success-foreground",
    warning: "bg-warning text-warning-foreground",
    destructive: "bg-destructive text-destructive-foreground",
    secondary: "bg-secondary text-secondary-foreground",
    outline:
      "border border-input bg-background text-foreground hover:bg-accent hover:text-accent-foreground",
  };

  return (
    <div className={`${baseClasses} ${variantClasses[variant]} ${className}`}>
      {children}
    </div>
  );
};
