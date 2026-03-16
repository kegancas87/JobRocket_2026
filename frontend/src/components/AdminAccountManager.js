import React, { useState, useEffect, useCallback } from 'react';
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Input } from "./ui/input";
import { Textarea } from "./ui/textarea";
import { Label } from "./ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import {
  Search, Building2, Crown, Zap, Users, CreditCard, Plus,
  ArrowUpRight, ChevronRight, Loader2, Check, X, Shield,
  History, DollarSign, UserPlus, Package, AlertCircle, Trash2,
  User, Briefcase, GraduationCap, Award, Mail, Phone, MapPin,
  Save, Pencil, Eye, ChevronDown
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
const Modal = ({ open, onClose, title, children, size = 'md' }) => {
  if (!open) return null;
  const sizeClasses = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl'
  };
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-y-auto" onClick={onClose}>
      <Card className={`w-full ${sizeClasses[size]} bg-white shadow-2xl my-8`} onClick={e => e.stopPropagation()}>
        <CardHeader className="pb-3 sticky top-0 bg-white z-10 border-b">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">{title}</CardTitle>
            <button onClick={onClose} className="text-slate-400 hover:text-slate-600"><X className="w-5 h-5" /></button>
          </div>
        </CardHeader>
        <CardContent className="max-h-[70vh] overflow-y-auto">{children}</CardContent>
      </Card>
    </div>
  );
};

