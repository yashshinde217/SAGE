"use client";

import { motion, AnimatePresence } from "framer-motion";
import { BookOpen, Hash } from "lucide-react";
import type { SourceMeta } from "@/lib/types";

interface DocumentPanelProps {
  sources: SourceMeta[];
}

export default function DocumentPanel({ sources }: DocumentPanelProps) {
  return (
    <div className="flex flex-col h-full glass-panel">
      <div className="px-5 py-4 border-b border-white/10">
        <h2 className="text-sm font-mono tracking-widest text-accent-purple/80 uppercase">
          Knowledge Vault
        </h2>
      </div>

      <div className="flex-1 overflow-y-auto scrollbar-thin px-5 py-4 space-y-3">
        {sources.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-white/30 text-sm font-mono gap-2">
            <BookOpen size={24} className="opacity-40" />
            Retrieved source chunks will appear here.
          </div>
        )}

        <AnimatePresence initial={false}>
          {sources.map((source, idx) => (
            <motion.div
              key={`${source.chunk_id}-${idx}`}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, delay: idx * 0.03 }}
              className="rounded-lg bg-white/[0.03] border border-white/10 p-4"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-mono text-accent-purple/70 truncate">
                  {source.source_file ?? "unknown"}
                </span>
                {source.page_number != null && source.page_number !== -1 && (
                  <span className="flex items-center gap-1 text-[10px] font-mono text-white/40">
                    <Hash size={10} />
                    page {source.page_number}
                  </span>
                )}
              </div>
              <div className="text-[10px] font-mono text-white/25 truncate">
                {source.chunk_id}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}
