import React, { useState, useEffect, useCallback } from 'react';
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, ResponsiveContainer,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend
} from 'recharts';
import {
  TrendingUp, Users, Briefcase, Building2, FileText, DollarSign,
  Download, RefreshCw, Loader2, ChevronDown, ChevronUp,
  UserCheck, Target, Activity, ArrowUpRight, ArrowDownRight
} from "lucide-react";
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'];
const TIER_COLORS = { starter: '#64748b', growth: '#3b82f6', pro: '#8b5cf6', enterprise: '#f59e0b' };

const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return { headers: { Authorization: `Bearer ${token}` } };
};

const formatZAR = (val) => new Intl.NumberFormat('en-ZA', { style: 'currency', currency: 'ZAR', minimumFractionDigits: 0 }).format(val);

// Stat Card
const StatCard = ({ title, value, subtitle, icon: Icon, color = 'blue', trend }) => (
  <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0" data-testid={`stat-${title.toLowerCase().replace(/\s/g, '-')}`}>
    <CardContent className="p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500">{title}</p>
          <p className="text-2xl font-bold text-slate-900 mt-1">{value}</p>
          {subtitle && <p className="text-xs text-slate-500 mt-1">{subtitle}</p>}
        </div>
        <div className={`p-2.5 rounded-xl bg-${color}-100`}>
          <Icon className={`w-5 h-5 text-${color}-600`} />
        </div>
      </div>
      {trend !== undefined && (
        <div className={`mt-3 flex items-center text-xs font-medium ${trend >= 0 ? 'text-green-600' : 'text-red-500'}`}>
          {trend >= 0 ? <ArrowUpRight className="w-3.5 h-3.5 mr-1" /> : <ArrowDownRight className="w-3.5 h-3.5 mr-1" />}
          {Math.abs(trend)} this month
        </div>
      )}
    </CardContent>
  </Card>
);

// Collapsible Section
const Section = ({ title, icon: Icon, children, defaultOpen = true }) => {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="mb-6">
      <button onClick={() => setOpen(!open)} className="w-full flex items-center justify-between mb-4 group">
        <h2 className="text-lg font-bold text-slate-800 flex items-center">
          <Icon className="w-5 h-5 mr-2 text-blue-600" /> {title}
        </h2>
        {open ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
      </button>
      {open && children}
    </div>
  );
};

// Custom tooltip for charts
const ChartTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-white p-3 rounded-lg shadow-lg border border-slate-200 text-sm">
      <p className="font-medium text-slate-800 mb-1">{label}</p>
      {payload.map((entry, i) => (
        <p key={i} style={{ color: entry.color }} className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
          {entry.name}: <span className="font-semibold">{entry.value}</span>
        </p>
      ))}
    </div>
  );
};

