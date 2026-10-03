import { useState, useEffect } from 'react';
import { 
  HelpCircle, 
  Loader2, 
  Sparkles, 
  X, 
  ArrowRight, 
  SkipForward, 
  CheckCircle, 
  AlertCircle 
} from 'lucide-react';
import { agentApi } from '../services/api';

interface StuckModalProps {
  isOpen: boolean;
  onClose: () => void;
  goalId: string;
  taskTitle: string;
  onResolved: () => void;
}

export default function StuckModal({ isOpen, onClose, goalId, taskTitle, onResolved }: StuckModalProps) {
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [skipLoading, setSkipLoading] = useState(false);
  const [analysis, setAnalysis] = useState<any>(null);
  const [error, setError] = useState('');

  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        handleClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

  if (!isOpen) return null;

  const handleAskAgent = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await agentApi.action(goalId, 'stuck', message || 'I need guidance to unblock this task.');
      if (res.data?.stuck_analysis) {
        setAnalysis(res.data.stuck_analysis);
      } else {
        setAnalysis({
          diagnosis: "This task has multiple dependencies or conceptual hurdles.",
          suggestion: "Try breaking it into 10-minute micro-steps or consult the reference documentation.",
          alternatives: [
            "Skip to the next task and come back later with fresh eyes.",
            "Write down the single next line of code or command needed.",
            "Review the sample boilerplate in the project repository."
          ]
        });
      }
    } catch (err: any) {
      console.error(err);
      setError('Unable to fetch AI diagnosis right now. You can skip to the next task or close this popup.');
      // Provide fallback advice so user is never stuck
      setAnalysis({
        diagnosis: "You encountered a roadblock on this task.",
        suggestion: "Break the step down into smaller parts, or skip forward to keep your momentum going.",
        alternatives: [
          "Click 'Skip & Move to Next Action' below to advance immediately.",
          "Take a 5-minute break and return fresh.",
          "Check the official documentation or example code."
        ]
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSkipAndMoveNext = async () => {
    setSkipLoading(true);
    try {
      await agentApi.action(goalId, 'skip', 'Skipped from stuck modal');
      handleClose();
      onResolved();
    } catch (err) {
      console.error('Failed to skip task', err);
    } finally {
      setSkipLoading(false);
    }
  };

  const handleClose = () => {
    setMessage('');
    setAnalysis(null);
    setError('');
    onClose();
  };

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-900/80 backdrop-blur-md animate-fade-in"
      onClick={(e) => {
        // Click outside backdrop to close
        if (e.target === e.currentTarget) {
          handleClose();
        }
      }}
    >
      <div className="bg-navy-800 border border-white/15 rounded-2xl max-w-lg w-full max-h-[85vh] flex flex-col shadow-2xl relative overflow-hidden animate-fade-in">
        {/* Sticky Header */}
        <div className="p-5 border-b border-white/10 flex items-center justify-between bg-navy-800/90 sticky top-0 z-10">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-accent-amber/20 border border-accent-amber/30 flex items-center justify-center text-accent-amber">
              <HelpCircle className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Stuck on this step?</h3>
              <p className="text-xs text-white/50">NextStep Agent Diagnosis & Pathways</p>
            </div>
          </div>

          <button
            onClick={handleClose}
            aria-label="Close modal"
            className="px-2.5 py-1.5 rounded-lg text-white/50 hover:text-white bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-semibold flex items-center gap-1 transition-colors"
          >
            <X className="w-4 h-4" />
            <span>Close</span>
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="p-5 overflow-y-auto space-y-4 flex-1">
          {/* Target task context */}
          <div className="p-3 bg-white/5 border border-white/10 rounded-xl text-xs">
            <span className="text-white/40 block mb-1 font-semibold uppercase text-[10px] tracking-wider">
              Current Target Task:
            </span>
            <span className="text-white font-medium text-sm">{taskTitle}</span>
          </div>

          {error && (
            <div className="p-3 rounded-lg bg-accent-amber/10 border border-accent-amber/20 text-accent-amber text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {!analysis ? (
            <div className="space-y-4">
              <div>
                <label className="label text-xs">Describe the roadblock (Optional):</label>
                <textarea
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="e.g. I'm facing an error installing the package, or I don't know what parameters to pass..."
                  className="input text-xs min-h-[90px] resize-none"
                />
              </div>

              <div className="p-3.5 bg-electric-500/10 border border-electric-500/20 rounded-xl text-xs text-white/70">
                <span className="text-electric-300 font-semibold block mb-1 flex items-center gap-1">
                  <Sparkles className="w-3.5 h-3.5" />
                  How NextStep Unblocks You:
                </span>
                The agent analyzes your roadblock, creates 10-minute micro-tasks, and gives you alternate ways forward. You can also skip to the next task anytime.
              </div>
            </div>
          ) : (
            <div className="space-y-4 animate-fade-in">
              {/* Diagnosis */}
              <div className="p-3.5 bg-electric-500/10 border border-electric-500/20 rounded-xl">
                <div className="flex items-center gap-2 text-electric-400 font-semibold text-xs mb-1">
                  <Sparkles className="w-4 h-4" />
                  <span>Agent Diagnosis</span>
                </div>
                <p className="text-xs text-white/80 leading-relaxed">{analysis.diagnosis}</p>
              </div>

              {/* Recommended action */}
              <div className="p-3.5 bg-accent-green/10 border border-accent-green/20 rounded-xl">
                <div className="flex items-center gap-2 text-accent-green font-semibold text-xs mb-1">
                  <ArrowRight className="w-4 h-4" />
                  <span>Recommended Immediate Action</span>
                </div>
                <p className="text-xs text-white/95 font-medium leading-relaxed">{analysis.suggestion}</p>
              </div>

              {/* Alternatives */}
              {analysis.alternatives && analysis.alternatives.length > 0 && (
                <div>
                  <span className="text-xs font-semibold text-white/60 block mb-2">Alternative Pathways:</span>
                  <ul className="space-y-1.5">
                    {analysis.alternatives.map((alt: string, i: number) => (
                      <li key={i} className="text-xs text-white/70 flex items-start gap-2 bg-white/5 p-2 rounded-lg border border-white/5">
                        <span className="text-accent-amber font-bold">•</span>
                        <span>{alt}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Sticky Action Footer with Close AND Move Next buttons */}
        <div className="p-4 border-t border-white/10 bg-navy-800/90 flex flex-wrap items-center justify-between gap-2 sticky bottom-0 z-10">
          <button
            type="button"
            onClick={handleClose}
            className="btn-secondary text-xs py-2 px-3 flex items-center gap-1.5 text-white/70 hover:text-white"
          >
            <X className="w-3.5 h-3.5" />
            <span>Close</span>
          </button>

          <div className="flex items-center gap-2">
            {/* Direct button to move next / skip right from the pop-up */}
            <button
              type="button"
              onClick={handleSkipAndMoveNext}
              disabled={skipLoading}
              className="btn-secondary text-xs py-2 px-3 flex items-center gap-1.5 text-accent-amber hover:text-accent-amber bg-accent-amber/10 border-accent-amber/20 hover:bg-accent-amber/20"
              title="Skip this task and advance to the next action immediately"
            >
              {skipLoading ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <SkipForward className="w-3.5 h-3.5" />
              )}
              <span>Skip & Move to Next</span>
            </button>

            {!analysis ? (
              <button
                type="button"
                onClick={handleAskAgent}
                disabled={loading}
                className="btn-primary text-xs flex items-center gap-2 py-2 px-3.5"
              >
                {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
                <span>{loading ? 'Analyzing…' : 'Get Guidance'}</span>
              </button>
            ) : (
              <button
                type="button"
                onClick={() => {
                  handleClose();
                  onResolved();
                }}
                className="btn-primary text-xs flex items-center gap-1.5 py-2 px-3.5"
              >
                <CheckCircle className="w-3.5 h-3.5 text-emerald-300" />
                <span>Got It, Back to Task</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
