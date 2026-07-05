import React, { useState, useRef, useEffect } from 'react';
import { Send, MessageSquare, ShieldAlert, Loader2 } from 'lucide-react';
import type { ChatMessage } from '../types';
import { apiService } from '../services/api';

interface FollowUpChatProps {
  sessionId: string;
  initialMessages: ChatMessage[];
}

export const FollowUpChat: React.FC<FollowUpChatProps> = ({ sessionId, initialMessages }) => {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  
  const chatEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    setMessages(initialMessages);
  }, [initialMessages]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || loading) return;

    const userText = inputValue.trim();
    setInputValue('');
    setLoading(true);

    // Optimistically add user message to list (will get refreshed by API response or reload)
    const tempUserMsg: ChatMessage = {
      id: Math.random().toString(),
      session_id: sessionId,
      role: 'user',
      content: userText,
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempUserMsg]);

    try {
      const savedAiMsg = await apiService.sendChatMessage(sessionId, userText);
      setMessages(prev => {
        // Remove temp message and append saved user + assistant messages
        // Actually, just append the AI response since we optimistically appended user msg
        return [...prev, savedAiMsg];
      });
    } catch (err) {
      console.error('Failed to send chat message:', err);
      // Append a system error message
      const errorMsg: ChatMessage = {
        id: Math.random().toString(),
        session_id: sessionId,
        role: 'assistant',
        content: '⚠️ Failed to connect to sales assistant. Please check your network and API keys.',
        created_at: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white w-96 border-l border-slate-200">
      {/* Chat Header */}
      <div className="px-5 py-4 border-b border-slate-200 flex items-center gap-2.5">
        <MessageSquare className="h-5 w-5 text-indigo-600" />
        <div>
          <h3 className="font-bold text-slate-800 text-sm">Follow-up Copilot</h3>
          <p className="text-[10px] text-slate-400 flex items-center gap-1">
            <ShieldAlert className="h-3 w-3 text-amber-500" />
            Strictly report context-aware. No hallucinations.
          </p>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50/50">
        {messages.length === 0 && (
          <div className="text-center py-12 px-6">
            <MessageSquare className="h-8 w-8 text-slate-300 mx-auto mb-3" />
            <p className="text-xs text-slate-500 font-medium">Ask questions about this company report.</p>
            <p className="text-[10px] text-slate-400 mt-1 max-w-[200px] mx-auto">
              e.g., "What are their primary risks?" or "What discovery questions are suggested?"
            </p>
          </div>
        )}
        
        {messages.map((msg) => {
          const isUser = msg.role === 'user';
          return (
            <div
              key={msg.id}
              className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}
            >
              <div
                className={`max-w-[85%] px-4 py-2.5 rounded-2xl text-xs leading-relaxed shadow-sm border ${
                  isUser
                    ? 'bg-indigo-600 text-white border-transparent rounded-tr-none'
                    : 'bg-white text-slate-800 border-slate-200/80 rounded-tl-none'
                }`}
              >
                <p className="whitespace-pre-line">{msg.content}</p>
              </div>
              <span className="text-[9px] text-slate-400 mt-1 px-1">
                {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          );
        })}

        {loading && (
          <div className="flex items-start">
            <div className="bg-white border border-slate-200/80 px-4 py-2.5 rounded-2xl rounded-tl-none shadow-sm flex items-center gap-2">
              <Loader2 className="h-3.5 w-3.5 animate-spin text-indigo-600" />
              <span className="text-[11px] text-slate-500">Synthesizing answer...</span>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Chat Input form */}
      <form onSubmit={handleSend} className="p-3 border-t border-slate-200 bg-white">
        <div className="flex items-center gap-2">
          <input
            type="text"
            className="flex-grow px-3 py-2 border border-slate-200 rounded-xl text-xs placeholder-slate-400 focus:outline-none focus:border-indigo-500 transition"
            placeholder="Query report context..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            disabled={loading}
          />
          <button
            type="submit"
            className="p-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-xl transition flex-shrink-0"
            disabled={loading || !inputValue.trim()}
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
      </form>
    </div>
  );
};