const AnalyticsDashboard = ({ user }) => {
  const [stats, setStats] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);

  const fetchData = useCallback(async (forceRefresh = false) => {
    try {
      setLoading(true);
      const [statsRes, analyticsRes] = await Promise.all([
        axios.get(`${API}/admin/stats${forceRefresh ? '?force_refresh=true' : ''}`, getAuthHeaders()),
        axios.get(`${API}/admin/analytics`, getAuthHeaders()),
      ]);
      setStats(statsRes.data);
      setAnalytics(analyticsRes.data);
    } catch (err) {
      console.error('Failed to load analytics:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  // Excel export
  const handleExport = async () => {
    setExporting(true);
    try {
      const s = stats?.summary || {};
      const a = analytics || {};

      // Build CSV sections
      let csv = 'JOBROCKET ANALYTICS REPORT\n';
      csv += `Generated: ${new Date().toLocaleString('en-ZA')}\n\n`;

      // Summary
      csv += 'SUMMARY\n';
      csv += 'Metric,Value\n';
      csv += `Monthly Revenue,${formatZAR(s.monthly_revenue || 0)}\n`;
      csv += `Total Accounts,${s.total_accounts || 0}\n`;
      csv += `Active Subscriptions,${s.active_subscriptions || 0}\n`;
      csv += `Total Users,${s.total_users || 0}\n`;
      csv += `Recruiters,${s.total_recruiters || 0}\n`;
      csv += `Job Seekers,${s.total_job_seekers || 0}\n`;
      csv += `Total Jobs,${s.total_jobs || 0}\n`;
      csv += `Active Jobs,${s.active_jobs || 0}\n`;
      csv += `Total Applications,${s.total_applications || 0}\n`;
      csv += `New Accounts (30d),${s.new_accounts_30d || 0}\n\n`;

      // Tier Distribution
      csv += 'TIER DISTRIBUTION\n';
      csv += 'Tier,Count\n';
      Object.entries(stats?.tier_distribution || {}).forEach(([k, v]) => {
        csv += `${k.charAt(0).toUpperCase() + k.slice(1)},${v}\n`;
      });
      csv += '\n';

      // Monthly Trends
      csv += 'MONTHLY TRENDS\n';
      csv += 'Month,New Accounts,New Users,New Jobs,Applications\n';
      (a.monthly_trends || []).forEach(m => {
        csv += `${m.month},${m.accounts},${m.users},${m.jobs},${m.applications}\n`;
      });
      csv += '\n';

      // Jobs by Industry
      csv += 'JOBS BY INDUSTRY\n';
      csv += 'Industry,Count\n';
      (a.jobs_by_industry || []).forEach(d => { csv += `${d.name},${d.count}\n`; });
      csv += '\n';

      // Jobs by Location
      csv += 'JOBS BY LOCATION\n';
      csv += 'Location,Count\n';
      (a.jobs_by_location || []).forEach(d => { csv += `"${d.name}",${d.count}\n`; });
      csv += '\n';

      // Account Details
      csv += 'ACCOUNT DETAILS\n';
      csv += 'Company,Tier,Status,Owner,Email,Users,Extra Users,Jobs,Applications,MRR,Created\n';
      (a.accounts_detail || []).forEach(acc => {
        csv += `"${acc.name}",${acc.tier_id},${acc.subscription_status},"${acc.owner_name}",${acc.owner_email},${acc.user_count},${acc.extra_users},${acc.job_count},${acc.application_count},${formatZAR(acc.mrr)},${acc.created_at}\n`;
      });

      // Onboarding
      csv += '\nONBOARDING COMPLETION\n';
      csv += 'Role,Completed,Total,Rate\n';
      const ob = a.onboarding || {};
      if (ob.job_seekers) {
        const rate = ob.job_seekers.total ? Math.round((ob.job_seekers.completed / ob.job_seekers.total) * 100) : 0;
        csv += `Job Seekers,${ob.job_seekers.completed},${ob.job_seekers.total},${rate}%\n`;
      }
      if (ob.recruiters) {
        const rate = ob.recruiters.total ? Math.round((ob.recruiters.completed / ob.recruiters.total) * 100) : 0;
        csv += `Recruiters,${ob.recruiters.completed},${ob.recruiters.total},${rate}%\n`;
      }

      // Download
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `jobrocket_analytics_${new Date().toISOString().slice(0, 10)}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Export error:', err);
    } finally {
      setExporting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-10 h-10 animate-spin text-blue-600 mx-auto mb-3" />
          <p className="text-slate-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  const s = stats?.summary || {};
  const a = analytics || {};
  const tierDist = stats?.tier_distribution || {};
  const tierPieData = Object.entries(tierDist).map(([k, v]) => ({ name: k.charAt(0).toUpperCase() + k.slice(1), value: v }));
  const currentMonthData = (a.monthly_trends || []).at(-1) || {};

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-8 gap-4">
          <div>
            <h1 className="text-3xl font-bold text-slate-800 flex items-center" data-testid="analytics-title">
              <Activity className="w-8 h-8 mr-3 text-blue-600" />
              Analytics Dashboard
            </h1>
            <p className="text-slate-600 mt-1">
              Platform overview &middot; Last refreshed {stats?.last_refresh ? new Date(stats.last_refresh).toLocaleString('en-ZA') : 'N/A'}
            </p>
          </div>
          <div className="flex gap-3">
            <Button variant="outline" onClick={() => fetchData(true)} data-testid="refresh-btn">
              <RefreshCw className="w-4 h-4 mr-2" /> Refresh
            </Button>
            <Button onClick={handleExport} disabled={exporting} className="bg-blue-600 hover:bg-blue-700" data-testid="export-btn">
              {exporting ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Download className="w-4 h-4 mr-2" />}
              Export to CSV
            </Button>
          </div>
        </div>

        {/* Snapshot Stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard title="Monthly Revenue" value={formatZAR(s.monthly_revenue || 0)} icon={DollarSign} color="green" subtitle={`${s.active_subscriptions || 0} active subscriptions`} />
          <StatCard title="Total Accounts" value={s.total_accounts || 0} icon={Building2} color="blue" trend={currentMonthData.accounts} />
          <StatCard title="Total Users" value={s.total_users || 0} icon={Users} color="purple" subtitle={`${s.total_recruiters || 0} recruiters · ${s.total_job_seekers || 0} seekers`} trend={currentMonthData.users} />
          <StatCard title="Active Jobs" value={s.active_jobs || 0} icon={Briefcase} color="amber" subtitle={`${s.total_jobs || 0} total posted`} trend={currentMonthData.jobs} />
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard title="Applications" value={s.total_applications || 0} icon={FileText} color="rose" trend={currentMonthData.applications} />
          <StatCard title="New Accounts (30d)" value={s.new_accounts_30d || 0} icon={TrendingUp} color="emerald" />
          <StatCard title="Active Add-ons" value={s.active_addons || 0} icon={Target} color="indigo" />
          <StatCard title="Extra User Seats" value={s.total_extra_users || 0} icon={UserCheck} color="sky" subtitle={`${formatZAR((s.total_extra_users || 0) * 899)}/mo revenue`} />
        </div>

        {/* Monthly Trends Chart */}
        <Section title="Monthly Trends" icon={TrendingUp}>
          <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
            <CardContent className="p-6">
              <ResponsiveContainer width="100%" height={320}>
                <BarChart data={a.monthly_trends || []} barGap={4}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="month" tick={{ fontSize: 12, fill: '#64748b' }} />
                  <YAxis tick={{ fontSize: 12, fill: '#64748b' }} />
                  <Tooltip content={<ChartTooltip />} />
                  <Legend />
                  <Bar dataKey="accounts" name="Accounts" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="users" name="Users" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="jobs" name="Jobs" fill="#10b981" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="applications" name="Applications" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Section>

        {/* Tier Distribution + Onboarding */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <Section title="Tier Distribution" icon={Building2}>
            <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
              <CardContent className="p-6">
                <ResponsiveContainer width="100%" height={240}>
                  <PieChart>
                    <Pie data={tierPieData} cx="50%" cy="50%" innerRadius={55} outerRadius={90} paddingAngle={4} dataKey="value" label={({ name, value }) => `${name}: ${value}`}>
                      {tierPieData.map((entry, i) => (
                        <Cell key={entry.name} fill={TIER_COLORS[entry.name.toLowerCase()] || COLORS[i]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
                <div className="flex justify-center gap-4 mt-2">
                  {tierPieData.map((t) => (
                    <div key={t.name} className="flex items-center gap-1.5 text-sm">
                      <span className="w-3 h-3 rounded-full" style={{ backgroundColor: TIER_COLORS[t.name.toLowerCase()] }} />
                      {t.name}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </Section>

          <Section title="Onboarding Completion" icon={UserCheck}>
            <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
              <CardContent className="p-6 space-y-6">
                {[
                  { label: 'Job Seekers', data: a.onboarding?.job_seekers, color: 'blue' },
                  { label: 'Recruiters', data: a.onboarding?.recruiters, color: 'emerald' },
                ].map(({ label, data, color }) => {
                  const rate = data?.total ? Math.round((data.completed / data.total) * 100) : 0;
                  return (
                    <div key={label}>
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-sm font-medium text-slate-700">{label}</span>
                        <span className="text-sm text-slate-500">{data?.completed || 0} / {data?.total || 0} ({rate}%)</span>
                      </div>
                      <div className="w-full bg-slate-200 rounded-full h-3">
                        <div className={`h-3 rounded-full bg-${color}-500 transition-all`} style={{ width: `${rate}%` }} />
                      </div>
                    </div>
                  );
                })}
                <p className="text-xs text-slate-400 text-center pt-2">Percentage of users who completed onboarding</p>
              </CardContent>
            </Card>
          </Section>
        </div>

        {/* Job Breakdown Charts */}
        <Section title="Job Analytics" icon={Briefcase}>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
              <CardHeader className="pb-2"><CardTitle className="text-base text-slate-700">By Industry</CardTitle></CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={260}>
                  <BarChart data={a.jobs_by_industry || []} layout="vertical" margin={{ left: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis type="number" tick={{ fontSize: 12 }} />
                    <YAxis dataKey="name" type="category" tick={{ fontSize: 11 }} width={110} />
                    <Tooltip />
                    <Bar dataKey="count" fill="#3b82f6" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
            <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
              <CardHeader className="pb-2"><CardTitle className="text-base text-slate-700">By Location</CardTitle></CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={260}>
                  <BarChart data={a.jobs_by_location || []} layout="vertical" margin={{ left: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis type="number" tick={{ fontSize: 12 }} />
                    <YAxis dataKey="name" type="category" tick={{ fontSize: 11 }} width={140} />
                    <Tooltip />
                    <Bar dataKey="count" fill="#10b981" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
            <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
              <CardHeader className="pb-2"><CardTitle className="text-base text-slate-700">By Work Type</CardTitle></CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie data={a.jobs_by_work_type || []} cx="50%" cy="50%" outerRadius={70} dataKey="count" label={({ name, count }) => `${name}: ${count}`}>
                      {(a.jobs_by_work_type || []).map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
            <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
              <CardHeader className="pb-2"><CardTitle className="text-base text-slate-700">By Job Type</CardTitle></CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie data={a.jobs_by_job_type || []} cx="50%" cy="50%" outerRadius={70} dataKey="count" label={({ name, count }) => `${name}: ${count}`}>
                      {(a.jobs_by_job_type || []).map((_, i) => <Cell key={i} fill={COLORS[(i + 3) % COLORS.length]} />)}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </Section>

        {/* Account Details Table */}
        <Section title="Account Details" icon={Building2} defaultOpen={false}>
          <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-sm" data-testid="accounts-table">
                  <thead className="bg-slate-50 border-y border-slate-200">
                    <tr>
                      <th className="text-left py-3 px-4 font-semibold text-slate-700">Company</th>
                      <th className="text-left py-3 px-4 font-semibold text-slate-700">Tier</th>
                      <th className="text-left py-3 px-4 font-semibold text-slate-700">Status</th>
                      <th className="text-left py-3 px-4 font-semibold text-slate-700">Owner</th>
                      <th className="text-center py-3 px-4 font-semibold text-slate-700">Users</th>
                      <th className="text-center py-3 px-4 font-semibold text-slate-700">Jobs</th>
                      <th className="text-center py-3 px-4 font-semibold text-slate-700">Apps</th>
                      <th className="text-right py-3 px-4 font-semibold text-slate-700">MRR</th>
                      <th className="text-left py-3 px-4 font-semibold text-slate-700">Created</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(a.accounts_detail || []).map((acc, i) => (
                      <tr key={acc.id} className={i % 2 === 0 ? 'bg-white' : 'bg-slate-50/50'}>
                        <td className="py-3 px-4 font-medium text-slate-900">{acc.name}</td>
                        <td className="py-3 px-4">
                          <Badge style={{ backgroundColor: TIER_COLORS[acc.tier_id] + '20', color: TIER_COLORS[acc.tier_id] }} className="font-medium capitalize border-0">
                            {acc.tier_id}
                          </Badge>
                        </td>
                        <td className="py-3 px-4">
                          <Badge className={acc.subscription_status === 'active' ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-600'}>
                            {acc.subscription_status}
                          </Badge>
                        </td>
                        <td className="py-3 px-4 text-slate-600">{acc.owner_email}</td>
                        <td className="py-3 px-4 text-center">{acc.user_count}{acc.extra_users > 0 && <span className="text-blue-600"> (+{acc.extra_users})</span>}</td>
                        <td className="py-3 px-4 text-center">{acc.job_count}</td>
                        <td className="py-3 px-4 text-center">{acc.application_count}</td>
                        <td className="py-3 px-4 text-right font-medium">{formatZAR(acc.mrr)}</td>
                        <td className="py-3 px-4 text-slate-500 text-xs">{new Date(acc.created_at).toLocaleDateString('en-ZA')}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </Section>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
