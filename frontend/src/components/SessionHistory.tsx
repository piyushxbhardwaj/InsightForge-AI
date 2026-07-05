import React, { useState } from 'react';
import { Search as SearchIcon, Calendar, CheckCircle2, XCircle, AlertCircle, RefreshCw, Layers } from 'lucide-react';
import { Session } from '../types';

interface SessionHistoryProps {
  sessions: Session[];
  activeSessionId: string | null;
  onSelectSession: (id: string) => void;
  loading: boolean;
}

const statusColors: Record<string, string> = {
  pending: 'bg-slate-100 text-slate-700 border-slate-200',
  planning: 'bg-blue-50 text-blue-700 border-blue-100 animate-pulse',
  researching: 'bg-yellow-50 text-yellow-700 border-yellow-100 animate-pulse',
  analyzing: 'bg-purple-50 text-purple-700 border-purple-100 animate-pulse',
  quality_check: 'bg-orange-50 text-orange-700 border-orange-100 animate-pulse',
  report_generation: 'bg-pink-50 text-pink-700 border-pink-100 animate-pulse',
  completed: 'bg-emerald-50 text-emerald-700 border-emerald-100',
  failed: 'bg-red-50 text-red-700 border-red-100',
};

const statusLabels: Record<string, string> = {
  pending: 'Pending',
  planning: 'Planning',
  researching: 'Researching',
  analyzing: 'Analyzing',
  quality_check: 'Quality Check',
  report_generation: 'Generating Report',
  completed: 'Completed',
  failed: 'Failed',
};

export const SessionHistory: React.FC<SessionHistoryProps> = ({
  sessions,
  activeSessionId,
  onSelectSession,
  loading,
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredSessions = sessions.filter((s) =>
    s.company_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="h-4.5 w-4.5 text-emerald-500" />;
      case 'failed':
        return <XCircle className="h-4.5 w-4.5 text-red-500" />;
      case 'pending':
        return <AlertCircle className="h-4.5 w-4.5 text-slate-400" />;
      default:
        return <RefreshCw className="h-4.5 w-4.5 text-indigo-500 animate-spin" />;
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-900 border-r border-slate-800 text-slate-300 w-80">
      {/* Sidebar Header */}
      <div className="p-5 border-b border-slate-800 flex items-center gap-3">
        <div className="p-2 bg-indigo-600 rounded-lg text-white">
          <Layers className="h-5 w-5" />
        </div>
        <div>
          <h1 className="font-bold text-white text-lg tracking-wide">InsightForge AI</h1>
          <p className="text-xs text-slate-500">Research Copilot Workspace</p>
        </div>
      </div>

      {/* Search Input */}
      <div className="p-4 border-b border-slate-800">
        <div className="relative">
          <SearchIcon className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
          <input
            type="text"
            className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 placeholder-slate-500 text-sm focus:outline-none focus:border-indigo-500 transition duration-200"
            placeholder="Search sessions..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {/* Sessions list */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <RefreshCw className="h-6 w-6 animate-spin text-slate-600" />
          </div>
        ) : filteredSessions.length === 0 ? (
          <div className="text-center py-8 text-sm text-slate-600">
            No research sessions found.
          </div>
        ) : (
          filteredSessions.map((session) => {
            const isActive = session.id === activeSessionId;
            const formattedDate = new Date(session.created_at).toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric',
              year: '2-digit',
            });
            
            return (
              <button
                key={session.id}
                onClick={() => onSelectSession(session.id)}
                className={`w-full text-left p-3.5 rounded-xl border transition-all duration-200 flex flex-col gap-2 ${
                  isActive 
                    ? 'bg-indigo-600/10 border-indigo-500/50 text-white shadow-sm shadow-indigo-500/5' 
                    : 'bg-slate-950/40 border-transparent hover:bg-slate-800/40 text-slate-300'
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <span className={`font-semibold truncate text-sm ${isActive ? 'text-white' : 'text-slate-200'}`}>
                    {session.company_name}
                  </span>
                  {getStatusIcon(session.status)}
                </div>

                <p className="text-xs text-slate-500 line-clamp-1">
                  {session.research_objective}
                </p>

                <div className="flex items-center justify-between mt-1 pt-1.5 border-t border-slate-800/60 text-[10px] text-slate-500">
                  <span className="flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    {formattedDate}
                  </span>
                  <span className={`px-2 py-0.5 rounded-full border ${statusColors[session.status]} font-medium`}>
                    {statusLabels[session.status]}
                  </span>
                </div>
              </button>
            );
          })
        )}
      </div>
    </div>
  );
};
