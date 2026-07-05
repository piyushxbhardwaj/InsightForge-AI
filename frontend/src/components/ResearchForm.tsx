import React, { useState } from 'react';
import { Search, Loader2, Sparkles, RefreshCw } from 'lucide-react';
import { apiService } from '../services/api';

interface ResearchFormProps {
  onSessionCreated: (sessionId: string, triggered: boolean) => void;
}

export const ResearchForm: React.FC<ResearchFormProps> = ({ onSessionCreated }) => {
  const [companyName, setCompanyName] = useState('');
  const [website, setWebsite] = useState('');
  const [objective, setObjective] = useState('');
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  
  // Cache state
  const [cacheHit, setCacheHit] = useState<{ has_cached: boolean; sessionId: string | null } | null>(null);

  const validate = (): boolean => {
    const newErrors: { [key: string]: string } = {};
    if (!companyName.trim()) newErrors.companyName = 'Company name is required';
    if (!website.trim()) {
      newErrors.website = 'Website URL is required';
    } else {
      // Basic domain name check
      const domainRegex = /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?$/;
      if (!domainRegex.test(website.trim())) {
        newErrors.website = 'Please enter a valid website domain (e.g. microsoft.com)';
      }
    }
    if (!objective.trim()) {
      newErrors.objective = 'Research objective is required';
    } else if (objective.trim().length < 5) {
      newErrors.objective = 'Objective must be at least 5 characters long';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleBlurCompanyName = async () => {
    if (!companyName.trim()) return;
    try {
      const res = await apiService.checkCache(companyName.trim());
      if (res.has_cached) {
        setCacheHit({ has_cached: true, sessionId: res.cached_session_id });
      } else {
        setCacheHit(null);
      }
    } catch (err) {
      console.error('Failed to check cache:', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent, forceNew: boolean = false) => {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    try {
      const useCache = !forceNew && !!(cacheHit && cacheHit.has_cached);
      
      const cleanWebsite = website.replace(/^(https?:\/\/)?(www\.)?/, '').split('/')[0];
      
      const session = await apiService.createSession(
        companyName.trim(),
        cleanWebsite,
        objective.trim(),
        useCache
      );

      // If we reused a cache hit, we directly return the completed session.
      // Otherwise, we need to trigger the workflow.
      const triggered = !useCache;
      if (triggered) {
        // Trigger workflow in background
        await apiService.startWorkflow(session.id);
      }
      
      onSessionCreated(session.id, triggered);
      
      // Clear form
      setCompanyName('');
      setWebsite('');
      setObjective('');
      setCacheHit(null);
    } catch (err: any) {
      console.error(err);
      setErrors({ api: err.response?.data?.detail || 'Failed to create research session.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 md:p-8 max-w-2xl mx-auto backdrop-blur-md bg-white/95">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2.5 bg-indigo-50 rounded-xl text-indigo-600">
          <Sparkles className="h-6 w-6" />
        </div>
        <div>
          <h2 className="text-xl font-semibold text-slate-800">Launch New Research</h2>
          <p className="text-sm text-slate-500">Provide company details to start an automated LangGraph analysis.</p>
        </div>
      </div>

      <form onSubmit={(e) => handleSubmit(e, false)} className="space-y-5">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Company Name</label>
          <input
            type="text"
            className={`w-full px-4 py-2.5 rounded-xl border ${errors.companyName ? 'border-red-400 focus:ring-red-200' : 'border-slate-200 focus:ring-indigo-200'} focus:outline-none focus:ring-4 transition duration-200`}
            placeholder="e.g. Microsoft"
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            onBlur={handleBlurCompanyName}
            disabled={loading}
          />
          {errors.companyName && <p className="text-xs text-red-500 mt-1">{errors.companyName}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Website URL / Domain</label>
          <input
            type="text"
            className={`w-full px-4 py-2.5 rounded-xl border ${errors.website ? 'border-red-400 focus:ring-red-200' : 'border-slate-200 focus:ring-indigo-200'} focus:outline-none focus:ring-4 transition duration-200`}
            placeholder="e.g. microsoft.com"
            value={website}
            onChange={(e) => setWebsite(e.target.value)}
            disabled={loading}
          />
          {errors.website && <p className="text-xs text-red-500 mt-1">{errors.website}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Research Objective</label>
          <textarea
            rows={4}
            className={`w-full px-4 py-2.5 rounded-xl border ${errors.objective ? 'border-red-400 focus:ring-red-200' : 'border-slate-200 focus:ring-indigo-200'} focus:outline-none focus:ring-4 transition duration-200 resize-none`}
            placeholder="e.g. Understand their current cloud operations, identify challenges in scaling their Sales CRM integrations, and prepare discovery questions for the director of Sales Engineering."
            value={objective}
            onChange={(e) => setObjective(e.target.value)}
            disabled={loading}
          />
          {errors.objective && <p className="text-xs text-red-500 mt-1">{errors.objective}</p>}
        </div>

        {errors.api && (
          <div className="p-3 bg-red-50 text-red-700 text-sm rounded-xl border border-red-100">
            {errors.api}
          </div>
        )}

        {cacheHit && cacheHit.has_cached && (
          <div className="p-4 bg-emerald-50 rounded-xl border border-emerald-100 flex flex-col gap-2">
            <p className="text-sm font-medium text-emerald-800">
              💡 Cache Hit: We have recently completed research for "{companyName}".
            </p>
            <div className="flex gap-3 mt-1">
              <button
                type="submit"
                className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white font-medium text-xs rounded-lg transition"
              >
                Load Instant Cached Report
              </button>
              <button
                type="button"
                onClick={(e) => handleSubmit(e, true)}
                className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium text-xs rounded-lg flex items-center gap-1 transition"
              >
                <RefreshCw className="h-3 w-3" /> Force New Run
              </button>
            </div>
          </div>
        )}

        {!(cacheHit && cacheHit.has_cached) && (
          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-3 rounded-xl transition duration-200 disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                Initializing agent graph...
              </>
            ) : (
              <>
                <Search className="h-5 w-5" />
                Start Research Session
              </>
            )}
          </button>
        )}
      </form>
    </div>
  );
};
