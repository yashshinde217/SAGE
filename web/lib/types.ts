export interface SourceMeta {
  source_file: string | null;
  page_number: number | null;
  chunk_id: string;
  text: string;
}

export interface ChatResponse {
  response: string;
  model: string;
  processing_time: number;
  sources: SourceMeta[];
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: SourceMeta[];
  processingTime?: number;
}

export interface SystemStatus {
  cpu_percent: number;
  ram_used_gb: number;
  ram_total_gb: number;
  ram_percent: number;
}
