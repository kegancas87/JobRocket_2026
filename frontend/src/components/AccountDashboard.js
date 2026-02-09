import React, { useState, useEffect } from 'react';
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "./ui/card";
import { Badge } from "./ui/badge";
import { Separator } from "./ui/separator";
import { 
  Building2,
  Users,
  CreditCard,
  Settings,
  BarChart3,
  Search,
  Plus,
  Edit2,
  Trash2,
  Mail,
  UserPlus,
  Shield,
  Crown,
  Eye,
  UserCheck,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  RefreshCw,
  Download,
  Filter,
  MoreVertical,
  Zap,
  Rocket,
  Star
} from "lucide-react";
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AccountDashboard = ({ user, onUpdateUser }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [account, setAccount] = useState(null);
  const [teamMembers, setTeamMembers] = useState([]);
  const [invitations, setInvitations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [inviteModalOpen, setInviteModalOpen] = useState(false);
  const [inviteForm, setInviteForm] = useState({
    email: '',
    first_name: '',
    last_name: '',
    account_role: 'recruiter'
  });
  const [inviting, setInviting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    return {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    };
  };

  useEffect(() => {
    fetchAccountData();
  }, []);

  const fetchAccountData = async () => {
    try {
      setLoading(true);
      setError('');
      
      const [accountRes, usersRes, invitationsRes] = await Promise.all([
        axios.get(`${API}/account`, getAuthHeaders()),
        axios.get(`${API}/account/users`, getAuthHeaders()),
        axios.get(`${API}/account/invitations`, getAuthHeaders())
      ]);
      
      setAccount(accountRes.data);
      setTeamMembers(usersRes.data);
      setInvitations(invitationsRes.data);
    } catch (error) {
      console.error('Error fetching account data:', error);
      setError('Failed to load account data');
    } finally {
      setLoading(false);
    }
  };

  const handleInvite = async (e) => {
    e.preventDefault();
    setInviting(true);
    setError('');
    setSuccess('');

    try {
      const response = await axios.post(`${API}/account/invite`, inviteForm, getAuthHeaders());
      setSuccess(`Invitation sent to ${inviteForm.email}`);
      setInviteForm({ email: '', first_name: '', last_name: '', account_role: 'recruiter' });
      setInviteModalOpen(false);
      fetchAccountData();
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Failed to send invitation';
      setError(errorMessage);
    } finally {
      setInviting(false);
    }
  };

  const handleRemoveUser = async (userId) => {
    if (!window.confirm('Are you sure you want to remove this user from your account?')) {
      return;
    }

    try {
      await axios.delete(`${API}/account/users/${userId}`, getAuthHeaders());
      setSuccess('User removed successfully');
      fetchAccountData();
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Failed to remove user';
      setError(errorMessage);
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-ZA', {
      style: 'currency',
      currency: 'ZAR',
      minimumFractionDigits: 0
    }).format(price);
  };

  const getRoleIcon = (role) => {
    switch (role) {
      case 'owner': return <Crown className="w-4 h-4 text-amber-500" />;
      case 'admin': return <Shield className="w-4 h-4 text-purple-500" />;
      case 'recruiter': return <UserCheck className="w-4 h-4 text-blue-500" />;
      case 'viewer': return <Eye className="w-4 h-4 text-slate-500" />;
      default: return <Users className="w-4 h-4 text-slate-500" />;
    }
  };

  const getRoleBadgeColor = (role) => {
    switch (role) {
      case 'owner': return 'bg-amber-100 text-amber-700 border-amber-200';
      case 'admin': return 'bg-purple-100 text-purple-700 border-purple-200';
      case 'recruiter': return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'viewer': return 'bg-slate-100 text-slate-700 border-slate-200';
      default: return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  };

  const getTierIcon = (tierId) => {
    switch (tierId) {
      case 'starter': return <Zap className="w-6 h-6 text-slate-600" />;
      case 'growth': return <Rocket className="w-6 h-6 text-blue-600" />;
      case 'pro': return <Crown className="w-6 h-6 text-purple-600" />;
      case 'enterprise': return <Building2 className="w-6 h-6 text-amber-600" />;
      default: return <Star className="w-6 h-6 text-slate-600" />;
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'active':
        return <Badge className="bg-green-100 text-green-700 border-green-200">Active</Badge>;
      case 'trial':
        return <Badge className="bg-blue-100 text-blue-700 border-blue-200">Trial</Badge>;
      case 'pending':
        return <Badge className="bg-yellow-100 text-yellow-700 border-yellow-200">Pending</Badge>;
      case 'cancelled':
        return <Badge className="bg-red-100 text-red-700 border-red-200">Cancelled</Badge>;
      case 'expired':
        return <Badge className="bg-slate-100 text-slate-700 border-slate-200">Expired</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading account dashboard...</p>
        </div>
      </div>
    );
  }

  if (!account) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-slate-800 mb-2">No Account Found</h2>
          <p className="text-slate-600">Unable to load account information.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-slate-800">Account Dashboard</h1>
              <p className="text-slate-600 mt-1">Manage your subscription, team, and settings</p>
            </div>
            <Button 
              onClick={fetchAccountData}
              variant="outline"
              className="flex items-center space-x-2"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Refresh</span>
            </Button>
          </div>
        </div>

        {/* Alerts */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-3">
            <XCircle className="w-5 h-5 text-red-600" />
            <span className="text-red-700">{error}</span>
            <button onClick={() => setError('')} className="ml-auto text-red-600 hover:text-red-800">
              <XCircle className="w-4 h-4" />
            </button>
          </div>
        )}

        {success && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center space-x-3">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <span className="text-green-700">{success}</span>
            <button onClick={() => setSuccess('')} className="ml-auto text-green-600 hover:text-green-800">
              <XCircle className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Tabs */}
        <div className="mb-8 border-b border-slate-200">
          <nav className="flex space-x-8">
            {['overview', 'team', 'features'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`pb-4 px-1 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-slate-600 hover:text-slate-900 hover:border-slate-300'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </nav>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {/* Account Overview Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Subscription Card */}
              <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg font-semibold text-slate-700 flex items-center">
                    <CreditCard className="w-5 h-5 mr-2 text-blue-600" />
                    Subscription
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center space-x-3 mb-4">
                    {getTierIcon(account.tier_id)}
                    <div>
                      <p className="text-2xl font-bold text-slate-900">{account.tier_name}</p>
                      <p className="text-slate-600">{formatPrice(account.tier_price)}/month</p>
                    </div>
                  </div>
                  {getStatusBadge(account.subscription_status)}
                  {account.subscription_end_date && (
                    <p className="text-sm text-slate-500 mt-2">
                      Renews: {new Date(account.subscription_end_date).toLocaleDateString()}
                    </p>
                  )}
                  <Button 
                    className="w-full mt-4 bg-blue-600 hover:bg-blue-700"
                    onClick={() => window.location.href = '/pricing'}
                  >
                    Manage Subscription
                  </Button>
                </CardContent>
              </Card>

              {/* Team Card */}
              <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg font-semibold text-slate-700 flex items-center">
                    <Users className="w-5 h-5 mr-2 text-purple-600" />
                    Team
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-baseline space-x-2 mb-2">
                    <span className="text-4xl font-bold text-slate-900">{account.current_user_count}</span>
                    <span className="text-slate-600">/ {account.max_users} users</span>
                  </div>
                  <div className="w-full bg-slate-200 rounded-full h-2 mb-4">
                    <div 
                      className="bg-purple-600 h-2 rounded-full transition-all"
                      style={{ width: `${(account.current_user_count / account.max_users) * 100}%` }}
                    ></div>
                  </div>
                  <p className="text-sm text-slate-600 mb-4">
                    {account.included_users} included • {account.extra_users_count} extra
                  </p>
                  <Button 
                    variant="outline"
                    className="w-full"
                    onClick={() => setActiveTab('team')}
                  >
                    Manage Team
                  </Button>
                </CardContent>
              </Card>

              {/* Features Card */}
              <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg font-semibold text-slate-700 flex items-center">
                    <Zap className="w-5 h-5 mr-2 text-amber-600" />
                    Features
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-baseline space-x-2 mb-4">
                    <span className="text-4xl font-bold text-slate-900">{account.features?.length || 0}</span>
                    <span className="text-slate-600">features</span>
                  </div>
                  <div className="flex flex-wrap gap-2 mb-4">
                    {account.active_addons?.length > 0 && (
                      <Badge className="bg-green-100 text-green-700">
                        +{account.active_addons.length} add-ons
                      </Badge>
                    )}
                    {account.available_addons?.length > 0 && (
                      <Badge variant="outline" className="text-slate-600">
                        {account.available_addons.length} available
                      </Badge>
                    )}
                  </div>
                  <Button 
                    variant="outline"
                    className="w-full"
                    onClick={() => setActiveTab('features')}
                  >
                    View Features
                  </Button>
                </CardContent>
              </Card>
            </div>

            {/* Company Information */}
            <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
              <CardHeader>
                <CardTitle className="text-xl font-semibold text-slate-800 flex items-center">
                  <Building2 className="w-5 h-5 mr-2 text-blue-600" />
                  Company Information
                </CardTitle>
                <CardDescription>Your company profile details</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-medium text-slate-600">Company Name</label>
                      <p className="text-lg text-slate-900">{account.name}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-slate-600">Industry</label>
                      <p className="text-slate-900">{account.company_industry || 'Not specified'}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-slate-600">Location</label>
                      <p className="text-slate-900">{account.company_location || 'Not specified'}</p>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-medium text-slate-600">Website</label>
                      <p className="text-slate-900">
                        {account.company_website ? (
                          <a href={account.company_website} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                            {account.company_website}
                          </a>
                        ) : 'Not specified'}
                      </p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-slate-600">Company Profile Level</label>
                      <Badge className={`${
                        account.company_profile_level === 'white_label' ? 'bg-amber-100 text-amber-700' :
                        account.company_profile_level === 'featured' ? 'bg-purple-100 text-purple-700' :
                        account.company_profile_level === 'enhanced' ? 'bg-blue-100 text-blue-700' :
                        'bg-slate-100 text-slate-700'
                      }`}>
                        {account.company_profile_level}
                      </Badge>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Team Tab */}
        {activeTab === 'team' && (
          <div className="space-y-6">
            {/* Team Header */}
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-slate-800">Team Members</h2>
                <p className="text-slate-600">
                  {account.current_user_count} of {account.max_users} seats used
                </p>
              </div>
              <Button 
                onClick={() => setInviteModalOpen(true)}
                className="bg-blue-600 hover:bg-blue-700"
                disabled={account.current_user_count >= account.max_users}
              >
                <UserPlus className="w-4 h-4 mr-2" />
                Invite User
              </Button>
            </div>

            {/* User Limit Warning */}
            {account.current_user_count >= account.max_users && (
              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg flex items-center space-x-3">
                <AlertCircle className="w-5 h-5 text-yellow-600" />
                <div className="flex-1">
                  <p className="text-yellow-700 font-medium">User limit reached</p>
                  <p className="text-yellow-600 text-sm">Upgrade your plan or purchase additional user seats to add more team members.</p>
                </div>
                <Button 
                  size="sm"
                  className="bg-yellow-600 hover:bg-yellow-700"
                  onClick={() => window.location.href = '/pricing'}
                >
                  Upgrade
                </Button>
              </div>
            )}

            {/* Team Members List */}
            <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
              <CardContent className="p-0">
                <div className="divide-y divide-slate-200">
                  {teamMembers.map((member) => (
                    <div key={member.id} className="p-4 flex items-center justify-between hover:bg-slate-50 transition-colors">
                      <div className="flex items-center space-x-4">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-semibold">
                          {member.first_name?.[0]}{member.last_name?.[0]}
                        </div>
                        <div>
                          <p className="font-medium text-slate-900">
                            {member.first_name} {member.last_name}
                          </p>
                          <p className="text-sm text-slate-600">{member.email}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <Badge className={`flex items-center space-x-1 ${getRoleBadgeColor(member.account_role)}`}>
                          {getRoleIcon(member.account_role)}
                          <span className="ml-1 capitalize">{member.account_role}</span>
                        </Badge>
                        {member.account_role !== 'owner' && user.account_role === 'owner' && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleRemoveUser(member.id)}
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Pending Invitations */}
            {invitations.length > 0 && (
              <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold text-slate-700 flex items-center">
                    <Mail className="w-5 h-5 mr-2 text-blue-600" />
                    Pending Invitations
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="divide-y divide-slate-200">
                    {invitations.map((invitation) => (
                      <div key={invitation.id} className="p-4 flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center text-slate-500">
                            <Mail className="w-5 h-5" />
                          </div>
                          <div>
                            <p className="font-medium text-slate-900">
                              {invitation.first_name} {invitation.last_name}
                            </p>
                            <p className="text-sm text-slate-600">{invitation.email}</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-4">
                          <Badge variant="outline" className="text-yellow-600 border-yellow-300">
                            <Clock className="w-3 h-3 mr-1" />
                            Pending
                          </Badge>
                          <span className="text-sm text-slate-500">
                            Expires: {new Date(invitation.expires_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {/* Features Tab */}
        {activeTab === 'features' && (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-slate-800">Your Features</h2>
              <p className="text-slate-600">Features available on your {account.tier_name} plan</p>
            </div>

            {/* Active Features */}
            <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-slate-700 flex items-center">
                  <CheckCircle className="w-5 h-5 mr-2 text-green-600" />
                  Active Features ({account.features?.length || 0})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {account.features?.map((feature) => (
                    <div key={feature} className="flex items-center space-x-2 p-3 bg-green-50 rounded-lg">
                      <CheckCircle className="w-4 h-4 text-green-600 flex-shrink-0" />
                      <span className="text-sm text-slate-700">{feature.replace(/_/g, ' ')}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Active Add-ons */}
            {account.active_addons?.length > 0 && (
              <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold text-slate-700 flex items-center">
                    <Zap className="w-5 h-5 mr-2 text-purple-600" />
                    Active Add-ons ({account.active_addons.length})
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {account.active_addons.map((addon) => (
                      <div key={addon} className="flex items-center space-x-2 p-3 bg-purple-50 rounded-lg">
                        <Zap className="w-4 h-4 text-purple-600 flex-shrink-0" />
                        <span className="text-sm text-slate-700">{addon.replace(/_/g, ' ')}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Available Add-ons */}
            {account.available_addons?.length > 0 && (
              <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold text-slate-700 flex items-center">
                    <Plus className="w-5 h-5 mr-2 text-blue-600" />
                    Available Add-ons ({account.available_addons.length})
                  </CardTitle>
                  <CardDescription>Enhance your plan with additional features</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {account.available_addons.map((addon) => (
                      <div key={addon.id} className="flex items-center justify-between p-4 bg-slate-50 rounded-lg border border-slate-200">
                        <div>
                          <p className="font-medium text-slate-900">{addon.name}</p>
                          <p className="text-sm text-slate-600">{addon.description}</p>
                        </div>
                        <div className="text-right">
                          <p className="font-semibold text-slate-900">
                            {addon.price_monthly ? formatPrice(addon.price_monthly) + '/mo' : formatPrice(addon.price_once)}
                          </p>
                          <Button size="sm" variant="outline" className="mt-2">
                            Add
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {/* Invite Modal */}
        {inviteModalOpen && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <Card className="w-full max-w-md bg-white">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <UserPlus className="w-5 h-5 mr-2 text-blue-600" />
                  Invite Team Member
                </CardTitle>
                <CardDescription>
                  Send an invitation to join your account
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleInvite} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-slate-700">First Name</label>
                      <Input
                        value={inviteForm.first_name}
                        onChange={(e) => setInviteForm({ ...inviteForm, first_name: e.target.value })}
                        placeholder="John"
                        required
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium text-slate-700">Last Name</label>
                      <Input
                        value={inviteForm.last_name}
                        onChange={(e) => setInviteForm({ ...inviteForm, last_name: e.target.value })}
                        placeholder="Doe"
                        required
                      />
                    </div>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium text-slate-700">Email Address</label>
                    <Input
                      type="email"
                      value={inviteForm.email}
                      onChange={(e) => setInviteForm({ ...inviteForm, email: e.target.value })}
                      placeholder="john@company.com"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium text-slate-700">Role</label>
                    <select
                      value={inviteForm.account_role}
                      onChange={(e) => setInviteForm({ ...inviteForm, account_role: e.target.value })}
                      className="w-full mt-1 px-3 py-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="recruiter">Recruiter</option>
                      <option value="admin">Admin</option>
                      <option value="viewer">Viewer</option>
                    </select>
                  </div>

                  <div className="flex justify-end space-x-3 pt-4">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => setInviteModalOpen(false)}
                    >
                      Cancel
                    </Button>
                    <Button
                      type="submit"
                      className="bg-blue-600 hover:bg-blue-700"
                      disabled={inviting}
                    >
                      {inviting ? (
                        <div className="flex items-center">
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                          Sending...
                        </div>
                      ) : (
                        'Send Invitation'
                      )}
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default AccountDashboard;
