import React, { useState, useEffect, useCallback } from 'react';
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Input } from "./ui/input";
import {
  Search, Building2, Crown, Zap, Users, CreditCard, Plus,
  ArrowUpRight, ChevronRight, Loader2, Check, X, Shield,
  History, DollarSign, UserPlus, Package, AlertCircle, Trash2
} from "lucide-react";
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TIER_COLORS = { starter: '#64748b', growth: '#3b82f6', pro: '#8b5cf6', enterprise: '#f59e0b' };
const TIERS = [
  { id: 'starter', name: 'Starter', price: 6899 },
  { id: 'growth', name: 'Growth', price: 10499 },
  { id: 'pro', name: 'Pro', price: 19999 },
  { id: 'enterprise', name: 'Enterprise', price: 39999 },
];

const ALL_ADDONS = [
  { id: 'addon_candidate_notes', name: 'Candidate Notes & Tags' },
  { id: 'addon_talent_alerts', name: 'Talent Pool Alerts' },
  { id: 'addon_whatsapp_dist', name: 'WhatsApp Distribution' },
  { id: 'addon_social_dist', name: 'Social Media Distribution' },
  { id: 'addon_monthly_campaigns', name: 'Monthly Job Campaigns' },
  { id: 'addon_featured_listings', name: 'Featured Job Listings' },
  { id: 'addon_employer_video', name: 'Employer Video' },
  { id: 'addon_branding_pack', name: 'Employer Branding Pack' },
  { id: 'addon_interview_sched', name: 'Interview Scheduling' },
  { id: 'addon_ats_export', name: 'ATS Export' },
  { id: 'addon_priority_access', name: 'Priority Candidate Access' },
  { id: 'addon_hot_alerts', name: 'Hot Candidate Alerts' },
];

const formatZAR = (val) => new Intl.NumberFormat('en-ZA', { style: 'currency', currency: 'ZAR', minimumFractionDigits: 0 }).format(val);

const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return { headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' } };
};

// Action labels for audit log
const ACTION_LABELS = {
  tier_change: { label: 'Tier Changed', icon: Crown, color: 'text-purple-600 bg-purple-50' },
  addon_grant: { label: 'Add-on Granted', icon: Zap, color: 'text-blue-600 bg-blue-50' },
  addon_revoke: { label: 'Add-on Revoked', icon: Trash2, color: 'text-red-600 bg-red-50' },
  seats_added: { label: 'Seats Added', icon: UserPlus, color: 'text-emerald-600 bg-emerald-50' },
  credit_added: { label: 'Credits Added', icon: DollarSign, color: 'text-green-600 bg-green-50' },
};

// Modal wrapper
const Modal = ({ open, onClose, title, children }) => {
  if (!open) return null;
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <Card className="w-full max-w-md bg-white shadow-2xl" onClick={e => e.stopPropagation()}>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">{title}</CardTitle>
            <button onClick={onClose} className="text-slate-400 hover:text-slate-600"><X className="w-5 h-5" /></button>
          </div>
        </CardHeader>
        <CardContent>{children}</CardContent>
      </Card>
    </div>
  );
};

