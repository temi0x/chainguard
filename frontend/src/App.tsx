import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "./contexts/ThemeContext";
import Header from "./components/Header";
import HomePage from "./pages/HomePage";
import DashboardPage from "./pages/DashboardPage";
import ProtocolDetailPage from "./pages/ProtocolDetailPage";
import InsightsPage from "./pages/InsightsPage";
import ComparePage from "./pages/ComparePage";
import ContractIntegration from "./components/ContractIntegration";

function App() {
  return (
    <ThemeProvider>
      <Router>
        <div className="min-h-screen bg-background text-foreground flex flex-col">
          <Header />
          <main className="flex-1 font-SpaceGrotesk">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route
                path="/protocol/:protocolId"
                element={<ProtocolDetailPage />}
              />
              <Route path="/insights" element={<InsightsPage />} />
              <Route path="/insights/:protocolId" element={<InsightsPage />} />
              <Route path="/compare" element={<ComparePage />} />
              <Route path="/contract" element={<ContractIntegration />} />
            </Routes>
          </main>
          <footer className="border-t border-border">
            <div className="container mx-auto px-4 py-8">
              <div className="flex flex-col md:flex-row justify-between items-center">
                <div className="flex items-center mb-4 md:mb-0">
                  <div className="mr-2 flex h-8 w-8 items-center justify-center rounded-full bg-primary">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      strokeWidth={2}
                      stroke="currentColor"
                      className="h-4 w-4 text-primary-foreground"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z"
                      />
                    </svg>
                  </div>
                  <span className="font-bold">ChainGuard AI</span>
                </div>
                <div className="flex space-x-4 text-sm text-muted-foreground">
                  <a href="#" className="hover:text-primary transition-colors">
                    Privacy
                  </a>
                  <a href="#" className="hover:text-primary transition-colors">
                    Terms
                  </a>
                  <a href="#" className="hover:text-primary transition-colors">
                    Documentation
                  </a>
                  <a href="#" className="hover:text-primary transition-colors">
                    API
                  </a>
                </div>
              </div>
              <div className="mt-4 text-center text-xs text-muted-foreground">
                © {new Date().getFullYear()} ChainGuard AI. All rights reserved.
              </div>
            </div>
          </footer>
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;
