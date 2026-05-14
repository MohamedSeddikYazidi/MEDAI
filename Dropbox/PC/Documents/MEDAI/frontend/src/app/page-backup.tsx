"use client";

import { useState } from "react";
import { AuthProvider, useAuth } from "@/lib/auth-context";
import LoginPage from "@/components/LoginPage";
import Sidebar from "@/components/Sidebar";
import Dashboard from "@/components/Dashboard";
import ChatInterface from "@/components/ChatInterface";
import AnalysisPanel from "@/components/AnalysisPanel";
import { motion, AnimatePresence } from "framer-motion";

function AppContent() {
  const { user, isLoading } = useAuth();
  const [activeTab, setActiveTab] = useState("dashboard");

  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
          className="w-16 h-16 border-4 border-blue-500/20 border-t-blue-500 rounded-full"
        />
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="text-slate-400 text-sm"
        >
          Loading MedAI...
        </motion.p>
      </div>
    );
  }

  if (!user) {
    return <LoginPage onLogin={() => {}} />;
  }

  const renderContent = () => {
    switch (activeTab) {
      case "dashboard":
        return <Dashboard type="dashboard" />;
      case "predictive":
        return <Dashboard type="predictive" />;
      case "clinical":
        return <Dashboard type="clinical" />;
      case "operational":
        return <Dashboard type="operational" />;
      case "chat":
        return <ChatInterface />;
      case "analyze":
        return <AnalysisPanel />;
      default:
        return <Dashboard type="dashboard" />;
    }
  };

  return (
    <div className="flex min-h-screen bg-gradient-to-br from-slate-950 via-blue-950/20 to-slate-950">
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
      <main className="flex-1 p-4 md:p-6 lg:p-8 overflow-y-auto">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.2, ease: "easeInOut" }}
          >
            {renderContent()}
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
}

export default function Home() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
