import React from 'react';
import { motion } from 'framer-motion';
import { Check, Loader2, Play, AlertTriangle } from 'lucide-react';

interface ProgressStep {
  key: string;
  label: string;
  description: string;
}

const steps: ProgressStep[] = [
  { key: 'planning', label: '1. Planner Node', description: 'Formulating research strategy and search queries' },
  { key: 'researching', label: '2. Research Node', description: 'Executing web searches and collecting source content' },
  { key: 'analyzing', label: '3. Analysis Node', description: 'Extracting key signals, risks, and products' },
  { key: 'quality_check', label: '4. Quality Check', description: 'Assessing accuracy, freshness, and completeness' },
  { key: 'report_generation', label: '5. Report Generator', description: 'Drafting structured markdown and storing metadata' },
];

interface WorkflowProgressProps {
  currentStatus: string;
  metrics: Record<string, number>;
  retryCount: number;
  qualityScore: number;
}

export const WorkflowProgress: React.FC<WorkflowProgressProps> = ({
  currentStatus,
  metrics,
  retryCount,
  qualityScore,
}) => {
  const getStepStatus = (stepKey: string): 'completed' | 'active' | 'pending' | 'failed' => {
    if (currentStatus === 'failed') return 'failed';
    if (currentStatus === 'completed') return 'completed';

    const statusOrder = ['planning', 'researching', 'analyzing', 'quality_check', 'report_generation'];
    const currentIdx = statusOrder.indexOf(currentStatus);
    const stepIdx = statusOrder.indexOf(stepKey);

    if (stepIdx < currentIdx) return 'completed';
    if (stepIdx === currentIdx) return 'active';
    return 'pending';
  };

  const getStepTime = (stepKey: string): string => {
    // Map status key to execution timing label
    const mapped: Record<string, string> = {
      planning: 'planner',
      researching: 'research',
      analyzing: 'analyzing',
      quality_check: 'quality_check',
      report_generation: 'report_generation',
    };
    const metricKey = mapped[stepKey];
    const timeVal = metrics[metricKey];
    return timeVal ? `${timeVal}s` : '';
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 md:p-8 max-w-xl mx-auto">
      <div className="mb-6 text-center">
        <h2 className="text-xl font-bold text-slate-800">Researching Company Intelligence</h2>
        <p className="text-sm text-slate-500 mt-1">Real-time multi-node LangGraph execution stream</p>
        
        {retryCount > 0 && (
          <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-amber-50 border border-amber-100 text-amber-700 text-xs font-semibold rounded-full mt-3">
            <AlertTriangle className="h-3.5 w-3.5" />
            Quality below threshold. Retrying search loop (Attempt #{retryCount + 1})
          </div>
        )}
      </div>

      <div className="relative pl-8 space-y-8 before:absolute before:left-3.5 before:top-2 before:bottom-2 before:w-[2px] before:bg-slate-100">
        {steps.map((step) => {
          const status = getStepStatus(step.key);
          const timeTaken = getStepTime(step.key);

          return (
            <motion.div
              key={step.key}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className="relative flex items-start gap-4"
            >
              {/* Dot Icon */}
              <div className="absolute -left-[29px] mt-0.5">
                {status === 'completed' && (
                  <div className="h-7 w-7 rounded-full bg-emerald-500 text-white flex items-center justify-center border-4 border-white shadow-sm">
                    <Check className="h-3.5 w-3.5" />
                  </div>
                )}
                {status === 'active' && (
                  <div className="h-7 w-7 rounded-full bg-indigo-600 text-white flex items-center justify-center border-4 border-white shadow-md animate-pulse">
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  </div>
                )}
                {status === 'pending' && (
                  <div className="h-7 w-7 rounded-full bg-slate-100 text-slate-400 flex items-center justify-center border-4 border-white shadow-sm">
                    <Play className="h-2.5 w-2.5" />
                  </div>
                )}
                {status === 'failed' && (
                  <div className="h-7 w-7 rounded-full bg-red-500 text-white flex items-center justify-center border-4 border-white shadow-sm">
                    <AlertTriangle className="h-3.5 w-3.5" />
                  </div>
                )}
              </div>

              {/* Text details */}
              <div className="flex-1">
                <div className="flex items-center justify-between gap-2">
                  <h3 className={`font-semibold text-sm ${status === 'active' ? 'text-indigo-600' : 'text-slate-800'}`}>
                    {step.label}
                  </h3>
                  {timeTaken && (
                    <span className="text-xs text-slate-400 font-mono bg-slate-50 px-2 py-0.5 rounded border border-slate-100">
                      {timeTaken}
                    </span>
                  )}
                </div>
                <p className="text-xs text-slate-500 mt-0.5">{step.description}</p>
              </div>
            </motion.div>
          );
        })}
      </div>

      {currentStatus === 'completed' && (
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="mt-8 p-4 bg-emerald-50 rounded-xl border border-emerald-100 text-center"
        >
          <p className="text-sm font-bold text-emerald-800">✅ Research Complete!</p>
          <p className="text-xs text-emerald-600 mt-1">
            Data accuracy: {(qualityScore * 100).toFixed(0)}% | Compiled & saved report successfully.
          </p>
        </motion.div>
      )}
    </div>
  );
};
