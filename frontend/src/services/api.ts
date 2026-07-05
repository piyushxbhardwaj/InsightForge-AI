import axios from 'axios';
import type { 
  Session, 
  SessionDetail, 
  CacheCheckResponse, 
  ChatMessage 
} from '../types';

const API_BASE = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  // Check if a completed session exists in SQLite cache
  checkCache: async (companyName: string): Promise<CacheCheckResponse> => {
    const response = await api.get<CacheCheckResponse>(`/sessions/check-cache`, {
      params: { company_name: companyName },
    });
    return response.data;
  },

  // Create a new research session
  createSession: async (
    companyName: string, 
    website: string, 
    researchObjective: string,
    useCache: boolean = true
  ): Promise<Session> => {
    const response = await api.post<Session>(`/sessions`, {
      company_name: companyName,
      website: website,
      research_objective: researchObjective
    }, {
      params: { use_cache: useCache }
    });
    return response.data;
  },

  // List all sessions
  listSessions: async (): Promise<Session[]> => {
    const response = await api.get<Session[]>('/sessions');
    return response.data;
  },

  // Get details of a session (reports, sources, chat, logs)
  getSessionDetails: async (sessionId: string): Promise<SessionDetail> => {
    const response = await api.get<SessionDetail>(`/sessions/${sessionId}`);
    return response.data;
  },

  // Trigger the LangGraph research workflow on the backend
  startWorkflow: async (sessionId: string): Promise<any> => {
    const response = await api.post(`/workflow/${sessionId}`);
    return response.data;
  },

  // Send a chat follow-up query
  sendChatMessage: async (sessionId: string, message: string): Promise<ChatMessage> => {
    const response = await api.post<ChatMessage>(`/chat/${sessionId}`, {
      content: message,
    });
    return response.data;
  },

  // Fetch chat history for a session
  getChatHistory: async (sessionId: string): Promise<ChatMessage[]> => {
    const response = await api.get<ChatMessage[]>(`/chat/${sessionId}`);
    return response.data;
  }
};
