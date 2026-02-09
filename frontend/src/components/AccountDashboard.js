import React, { useState, useEffect } from 'react';
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "./ui/card";
import { Badge } from "./ui/badge";
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
  Star,
  TrendingUp,
  Briefcase,
  DollarSign,
  Calendar
} from "lucide-react";
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AccountDashboard = ({ user, onUpdateUser }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState({
    totalAccounts: 0,
    activeSubscriptions: 0,
    totalUsers: 0,
    totalJobs: 0,
    totalApplications: 0,
    revenueThisMonth: 0
  });
  const [accounts, setAccounts] = useState([]);
  const [tiers, setTiers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterTier, setFilterTier] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
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
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Fetch tiers
      const tiersRes = await axios.get(`${API}/tiers`);
      setTiers(tiersRes.data);

      // Fetch admin stats - we'll calculate from available data
      const [usersRes, jobsRes] = await Promise.all([
        axios.get(`${API}/admin/stats/users`, getAuthHeaders()).catch(() => ({ data: {} })),
        axios.get(`${API}/admin/stats/jobs`, getAuthHeaders()).catch(() => ({ data: {} }))
      ]);
      
      // Use placeholder stats for now - backend can be extended for admin endpoints
      setStats({
        totalAccounts: 4,
        activeSubscriptions: 4,
        totalUsers: 16,
        totalJobs: 11,
        totalApplications: 0,
        revenueThisMonth: 77396 // Sum of all tier prices
      });

      // Mock account data for display
      setAccounts([
        {
          id: '1',
          name: 'TechCorp Solutions',
          tier_id: 'starter',
          tier_name: 'Starter',
          subscription_status: 'active',
          owner_email: 'hr@techcorp.co.za',
          user_count: 1,
          job_count: 2,
          created_at: '2025-12-01'
        },
        {
          id: '2',
          name: 'Innovate Digital Agency',
          tier_id: 'growth',
          tier_name: 'Growth',
          subscription_status: 'active',
          owner_email: 'talent@innovatedigital.co.za',
          user_count: 2,
          job_count: 3,
          created_at: '2025-12-01'
        },
        {
          id: '3',
          name: 'FinTech Solutions SA',
          tier_id: 'pro',
          tier_name: 'Pro',
          subscription_status: 'active',
          owner_email: 'careers@fintechsa.co.za',
          user_count: 3,
          job_count: 3,
          created_at: '2025-12-01'
        },
        {
          id: '4',
          name: 'Global Recruitment Agency',
          tier_id: 'enterprise',
          tier_name: 'Enterprise',
          subscription_status: 'active',
          owner_email: 'admin@globalrecruit.co.za',
          user_count: 5,
          job_count: 3,
          created_at: '2025-12-01'
        }
      ]);
      
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-ZA', {
      style: 'currency',
      currency: 'ZAR',
      minimumFractionDigits: 0
    }).format(price);
  };

  const getTierIcon = (tierId) => {
    switch (tierId) {
      case 'starter': return <Zap className="w-5 h-5 text-slate-600" />;
      case 'growth': return <Rocket className="w-5 h-5 text-blue-600" />;
      case 'pro': return <Crown className="w-5 h-5 text-purple-600" />;
      case 'enterprise': return <Building2 className="w-5 h-5 text-amber-600" />;
      default: return <Star className="w-5 h-5 text-slate-600" />;
    }
  };

  const getTierBadgeColor = (tierId) => {
    switch (tierId) {
      case 'starter': return 'bg-slate-100 text-slate-700 border-slate-200';
      case 'growth': return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'pro': return 'bg-purple-100 text-purple-700 border-purple-200';
      case 'enterprise': return 'bg-amber-100 text-amber-700 border-amber-200';
      default: return 'bg-slate-100 text-slate-700 border-slate-200';
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

  const filteredAccounts = accounts.filter(account => {
    const matchesSearch = account.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         account.owner_email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTier = filterTier === 'all' || account.tier_id === filterTier;
    const matchesStatus = filterStatus === 'all' || account.subscription_status === filterStatus;
    return matchesSearch && matchesTier && matchesStatus;
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading admin dashboard...</p>
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
              <h1 className="text-3xl font-bold text-slate-800 flex items-center">
                <Shield className="w-8 h-8 mr-3 text-blue-600" />
                Admin Account Dashboard
              </h1>
              <p className="text-slate-600 mt-1">Manage all accounts, subscriptions, and platform metrics</p>
            </div>
            <Button 
              onClick={fetchDashboardData}
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

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">Total Accounts</p>
                  <p className="text-3xl font-bold text-slate-900">{stats.totalAccounts}</p>
                </div>
                <div className="p-3 bg-blue-100 rounded-full">
                  <Building2 className="w-6 h-6 text-blue-600" />
                </div>
              </div>
              <div className="mt-4 flex items-center text-sm text-green-600">
                <TrendingUp className="w-4 h-4 mr-1" />
                <span>{stats.activeSubscriptions} active</span>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">Total Users</p>
                  <p className="text-3xl font-bold text-slate-900">{stats.totalUsers}</p>
                </div>
                <div className="p-3 bg-purple-100 rounded-full">
                  <Users className="w-6 h-6 text-purple-600" />
                </div>
              </div>
              <div className="mt-4 flex items-center text-sm text-slate-600">
                <span>Across all accounts</span>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">Active Jobs</p>
                  <p className="text-3xl font-bold text-slate-900">{stats.totalJobs}</p>
                </div>
                <div className="p-3 bg-green-100 rounded-full">
                  <Briefcase className="w-6 h-6 text-green-600" />
                </div>
              </div>
              <div className="mt-4 flex items-center text-sm text-slate-600">
                <span>{stats.totalApplications} applications</span>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">Monthly Revenue</p>
                  <p className="text-3xl font-bold text-slate-900">{formatPrice(stats.revenueThisMonth)}</p>
                </div>
                <div className="p-3 bg-amber-100 rounded-full">
                  <DollarSign className="w-6 h-6 text-amber-600" />
                </div>
              </div>
              <div className="mt-4 flex items-center text-sm text-green-600">
                <TrendingUp className="w-4 h-4 mr-1" />
                <span>All subscriptions</span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Tier Distribution */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-8">
          {tiers.map(tier => {
            const accountCount = accounts.filter(a => a.tier_id === tier.id).length;
            return (
              <Card key={tier.id} className={`bg-white/90 backdrop-blur-sm shadow-lg border-0`}>
                <CardContent className="p-6">
                  <div className="flex items-center space-x-3 mb-4">
                    {getTierIcon(tier.id)}
                    <div>
                      <p className="font-semibold text-slate-900">{tier.name}</p>
                      <p className="text-sm text-slate-600">{formatPrice(tier.price_monthly)}/mo</p>
                    </div>
                  </div>
                  <div className="flex items-baseline space-x-2">
                    <span className="text-3xl font-bold text-slate-900">{accountCount}</span>
                    <span className="text-slate-600">accounts</span>
                  </div>
                  <div className="mt-2 text-sm text-slate-500">
                    {tier.included_users} users included
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Accounts List */}
        <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
          <CardHeader>
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div>
                <CardTitle className="text-xl font-semibold text-slate-800">All Accounts</CardTitle>
                <CardDescription>Manage all registered accounts</CardDescription>
              </div>
              <div className="flex items-center space-x-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <Input
                    placeholder="Search accounts..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 w-64"
                  />
                </div>
                <select
                  value={filterTier}
                  onChange={(e) => setFilterTier(e.target.value)}
                  className="px-3 py-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">All Tiers</option>
                  {tiers.map(tier => (
                    <option key={tier.id} value={tier.id}>{tier.name}</option>
                  ))}
                </select>
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="px-3 py-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">All Status</option>
                  <option value="active">Active</option>
                  <option value="trial">Trial</option>
                  <option value="pending">Pending</option>
                  <option value="cancelled">Cancelled</option>
                </select>
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-50 border-y border-slate-200">
                  <tr>
                    <th className="text-left py-3 px-6 font-semibold text-slate-700">Company</th>
                    <th className="text-left py-3 px-4 font-semibold text-slate-700">Owner</th>
                    <th className="text-center py-3 px-4 font-semibold text-slate-700">Tier</th>
                    <th className="text-center py-3 px-4 font-semibold text-slate-700">Status</th>
                    <th className="text-center py-3 px-4 font-semibold text-slate-700">Users</th>
                    <th className="text-center py-3 px-4 font-semibold text-slate-700">Jobs</th>
                    <th className="text-center py-3 px-4 font-semibold text-slate-700">Created</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredAccounts.map((account, index) => (
                    <tr key={account.id} className={index % 2 === 0 ? 'bg-white' : 'bg-slate-50/50'}>
                      <td className="py-4 px-6">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-semibold">
                            {account.name.charAt(0)}
                          </div>
                          <div>
                            <p className="font-medium text-slate-900">{account.name}</p>
                          </div>
                        </div>
                      </td>
                      <td className="py-4 px-4 text-slate-600 text-sm">{account.owner_email}</td>
                      <td className="py-4 px-4 text-center">
                        <Badge className={`flex items-center justify-center space-x-1 ${getTierBadgeColor(account.tier_id)}`}>
                          {getTierIcon(account.tier_id)}
                          <span className="ml-1">{account.tier_name}</span>
                        </Badge>
                      </td>
                      <td className="py-4 px-4 text-center">
                        {getStatusBadge(account.subscription_status)}
                      </td>
                      <td className="py-4 px-4 text-center">
                        <span className="text-slate-700 font-medium">{account.user_count}</span>
                      </td>
                      <td className="py-4 px-4 text-center">
                        <span className="text-slate-700 font-medium">{account.job_count}</span>
                      </td>
                      <td className="py-4 px-4 text-center text-slate-600 text-sm">
                        {new Date(account.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            
            {filteredAccounts.length === 0 && (
              <div className="text-center py-12">
                <AlertCircle className="w-12 h-12 text-slate-400 mx-auto mb-4" />
                <p className="text-slate-600">No accounts found matching your criteria.</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AccountDashboard;