const AdminAccountManager = ({ user }) => {
  const [activeTab, setActiveTab] = useState('accounts');
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

  // User management states
  const [users, setUsers] = useState([]);
  const [userSearchTerm, setUserSearchTerm] = useState('');
  const [userRoleFilter, setUserRoleFilter] = useState('');
  const [usersLoading, setUsersLoading] = useState(false);
  const [showUserModal, setShowUserModal] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [accountsList, setAccountsList] = useState([]);
  const [userForm, setUserForm] = useState({
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    role: 'job_seeker',
    phone: '',
    location: '',
    about_me: '',
    skills: [],
    job_title: '',
    linkedin_url: '',
    portfolio_url: '',
    expected_salary_min: '',
    expected_salary_max: '',
    work_experience: [],
    education: [],
    achievements: [],
    // Recruiter fields
    account_id: '',
    company_name: '',
    company_website: '',
    company_industry: '',
    company_size: '',
    company_description: '',
    tier_id: 'starter',
    credit_balance: 0
  });
  const [newSkill, setNewSkill] = useState('');
  const [newWorkExp, setNewWorkExp] = useState({ company: '', position: '', location: '', start_date: '', end_date: '', current: false, description: '' });
  const [newEducation, setNewEducation] = useState({ institution: '', degree: '', field_of_study: '', level: 'Bachelors', start_date: '', end_date: '', current: false, grade: '' });
  const [newAchievement, setNewAchievement] = useState({ title: '', issuer: '', date_achieved: '', description: '', credential_url: '' });

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

  const fetchUsers = useCallback(async () => {
    try {
      setUsersLoading(true);
      const params = new URLSearchParams();
      if (userRoleFilter) params.append('role', userRoleFilter);
      if (userSearchTerm) params.append('search', userSearchTerm);
      params.append('limit', '100');
      
      const res = await axios.get(`${API}/admin/users?${params.toString()}`, getAuthHeaders());
      setUsers(res.data.users || []);
    } catch (err) {
      console.error('Failed to load users:', err);
    } finally {
      setUsersLoading(false);
    }
  }, [userRoleFilter, userSearchTerm]);

  const fetchAccountsList = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/admin/accounts-list`, getAuthHeaders());
      setAccountsList(res.data.accounts || []);
    } catch (err) {
      console.error('Failed to load accounts list:', err);
    }
  }, []);

  useEffect(() => { fetchAccounts(); }, [fetchAccounts]);
  useEffect(() => { 
    if (activeTab === 'users') {
      fetchUsers();
      fetchAccountsList();
    }
  }, [activeTab, fetchUsers, fetchAccountsList]);

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

  // User management handlers
  const resetUserForm = () => {
    setUserForm({
      email: '', password: '', first_name: '', last_name: '', role: 'job_seeker',
      phone: '', location: '', about_me: '', skills: [], job_title: '',
      linkedin_url: '', portfolio_url: '', expected_salary_min: '', expected_salary_max: '',
      work_experience: [], education: [], achievements: [],
      account_id: '', company_name: '', company_website: '', company_industry: '',
      company_size: '', company_description: '', tier_id: 'starter', credit_balance: 0
    });
    setNewSkill('');
    setNewWorkExp({ company: '', position: '', location: '', start_date: '', end_date: '', current: false, description: '' });
    setNewEducation({ institution: '', degree: '', field_of_study: '', level: 'Bachelors', start_date: '', end_date: '', current: false, grade: '' });
    setNewAchievement({ title: '', issuer: '', date_achieved: '', description: '', credential_url: '' });
  };

  const openCreateUserModal = () => {
    resetUserForm();
    setEditingUser(null);
    setShowUserModal(true);
  };

  const openEditUserModal = async (userId) => {
    try {
      setActionLoading(true);
      const res = await axios.get(`${API}/admin/users/${userId}`, getAuthHeaders());
      const userData = res.data;
      
      setUserForm({
        email: userData.email || '',
        password: '',
        first_name: userData.first_name || '',
        last_name: userData.last_name || '',
        role: userData.role || 'job_seeker',
        phone: userData.phone || '',
        location: userData.location || '',
        about_me: userData.about_me || '',
        skills: userData.skills || [],
        job_title: userData.job_title || '',
        linkedin_url: userData.linkedin_url || '',
        portfolio_url: userData.portfolio_url || '',
        expected_salary_min: userData.expected_salary_min || '',
        expected_salary_max: userData.expected_salary_max || '',
        work_experience: userData.work_experience || [],
        education: userData.education || [],
        achievements: userData.achievements || [],
        account_id: userData.account_id || '',
        company_name: userData.account?.name || '',
        company_website: userData.account?.website || '',
        company_industry: userData.account?.industry || '',
        company_size: userData.account?.company_size || '',
        company_description: userData.account?.description || '',
        tier_id: userData.account?.tier_id || 'starter',
        credit_balance: userData.account?.credit_balance || 0
      });
      setEditingUser(userData);
      setShowUserModal(true);
    } catch (err) {
      showFeedback('error', 'Failed to load user details');
    } finally {
      setActionLoading(false);
    }
  };

  const handleSaveUser = async () => {
    if (!userForm.first_name || !userForm.last_name || !userForm.email) {
      showFeedback('error', 'First name, last name, and email are required');
      return;
    }
    if (!editingUser && !userForm.password) {
      showFeedback('error', 'Password is required for new users');
      return;
    }

    setActionLoading(true);
    try {
      if (editingUser) {
        await axios.put(`${API}/admin/users/${editingUser.id}`, userForm, getAuthHeaders());
        showFeedback('success', 'User updated successfully');
      } else {
        await axios.post(`${API}/admin/users`, userForm, getAuthHeaders());
        showFeedback('success', 'User created successfully');
      }
      setShowUserModal(false);
      resetUserForm();
      fetchUsers();
    } catch (err) {
      showFeedback('error', err.response?.data?.detail || 'Failed to save user');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDeactivateUser = async (userId) => {
    if (!window.confirm('Are you sure you want to deactivate this user?')) return;
    try {
      await axios.delete(`${API}/admin/users/${userId}`, getAuthHeaders());
      showFeedback('success', 'User deactivated');
      fetchUsers();
    } catch (err) {
      showFeedback('error', err.response?.data?.detail || 'Failed to deactivate user');
    }
  };

  const addSkill = () => {
    if (newSkill.trim() && !userForm.skills.includes(newSkill.trim())) {
      setUserForm(f => ({ ...f, skills: [...f.skills, newSkill.trim()] }));
      setNewSkill('');
    }
  };

  const removeSkill = (skill) => {
    setUserForm(f => ({ ...f, skills: f.skills.filter(s => s !== skill) }));
  };

  const addWorkExperience = () => {
    if (newWorkExp.company && newWorkExp.position) {
      setUserForm(f => ({ ...f, work_experience: [...f.work_experience, { ...newWorkExp, id: Date.now().toString() }] }));
      setNewWorkExp({ company: '', position: '', location: '', start_date: '', end_date: '', current: false, description: '' });
    }
  };

  const removeWorkExperience = (index) => {
    setUserForm(f => ({ ...f, work_experience: f.work_experience.filter((_, i) => i !== index) }));
  };

  const addEducation = () => {
    if (newEducation.institution && newEducation.degree) {
      setUserForm(f => ({ ...f, education: [...f.education, { ...newEducation, id: Date.now().toString() }] }));
      setNewEducation({ institution: '', degree: '', field_of_study: '', level: 'Bachelors', start_date: '', end_date: '', current: false, grade: '' });
    }
  };

  const removeEducation = (index) => {
    setUserForm(f => ({ ...f, education: f.education.filter((_, i) => i !== index) }));
  };

  const addAchievement = () => {
    if (newAchievement.title && newAchievement.issuer) {
      setUserForm(f => ({ ...f, achievements: [...f.achievements, { ...newAchievement, id: Date.now().toString() }] }));
      setNewAchievement({ title: '', issuer: '', date_achieved: '', description: '', credential_url: '' });
    }
  };

  const removeAchievement = (index) => {
    setUserForm(f => ({ ...f, achievements: f.achievements.filter((_, i) => i !== index) }));
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
            Admin Management
          </h1>
          <p className="text-slate-600 mt-1">Manage accounts, users, subscriptions, and more</p>
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

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="bg-white/80 p-1 shadow-sm">
            <TabsTrigger value="accounts" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white">
              <Building2 className="w-4 h-4 mr-2" />
              Accounts
            </TabsTrigger>
            <TabsTrigger value="users" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white">
              <Users className="w-4 h-4 mr-2" />
              Users
            </TabsTrigger>
          </TabsList>

          {/* Accounts Tab */}
          <TabsContent value="accounts">
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
          </TabsContent>

          {/* Users Tab */}
          <TabsContent value="users">
            <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
              <CardHeader>
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                  <CardTitle className="text-lg text-slate-700 flex items-center">
                    <Users className="w-5 h-5 mr-2 text-blue-600" />
                    User Management
                  </CardTitle>
                  <Button onClick={openCreateUserModal} className="bg-blue-600 hover:bg-blue-700" data-testid="create-user-btn">
                    <Plus className="w-4 h-4 mr-2" />
                    Create User
                  </Button>
                </div>
                <div className="flex flex-col sm:flex-row gap-3 mt-4">
                  <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                    <Input
                      value={userSearchTerm}
                      onChange={(e) => setUserSearchTerm(e.target.value)}
                      placeholder="Search by name or email..."
                      className="pl-9"
                      data-testid="user-search-input"
                    />
                  </div>
                  <select
                    value={userRoleFilter}
                    onChange={(e) => setUserRoleFilter(e.target.value)}
                    className="px-3 py-2 border border-slate-300 rounded-md text-sm"
                    data-testid="user-role-filter"
                  >
                    <option value="">All Roles</option>
                    <option value="job_seeker">Job Seekers</option>
                    <option value="recruiter">Recruiters</option>
                  </select>
                  <Button variant="outline" onClick={fetchUsers} disabled={usersLoading}>
                    {usersLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Refresh'}
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {usersLoading ? (
                  <div className="p-12 text-center"><Loader2 className="w-8 h-8 animate-spin mx-auto text-blue-500" /></div>
                ) : users.length === 0 ? (
                  <div className="p-12 text-center text-slate-500">
                    <Users className="w-12 h-12 mx-auto mb-4 text-slate-300" />
                    <p>No users found</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-slate-200">
                          <th className="text-left p-3 font-medium text-slate-600">User</th>
                          <th className="text-left p-3 font-medium text-slate-600">Role</th>
                          <th className="text-left p-3 font-medium text-slate-600">Status</th>
                          <th className="text-left p-3 font-medium text-slate-600">Created</th>
                          <th className="text-right p-3 font-medium text-slate-600">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {users.map((u) => (
                          <tr key={u.id} className="border-b border-slate-100 hover:bg-slate-50">
                            <td className="p-3">
                              <div className="flex items-center gap-3">
                                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-100 to-slate-200 flex items-center justify-center">
                                  <User className="w-4 h-4 text-slate-500" />
                                </div>
                                <div>
                                  <p className="font-medium text-slate-900">{u.first_name} {u.last_name}</p>
                                  <p className="text-xs text-slate-500">{u.email}</p>
                                </div>
                              </div>
                            </td>
                            <td className="p-3">
                              <Badge className={u.role === 'recruiter' ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700'}>
                                {u.role === 'recruiter' ? 'Recruiter' : 'Job Seeker'}
                              </Badge>
                            </td>
                            <td className="p-3">
                              <Badge className={u.is_active !== false ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}>
                                {u.is_active !== false ? 'Active' : 'Inactive'}
                              </Badge>
                            </td>
                            <td className="p-3 text-slate-600">
                              {u.created_at ? new Date(u.created_at).toLocaleDateString('en-ZA') : '-'}
                            </td>
                            <td className="p-3 text-right">
                              <div className="flex justify-end gap-2">
                                <Button variant="ghost" size="sm" onClick={() => openEditUserModal(u.id)} className="text-blue-600 hover:text-blue-700 hover:bg-blue-50" data-testid={`edit-user-${u.id}`}>
                                  <Pencil className="w-4 h-4" />
                                </Button>
                                <Button variant="ghost" size="sm" onClick={() => handleDeactivateUser(u.id)} className="text-red-600 hover:text-red-700 hover:bg-red-50" data-testid={`deactivate-user-${u.id}`}>
                                  <Trash2 className="w-4 h-4" />
                                </Button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
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

      {/* Create/Edit User Modal */}
      <Modal open={showUserModal} onClose={() => { setShowUserModal(false); resetUserForm(); }} title={editingUser ? 'Edit User' : 'Create New User'} size="xl">
        <div className="space-y-6">
          {/* Basic Info */}
          <div className="space-y-4">
            <h3 className="font-semibold text-slate-800 flex items-center border-b pb-2">
              <User className="w-4 h-4 mr-2 text-blue-600" />
              Basic Information
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>First Name *</Label>
                <Input value={userForm.first_name} onChange={(e) => setUserForm(f => ({ ...f, first_name: e.target.value }))} placeholder="John" data-testid="user-first-name" />
              </div>
              <div className="space-y-2">
                <Label>Last Name *</Label>
                <Input value={userForm.last_name} onChange={(e) => setUserForm(f => ({ ...f, last_name: e.target.value }))} placeholder="Doe" data-testid="user-last-name" />
              </div>
              <div className="space-y-2">
                <Label>Email *</Label>
                <Input type="email" value={userForm.email} onChange={(e) => setUserForm(f => ({ ...f, email: e.target.value }))} placeholder="john@example.com" disabled={!!editingUser} data-testid="user-email" />
              </div>
              <div className="space-y-2">
                <Label>{editingUser ? 'New Password (leave blank to keep)' : 'Password *'}</Label>
                <Input type="password" value={userForm.password} onChange={(e) => setUserForm(f => ({ ...f, password: e.target.value }))} placeholder="••••••••" data-testid="user-password" />
              </div>
              <div className="space-y-2">
                <Label>Role *</Label>
                <select value={userForm.role} onChange={(e) => setUserForm(f => ({ ...f, role: e.target.value }))} disabled={!!editingUser}
                  className="w-full px-3 py-2 border border-slate-300 rounded-md" data-testid="user-role">
                  <option value="job_seeker">Job Seeker</option>
                  <option value="recruiter">Recruiter</option>
                </select>
              </div>
              <div className="space-y-2">
                <Label>Phone</Label>
                <Input value={userForm.phone} onChange={(e) => setUserForm(f => ({ ...f, phone: e.target.value }))} placeholder="+27 82 123 4567" />
              </div>
              <div className="space-y-2 md:col-span-2">
                <Label>Location</Label>
                <Input value={userForm.location} onChange={(e) => setUserForm(f => ({ ...f, location: e.target.value }))} placeholder="Cape Town, South Africa" />
              </div>
            </div>
          </div>

          {/* Job Seeker Specific Fields */}
          {userForm.role === 'job_seeker' && (
            <>
              {/* Profile */}
              <div className="space-y-4">
                <h3 className="font-semibold text-slate-800 flex items-center border-b pb-2">
                  <Briefcase className="w-4 h-4 mr-2 text-blue-600" />
                  Profile Details
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Job Title</Label>
                    <Input value={userForm.job_title} onChange={(e) => setUserForm(f => ({ ...f, job_title: e.target.value }))} placeholder="Software Developer" />
                  </div>
                  <div className="space-y-2">
                    <Label>LinkedIn URL</Label>
                    <Input value={userForm.linkedin_url} onChange={(e) => setUserForm(f => ({ ...f, linkedin_url: e.target.value }))} placeholder="https://linkedin.com/in/..." />
                  </div>
                  <div className="space-y-2">
                    <Label>Portfolio URL</Label>
                    <Input value={userForm.portfolio_url} onChange={(e) => setUserForm(f => ({ ...f, portfolio_url: e.target.value }))} placeholder="https://..." />
                  </div>
                  <div className="space-y-2">
                    <Label>Expected Salary (Min)</Label>
                    <Input type="number" value={userForm.expected_salary_min} onChange={(e) => setUserForm(f => ({ ...f, expected_salary_min: e.target.value }))} placeholder="30000" />
                  </div>
                  <div className="space-y-2">
                    <Label>Expected Salary (Max)</Label>
                    <Input type="number" value={userForm.expected_salary_max} onChange={(e) => setUserForm(f => ({ ...f, expected_salary_max: e.target.value }))} placeholder="50000" />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>About</Label>
                  <Textarea value={userForm.about_me} onChange={(e) => setUserForm(f => ({ ...f, about_me: e.target.value }))} placeholder="Brief description about the candidate..." rows={3} />
                </div>
              </div>

              {/* Skills */}
              <div className="space-y-4">
                <h3 className="font-semibold text-slate-800 border-b pb-2">Skills</h3>
                <div className="flex gap-2">
                  <Input value={newSkill} onChange={(e) => setNewSkill(e.target.value)} placeholder="Add skill..." onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill())} />
                  <Button type="button" variant="outline" onClick={addSkill}><Plus className="w-4 h-4" /></Button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {userForm.skills.map((skill, i) => (
                    <Badge key={i} className="bg-blue-100 text-blue-700 px-3 py-1">
                      {skill}
                      <button onClick={() => removeSkill(skill)} className="ml-2 text-blue-500 hover:text-blue-700"><X className="w-3 h-3" /></button>
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Work Experience */}
              <div className="space-y-4">
                <h3 className="font-semibold text-slate-800 flex items-center border-b pb-2">
                  <Briefcase className="w-4 h-4 mr-2 text-blue-600" />
                  Work Experience
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 p-4 bg-slate-50 rounded-lg">
                  <Input value={newWorkExp.company} onChange={(e) => setNewWorkExp(f => ({ ...f, company: e.target.value }))} placeholder="Company" />
                  <Input value={newWorkExp.position} onChange={(e) => setNewWorkExp(f => ({ ...f, position: e.target.value }))} placeholder="Position" />
                  <Input value={newWorkExp.location} onChange={(e) => setNewWorkExp(f => ({ ...f, location: e.target.value }))} placeholder="Location" />
                  <Input type="date" value={newWorkExp.start_date} onChange={(e) => setNewWorkExp(f => ({ ...f, start_date: e.target.value }))} />
                  <Input type="date" value={newWorkExp.end_date} onChange={(e) => setNewWorkExp(f => ({ ...f, end_date: e.target.value }))} disabled={newWorkExp.current} />
                  <div className="flex items-center gap-2">
                    <input type="checkbox" checked={newWorkExp.current} onChange={(e) => setNewWorkExp(f => ({ ...f, current: e.target.checked }))} />
                    <Label>Current</Label>
                  </div>
                  <Textarea className="md:col-span-2" value={newWorkExp.description} onChange={(e) => setNewWorkExp(f => ({ ...f, description: e.target.value }))} placeholder="Description..." rows={2} />
                  <Button type="button" variant="outline" onClick={addWorkExperience} className="md:col-span-2"><Plus className="w-4 h-4 mr-2" />Add Experience</Button>
                </div>
                {userForm.work_experience.map((exp, i) => (
                  <div key={i} className="p-3 border border-slate-200 rounded-lg flex justify-between items-start">
                    <div>
                      <p className="font-medium text-slate-800">{exp.position}</p>
                      <p className="text-sm text-blue-600">{exp.company}</p>
                      <p className="text-xs text-slate-500">{exp.start_date} - {exp.current ? 'Present' : exp.end_date}</p>
                    </div>
                    <Button variant="ghost" size="sm" onClick={() => removeWorkExperience(i)} className="text-red-500"><Trash2 className="w-4 h-4" /></Button>
                  </div>
                ))}
              </div>

              {/* Education */}
              <div className="space-y-4">
                <h3 className="font-semibold text-slate-800 flex items-center border-b pb-2">
                  <GraduationCap className="w-4 h-4 mr-2 text-blue-600" />
                  Education
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 p-4 bg-slate-50 rounded-lg">
                  <Input value={newEducation.institution} onChange={(e) => setNewEducation(f => ({ ...f, institution: e.target.value }))} placeholder="Institution" />
                  <Input value={newEducation.degree} onChange={(e) => setNewEducation(f => ({ ...f, degree: e.target.value }))} placeholder="Degree" />
                  <Input value={newEducation.field_of_study} onChange={(e) => setNewEducation(f => ({ ...f, field_of_study: e.target.value }))} placeholder="Field of Study" />
                  <select value={newEducation.level} onChange={(e) => setNewEducation(f => ({ ...f, level: e.target.value }))} className="px-3 py-2 border border-slate-300 rounded-md">
                    <option value="Matric">Matric</option>
                    <option value="Certificate">Certificate</option>
                    <option value="Diploma">Diploma</option>
                    <option value="Bachelors">Bachelors</option>
                    <option value="Honours">Honours</option>
                    <option value="Masters">Masters</option>
                    <option value="Doctorate">Doctorate</option>
                  </select>
                  <Input type="date" value={newEducation.start_date} onChange={(e) => setNewEducation(f => ({ ...f, start_date: e.target.value }))} />
                  <Input type="date" value={newEducation.end_date} onChange={(e) => setNewEducation(f => ({ ...f, end_date: e.target.value }))} disabled={newEducation.current} />
                  <Input value={newEducation.grade} onChange={(e) => setNewEducation(f => ({ ...f, grade: e.target.value }))} placeholder="Grade/GPA" />
                  <div className="flex items-center gap-2">
                    <input type="checkbox" checked={newEducation.current} onChange={(e) => setNewEducation(f => ({ ...f, current: e.target.checked }))} />
                    <Label>Currently studying</Label>
                  </div>
                  <Button type="button" variant="outline" onClick={addEducation} className="md:col-span-2"><Plus className="w-4 h-4 mr-2" />Add Education</Button>
                </div>
                {userForm.education.map((edu, i) => (
                  <div key={i} className="p-3 border border-slate-200 rounded-lg flex justify-between items-start">
                    <div>
                      <p className="font-medium text-slate-800">{edu.degree}</p>
                      <p className="text-sm text-blue-600">{edu.institution}</p>
                      <p className="text-xs text-slate-500">{edu.field_of_study} • {edu.level}</p>
                    </div>
                    <Button variant="ghost" size="sm" onClick={() => removeEducation(i)} className="text-red-500"><Trash2 className="w-4 h-4" /></Button>
                  </div>
                ))}
              </div>

              {/* Achievements */}
              <div className="space-y-4">
                <h3 className="font-semibold text-slate-800 flex items-center border-b pb-2">
                  <Award className="w-4 h-4 mr-2 text-blue-600" />
                  Awards & Achievements
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 p-4 bg-slate-50 rounded-lg">
                  <Input value={newAchievement.title} onChange={(e) => setNewAchievement(f => ({ ...f, title: e.target.value }))} placeholder="Title" />
                  <Input value={newAchievement.issuer} onChange={(e) => setNewAchievement(f => ({ ...f, issuer: e.target.value }))} placeholder="Issuing Organization" />
                  <Input type="date" value={newAchievement.date_achieved} onChange={(e) => setNewAchievement(f => ({ ...f, date_achieved: e.target.value }))} />
                  <Input value={newAchievement.credential_url} onChange={(e) => setNewAchievement(f => ({ ...f, credential_url: e.target.value }))} placeholder="Credential URL" />
                  <Textarea className="md:col-span-2" value={newAchievement.description} onChange={(e) => setNewAchievement(f => ({ ...f, description: e.target.value }))} placeholder="Description..." rows={2} />
                  <Button type="button" variant="outline" onClick={addAchievement} className="md:col-span-2"><Plus className="w-4 h-4 mr-2" />Add Achievement</Button>
                </div>
                {userForm.achievements.map((ach, i) => (
                  <div key={i} className="p-3 border border-slate-200 rounded-lg flex justify-between items-start">
                    <div>
                      <p className="font-medium text-slate-800">{ach.title}</p>
                      <p className="text-sm text-blue-600">{ach.issuer}</p>
                      <p className="text-xs text-slate-500">{ach.date_achieved}</p>
                    </div>
                    <Button variant="ghost" size="sm" onClick={() => removeAchievement(i)} className="text-red-500"><Trash2 className="w-4 h-4" /></Button>
                  </div>
                ))}
              </div>
            </>
          )}

          {/* Recruiter Specific Fields */}
          {userForm.role === 'recruiter' && (
            <div className="space-y-4">
              <h3 className="font-semibold text-slate-800 flex items-center border-b pb-2">
                <Building2 className="w-4 h-4 mr-2 text-blue-600" />
                Company & Account
              </h3>
              
              {!editingUser && (
                <div className="space-y-2">
                  <Label>Assign to Existing Account (optional)</Label>
                  <select value={userForm.account_id} onChange={(e) => setUserForm(f => ({ ...f, account_id: e.target.value }))}
                    className="w-full px-3 py-2 border border-slate-300 rounded-md">
                    <option value="">Create New Account</option>
                    {accountsList.map((acc) => (
                      <option key={acc.id} value={acc.id}>{acc.name} ({acc.tier_id})</option>
                    ))}
                  </select>
                </div>
              )}

              {(!userForm.account_id || editingUser) && (
                <>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Company Name</Label>
                      <Input value={userForm.company_name} onChange={(e) => setUserForm(f => ({ ...f, company_name: e.target.value }))} placeholder="Acme Inc" />
                    </div>
                    <div className="space-y-2">
                      <Label>Website</Label>
                      <Input value={userForm.company_website} onChange={(e) => setUserForm(f => ({ ...f, company_website: e.target.value }))} placeholder="https://..." />
                    </div>
                    <div className="space-y-2">
                      <Label>Industry</Label>
                      <Input value={userForm.company_industry} onChange={(e) => setUserForm(f => ({ ...f, company_industry: e.target.value }))} placeholder="Technology" />
                    </div>
                    <div className="space-y-2">
                      <Label>Company Size</Label>
                      <select value={userForm.company_size} onChange={(e) => setUserForm(f => ({ ...f, company_size: e.target.value }))}
                        className="w-full px-3 py-2 border border-slate-300 rounded-md">
                        <option value="">Select size</option>
                        <option value="1-10">1-10 employees</option>
                        <option value="11-50">11-50 employees</option>
                        <option value="51-200">51-200 employees</option>
                        <option value="201-500">201-500 employees</option>
                        <option value="501+">501+ employees</option>
                      </select>
                    </div>
                    <div className="space-y-2">
                      <Label>Subscription Tier</Label>
                      <select value={userForm.tier_id} onChange={(e) => setUserForm(f => ({ ...f, tier_id: e.target.value }))}
                        className="w-full px-3 py-2 border border-slate-300 rounded-md">
                        {TIERS.map((t) => (
                          <option key={t.id} value={t.id}>{t.name} - {formatZAR(t.price)}/mo</option>
                        ))}
                      </select>
                    </div>
                    <div className="space-y-2">
                      <Label>Credit Balance (ZAR)</Label>
                      <Input type="number" value={userForm.credit_balance} onChange={(e) => setUserForm(f => ({ ...f, credit_balance: parseInt(e.target.value) || 0 }))} placeholder="0" />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label>Company Description</Label>
                    <Textarea value={userForm.company_description} onChange={(e) => setUserForm(f => ({ ...f, company_description: e.target.value }))} placeholder="About the company..." rows={3} />
                  </div>
                </>
              )}
            </div>
          )}

          {/* Save Button */}
          <div className="flex justify-end gap-3 pt-4 border-t">
            <Button variant="outline" onClick={() => { setShowUserModal(false); resetUserForm(); }}>Cancel</Button>
            <Button onClick={handleSaveUser} disabled={actionLoading} className="bg-blue-600 hover:bg-blue-700" data-testid="save-user-btn">
              {actionLoading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Save className="w-4 h-4 mr-2" />}
              {editingUser ? 'Update User' : 'Create User'}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default AdminAccountManager;
