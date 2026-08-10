"use client";

import { useEffect, useState } from "react";
import { Cpu, MemoryStick } from "lucide-react";
import type { SystemStatus } from "@/lib/types";

const STATUS_URL = "http://localhost:8000/api/v1/system/status";
const POLL_INTERVAL_MS = 5000;

export default function TelemetryHUD() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [connected, setConnected] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function poll() {
      try {
        const res = await fetch(STATUS_URL);
        if (!res.ok) throw new Error("bad status");
        const data: SystemStatus = await res.json();
        if (!cancelled) {
          setStatus(data);
          setConnected(true);
        }
      } catch {
        if (!cancelled) setConnected(false);
      }
    }

    poll();
    const interval = setInterval(poll, POLL_INTERVAL_MS);

    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <div className="glass-panel flex items-center gap-4 px-4 py-2 text-[11px] font-mono">
        <div className="flex items-center gap-1.5">
          <span
            className={`h-1.5 w-1.5 rounded-full ${
              connected ? "bg-accent-cyan shadow-glow-cyan" : "bg-red-500"
            }`}
          />
          <span className="text-white/50 uppercase tracking-wider">
            {connected ? "online" : "offline"}
          </span>
        </div>

        {status && (
          <>
            <div className="flex items-center gap-1.5 text-white/70">
              <Cpu size={12} className="text-accent-cyan/70" />
              {status.cpu_percent.toFixed(0)}%
            </div>
            <div className="flex items-center gap-1.5 text-white/70">
              <MemoryStick size={12} className="text-accent-purple/70" />
              {status.ram_used_gb.toFixed(1)}/{status.ram_total_gb.toFixed(1)}GB
            </div>
          </>
        )}
      </div>
    </div>
  );
}
