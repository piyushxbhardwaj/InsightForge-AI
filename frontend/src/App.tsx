import { useState, useEffect, useRef } from 'react';
import { 
  Sparkles, 
  RefreshCw, 
  Workflow, 
  AlertCircle
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

import type { Session, SessionDetail } from './types';
import { apiService } from './services/api';
import { SessionHistory } from './components/SessionHistory';
import { ResearchForm } from './components/ResearchForm';
import { WorkflowProgress } from './components/WorkflowProgress';
import { ReportViewer } from './components/ReportViewer';
import { FollowUpChat } from './components/FollowUpChat';

function App() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [activeSession, setActiveSession] = useState<SessionDetail | null>(null);
  const [loadingSessions, setLoadingSessions] = useState(false);

  // SSE Stream state
  const [streamMetrics, setStreamMetrics] = useState<Record<string, number>>({});
  const [streamRetryCount, setStreamRetryCount] = useState(0);
  const [streamQualityScore, setStreamQualityScore] = useState(0.0);

  const eventSourceRef = useRef<EventSource | null>(null);
  const connectedSessionIdRef = useRef<string | null>(null);

  // Fetch session list
  const fetchSessions = async () => {
    setLoadingSessions(true);
    try {
      const data = await apiService.listSessions();
      setSessions(data);
    } catch (err) {
      console.error('Failed to fetch sessions:', err);
    } finally {
      setLoadingSessions(false);
    }
  };

  // Fetch details of active session
  const fetchSessionDetails = async (id: string) => {
    try {
      const details = await apiService.getSessionDetails(id);
      setActiveSession(details);
    } catch (err) {
      console.error('Failed to fetch session details:', err);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  // Handle active session changes
  useEffect(() => {
    if (activeSessionId) {
      fetchSessionDetails(activeSessionId);
    } else {
      setActiveSession(null);
    }
  }, [activeSessionId]);

  // Connect to SSE stream helper
  const connectSSE = (sessionId: string) => {
    if (eventSourceRef.current && connectedSessionIdRef.current === sessionId) {
      return;
    }

    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    // Reset stream state
    setStreamMetrics({});
    setStreamRetryCount(0);
    setStreamQualityScore(0.0);

    const sseUrl = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/workflow/${sessionId}/stream`;
    console.log(`Connecting to SSE Stream: ${sseUrl}`);
    const eventSource = new EventSource(sseUrl);
    eventSourceRef.current = eventSource;
    connectedSessionIdRef.current = sessionId;

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('SSE Event:', data);
        
        // Update temporary metrics and status values
        if (data.metrics) setStreamMetrics(data.metrics);
        if (data.retry_count) setStreamRetryCount(data.retry_count);
        if (data.quality_score) setStreamQualityScore(data.quality_score);

        // Update main session status list to animate step transitions
        setSessions(prev => prev.map(s => {
          if (s.id === sessionId) {
            // Map event nodes to DB statuses
            const statusMap: Record<string, string> = {
              planner: 'planning',
              research: 'researching',
              analysis: 'analyzing',
              quality_check: 'quality_check',
              report_generator: 'report_generation',
              completed: 'completed',
              failed: 'failed'
            };
            return { ...s, status: (statusMap[data.node] || s.status) as any };
          }
          return s;
        }));

        setActiveSession(prev => {
          if (!prev) return null;
          const statusMap: Record<string, string> = {
            planner: 'planning',
            research: 'researching',
            analysis: 'analyzing',
            quality_check: 'quality_check',
            report_generator: 'report_generation',
            completed: 'completed',
            failed: 'failed'
          };
          return { ...prev, status: (statusMap[data.node] || prev.status) as any };
        });

        if (data.node === 'completed' || data.node === 'failed') {
          console.log('SSE Stream finished.');
          eventSource.close();
          if (eventSourceRef.current === eventSource) {
            eventSourceRef.current = null;
            connectedSessionIdRef.current = null;
          }
          // Reload all lists and load finalized reports
          fetchSessions();
          fetchSessionDetails(sessionId);
        }
      } catch (err) {
        console.error('Error parsing SSE event:', err);
      }
    };

    eventSource.onerror = (err) => {
      console.error('SSE connection error:', err);
      eventSource.close();
      if (eventSourceRef.current === eventSource) {
        eventSourceRef.current = null;
        connectedSessionIdRef.current = null;
      }
      // Flag session as failed
      setSessions(prev => prev.map(s => s.id === sessionId ? { ...s, status: 'failed' } : s));
      setActiveSession(prev => prev ? { ...prev, status: 'failed' } : null);
    };
  };

  // SSE stream lifecycle manager
  useEffect(() => {
    if (!activeSession) {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
        connectedSessionIdRef.current = null;
      }
      return;
    }
    
    const isRunning = [
      'planning', 
      'researching', 
      'analyzing', 
      'quality_check', 
      'report_generation'
    ].includes(activeSession.status);

    if (!isRunning) {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
        connectedSessionIdRef.current = null;
      }
      return;
    }

    connectSSE(activeSession.id);

    return () => {
      // Clean up connection when the active session changes or component unmounts
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
        connectedSessionIdRef.current = null;
      }
    };
  }, [activeSessionId]);

  // Secondary effect to start SSE connection when status changes to running
  useEffect(() => {
    if (!activeSession) return;

    const isRunning = [
      'planning', 
      'researching', 
      'analyzing', 
      'quality_check', 
      'report_generation'
    ].includes(activeSession.status);

    if (isRunning && !eventSourceRef.current) {
      connectSSE(activeSession.id);
    }
  }, [activeSession?.status]);

  const handleSelectSession = (id: string) => {
    setActiveSessionId(id);
  };

  const handleCreateSession = (id: string, _triggered: boolean) => {
    fetchSessions();
    setActiveSessionId(id);
  };

  const handleBackToDashboard = () => {
    setActiveSessionId(null);
  };

  const handleRetryWorkflow = async () => {
    if (!activeSessionId) return;
    try {
      await apiService.startWorkflow(activeSessionId);
      // Update local state to planning to trigger SSE listener again
      setActiveSession(prev => prev ? { ...prev, status: 'planning' } : null);
    } catch (err) {
      console.error('Failed to restart workflow:', err);
    }
  };

  // Determine current display status mapping
  const currentStatus = activeSession?.status || 'pending';
  const showProgress = [
    'planning', 
    'researching', 
    'analyzing', 
    'quality_check', 
    'report_generation'
  ].includes(currentStatus);

  const hasReport = activeSession && activeSession.reports && activeSession.reports.length > 0;

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden font-sans">
      {/* 1. Sidebar Session History */}
      <SessionHistory
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={handleSelectSession}
        loading={loadingSessions}
      />

      {/* 2. Main Workspace */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Workspace Top Header */}
        <header className="bg-white border-b border-slate-200/80 px-6 py-4 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            {activeSessionId && (
              <button 
                onClick={handleBackToDashboard}
                className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg transition"
              >
                ← Workspace Dashboard
              </button>
            )}
            {!activeSessionId && (
              <div className="flex items-center gap-2">
                <Workflow className="h-5 w-5 text-indigo-600 animate-spin-slow" />
                <h2 className="text-md font-bold text-slate-800">Intelligence Workstation</h2>
              </div>
            )}
          </div>

          <div className="flex items-center gap-2 text-xs text-slate-400">
            <span>Server status:</span>
            <span className="h-2 w-2 rounded-full bg-emerald-500 shadow-sm shadow-emerald-500/50"></span>
            <span className="font-semibold text-emerald-600">Online</span>
          </div>
        </header>

        {/* Workspace Content Panels */}
        <div className="flex-grow overflow-hidden flex">
          <AnimatePresence mode="wait">
            {!activeSessionId ? (
              // Case A: Dashboard Mode - Show Research Form
              <motion.div
                key="dashboard"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="flex-grow overflow-y-auto p-6 md:p-12 flex flex-col justify-start"
              >
                <div className="text-center mb-8 max-w-xl mx-auto">
                  <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight flex items-center justify-center gap-2">
                    <Sparkles className="h-7 w-7 text-indigo-600 animate-pulse" />
                    InsightForge AI
                  </h1>
                  <p className="text-slate-500 text-sm mt-2 leading-relaxed">
                    A production-grade multi-node research assistant. Scrapes websites, extracts market positioning, evaluates confidence levels, and generates target outreach discovery questions.
                  </p>
                </div>
                <ResearchForm onSessionCreated={handleCreateSession} />
              </motion.div>
            ) : showProgress ? (
              // Case B: Researching Progress Mode - SSE visualization
              <motion.div
                key="progress"
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0 }}
                className="flex-grow overflow-y-auto p-6 md:p-12 flex items-center justify-center"
              >
                <WorkflowProgress
                  currentStatus={currentStatus}
                  metrics={streamMetrics}
                  retryCount={streamRetryCount}
                  qualityScore={streamQualityScore}
                />
              </motion.div>
            ) : currentStatus === 'failed' ? (
              // Case C: Error State
              <motion.div
                key="failed"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex-grow flex flex-col items-center justify-center p-8 text-center"
              >
                <div className="p-4 bg-red-50 text-red-600 rounded-full mb-4 border border-red-100">
                  <AlertCircle className="h-10 w-10" />
                </div>
                <h3 className="text-lg font-bold text-slate-800">Workflow Execution Failed</h3>
                <p className="text-slate-500 text-sm mt-1 max-w-sm">
                  The research workflow crashed due to an external service error. Check your API keys and search parameters.
                </p>
                <button
                  onClick={handleRetryWorkflow}
                  className="mt-5 px-5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs rounded-xl shadow-md transition"
                >
                  Retry Execution Loop
                </button>
              </motion.div>
            ) : hasReport ? (
              // Case D: Completed Mode - Show Report Viewer and Follow-Up Chat Side-by-Side!
              <motion.div
                key="workspace-completed"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex-grow flex overflow-hidden"
              >
                {/* Center Panel: Report details */}
                <div className="flex-grow overflow-hidden h-full">
                  <ReportViewer
                    report={activeSession.reports[0]}
                    sources={activeSession.sources}
                  />
                </div>

                {/* Right Panel: Chat Sidebar */}
                <div className="flex-shrink-0 h-full">
                  <FollowUpChat
                    sessionId={activeSession.id}
                    initialMessages={activeSession.chat_messages}
                  />
                </div>
              </motion.div>
            ) : (
              // Case E: Loading/Fallback state
              <div className="flex-grow flex items-center justify-center">
                <RefreshCw className="h-8 w-8 animate-spin text-slate-400" />
              </div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}

export default App;
