"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Send, Loader2, FileText } from "lucide-react";
import { cn } from "@/lib/utils";
import type { ChatMessage, ChatResponse, SourceMeta } from "@/lib/types";

const API_URL = "http://localhost:8000/api/v1/chat/generate";

interface ChatPanelProps {
  onSourcesSelect: (sources: SourceMeta[]) => void;
}

export default function ChatPanel({ onSourcesSelect }: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages]);

  async function handleSend() {
    const trimmed = input.trim();
    if (!trimmed || loading) return;

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: trimmed,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: trimmed }),
      });

      if (!res.ok) {
        throw new Error(`Request failed: ${res.status}`);
      }

      const data: ChatResponse = await res.json();

      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: data.response,
        sources: data.sources,
        processingTime: data.processing_time,
      };

      setMessages((prev) => [...prev, assistantMessage]);
      if (data.sources?.length) {
        onSourcesSelect(data.sources);
      }
    } catch (err) {
      const errorMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content:
          "⚠️ Could not reach SAGE backend. Confirm the API is running on `localhost:8000`.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="flex flex-col h-full glass-panel">
      <div className="px-5 py-4 border-b border-white/10">
        <h2 className="text-sm font-mono tracking-widest text-accent-cyan/80 uppercase">
          SAGE // Chat
        </h2>
      </div>

      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto scrollbar-thin px-5 py-4 space-y-4"
      >
        {messages.length === 0 && (
          <div className="h-full flex items-center justify-center text-white/30 text-sm font-mono">
            Ask SAGE about your ingested documents.
          </div>
        )}

        <AnimatePresence initial={false}>
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.25 }}
              className={cn(
                "flex",
                msg.role === "user" ? "justify-end" : "justify-start",
              )}
            >
              <div
                className={cn(
                  "max-w-[85%] rounded-xl px-4 py-3 text-sm leading-relaxed",
                  msg.role === "user"
                    ? "bg-accent-cyan/10 border border-accent-cyan/20 text-white"
                    : "bg-white/5 border border-white/10 text-white/90",
                )}
              >
                <div className="prose prose-invert prose-sm max-w-none prose-p:my-1">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {msg.content}
                  </ReactMarkdown>
                </div>

                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {msg.sources.map((source) => (
                      <button
                        key={source.chunk_id}
                        onClick={() => onSourcesSelect([source])}
                        className="source-chip"
                      >
                        <FileText size={12} />
                        {source.source_file ?? "unknown"}
                        {source.page_number != null && source.page_number !== -1
                          ? ` · p.${source.page_number}`
                          : ""}
                      </button>
                    ))}
                  </div>
                )}

                {msg.processingTime != null && (
                  <div className="mt-2 text-[10px] font-mono text-white/30">
                    {msg.processingTime}s
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {loading && (
          <div className="flex items-center gap-2 text-white/40 text-sm font-mono">
            <Loader2 size={14} className="animate-spin" />
            Retrieving & generating...
          </div>
        )}
      </div>

      <div className="p-4 border-t border-white/10">
        <div className="flex items-end gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about your documents..."
            rows={1}
            className="glass-input flex-1 resize-none px-4 py-3 text-sm text-white placeholder:text-white/30"
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="glow-button p-3 disabled:opacity-30 disabled:hover:shadow-none"
          >
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
