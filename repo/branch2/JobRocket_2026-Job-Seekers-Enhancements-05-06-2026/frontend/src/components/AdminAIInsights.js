import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import {
  Zap, TrendingUp, Users, DollarSign, BarChart3,
  CreditCard, RefreshCw, ArrowUpRight, ArrowDownRight,
  Loader2, Target, Search, Send, FileText, Wallet,
  ChevronDown, ChevronUp
} from "lucide-react";
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const FEATURE_META = {
  match_score: { label: 'Match Score', icon: Target, color: '#3B82F6' },
  top_matches: { label: 'Top 10 Jobs', icon: Search, color: '#8B5CF6' },
  auto_apply: { label: 'Auto-Apply', icon: Send, color: '#10B981' },
  cv_enhance: { label: 'CV Enhance', icon: FileText, color: '#F59E0B' },
};

const ACTION_LABELS = {
  match_score: 'Match Score',
  top_matches: 'Top 10 Jobs',
  auto_apply: 'Auto-Apply',
  cv_enhance: 'CV Enhance',
  topup: 'Wallet Top-Up',
  refund: 'Refund',
  auto_topup: 'Auto Top-Up',
  auto_topup_failed: 'Auto Top-Up Failed',
};

const StatCard = ({ title, value, subtitle, icon: Icon, iconColor, trend }) => (
  <Card className="bg-slate-800/50 border-slate-700" data-testid={`stat-card-${title.toLowerCase().replace(/\s+/g, '-')}`}>
    <CardContent className="p-4">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs text-slate-400 uppercase tracking-wider">{title}</p>
          <p className="text-2xl font-bold text-white mt-1">{value}</p>
          {subtitle && <p className="text-xs text-slate-500 mt-1">{subtitle}</p>}
        </div>
        <div className={`p-2 rounded-lg ${iconColor || 'bg-blue-500/20'}`}>
          <Icon className={`w-5 h-5 ${iconColor?.includes('blue') ? 'text-blue-400' : iconColor?.includes('emerald') ? 'text-emerald-400' : iconColor?.includes('amber') ? 'text-amber-400' : iconColor?.includes('red') ? 'text-red-400' : iconColor?.includes('purple') ? 'text-purple-400' : 'text-blue-400'}`} />
        </div>
      </div>
      {trend !== undefined && (
        <div className={`flex items-center gap-1 mt-2 text-xs ${trend >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
          {trend >= 0 ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
          <span>{Math.abs(trend)}% vs last period</span>
        </div>
      )}
    </CardContent>
  </Card>
);

const FeatureBar = ({ name, revenue, count, maxRevenue, color }) => {
  const pct = maxRevenue > 0 ? (revenue / maxRevenue) * 100 : 0;
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span className="text-slate-300">{name}</span>
        <span className="text-slate-400">R{revenue.toFixed(2)} ({count} uses)</span>
      </div>
      <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
        <div className="h-full rounded-full transition-all duration-500" style={{ width: `${pct}%`, backgroundColor: color }} />
      </div>
    </div>
  );
};

const MiniChart = ({ data }) => {
  if (!data || data.length === 0) return <p className="text-slate-500 text-sm text-center py-8">No data yet</p>;
  const maxRev = Math.max(...data.map(d => d.revenue), 1);
  const barWidth = Math.max(12, Math.min(40, 500 / data.length));

  return (
    <div className="flex items-end gap-1 h-32 px-2">
      {data.map((d, i) => (
        <div key={i} className="flex flex-col items-center flex-1 min-w-0" title={`${d.date}: R${d.revenue.toFixed(2)} (${d.actions} actions)`}>
          <div
            className="w-full bg-blue-500 rounded-t hover:bg-blue-400 transition-colors cursor-default"
            style={{ height: `${Math.max(4, (d.revenue / maxRev) * 100)}%`, maxWidth: `${barWidth}px` }}
          />
          {data.length <= 14 && (
            <span className="text-[9px] text-slate-500 mt-1 truncate w-full text-center">{d.date.slice(5)}</span>
          )}
        </div>
      ))}
    </div>
  );
};

const AdminAIInsights = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAllTx, setShowAllTx] = useState(false);

  const token = localStorage.getItem('token');
  const headers = { Authorization: `Bearer ${token}` };

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const res = await axios.get(`${API}/admin/ai/analytics`, { headers });
      setData(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load AI analytics');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
        <span className="ml-3 text-slate-400">Loading AI Insights...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-20">
        <p className="text-red-400 mb-4">{error}</p>
        <Button onClick={fetchData} variant="outline" className="border-slate-600 text-slate-300">Retry</Button>
      </div>
    );
  }

  if (!data) return null;

  const { summary, revenue_by_feature, daily_trend, top_users, wallet_stats, auto_topup_stats, recent_transactions, pricing } = data;
  const maxFeatureRevenue = Math.max(...Object.values(revenue_by_feature).map(r => r.total_revenue), 1);
  const visibleTx = showAllTx ? recent_transactions : recent_transactions.slice(0, 10);

  return (
    <div className="space-y-6" data-testid="admin-ai-insights">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-500/20 rounded-xl">
            <Zap className="w-6 h-6 text-blue-400" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">AI Sidekick Insights</h2>
            <p className="text-sm text-slate-400">Usage analytics, revenue & wallet metrics</p>
          </div>
        </div>
        <Button onClick={fetchData} variant="outline" size="sm" className="border-slate-600 text-slate-300 hover:bg-slate-700" data-testid="refresh-insights-btn">
          <RefreshCw className="w-4 h-4 mr-1" /> Refresh
        </Button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <StatCard title="Net Revenue" value={`R${summary.net_revenue.toFixed(2)}`}
          subtitle={`Gross: R${summary.total_revenue.toFixed(2)}`}
          icon={DollarSign} iconColor="bg-emerald-500/20" />
        <StatCard title="AI Actions" value={summary.total_ai_actions}
          subtitle={`${summary.unique_ai_users} unique users`}
          icon={BarChart3} iconColor="bg-blue-500/20" />
        <StatCard title="Wallet Top-Ups" value={`R${summary.total_topups.toFixed(2)}`}
          subtitle={`${summary.topup_count} manual + ${summary.auto_topup_count} auto`}
          icon={Wallet} iconColor="bg-purple-500/20" />
        <StatCard title="Refunds" value={`R${summary.total_refunds.toFixed(2)}`}
          subtitle={`${summary.refund_count} refunds issued`}
          icon={RefreshCw} iconColor="bg-red-500/20" />
      </div>

      {/* Revenue Trend + Feature Breakdown */}
      <div className="grid lg:grid-cols-2 gap-4">
        {/* Daily Revenue Chart */}
        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-slate-300 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-blue-400" /> Daily Revenue (Last 30 Days)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <MiniChart data={daily_trend} />
          </CardContent>
        </Card>

        {/* Feature Revenue Breakdown */}
        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-slate-300 flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-purple-400" /> Revenue by Feature
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {Object.entries(revenue_by_feature).map(([action, stats]) => {
              const meta = FEATURE_META[action] || { label: action, color: '#6B7280' };
              return (
                <FeatureBar
                  key={action}
                  name={meta.label}
                  revenue={stats.total_revenue}
                  count={stats.usage_count}
                  maxRevenue={maxFeatureRevenue}
                  color={meta.color}
                />
              );
            })}
          </CardContent>
        </Card>
      </div>

      {/* Wallet & Auto Top-Up Stats + Top Users */}
      <div className="grid lg:grid-cols-2 gap-4">
        {/* Wallet & Auto Top-Up */}
        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-slate-300 flex items-center gap-2">
              <CreditCard className="w-4 h-4 text-amber-400" /> Wallet & Auto Top-Up
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-slate-700/50 p-3 rounded-lg">
                <p className="text-xs text-slate-400">Total Balance Held</p>
                <p className="text-lg font-bold text-white">R{wallet_stats.total_balance_held.toFixed(2)}</p>
                <p className="text-xs text-slate-500">{wallet_stats.users_with_balance} users with balance</p>
              </div>
              <div className="bg-slate-700/50 p-3 rounded-lg">
                <p className="text-xs text-slate-400">Avg Balance</p>
                <p className="text-lg font-bold text-white">R{wallet_stats.avg_balance.toFixed(2)}</p>
              </div>
              <div className="bg-slate-700/50 p-3 rounded-lg">
                <p className="text-xs text-slate-400">Cards Saved</p>
                <p className="text-lg font-bold text-white">{auto_topup_stats.users_with_card}</p>
              </div>
              <div className="bg-slate-700/50 p-3 rounded-lg">
                <p className="text-xs text-slate-400">Auto Top-Up Enabled</p>
                <p className="text-lg font-bold text-white">{auto_topup_stats.users_auto_topup_enabled}</p>
              </div>
            </div>
            <div className="mt-3 p-3 bg-slate-700/30 rounded-lg">
              <p className="text-xs text-slate-400 mb-1">Current Pricing</p>
              <div className="flex flex-wrap gap-2">
                {Object.entries(pricing).map(([action, price]) => (
                  <span key={action} className="text-xs bg-slate-600/50 text-slate-300 px-2 py-1 rounded">
                    {FEATURE_META[action]?.label || action}: R{price}
                  </span>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Top Users */}
        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-slate-300 flex items-center gap-2">
              <Users className="w-4 h-4 text-emerald-400" /> Top AI Users
            </CardTitle>
          </CardHeader>
          <CardContent>
            {top_users.length === 0 ? (
              <p className="text-slate-500 text-sm text-center py-6">No AI users yet</p>
            ) : (
              <div className="space-y-2">
                {top_users.map((u, i) => (
                  <div key={u.user_id} className="flex items-center gap-3 p-2 bg-slate-700/30 rounded-lg">
                    <span className={`w-6 h-6 flex items-center justify-center rounded-full text-xs font-bold ${
                      i === 0 ? 'bg-amber-500 text-black' : i === 1 ? 'bg-slate-400 text-black' : i === 2 ? 'bg-amber-700 text-white' : 'bg-slate-600 text-slate-300'
                    }`}>
                      {i + 1}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-white truncate">{u.name}</p>
                      <p className="text-xs text-slate-500 truncate">{u.email}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-bold text-emerald-400">R{u.total_spent.toFixed(2)}</p>
                      <p className="text-xs text-slate-500">{u.action_count} actions</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Recent Transactions */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-slate-300 flex items-center justify-between">
            <span className="flex items-center gap-2">
              <DollarSign className="w-4 h-4 text-blue-400" /> Recent Transactions
            </span>
            <span className="text-xs text-slate-500">{recent_transactions.length} total</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm" data-testid="ai-transactions-table">
              <thead>
                <tr className="text-slate-400 text-xs border-b border-slate-700">
                  <th className="text-left py-2 px-2">Time</th>
                  <th className="text-left py-2 px-2">User</th>
                  <th className="text-left py-2 px-2">Action</th>
                  <th className="text-right py-2 px-2">Amount</th>
                </tr>
              </thead>
              <tbody>
                {visibleTx.map((tx, i) => {
                  const isRevenue = !['topup', 'refund', 'auto_topup', 'auto_topup_failed'].includes(tx.action);
                  const amount = tx.cost || tx.amount || 0;
                  const actionColor = tx.action === 'refund' ? 'text-red-400' : tx.action === 'topup' || tx.action === 'auto_topup' ? 'text-emerald-400' : 'text-blue-400';
                  return (
                    <tr key={tx.id || i} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                      <td className="py-2 px-2 text-slate-400 text-xs whitespace-nowrap">
                        {tx.created_at ? new Date(tx.created_at).toLocaleString('en-ZA', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' }) : '-'}
                      </td>
                      <td className="py-2 px-2">
                        <p className="text-slate-300 text-xs truncate max-w-[150px]">{tx.user_name}</p>
                      </td>
                      <td className="py-2 px-2">
                        <span className={`text-xs font-medium ${actionColor}`}>
                          {ACTION_LABELS[tx.action] || tx.action}
                        </span>
                      </td>
                      <td className="py-2 px-2 text-right">
                        <span className={`text-xs font-bold ${isRevenue ? 'text-emerald-400' : tx.action === 'refund' ? 'text-red-400' : 'text-slate-300'}`}>
                          {isRevenue ? '+' : tx.action === 'refund' ? '-' : ''}R{amount.toFixed(2)}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          {recent_transactions.length > 10 && (
            <button
              onClick={() => setShowAllTx(!showAllTx)}
              className="w-full mt-3 py-2 text-xs text-slate-400 hover:text-slate-200 flex items-center justify-center gap-1 transition-colors"
              data-testid="show-all-tx-btn"
            >
              {showAllTx ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
              {showAllTx ? 'Show Less' : `Show All ${recent_transactions.length} Transactions`}
            </button>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminAIInsights;
