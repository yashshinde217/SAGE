"use client";

import { useState } from "react";
import ChatPanel from "@/components/ChatPanel";
import DocumentPanel from "@/components/DocumentPanel";
import TelemetryHUD from "@/components/TelemetryHUD";
import type { SourceMeta } from "@/lib/types";

export default function Home() {
  const [activeSources, setActiveSources] = useState<SourceMeta[]>([]);

  return (
    <main className="h-screen w-screen flex flex-col bg-base-950 overflow-hidden">
      <header className="flex items-center justify-between px-6 py-4 border-b border-white/10">
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-accent-cyan shadow-glow-cyan" />
          <h1 className="text-lg font-mono font-semibold tracking-wide text-white">
            SAGE
          </h1>
          <span className="text-xs font-mono text-white/30">
            Self-Hosted AI for Grounded Explanation
          </span>
        </div>
        <span className="text-xs font-mono text-white/20">
          native · air-gapped
        </span>
      </header>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-4 p-4 overflow-hidden">
        <div className="h-full overflow-hidden">
          <ChatPanel onSourcesSelect={setActiveSources} />
        </div>
        <div className="h-full overflow-hidden">
          <DocumentPanel sources={activeSources} />
        </div>
      </div>

      <TelemetryHUD />
    </main>
  );
}
