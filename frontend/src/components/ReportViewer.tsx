import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { 
  FileText, 
  ExternalLink, 
  Layers, 
  Target, 
  TrendingUp, 
  AlertTriangle, 
  HelpCircle, 
  Send, 
  BookOpen,
  Calendar,
  Compass
} from 'lucide-react';
import { Report, Source } from '../types';

interface ReportViewerProps {
  report: Report;
  sources: Source[];
}

export const ReportViewer: React.FC<ReportViewerProps> = ({ report, sources }) => {
  const [activeTab, setActiveTab] = useState<'structured' | 'markdown' | 'sources'>('structured');
  
  const getDomain = (urlStr: string): string => {
    try {
      const url = new URL(urlStr);
      return url.hostname.replace('www.', '');
    } catch {
      return 'external-link';
    }
  };

  const getSourceTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'news': return 'bg-sky-50 text-sky-700 border-sky-100';
      case 'blog': return 'bg-amber-50 text-amber-700 border-amber-100';
      case 'press_release': return 'bg-pink-50 text-pink-700 border-pink-100';
      default: return 'bg-slate-50 text-slate-700 border-slate-100';
    }
  };

  // Safe fallback if JSON parsing failed in DB
  const sections = report.json_content || {
    company_overview: "N/A",
    products_services: "N/A",
    target_customers: "N/A",
    business_signals: "N/A",
    risks_challenges: "N/A",
    suggested_discovery_questions: [],
    suggested_outreach_strategy: "N/A",
    unknowns: []
  };

  const questionsList = Array.isArray(sections.suggested_discovery_questions)
    ? sections.suggested_discovery_questions
    : typeof sections.suggested_discovery_questions === 'string'
      ? sections.suggested_discovery_questions.split('\n').filter(Boolean).map(q => q.replace(/^\d+\.\s*/, ''))
      : [];

  const unknownsList = Array.isArray(sections.unknowns)
    ? sections.unknowns
    : typeof sections.unknowns === 'string'
      ? sections.unknowns.split('\n').filter(Boolean).map(u => u.replace(/^-\s*/, ''))
      : [];

  return (
    <div className="flex flex-col h-full bg-slate-50 border-r border-slate-200">
      {/* Top Navbar tabs */}
      <div className="flex items-center justify-between px-6 py-4 bg-white border-b border-slate-200/80">
        <div>
          <h2 className="text-lg font-bold text-slate-800 flex items-center gap-2">
            <FileText className="h-5 w-5 text-indigo-600" />
            AI Intelligence Report
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Confidence score: {(report.confidence_score * 100).toFixed(0)}% | Compiled via LangGraph
          </p>
        </div>

        {/* Tab Buttons */}
        <div className="flex bg-slate-100 p-1 rounded-xl">
          <button
            onClick={() => setActiveTab('structured')}
            className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === 'structured' 
                ? 'bg-white text-slate-900 shadow-sm' 
                : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            Dashboard
          </button>
          <button
            onClick={() => setActiveTab('markdown')}
            className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === 'markdown' 
                ? 'bg-white text-slate-900 shadow-sm' 
                : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            Markdown
          </button>
          <button
            onClick={() => setActiveTab('sources')}
            className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === 'sources' 
                ? 'bg-white text-slate-900 shadow-sm' 
                : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            Sources ({sources.length})
          </button>
        </div>
      </div>

      {/* Main View Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {activeTab === 'structured' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* Overview - Span full width */}
            <div className="bg-white p-6 rounded-2xl border border-slate-200/60 shadow-sm md:col-span-2">
              <div className="flex items-center gap-2.5 mb-3 text-indigo-700 font-bold text-sm uppercase tracking-wider">
                <Compass className="h-4 w-4" />
                Company Overview
              </div>
              <p className="text-slate-700 leading-relaxed text-sm whitespace-pre-line">
                {sections.company_overview}
              </p>
            </div>

            {/* Products & Services */}
            <div className="bg-white p-6 rounded-2xl border border-slate-200/60 shadow-sm flex flex-col">
              <div className="flex items-center gap-2.5 mb-3 text-indigo-700 font-bold text-sm uppercase tracking-wider">
                <Layers className="h-4 w-4" />
                Products & Services
              </div>
              <div className="text-slate-700 text-sm whitespace-pre-line leading-relaxed flex-1">
                {sections.products_services}
              </div>
            </div>

            {/* Target Customers */}
            <div className="bg-white p-6 rounded-2xl border border-slate-200/60 shadow-sm flex flex-col">
              <div className="flex items-center gap-2.5 mb-3 text-indigo-700 font-bold text-sm uppercase tracking-wider">
                <Target className="h-4 w-4" />
                Target Customers
              </div>
              <div className="text-slate-700 text-sm whitespace-pre-line leading-relaxed flex-1">
                {sections.target_customers}
              </div>
            </div>

            {/* Business Signals */}
            <div className="bg-white p-6 rounded-2xl border border-slate-200/60 shadow-sm flex flex-col">
              <div className="flex items-center gap-2.5 mb-3 text-indigo-700 font-bold text-sm uppercase tracking-wider">
                <TrendingUp className="h-4 w-4" />
                Business Signals
              </div>
              <div className="text-slate-700 text-sm whitespace-pre-line leading-relaxed flex-1">
                {sections.business_signals}
              </div>
            </div>

            {/* Risks & Challenges */}
            <div className="bg-white p-6 rounded-2xl border border-slate-200/60 shadow-sm flex flex-col">
              <div className="flex items-center gap-2.5 mb-3 text-red-700 font-bold text-sm uppercase tracking-wider">
                <AlertTriangle className="h-4 w-4" />
                Risks & Challenges
              </div>
              <div className="text-slate-700 text-sm whitespace-pre-line leading-relaxed flex-1">
                {sections.risks_challenges}
              </div>
            </div>

            {/* Discovery Questions */}
            <div className="bg-white p-6 rounded-2xl border border-slate-200/60 shadow-sm md:col-span-2">
              <div className="flex items-center gap-2.5 mb-4 text-indigo-700 font-bold text-sm uppercase tracking-wider">
                <HelpCircle className="h-4 w-4" />
                Suggested Discovery Questions
              </div>
              <ul className="space-y-3">
                {questionsList.map((q, idx) => (
                  <li key={idx} className="flex gap-3 text-sm text-slate-700 items-start">
                    <span className="flex items-center justify-center h-5 w-5 bg-indigo-50 text-indigo-600 rounded-md font-semibold text-xs mt-0.5">
                      {idx + 1}
                    </span>
                    <span className="flex-1 leading-relaxed">{q}</span>
                  </li>
                ))}
                {questionsList.length === 0 && (
                  <p className="text-sm text-slate-500">None parsed. Refer to full markdown report.</p>
                )}
              </ul>
            </div>

            {/* Outreach Strategy */}
            <div className="bg-white p-6 rounded-2xl border border-slate-200/60 shadow-sm md:col-span-2">
              <div className="flex items-center gap-2.5 mb-3 text-indigo-700 font-bold text-sm uppercase tracking-wider">
                <Send className="h-4 w-4" />
                Suggested Outreach Strategy
              </div>
              <p className="text-slate-700 leading-relaxed text-sm whitespace-pre-line">
                {sections.suggested_outreach_strategy}
              </p>
            </div>

            {/* Unknowns */}
            {unknownsList.length > 0 && (
              <div className="bg-white p-6 rounded-2xl border border-slate-200/60 shadow-sm md:col-span-2">
                <div className="flex items-center gap-2.5 mb-3 text-slate-700 font-bold text-sm uppercase tracking-wider">
                  <BookOpen className="h-4 w-4" />
                  Unknowns & Missing Data
                </div>
                <ul className="list-disc pl-5 space-y-1.5 text-sm text-slate-700 leading-relaxed">
                  {unknownsList.map((u, idx) => (
                    <li key={idx}>{u}</li>
                  ))}
                </ul>
              </div>
            )}

          </div>
        )}

        {activeTab === 'markdown' && (
          <div className="bg-white p-6 md:p-8 rounded-2xl border border-slate-200/60 shadow-sm prose prose-slate max-w-none text-slate-700">
            <ReactMarkdown className="markdown-content space-y-4">
              {report.markdown_content}
            </ReactMarkdown>
          </div>
        )}

        {activeTab === 'sources' && (
          <div className="space-y-4">
            <h3 className="font-semibold text-slate-800 text-sm">Validated Search Findings ({sources.length})</h3>
            <div className="grid grid-cols-1 gap-4">
              {sources.map((source) => (
                <div 
                  key={source.id} 
                  className="bg-white p-5 rounded-2xl border border-slate-200/60 shadow-sm flex flex-col gap-2 hover:border-indigo-100 transition duration-200"
                >
                  <div className="flex items-start justify-between gap-3">
                    <a 
                      href={source.url} 
                      target="_blank" 
                      rel="noreferrer"
                      className="font-semibold text-slate-900 hover:text-indigo-600 flex items-center gap-1.5 text-sm"
                    >
                      {source.title}
                      <ExternalLink className="h-3.5 w-3.5 flex-shrink-0" />
                    </a>
                    
                    <span className="text-[10px] text-slate-400 font-mono">
                      Relevance: {(source.relevance_score * 100).toFixed(0)}%
                    </span>
                  </div>

                  <p className="text-xs text-slate-500 line-clamp-3 leading-relaxed mt-1">
                    {source.content}
                  </p>

                  <div className="flex items-center gap-3 mt-2 text-[10px] text-slate-400 border-t border-slate-100 pt-2.5">
                    <span className="flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      {source.published_date || 'Date unknown'}
                    </span>
                    <span className="text-slate-300">|</span>
                    <span className="font-mono bg-slate-50 px-2 py-0.5 rounded border border-slate-100">
                      {getDomain(source.url)}
                    </span>
                    <span className="text-slate-300">|</span>
                    <span className={`px-2 py-0.5 rounded border ${getSourceTypeColor(source.source_type)} font-medium`}>
                      {source.source_type}
                    </span>
                  </div>
                </div>
              ))}
              
              {sources.length === 0 && (
                <div className="text-center py-8 text-sm text-slate-500">
                  No sources recorded for this research session.
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
