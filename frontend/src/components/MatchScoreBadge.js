import React, { useState } from 'react';
import { Target, Loader2 } from 'lucide-react';
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
    const color = score >= 80 ? 'bg-emerald-500 text-white' :
                  score >= 60 ? 'bg-blue-500 text-white' :
                  score >= 40 ? 'bg-amber-500 text-white' :
                  'bg-red-400 text-white';
    return (
      <div className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold shadow-md ${color}`} data-testid={`match-score-badge-${jobId}`}>
        <Target className="w-3.5 h-3.5" />
        {score}% Match
      </div>
    );
  }

  if (error) {
    return (
      <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-red-500 text-white shadow-md cursor-pointer hover:bg-red-600 transition-colors" 
        onClick={handleReveal} title="Click to retry" data-testid={`match-score-error-${jobId}`}>
        {error}
      </div>
    );
  }

  return (
    <button
      onClick={handleReveal}
      disabled={loading}
      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold bg-gradient-to-r from-pink-500 to-purple-600 text-white shadow-md hover:from-pink-600 hover:to-purple-700 transition-all cursor-pointer disabled:opacity-60"
      data-testid={`match-score-reveal-${jobId}`}
    >
      {loading ? (
        <><Loader2 className="w-3.5 h-3.5 animate-spin" /> Checking...</>
      ) : (
        <><Target className="w-3.5 h-3.5" /> Match Score</>
      )}
    </button>
  );
};

export default MatchScoreBadge;
