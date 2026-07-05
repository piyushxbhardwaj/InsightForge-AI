export interface Session {
  id: string;
  company_name: string;
  website: string;
  research_objective: string;
  status: 'pending' | 'planning' | 'researching' | 'analyzing' | 'quality_check' | 'report_generation' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
}

export interface Source {
  id: string;
  session_id: string;
  title: string;
  url: string;
  published_date: string | null;
  source_type: string;
  content: string;
  relevance_score: number;
  created_at: string;
}

export interface Report {
  id: string;
  session_id: string;
  markdown_content: string;
  json_content: Record<string, any> | null;
  confidence_score: number;
  created_at: string;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export interface WorkflowLog {
  id: string;
  session_id: string;
  node_name: string;
  status: 'started' | 'completed' | 'failed';
  execution_time_seconds: number;
  checkpoint_data: Record<string, any> | null;
  message: string | null;
  created_at: string;
}

export interface SessionDetail extends Session {
  reports: Report[];
  sources: Source[];
  workflow_logs: WorkflowLog[];
  chat_messages: ChatMessage[];
}

export interface CacheCheckResponse {
  has_cached: boolean;
  cached_session_id: string | null;
  company_name: string;
  created_at: string | null;
}
