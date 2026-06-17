import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import {
  Zap, X, Wallet, Target, Search, Send, FileText, Sparkles, 
  ChevronRight, Loader2, CheckCircle, AlertCircle, Briefcase,
  TrendingUp, ArrowRight, ExternalLink
} from "lucide-react";
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const getAuthHeaders = () => ({
  headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
});

const FEATURES = [
  { id: 'match_score', icon: Target, label: 'Job Match Score', price: 10, description: 'See how well you match a specific job', color: 'blue' },
  { id: 'top_matches', icon: Search, label: 'Find My Top 10 Jobs', price: 50, description: 'AI finds the best jobs for you', color: 'purple' },
  { id: 'auto_apply', icon: Send, label: 'Auto-Apply to Jobs', price: 50, description: 'Apply to top matches with AI cover letters', color: 'green' },
  { id: 'cv_enhance', icon: FileText, label: 'Enhance My CV', price: 80, description: 'AI-powered CV and profile improvement', color: 'amber' },
];

const FeatureButton = ({ feature, onClick, disabled }) => {
  const Icon = feature.icon;
  const colors = {
    blue: 'from-blue-500 to-blue-700 hover:from-blue-600 hover:to-blue-800',
    purple: 'from-purple-500 to-purple-700 hover:from-purple-600 hover:to-purple-800',
    green: 'from-emerald-500 to-emerald-700 hover:from-emerald-600 hover:to-emerald-800',
    amber: 'from-amber-500 to-amber-700 hover:from-amber-600 hover:to-amber-800',
  };
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`w-full text-left p-3 rounded-xl bg-gradient-to-r ${colors[feature.color]} text-white transition-all duration-200 shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed`}
      data-testid={`sidekick-${feature.id}-btn`}
    >
      <div className="flex items-center gap-3">
        <div className="bg-white/20 p-2 rounded-lg">
          <Icon className="w-5 h-5" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="font-semibold text-sm">{feature.label}</div>
          <div className="text-xs text-white/70">{feature.description}</div>
        </div>
        <div className="text-right">
          <div className="text-xs font-bold bg-white/20 px-2 py-1 rounded-full">R{feature.price}</div>
        </div>
      </div>
    </button>
  );
};


const MatchScoreResult = ({ data }) => {
  const r = data.result || data;
  const score = r.match_score || 0;
  const scoreColor = score >= 80 ? 'text-emerald-400' : score >= 60 ? 'text-amber-400' : 'text-red-400';
  const ringColor = score >= 80 ? 'border-emerald-400' : score >= 60 ? 'border-amber-400' : 'border-red-400';

  return (
    <div className="space-y-3" data-testid="match-score-result">
      <div className="flex items-center gap-4">
        <div className={`w-16 h-16 rounded-full border-4 ${ringColor} flex items-center justify-center`}>
          <span className={`text-xl font-bold ${scoreColor}`}>{score}%</span>
        </div>
        <div>
          <div className="font-semibold text-white">{r.match_rating || 'Match Analysis'}</div>
          <div className="text-xs text-slate-400">{r.job_title} at {r.company_name}</div>
        </div>
      </div>

      {r.strengths?.length > 0 && (
        <div>
          <div className="text-xs font-semibold text-emerald-400 mb-1">Strengths</div>
          {r.strengths.map((s, i) => (
            <div key={i} className="flex items-start gap-2 text-xs text-slate-300 mb-1">
              <CheckCircle className="w-3 h-3 text-emerald-400 mt-0.5 flex-shrink-0" />
              <span>{s}</span>
            </div>
          ))}
        </div>
      )}

      {r.weaknesses?.length > 0 && (
        <div>
          <div className="text-xs font-semibold text-amber-400 mb-1">Areas to Improve</div>
          {r.weaknesses.map((w, i) => (
            <div key={i} className="flex items-start gap-2 text-xs text-slate-300 mb-1">
              <AlertCircle className="w-3 h-3 text-amber-400 mt-0.5 flex-shrink-0" />
              <span>{w}</span>
            </div>
          ))}
        </div>
      )}

      {r.missing_skills?.length > 0 && (
        <div>
          <div className="text-xs font-semibold text-red-400 mb-1">Missing Skills</div>
          <div className="flex flex-wrap gap-1">
            {r.missing_skills.map((s, i) => (
              <span key={i} className="text-xs bg-red-500/20 text-red-300 px-2 py-0.5 rounded-full">{s}</span>
            ))}
          </div>
        </div>
      )}

      {r.recommendation && (
        <div className="bg-slate-700/50 rounded-lg p-2 text-xs text-slate-300 border-l-2 border-blue-400">
          <span className="font-semibold text-blue-400">Recommendation: </span>{r.recommendation}
        </div>
      )}
    </div>
  );
};


