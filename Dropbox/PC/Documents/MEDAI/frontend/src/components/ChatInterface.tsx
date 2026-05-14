"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "@/lib/auth-context";
import { chatAPI } from "@/lib/api";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  agent?: string;
  confidence?: number;
  sources?: any[];
  timestamp: Date;
}

export default function ChatInterface() {
  const { token } = useAuth();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "Hello! I'm MedAI, your medical decision support assistant. I can help with:\n\n• **Symptom analysis** and diagnosis\n• **Risk prediction** for readmission\n• **Medical knowledge** search\n• **Treatment recommendations**\n• **Analytics** and insights\n\nHow can I assist you today?",
      agent: "Supervisor Agent",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    
    const userMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };
    
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      if (!token) throw new Error("Not authenticated");
      const res = await chatAPI.send(input, token);
      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: res.response || JSON.stringify(res.data, null, 2),
        agent: res.agent,
        confidence: res.confidence,
        sources: res.sources,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: `⚠️ Error: ${err.message}. Make sure the backend is running on port 8000.`,
          agent: "System",
          timestamp: new Date(),
        },
      ]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] max-h-[900px]">
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card p-4 mb-4 flex items-center justify-between"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center shadow-lg" style={{ background: "linear-gradient(135deg, #3b82f6, #8b5cf6)" }}>
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </div>
          <div>
            <h2 className="font-semibold text-lg">Medical AI Chat</h2>
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <span className="w-2 h-2 rounded-full bg-emerald-500 pulse-glow"></span>
              Multi-Agent System Active
            </div>
          </div>
        </div>
        <button
          onClick={() => setMessages([messages[0]])}
          className="px-3 py-1.5 text-xs font-medium text-slate-400 hover:text-white hover:bg-white/5 rounded-lg transition-all"
          aria-label="Clear chat"
        >
          Clear Chat
        </button>
      </motion.div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-2 mb-4">
        <AnimatePresence>
          {messages.map((msg, index) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div className={`max-w-[85%] md:max-w-[75%] ${msg.role === "user"
                ? "bg-gradient-to-br from-blue-500/20 to-violet-500/20 border border-blue-500/30 rounded-2xl rounded-tr-sm"
                : "glass-card rounded-2xl rounded-tl-sm"} p-4 shadow-lg`}
              >
                {msg.agent && msg.role === "assistant" && (
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-blue-400"></div>
                    <p className="text-[10px] text-blue-400 font-semibold uppercase tracking-wide">{msg.agent}</p>
                  </div>
                )}
                <div className="text-sm whitespace-pre-wrap leading-relaxed" dangerouslySetInnerHTML={{
                  __html: msg.content
                    .replace(/\*\*(.*?)\*\*/g, "<strong class='text-white font-semibold'>$1</strong>")
                    .replace(/\n/g, "<br/>")
                    .replace(/• /g, "<span class='text-blue-400'>•</span> ")
                }} />
                {msg.confidence !== undefined && (
                  <div className="mt-3 pt-3 border-t border-white/5">
                    <div className="flex items-center gap-2 text-[10px] text-slate-500">
                      <span className="font-medium">Confidence:</span>
                      <div className="flex-1 h-1.5 bg-white/5 rounded-full overflow-hidden">
                        <motion.div 
                          initial={{ width: 0 }}
                          animate={{ width: `${msg.confidence * 100}%` }}
                          transition={{ duration: 0.5, delay: 0.2 }}
                          className="h-full rounded-full" 
                          style={{
                            background: msg.confidence > 0.7 ? "#10b981" : msg.confidence > 0.4 ? "#f59e0b" : "#f43f5e",
                          }} 
                        />
                      </div>
                      <span className="font-semibold text-white">{(msg.confidence * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                )}
                <p className="text-[10px] text-slate-600 mt-2">
                  {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {loading && (
          <motion.div 
            initial={{ opacity: 0 }} 
            animate={{ opacity: 1 }} 
            className="flex justify-start"
          >
            <div className="glass-card p-4 rounded-2xl rounded-tl-sm shadow-lg">
              <div className="flex items-center gap-3 text-sm text-slate-400">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                  <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                  <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                </div>
                <span>Agents analyzing...</span>
              </div>
            </div>
          </motion.div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card p-3 flex gap-3 items-end shadow-xl"
      >
        <input
          ref={inputRef}
          id="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Describe symptoms, ask medical questions, or request analysis..."
          className="flex-1 bg-transparent text-sm text-white placeholder-slate-500 focus:outline-none py-2 px-1"
          disabled={loading}
          autoComplete="off"
        />
        <button
          id="chat-send"
          onClick={sendMessage}
          disabled={loading || !input.trim()}
          className="px-5 py-2.5 rounded-xl text-sm font-semibold text-white transition-all
                     disabled:opacity-30 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-blue-500/25 active:scale-95"
          style={{ background: "linear-gradient(135deg, #3b82f6, #8b5cf6)" }}
          aria-label="Send message"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </motion.div>
    </div>
  );
}