const AdminAccountManager = ({ user }) => {
  const [accounts, setAccounts] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [accountDetail, setAccountDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [feedback, setFeedback] = useState({ type: '', message: '' });

  // Modal states
  const [showTierModal, setShowTierModal] = useState(false);
  const [showAddonModal, setShowAddonModal] = useState(false);
  const [showSeatsModal, setShowSeatsModal] = useState(false);
  const [showCreditsModal, setShowCreditsModal] = useState(false);

  // Form states
  const [tierForm, setTierForm] = useState({ tier_id: '', reason: '' });
  const [addonForm, setAddonForm] = useState({ addon_id: '', reason: '' });
  const [seatsForm, setSeatsForm] = useState({ quantity: 1, reason: '' });
  const [creditsForm, setCreditsForm] = useState({ amount: '', reason: '' });

  const fetchAccounts = useCallback(async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${API}/admin/stats?force_refresh=true`, getAuthHeaders());
      setAccounts(res.data.accounts || []);
    } catch (err) {
      console.error('Failed to load accounts:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchAccounts(); }, [fetchAccounts]);

  const loadAccountDetail = async (accountId) => {
    setDetailLoading(true);
    setFeedback({ type: '', message: '' });
    try {
      const res = await axios.get(`${API}/admin/accounts/${accountId}`, getAuthHeaders());
      setAccountDetail(res.data);
      setSelectedAccount(accountId);
    } catch (err) {
      console.error('Failed to load account:', err);
    } finally {
      setDetailLoading(false);
    }
  };

  const showFeedback = (type, message) => {
    setFeedback({ type, message });
    setTimeout(() => setFeedback({ type: '', message: '' }), 5000);
  };

  // --- Actions ---
  const handleChangeTier = async () => {
    if (!tierForm.tier_id) return;
    setActionLoading(true);
    try {
      await axios.put(`${API}/admin/accounts/${selectedAccount}/tier`, tierForm, getAuthHeaders());
      showFeedback('success', `Tier changed to ${tierForm.tier_id}`);
      setShowTierModal(false);
      setTierForm({ tier_id: '', reason: '' });
      loadAccountDetail(selectedAccount);
      fetchAccounts();
    } catch (err) {
      showFeedback('error', err.response?.data?.detail || 'Failed to change tier');
    } finally {
      setActionLoading(false);
    }
  };

  const handleGrantAddon = async () => {
    if (!addonForm.addon_id) return;
    setActionLoading(true);
    try {
      await axios.post(`${API}/admin/accounts/${selectedAccount}/addon`, addonForm, getAuthHeaders());
      showFeedback('success', 'Add-on granted successfully');
      setShowAddonModal(false);
      setAddonForm({ addon_id: '', reason: '' });
      loadAccountDetail(selectedAccount);
    } catch (err) {
      showFeedback('error', err.response?.data?.detail || 'Failed to grant add-on');
    } finally {
      setActionLoading(false);
    }
  };

  const handleRevokeAddon = async (addonPurchaseId) => {
    if (!window.confirm('Revoke this add-on?')) return;
    setActionLoading(true);
    try {
      await axios.delete(`${API}/admin/accounts/${selectedAccount}/addon/${addonPurchaseId}`, getAuthHeaders());
      showFeedback('success', 'Add-on revoked');
      loadAccountDetail(selectedAccount);
    } catch (err) {
      showFeedback('error', err.response?.data?.detail || 'Failed to revoke add-on');
    } finally {
      setActionLoading(false);
    }
  };

  const handleAddSeats = async () => {
    if (seatsForm.quantity < 1) return;
    setActionLoading(true);
    try {
      await axios.post(`${API}/admin/accounts/${selectedAccount}/seats`, seatsForm, getAuthHeaders());
      showFeedback('success', `${seatsForm.quantity} seat(s) added`);
      setShowSeatsModal(false);
      setSeatsForm({ quantity: 1, reason: '' });
      loadAccountDetail(selectedAccount);
      fetchAccounts();
    } catch (err) {
      showFeedback('error', err.response?.data?.detail || 'Failed to add seats');
    } finally {
      setActionLoading(false);
    }
  };

  const handleAddCredits = async () => {
    const amount = parseFloat(creditsForm.amount);
    if (!amount || amount <= 0) return;
    setActionLoading(true);
    try {
      await axios.post(`${API}/admin/accounts/${selectedAccount}/credits`, { amount, reason: creditsForm.reason }, getAuthHeaders());
      showFeedback('success', `${formatZAR(amount)} credited`);
      setShowCreditsModal(false);
      setCreditsForm({ amount: '', reason: '' });
      loadAccountDetail(selectedAccount);
    } catch (err) {
      showFeedback('error', err.response?.data?.detail || 'Failed to add credits');
    } finally {
      setActionLoading(false);
    }
  };

  const filteredAccounts = accounts.filter(a =>
    a.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    a.owner_email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    a.tier_id?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-800 flex items-center" data-testid="admin-manage-title">
            <Shield className="w-8 h-8 mr-3 text-blue-600" />
            Account Management
          </h1>
          <p className="text-slate-600 mt-1">Manage subscriptions, add-ons, seats, and credits for any account</p>
        </div>

        {/* Feedback */}
        {feedback.message && (
          <div className={`mb-6 p-4 rounded-lg flex items-center space-x-3 ${
            feedback.type === 'success' ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
          }`}>
            {feedback.type === 'success' ? <Check className="w-5 h-5 text-green-600" /> : <AlertCircle className="w-5 h-5 text-red-600" />}
            <span className={feedback.type === 'success' ? 'text-green-700' : 'text-red-700'}>{feedback.message}</span>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Account List */}
          <div className="lg:col-span-1">
            <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
              <CardHeader className="pb-3">
                <CardTitle className="text-base text-slate-700">Accounts</CardTitle>
                <div className="relative mt-2">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <Input
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Search accounts..."
                    className="pl-9 h-9"
                    data-testid="account-search-input"
                  />
                </div>
              </CardHeader>
              <CardContent className="p-0 max-h-[600px] overflow-y-auto">
                {loading ? (
                  <div className="p-8 text-center"><Loader2 className="w-6 h-6 animate-spin mx-auto text-blue-500" /></div>
                ) : filteredAccounts.length === 0 ? (
                  <div className="p-8 text-center text-slate-500">No accounts found</div>
                ) : (
                  filteredAccounts.map((acc) => (
                    <button
                      key={acc.id}
                      onClick={() => loadAccountDetail(acc.id)}
                      data-testid={`account-item-${acc.id}`}
                      className={`w-full text-left p-4 border-b border-slate-100 hover:bg-blue-50 transition-colors ${
                        selectedAccount === acc.id ? 'bg-blue-50 border-l-4 border-l-blue-500' : ''
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium text-slate-900 text-sm">{acc.name}</p>
                          <p className="text-xs text-slate-500">{acc.owner_email}</p>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge style={{ backgroundColor: TIER_COLORS[acc.tier_id] + '20', color: TIER_COLORS[acc.tier_id] }} className="text-xs capitalize border-0">
                            {acc.tier_id}
                          </Badge>
                          <ChevronRight className="w-4 h-4 text-slate-400" />
                        </div>
                      </div>
                    </button>
                  ))
                )}
              </CardContent>
            </Card>
          </div>

          {/* Account Detail + Actions */}
          <div className="lg:col-span-2">
            {!selectedAccount ? (
              <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
                <CardContent className="p-12 text-center">
                  <Building2 className="w-12 h-12 mx-auto mb-4 text-slate-300" />
                  <p className="text-slate-500">Select an account to manage</p>
                </CardContent>
              </Card>
            ) : detailLoading ? (
              <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
                <CardContent className="p-12 text-center"><Loader2 className="w-8 h-8 animate-spin mx-auto text-blue-500" /></CardContent>
              </Card>
            ) : accountDetail && (
              <div className="space-y-4">
                {/* Account Summary */}
                <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h2 className="text-xl font-bold text-slate-900" data-testid="account-detail-name">{accountDetail.name}</h2>
                        <p className="text-sm text-slate-500">{accountDetail.owner?.email}</p>
                      </div>
                      <Badge style={{ backgroundColor: TIER_COLORS[accountDetail.tier_id] + '20', color: TIER_COLORS[accountDetail.tier_id] }} className="text-sm capitalize border-0 px-3 py-1">
                        {accountDetail.tier_id}
                      </Badge>
                    </div>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                      <div className="p-3 bg-slate-50 rounded-lg text-center">
                        <p className="text-xs text-slate-500">MRR</p>
                        <p className="text-lg font-bold text-slate-800">{formatZAR(accountDetail.tier_price || 0)}</p>
                      </div>
                      <div className="p-3 bg-slate-50 rounded-lg text-center">
                        <p className="text-xs text-slate-500">Users</p>
                        <p className="text-lg font-bold text-slate-800">{accountDetail.current_user_count || 1}</p>
                      </div>
                      <div className="p-3 bg-slate-50 rounded-lg text-center">
                        <p className="text-xs text-slate-500">Jobs</p>
                        <p className="text-lg font-bold text-slate-800">{accountDetail.job_count || 0}</p>
                      </div>
                      <div className="p-3 bg-green-50 rounded-lg text-center">
                        <p className="text-xs text-green-600">Credit Balance</p>
                        <p className="text-lg font-bold text-green-700" data-testid="credit-balance">{formatZAR(accountDetail.credit_balance || 0)}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Action Buttons */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <Button onClick={() => { setTierForm({ tier_id: '', reason: '' }); setShowTierModal(true); }}
                    variant="outline" className="h-auto py-3 flex flex-col items-center gap-1.5 border-purple-200 hover:bg-purple-50" data-testid="change-tier-btn">
                    <Crown className="w-5 h-5 text-purple-600" />
                    <span className="text-xs font-medium">Change Tier</span>
                  </Button>
                  <Button onClick={() => { setAddonForm({ addon_id: '', reason: '' }); setShowAddonModal(true); }}
                    variant="outline" className="h-auto py-3 flex flex-col items-center gap-1.5 border-blue-200 hover:bg-blue-50" data-testid="grant-addon-btn">
                    <Zap className="w-5 h-5 text-blue-600" />
                    <span className="text-xs font-medium">Grant Add-on</span>
                  </Button>
                  <Button onClick={() => { setSeatsForm({ quantity: 1, reason: '' }); setShowSeatsModal(true); }}
                    variant="outline" className="h-auto py-3 flex flex-col items-center gap-1.5 border-emerald-200 hover:bg-emerald-50" data-testid="add-seats-btn">
                    <UserPlus className="w-5 h-5 text-emerald-600" />
                    <span className="text-xs font-medium">Add Seats</span>
                  </Button>
                  <Button onClick={() => { setCreditsForm({ amount: '', reason: '' }); setShowCreditsModal(true); }}
                    variant="outline" className="h-auto py-3 flex flex-col items-center gap-1.5 border-green-200 hover:bg-green-50" data-testid="add-credits-btn">
                    <DollarSign className="w-5 h-5 text-green-600" />
                    <span className="text-xs font-medium">Add Credits</span>
                  </Button>
                </div>

                {/* Active Add-ons */}
                {accountDetail.active_addons?.length > 0 && (
                  <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-base text-slate-700 flex items-center">
                        <Package className="w-4 h-4 mr-2 text-blue-600" /> Active Add-ons
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="p-0">
                      <div className="divide-y divide-slate-100">
                        {accountDetail.active_addons.map((addon) => (
                          <div key={addon.id} className="p-3 px-6 flex items-center justify-between">
                            <div>
                              <p className="text-sm font-medium text-slate-800">{addon.addon_id}</p>
                              {addon.admin_granted && <Badge className="bg-purple-100 text-purple-700 text-xs mt-0.5">Admin Granted</Badge>}
                            </div>
                            <Button variant="ghost" size="sm" onClick={() => handleRevokeAddon(addon.id)} className="text-red-500 hover:text-red-700 hover:bg-red-50">
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Audit Log */}
                <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base text-slate-700 flex items-center">
                      <History className="w-4 h-4 mr-2 text-slate-500" /> Admin Activity Log
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="p-0">
                    {(accountDetail.audit_log || []).length === 0 ? (
                      <div className="p-6 text-center text-sm text-slate-400">No admin actions recorded yet</div>
                    ) : (
                      <div className="divide-y divide-slate-100 max-h-72 overflow-y-auto">
                        {(accountDetail.audit_log || []).map((log, i) => {
                          const config = ACTION_LABELS[log.action] || { label: log.action, icon: History, color: 'text-slate-600 bg-slate-50' };
                          const Icon = config.icon;
                          return (
                            <div key={i} className="p-3 px-6 flex items-start gap-3">
                              <div className={`p-1.5 rounded-lg ${config.color} mt-0.5`}>
                                <Icon className="w-3.5 h-3.5" />
                              </div>
                              <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-slate-800">{config.label}</p>
                                <p className="text-xs text-slate-500 mt-0.5">
                                  {log.details?.reason && <span>{log.details.reason} &middot; </span>}
                                  {Object.entries(log.details || {}).filter(([k]) => k !== 'reason').map(([k, v]) => `${k}: ${v}`).join(', ')}
                                </p>
                                <p className="text-xs text-slate-400 mt-0.5">{log.created_at ? new Date(log.created_at).toLocaleString('en-ZA') : ''}</p>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Change Tier Modal */}
      <Modal open={showTierModal} onClose={() => setShowTierModal(false)} title="Change Subscription Tier">
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium text-slate-700 block mb-2">New Tier</label>
            <div className="grid grid-cols-2 gap-2">
              {TIERS.map((t) => (
                <button key={t.id} onClick={() => setTierForm(f => ({ ...f, tier_id: t.id }))}
                  className={`p-3 rounded-lg border-2 text-left transition-all ${
                    tierForm.tier_id === t.id ? 'border-purple-500 bg-purple-50' : 'border-slate-200 hover:border-purple-300'
                  } ${accountDetail?.tier_id === t.id ? 'opacity-50' : ''}`}
                  disabled={accountDetail?.tier_id === t.id}
                >
                  <p className="font-medium text-sm capitalize">{t.name}</p>
                  <p className="text-xs text-slate-500">{formatZAR(t.price)}/mo</p>
                  {accountDetail?.tier_id === t.id && <p className="text-xs text-blue-600 mt-0.5">Current</p>}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700 block mb-1">Reason (optional)</label>
            <Input value={tierForm.reason} onChange={(e) => setTierForm(f => ({ ...f, reason: e.target.value }))} placeholder="e.g. Testing, Customer request" />
          </div>
          <Button onClick={handleChangeTier} disabled={!tierForm.tier_id || actionLoading} className="w-full bg-purple-600 hover:bg-purple-700" data-testid="confirm-tier-change-btn">
            {actionLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Change Tier'}
          </Button>
        </div>
      </Modal>

      {/* Grant Add-on Modal */}
      <Modal open={showAddonModal} onClose={() => setShowAddonModal(false)} title="Grant Add-on Feature">
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium text-slate-700 block mb-2">Select Add-on</label>
            <div className="max-h-48 overflow-y-auto space-y-1">
              {ALL_ADDONS.map((addon) => {
                const isActive = (accountDetail?.active_addons || []).some(a => a.addon_id === addon.id);
                return (
                  <button key={addon.id} onClick={() => setAddonForm(f => ({ ...f, addon_id: addon.id }))}
                    disabled={isActive}
                    className={`w-full p-2.5 rounded-lg text-left text-sm transition-all ${
                      addonForm.addon_id === addon.id ? 'bg-blue-50 border-2 border-blue-500' :
                      isActive ? 'bg-slate-50 opacity-50' : 'border-2 border-slate-200 hover:border-blue-300'
                    }`}>
                    <span className="font-medium">{addon.name}</span>
                    {isActive && <span className="text-xs text-green-600 ml-2">Active</span>}
                  </button>
                );
              })}
            </div>
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700 block mb-1">Reason (optional)</label>
            <Input value={addonForm.reason} onChange={(e) => setAddonForm(f => ({ ...f, reason: e.target.value }))} placeholder="e.g. Testing, Promotional" />
          </div>
          <Button onClick={handleGrantAddon} disabled={!addonForm.addon_id || actionLoading} className="w-full bg-blue-600 hover:bg-blue-700" data-testid="confirm-addon-grant-btn">
            {actionLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Grant Add-on'}
          </Button>
        </div>
      </Modal>

      {/* Add Seats Modal */}
      <Modal open={showSeatsModal} onClose={() => setShowSeatsModal(false)} title="Add User Seats">
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium text-slate-700 block mb-2">Number of Seats</label>
            <div className="flex items-center gap-4">
              <Button variant="outline" size="sm" onClick={() => setSeatsForm(f => ({ ...f, quantity: Math.max(1, f.quantity - 1) }))}>-</Button>
              <span className="text-2xl font-bold w-12 text-center">{seatsForm.quantity}</span>
              <Button variant="outline" size="sm" onClick={() => setSeatsForm(f => ({ ...f, quantity: Math.min(50, f.quantity + 1) }))}>+</Button>
            </div>
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700 block mb-1">Reason (optional)</label>
            <Input value={seatsForm.reason} onChange={(e) => setSeatsForm(f => ({ ...f, reason: e.target.value }))} placeholder="e.g. Testing, Customer request" />
          </div>
          <Button onClick={handleAddSeats} disabled={actionLoading} className="w-full bg-emerald-600 hover:bg-emerald-700" data-testid="confirm-seats-btn">
            {actionLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : `Add ${seatsForm.quantity} Seat(s)`}
          </Button>
        </div>
      </Modal>

      {/* Add Credits Modal */}
      <Modal open={showCreditsModal} onClose={() => setShowCreditsModal(false)} title="Add Credit Balance">
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium text-slate-700 block mb-2">Amount (ZAR)</label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 font-medium">R</span>
              <Input
                type="number"
                value={creditsForm.amount}
                onChange={(e) => setCreditsForm(f => ({ ...f, amount: e.target.value }))}
                placeholder="0"
                className="pl-8 h-12 text-lg"
                data-testid="credit-amount-input"
              />
            </div>
            <div className="flex gap-2 mt-2">
              {[500, 1000, 5000, 10000].map((amt) => (
                <button key={amt} onClick={() => setCreditsForm(f => ({ ...f, amount: String(amt) }))}
                  className="px-3 py-1 text-xs rounded-full border border-slate-200 hover:bg-green-50 hover:border-green-300 transition-colors">
                  {formatZAR(amt)}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700 block mb-1">Reason (optional)</label>
            <Input value={creditsForm.reason} onChange={(e) => setCreditsForm(f => ({ ...f, reason: e.target.value }))} placeholder="e.g. Testing credit, Goodwill" />
          </div>
          {creditsForm.amount && (
            <div className="p-3 bg-green-50 rounded-lg text-center">
              <p className="text-sm text-green-700">New balance: <span className="font-bold">{formatZAR((accountDetail?.credit_balance || 0) + Number(creditsForm.amount || 0))}</span></p>
            </div>
          )}
          <Button onClick={handleAddCredits} disabled={!creditsForm.amount || Number(creditsForm.amount) <= 0 || actionLoading}
            className="w-full bg-green-600 hover:bg-green-700" data-testid="confirm-credits-btn">
            {actionLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : `Add ${formatZAR(Number(creditsForm.amount || 0))}`}
          </Button>
        </div>
      </Modal>
    </div>
  );
};

export default AdminAccountManager;
