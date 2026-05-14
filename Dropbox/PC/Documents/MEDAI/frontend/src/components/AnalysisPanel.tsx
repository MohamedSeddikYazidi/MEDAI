"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "@/lib/auth-context";
import { agentAPI } from "@/lib/api";

const analysisTypes = [
  { id: "full_analysis", label: "Full Analysis", icon: "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" },
  { id: "diagnosis", label: "Diagnosis", icon: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" },
  { id: "risk_prediction", label: "Risk Prediction", icon: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" },
  { id: "knowledge_search", label: "Knowledge Search", icon: "M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" },
  { id: "treatment", label: "Treatment", icon: "M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" },
];

export default function AnalysisPanel() {
  const { token } = useAuth();
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [analysisType, setAnalysisType] = useState("full_analysis");

  const runAnalysis = async () => {
    if (!query.trim() || loading || !token) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await agentAPI.analyze(query, token, { query_type: analysisType });
      setResult(res);
    } catch (err: any) {
      setResult({ status: "error", data: { error: err.message } });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-2xl md:text-3xl font-bold">Multi-Agent Analysis</h1>
        <p className="text-slate-400 text-sm mt-1">Run the full AI agent pipeline on patient data</p>
      </motion.div>

      {/* Input Section */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="glass-card p-6 space-y-5"
      >
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-3">Analysis Type</label>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-2">
            {analysisTypes.map((t) => (
              <button
                key={t.id}
                onClick={() => setAnalysisType(t.id)}
                className={`flex flex-col items-center gap-2 p-3 rounded-xl text-xs font-medium transition-all ${
                  analysisType === t.id
                    ? "bg-blue-500/20 text-blue-400 border border-blue-500/40 shadow-lg shadow-blue-500/10"
                    : "bg-white/5 text-slate-400 hover:text-white hover:bg-white/10 border border-transparent"
                }`}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={t.icon} />
                </svg>
                <span className="text-center leading-tight">{t.label}</span>
              </button>
            ))}
          </div>
        </div>

        <div>
          <label htmlFor="analysis-input" className="block text-sm font-medium text-slate-300 mb-2">
            Patient Information
          </label>
          <textarea
            id="analysis-input"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Example: 65-year-old male with diabetes, presenting with fatigue, frequent urination, blurred vision, and numbness in extremities. Currently on metformin and insulin. History of hypertension."
            className="w-full h-40 bg-white/5 border border-white/10 rounded-xl p-4 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50 focus:ring-2 focus:ring-blue-500/20 resize-none transition-all"
          />
        </div>

        <button
          id="run-analysis"
          onClick={runAnalysis}
          disabled={loading || !query.trim()}
          className="w-full md:w-auto px-8 py-3 rounded-xl font-semibold text-white transition-all disabled:opacity-30 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-blue-500/25 active:scale-[0.98] flex items-center justify-center gap-2"
          style={{ background: "linear-gradient(135deg, #3b82f6, #8b5cf6)" }}
        >
          {loading ? (
            <>
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              <span>Agents Processing...</span>
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <span>Run Analysis</span>
            </>
          )}
        </button>
      </motion.div>

      {/* Results */}
      <AnimatePresence>
        {result && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }} 
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-4"
          >
            {result.status === "error" ? (
              <div className="glass-card p-6 border-rose-500/30">
                <div className="flex items-start gap-3">
                  <svg className="w-6 h-6 text-rose-400 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div>
                    <p className="text-rose-400 font-semibold">Error</p>
                    <p className="text-sm text-slate-300 mt-1">{result.data?.error}</p>
                    <p className="text-xs text-slate-500 mt-2">Make sure the backend is running on port 8000</p>
                  </div>
                </div>
              </div>
            ) : (
              <>
                {/* Summary */}
                <div className="glass-card p-6">
                  <div className="flex items-center gap-2 mb-3">
                    <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <h3 className="text-sm font-semibold text-blue-400">Analysis Summary</h3>
                  </div>
                  <p className="text-sm text-slate-300 leading-relaxed">{result.data?.summary || result.reasoning}</p>
                  {result.confidence > 0 && (
                    <div className="mt-4 p-3 bg-white/5 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs text-slate-400 font-medium">Confidence Level</span>
                        <span className="text-sm font-bold">{(result.confidence * 100).toFixed(0)}%</span>
                      </div>
                      <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${result.confidence * 100}%` }}
                          transition={{ duration: 0.8, ease: "easeOut" }}
                          className="h-full rounded-full"
                          style={{ background: result.confidence > 0.7 ? "linear-gradient(90deg, #10b981, #059669)" : result.confidence > 0.4 ? "linear-gradient(90deg, #f59e0b, #d97706)" : "linear-gradient(90deg, #f43f5e, #e11d48)" }}
                        />
                      </div>
                    </div>
                  )}
                </div>

                {/* Detailed results */}
                <div className="glass-card p-6">
                  <div className="flex items-center gap-2 mb-3">
                    <svg className="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <h3 className="text-sm font-semibold text-emerald-400">Detailed Results</h3>
                  </div>
                  <pre className="text-xs text-slate-400 overflow-x-auto whitespace-pre-wrap max-h-96 overflow-y-auto p-4 bg-black/20 rounded-lg border border-white/5">
                    {JSON.stringify(result.data, null, 2)}
                  </pre>
                </div>

                {/* Sources */}
                {result.sources?.length > 0 && (
                  <div className="glass-card p-6">
                    <div className="flex items-center gap-2 mb-3">
                      <svg className="w-5 h-5 text-violet-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                      </svg>
                      <h3 className="text-sm font-semibold text-violet-400">Sources Cited</h3>
                    </div>
                    <div className="space-y-2">
                      {result.sources.map((s: any, i: number) => (
                        <div key={i} className="flex items-start gap-3 p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-all">
                          <span className="text-blue-400 text-lg">📄</span>
                          <div className="flex-1">
                            <p className="text-sm text-slate-300">{s.title}</p>
                            {s.relevance && (
                              <p className="text-xs text-slate-500 mt-1">{(s.relevance * 100).toFixed(0)}% relevance match</p>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
