import React, { useState } from 'react';
import { Target, Loader2, Lock } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const getAuthHeaders = () => ({
  headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
});

const MatchScoreBadge = ({ jobId, cachedScore, onReveal }) => {
  const [score, setScore] = useState(cachedScore || null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleReveal = async (e) => {
    e.stopPropagation();
    e.preventDefault();
    if (score || loading) return;

    setLoading(true);
    setError('');
    try {
      const res = await axios.post(`${API}/ai/match-score`, { job_id: jobId }, getAuthHeaders());
      const matchData = res.data.result;
      setScore(matchData.match_score);
      if (onReveal) onReveal(res.data);
    } catch (err) {
      const detail = err.response?.data?.detail || 'Failed';
      if (err.response?.status === 402) {
        setError('Top up wallet');
      } else {
        setError(detail.length > 20 ? 'Error' : detail);
      }
    } finally {
      setLoading(false);
    }
  };

  if (score) {
    const color = score >= 80 ? 'bg-emerald-100 text-emerald-700 border-emerald-300' :
                  score >= 60 ? 'bg-amber-100 text-amber-700 border-amber-300' :
                  'bg-red-100 text-red-700 border-red-300';
    return (
      <div className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold border ${color}`} data-testid={`match-score-badge-${jobId}`}>
        <Target className="w-3 h-3" />
        {score}% Match
      </div>
    );
  }

  if (error) {
    return (
      <div className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs bg-red-50 text-red-600 border border-red-200 cursor-pointer" 
        onClick={handleReveal} title="Click to retry">
        {error}
      </div>
    );
  }

  return (
    <button
      onClick={handleReveal}
      disabled={loading}
      className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs bg-blue-50 text-blue-600 border border-blue-200 hover:bg-blue-100 hover:border-blue-300 transition-colors cursor-pointer disabled:opacity-50"
      data-testid={`match-score-reveal-${jobId}`}
    >
      {loading ? (
        <><Loader2 className="w-3 h-3 animate-spin" /> Checking...</>
      ) : (
        <><Lock className="w-3 h-3" /> Match Score (R10)</>
      )}
    </button>
  );
};

export default MatchScoreBadge;
