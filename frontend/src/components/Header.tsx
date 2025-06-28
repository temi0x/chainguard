import React, { useState, useEffect } from "react";
import { Shield, Menu, X, Wallet } from "lucide-react";
import { Link, useLocation } from "react-router-dom";
import { useAccount } from "wagmi";
import Button from "./ui/Button";
import ThemeToggle from "./ui/ThemeToggle";
import { Badge } from "./ui/Badge";

const Header: React.FC = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { isConnected, address } = useAccount();
  const location = useLocation();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };

    window.addEventListener("scroll", handleScroll);
    return () => {
      window.removeEventListener("scroll", handleScroll);
    };
  }, []);

  const formatAddress = (addr: string) => {
    return `${addr.slice(0, 6)}...${addr.slice(-4)}`;
  };

  const navItems = [
    { name: "Home", path: "/" },
    { name: "Dashboard", path: "/dashboard" },
    { name: "Insights", path: "/insights" },
    { name: "Compare", path: "/compare" },
  ];

  const isActivePath = (path: string) => {
    if (path === "/") {
      return location.pathname === "/";
    }
    return location.pathname.startsWith(path);
  };

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled
          ? "bg-background/80 backdrop-blur-lg shadow-md"
          : "bg-transparent"
      }`}
    >
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center">
            <div className="mr-2 flex h-9 w-9 items-center justify-center rounded-full bg-primary">
              <Shield className="h-5 w-5 text-primary-foreground" />
            </div>
            <div className="font-bold text-lg">ChainGuard AI</div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-6">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`text-sm font-medium transition-colors hover:text-primary ${
                  isActivePath(item.path)
                    ? "text-primary"
                    : "text-muted-foreground"
                }`}
              >
                {item.name}
              </Link>
            ))}
          </nav>

          <div className="hidden md:flex items-center space-x-2">
            <ThemeToggle />
            {isConnected && address && (
              <div className="flex items-center gap-2">
                <Badge variant="success" className="flex items-center gap-1">
                  <Wallet className="h-3 w-3" />
                  {formatAddress(address)}
                </Badge>
              </div>
            )}
            <Link to="/dashboard">
              <Button variant="primary" size="sm">
                {isConnected ? "Dashboard" : "Connect Wallet"}
              </Button>
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? (
              <X className="h-6 w-6" />
            ) : (
              <Menu className="h-6 w-6" />
            )}
          </button>
        </div>

        {/* Mobile Navigation */}
        {isMobileMenuOpen && (
          <div className="md:hidden mt-4 py-4 px-2 rounded-lg bg-card border border-border">
            <nav className="flex flex-col space-y-3">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`text-sm font-medium p-2 rounded-md transition-colors ${
                    isActivePath(item.path)
                      ? "bg-muted text-primary"
                      : "text-muted-foreground hover:bg-muted/50"
                  }`}
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  {item.name}
                </Link>
              ))}

              <div className="pt-2 flex flex-col space-y-2">
                <ThemeToggle className="justify-center" />
                {isConnected && address && (
                  <Badge
                    variant="success"
                    className="flex items-center justify-center gap-1"
                  >
                    <Wallet className="h-3 w-3" />
                    {formatAddress(address)}
                  </Badge>
                )}
                <Link to="/dashboard">
                  <Button
                    variant="primary"
                    size="sm"
                    className="justify-center w-full"
                  >
                    {isConnected ? "Dashboard" : "Connect Wallet"}
                  </Button>
                </Link>
              </div>
            </nav>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