const TopMatchesResult = ({ data, onAutoApply }) => {
  const matches = data.result?.matches || [];
  return (
    <div className="space-y-2" data-testid="top-matches-result">
      <div className="text-sm font-semibold text-white mb-2">Your Top {matches.length} Job Matches</div>
      {matches.map((m, i) => (
        <div key={i} className="bg-slate-700/50 rounded-lg p-2 border border-slate-600">
          <div className="flex items-center justify-between mb-1">
            <div className="font-semibold text-sm text-white truncate flex-1">{m.job_title}</div>
            <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${m.match_percentage >= 80 ? 'bg-emerald-500/20 text-emerald-400' : m.match_percentage >= 60 ? 'bg-amber-500/20 text-amber-400' : 'bg-red-500/20 text-red-400'}`}>
              {m.match_percentage}%
            </span>
          </div>
          <div className="text-xs text-slate-400">{m.company_name} - {m.location}</div>
          {m.salary && <div className="text-xs text-emerald-400">{m.salary}</div>}
          <div className="text-xs text-slate-300 mt-1">{m.why_matched}</div>
          <a href={`/jobs/${m.job_id}`} className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1 mt-1">
            View Job <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      ))}
      {matches.length > 0 && (
        <Button
          onClick={() => onAutoApply(matches.slice(0, 5).map(m => m.job_id))}
          className="w-full bg-gradient-to-r from-emerald-500 to-emerald-700 hover:from-emerald-600 hover:to-emerald-800 text-sm mt-2"
          data-testid="auto-apply-from-matches-btn"
        >
          <Send className="w-4 h-4 mr-2" />
          Auto-Apply to Top {Math.min(matches.length, 5)} Jobs (R50)
        </Button>
      )}
    </div>
  );
};


const AutoApplyResult = ({ data }) => {
  const apps = data.result?.applications || [];
  const appliedCount = data.result?.applied_count || 0;
  const alreadyCount = data.result?.already_applied_count || 0;
  const allAlready = data.result?.all_already_applied;

  return (
    <div className="space-y-2" data-testid="auto-apply-result">
      {/* Completion banner */}
      <div className="bg-emerald-500/20 border border-emerald-500/30 rounded-lg p-3">
        <div className="flex items-center gap-2 mb-1">
          <CheckCircle className="w-5 h-5 text-emerald-400" />
          <span className="text-sm font-semibold text-emerald-300">
            {allAlready ? 'Already Applied!' : 'Auto-Apply Complete!'}
          </span>
        </div>
        <p className="text-xs text-slate-300 ml-7">
          {appliedCount > 0 && `Successfully applied to ${appliedCount} job${appliedCount > 1 ? 's' : ''}`}
          {appliedCount > 0 && alreadyCount > 0 && '. '}
          {alreadyCount > 0 && `${alreadyCount} already applied`}
          {allAlready && 'You\'ve already applied to all these jobs. No charge applied.'}
        </p>
      </div>

      {/* Application list */}
      {apps.map((a, i) => (
        <div key={i} className={`flex items-center gap-2 p-2 rounded-lg text-xs ${
          a.status === 'applied' ? 'bg-emerald-500/10 border border-emerald-500/30' : 
          a.status === 'already_applied' ? 'bg-blue-500/10 border border-blue-500/30' :
          'bg-slate-700/50 border border-slate-600'
        }`}>
          {a.status === 'applied' ? <CheckCircle className="w-3 h-3 text-emerald-400" /> : 
           a.status === 'already_applied' ? <CheckCircle className="w-3 h-3 text-blue-400" /> :
           <AlertCircle className="w-3 h-3 text-amber-400" />}
          <span className="text-slate-300 flex-1">{a.job_title || a.job_id} {a.company_name ? `at ${a.company_name}` : ''}</span>
          <span className={`px-2 py-0.5 rounded-full text-[10px] ${
            a.status === 'applied' ? 'bg-emerald-500/20 text-emerald-400' : 
            a.status === 'already_applied' ? 'bg-blue-500/20 text-blue-400' :
            'bg-amber-500/20 text-amber-400'
          }`}>{a.status === 'already_applied' ? 'applied' : a.status}</span>
        </div>
      ))}

      {/* Link to My Applications */}
      <a
        href="/profile?tab=applications"
        className="flex items-center justify-center gap-2 mt-3 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors"
        data-testid="view-applications-link"
      >
        <FileText className="w-4 h-4" />
        View My Applications
      </a>
    </div>
  );
};


const CVEnhanceResult = ({ data }) => {
  const r = data.result?.result || {};
  return (
    <div className="space-y-3" data-testid="cv-enhance-result">
      <div className="grid grid-cols-3 gap-2">
        {[
          { label: 'Overall', score: r.overall_score, color: 'blue' },
          { label: 'ATS', score: r.ats_score, color: 'purple' },
          { label: 'Complete', score: r.profile_completion_score, color: 'emerald' },
        ].map(({ label, score, color }) => (
          <div key={label} className={`text-center p-2 rounded-lg bg-${color}-500/10 border border-${color}-500/30`}>
            <div className={`text-lg font-bold text-${color}-400`}>{score || 0}%</div>
            <div className="text-xs text-slate-400">{label}</div>
          </div>
        ))}
      </div>

      {r.improved_professional_summary && (
        <div>
          <div className="text-xs font-semibold text-blue-400 mb-1">Improved Professional Summary</div>
          <div className="bg-slate-700/50 rounded-lg p-2 text-xs text-slate-300">{r.improved_professional_summary}</div>
        </div>
      )}

      {r.suggested_skills?.length > 0 && (
        <div>
          <div className="text-xs font-semibold text-purple-400 mb-1">Suggested Skills to Add</div>
          <div className="flex flex-wrap gap-1">
            {r.suggested_skills.map((s, i) => (
              <span key={i} className="text-xs bg-purple-500/20 text-purple-300 px-2 py-0.5 rounded-full">{s}</span>
            ))}
          </div>
        </div>
      )}

      {r.suggested_keywords?.length > 0 && (
        <div>
          <div className="text-xs font-semibold text-amber-400 mb-1">Keywords for ATS</div>
          <div className="flex flex-wrap gap-1">
            {r.suggested_keywords.map((k, i) => (
              <span key={i} className="text-xs bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded-full">{k}</span>
            ))}
          </div>
        </div>
      )}

      {r.general_recommendations?.length > 0 && (
        <div>
          <div className="text-xs font-semibold text-emerald-400 mb-1">Recommendations</div>
          {r.general_recommendations.map((rec, i) => (
            <div key={i} className="flex items-start gap-2 text-xs text-slate-300 mb-1">
              <Sparkles className="w-3 h-3 text-emerald-400 mt-0.5 flex-shrink-0" />
              <span>{rec}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};


const Sidekick = ({ isOpen, onClose, currentJobId, currentJobTitle }) => {
  const [walletBalance, setWalletBalance] = useState(0);
  const [autoTopupEnabled, setAutoTopupEnabled] = useState(false);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingAction, setLoadingAction] = useState('');
  const [topupAmount, setTopupAmount] = useState('');
  const [showTopup, setShowTopup] = useState(false);
  const [lastTopMatches, setLastTopMatches] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      fetchWalletBalance();
      if (messages.length === 0) {
        setMessages([{
          type: 'system',
          content: "Hey! I'm your Sidekick — your AI-powered job search assistant. What would you like to do?",
        }]);
      }
    }
  }, [isOpen]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchWalletBalance = async () => {
    try {
      const res = await axios.get(`${API}/ai/wallet`, getAuthHeaders());
      setWalletBalance(res.data.wallet_balance || 0);
      // Also check auto top-up status
      const topupRes = await axios.get(`${API}/ai/wallet/auto-topup`, getAuthHeaders());
      setAutoTopupEnabled(topupRes.data.enabled && topupRes.data.has_card);
    } catch (err) {
      console.error('Failed to fetch wallet:', err);
    }
  };

  const handleTopup = async () => {
    const amount = parseFloat(topupAmount);
    if (!amount || amount <= 0) return;
    try {
      const res = await axios.post(`${API}/ai/wallet/topup`, { amount }, getAuthHeaders());
      setWalletBalance(res.data.wallet_balance);
      setTopupAmount('');
      setShowTopup(false);
      addMessage('system', `Wallet topped up by R${amount.toFixed(2)}. New balance: R${res.data.wallet_balance.toFixed(2)}`);
    } catch (err) {
      addMessage('error', err.response?.data?.detail || 'Top up failed');
    }
  };

  const addMessage = (type, content, data = null) => {
    setMessages(prev => [...prev, { type, content, data, timestamp: new Date() }]);
  };

  const handleFeatureAction = async (featureId) => {
    if (loading) return;

    if (featureId === 'match_score' && !currentJobId) {
      addMessage('error', 'Please open a job listing first, then use Match Score to see how well you match.');
      return;
    }

    if (featureId === 'auto_apply' && !lastTopMatches) {
      addMessage('error', 'Please run "Find My Top 10 Jobs" first, then you can auto-apply to them.');
      return;
    }

    const feature = FEATURES.find(f => f.id === featureId);
    addMessage('user', `${feature.label} (R${feature.price})`);
    setLoading(true);
    setLoadingAction(featureId);

    try {
      let res;
      switch (featureId) {
        case 'match_score':
          res = await axios.post(`${API}/ai/match-score`, { job_id: currentJobId }, getAuthHeaders());
          addMessage('result', 'match_score', res.data);
          break;

        case 'top_matches':
          res = await axios.post(`${API}/ai/top-matches`, {}, getAuthHeaders());
          setLastTopMatches(res.data.result?.matches?.map(m => m.job_id) || []);
          addMessage('result', 'top_matches', res.data);
          break;

        case 'auto_apply':
          res = await axios.post(`${API}/ai/auto-apply`, { job_ids: (lastTopMatches || []).slice(0, 5) }, {
            ...getAuthHeaders(),
            timeout: 90000
          });
          addMessage('result', 'auto_apply', res.data);
          break;

        case 'cv_enhance':
          res = await axios.post(`${API}/ai/cv-enhance`, {}, getAuthHeaders());
          addMessage('result', 'cv_enhance', res.data);
          break;
        
        default:
          break;
      }

      if (res?.data?.new_balance !== undefined) {
        setWalletBalance(res.data.new_balance);
      }
      // Handle auto top-up notification
      if (res?.data?.auto_topup?.success) {
        setWalletBalance(res.data.auto_topup.new_balance);
        addMessage('system', `Auto top-up triggered: +R${res.data.auto_topup.amount.toFixed(2)}. New balance: R${res.data.auto_topup.new_balance.toFixed(2)}`);
      }
    } catch (err) {
      if (err.code === 'ECONNABORTED' || !err.response) {
        addMessage('error', 'The request took too long. Your applications may still be processing — check "My Applications" in a moment.');
      } else {
        const detail = err.response?.data?.detail || 'Something went wrong';
        if (err.response?.status === 402) {
          addMessage('error', `${detail} Your balance: R${walletBalance.toFixed(2)}. Required: R${feature.price}.`);
          setShowTopup(true);
        } else {
          addMessage('error', detail);
        }
      }
    } finally {
      setLoading(false);
      setLoadingAction('');
    }
  };

  const handleAutoApplyFromMatches = async (jobIds) => {
    setLastTopMatches(jobIds);
    handleFeatureAction('auto_apply');
  };

  if (!isOpen) return null;

  return (
    <div className="fixed right-0 top-0 h-full w-96 bg-slate-900 border-l border-slate-700 shadow-2xl z-50 flex flex-col" data-testid="sidekick-panel">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="bg-white/20 p-2 rounded-xl">
            <Zap className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-white font-bold text-lg">Sidekick</h3>
            <p className="text-white/70 text-xs">Your AI Job Search Assistant</p>
          </div>
        </div>
        <button onClick={onClose} className="text-white/70 hover:text-white p-1" data-testid="sidekick-close-btn">
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Wallet Bar */}
      <div className="bg-slate-800 px-4 py-2 border-b border-slate-700 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Wallet className="w-4 h-4 text-emerald-400" />
          <span className="text-sm text-slate-300">Balance: </span>
          <span className="text-sm font-bold text-emerald-400" data-testid="sidekick-wallet-balance">R{walletBalance.toFixed(2)}</span>
          {autoTopupEnabled && (
            <span className="text-[10px] bg-amber-500/20 text-amber-400 px-1.5 py-0.5 rounded-full flex items-center gap-0.5" data-testid="auto-topup-badge">
              <Zap className="w-2.5 h-2.5" /> Auto
            </span>
          )}
        </div>
        <button
          onClick={() => setShowTopup(!showTopup)}
          className="text-xs bg-emerald-600 hover:bg-emerald-700 text-white px-3 py-1 rounded-full transition-colors"
          data-testid="sidekick-topup-toggle"
        >
          Top Up
        </button>
      </div>

      {/* Top-up Panel */}
      {showTopup && (
        <div className="bg-slate-800/80 px-4 py-3 border-b border-slate-700">
          <div className="flex gap-2">
            <div className="flex gap-1">
              {[50, 100, 200, 500].map(amt => (
                <button key={amt} onClick={() => setTopupAmount(String(amt))}
                  className={`text-xs px-2 py-1 rounded-full border transition-colors ${topupAmount === String(amt) ? 'bg-emerald-600 border-emerald-600 text-white' : 'border-slate-600 text-slate-400 hover:border-emerald-500'}`}>
                  R{amt}
                </button>
              ))}
            </div>
          </div>
          <div className="flex gap-2 mt-2">
            <Input
              type="number" placeholder="Amount (R)" value={topupAmount}
              onChange={(e) => setTopupAmount(e.target.value)}
              className="h-8 text-sm bg-slate-700 border-slate-600 text-white flex-1"
              data-testid="sidekick-topup-input"
            />
            <Button onClick={handleTopup} size="sm" className="bg-emerald-600 hover:bg-emerald-700 h-8 px-4" data-testid="sidekick-topup-confirm">
              Add
            </Button>
          </div>
        </div>
      )}

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((msg, i) => (
          <div key={i} className={`${msg.type === 'user' ? 'flex justify-end' : ''}`}>
            {msg.type === 'system' && (
              <div className="bg-slate-800 rounded-xl p-3 text-sm text-slate-300 border border-slate-700">
                <div className="flex items-start gap-2">
                  <Zap className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
                  <span>{msg.content}</span>
                </div>
              </div>
            )}
            {msg.type === 'user' && (
              <div className="bg-blue-600 rounded-xl px-3 py-2 text-sm text-white max-w-[80%]">
                {msg.content}
              </div>
            )}
            {msg.type === 'error' && (
              <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-3 text-sm text-red-300">
                <div className="flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 text-red-400 mt-0.5 flex-shrink-0" />
                  <span>{msg.content}</span>
                </div>
              </div>
            )}
            {msg.type === 'result' && msg.content === 'match_score' && <MatchScoreResult data={msg.data} />}
            {msg.type === 'result' && msg.content === 'top_matches' && <TopMatchesResult data={msg.data} onAutoApply={handleAutoApplyFromMatches} />}
            {msg.type === 'result' && msg.content === 'auto_apply' && <AutoApplyResult data={msg.data} />}
            {msg.type === 'result' && msg.content === 'cv_enhance' && <CVEnhanceResult data={msg.data} />}
          </div>
        ))}

        {loading && (
          <div className="bg-slate-800 rounded-xl p-3 text-sm text-slate-300 border border-slate-700">
            <div className="flex items-center gap-2">
              <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
              <span>{loadingAction === 'match_score' ? 'Analyzing your match...' : 
                     loadingAction === 'top_matches' ? 'Searching for your best matches...' :
                     loadingAction === 'auto_apply' ? 'Generating cover letters and applying...' :
                     loadingAction === 'cv_enhance' ? 'Analyzing your CV and profile...' : 
                     'Processing...'}</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Feature Buttons */}
      <div className="border-t border-slate-700 p-3 space-y-2 bg-slate-850">
        {currentJobId && (
          <div className="text-xs text-slate-400 mb-1 flex items-center gap-1">
            <Briefcase className="w-3 h-3" />
            Viewing: <span className="text-blue-400 font-medium truncate">{currentJobTitle || 'Current Job'}</span>
          </div>
        )}
        {FEATURES.map(feature => (
          <FeatureButton
            key={feature.id}
            feature={feature}
            disabled={loading || (feature.id === 'auto_apply' && !lastTopMatches)}
            onClick={() => handleFeatureAction(feature.id)}
          />
        ))}
      </div>
    </div>
  );
};


// Floating Sidekick toggle button
export const SidekickToggle = ({ onClick, isOpen }) => {
  if (isOpen) return null;
  return (
    <button
      onClick={onClick}
      className="fixed bottom-6 right-6 bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 rounded-full shadow-2xl hover:shadow-blue-500/25 z-40 transition-all duration-300 hover:scale-110 group"
      data-testid="sidekick-toggle-btn"
    >
      <Zap className="w-6 h-6" />
      <span className="absolute right-full mr-3 top-1/2 -translate-y-1/2 bg-slate-900 text-white text-sm px-3 py-1.5 rounded-lg whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity shadow-lg">
        Sidekick AI
      </span>
    </button>
  );
};

export default Sidekick;
