import React, { useState, useEffect } from 'react';
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "./ui/card";
import { Badge } from "./ui/badge";
import { 
  CreditCard,
  Users,
  Zap,
  Plus,
  Trash2,
  History,
  CheckCircle,
  XCircle,
  Clock,
  AlertCircle,
  RefreshCw,
  Crown,
  Rocket,
  Building2,
  Download,
  Calendar,
  DollarSign,
  ArrowUpRight,
  FileText
} from "lucide-react";
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const BillingPage = ({ user }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [billing, setBilling] = useState(null);
  const [history, setHistory] = useState([]);
  const [availableAddons, setAvailableAddons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [purchasing, setPurchasing] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [subscriptionStatus, setSubscriptionStatus] = useState(null);

  // Extra seats modal
  const [showSeatsModal, setShowSeatsModal] = useState(false);
  const [seatsQuantity, setSeatsQuantity] = useState(1);

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
    fetchBillingData();
    checkSubscriptionStatus();
    
    // Check for payment result from URL params
    const params = new URLSearchParams(window.location.search);
    if (params.get('payment') === 'success') {
      setSuccess('Payment successful! Your account has been updated.');
      // Clear the URL params
      window.history.replaceState({}, document.title, window.location.pathname);
    } else if (params.get('payment') === 'cancelled') {
      setError('Payment was cancelled.');
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, []);

  const checkSubscriptionStatus = async () => {
    try {
      const response = await axios.get(`${API}/subscription/status`, getAuthHeaders());
      setSubscriptionStatus(response.data);
    } catch (error) {
      console.error('Error checking subscription status:', error);
    }
  };

  const handleReactivateSubscription = async () => {
    try {
      setPurchasing('reactivate');
      setError('');
      
      const response = await axios.post(`${API}/subscription/reactivate`, {}, getAuthHeaders());
      
      // Redirect to PayFast
      const { payfast_url, payfast_data } = response.data;
      
      const form = document.createElement('form');
      form.method = 'POST';
      form.action = payfast_url;
      
      Object.entries(payfast_data).forEach(([key, value]) => {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = key;
        input.value = value;
        form.appendChild(input);
      });
      
      document.body.appendChild(form);
      form.submit();
      
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to initiate reactivation payment');
    } finally {
      setPurchasing(null);
    }
  };

  const fetchBillingData = async () => {
    try {
      setLoading(true);
      setError('');
      
      const [billingSummary, billingHistory, addons] = await Promise.all([
        axios.get(`${API}/billing`, getAuthHeaders()),
        axios.get(`${API}/billing/history`, getAuthHeaders()),
        axios.get(`${API}/addons`, getAuthHeaders()).catch(() => ({ data: [] }))
      ]);
      
      setBilling(billingSummary.data);
      setHistory(billingHistory.data.history || []);
      setAvailableAddons(addons.data || []);
    } catch (error) {
      console.error('Error fetching billing data:', error);
      setError('Failed to load billing information');
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

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('en-ZA', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const handlePurchaseAddon = async (addonId) => {
    try {
      setPurchasing(addonId);
      
      const response = await axios.post(`${API}/billing/addon`, null, {
        ...getAuthHeaders(),
        params: { addon_id: addonId }
      });

      // Redirect to Payfast
      const { payfast_url, payfast_data } = response.data;
      
      const form = document.createElement('form');
      form.method = 'POST';
      form.action = payfast_url;
      
      Object.entries(payfast_data).forEach(([key, value]) => {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = key;
        input.value = value;
        form.appendChild(input);
      });
      
      document.body.appendChild(form);
      form.submit();
      
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to initiate add-on purchase');
    } finally {
      setPurchasing(null);
    }
  };

  const handleCancelAddon = async (addonPurchaseId) => {
    if (!window.confirm('Are you sure you want to cancel this add-on? It will remain active until the end of the billing period.')) {
      return;
    }

    try {
      await axios.delete(`${API}/billing/addon/${addonPurchaseId}`, getAuthHeaders());
      setSuccess('Add-on cancelled successfully');
      fetchBillingData();
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to cancel add-on');
    }
  };

  const handlePurchaseSeats = async () => {
    try {
      setPurchasing('seats');
      
      const response = await axios.post(`${API}/billing/extra-seats`, null, {
        ...getAuthHeaders(),
        params: { quantity: seatsQuantity }
      });

      // Redirect to Payfast
      const { payfast_url, payfast_data } = response.data;
      
      const form = document.createElement('form');
      form.method = 'POST';
      form.action = payfast_url;
      
      Object.entries(payfast_data).forEach(([key, value]) => {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = key;
        input.value = value;
        form.appendChild(input);
      });
      
      document.body.appendChild(form);
      form.submit();
      
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to purchase extra seats');
    } finally {
      setPurchasing(null);
      setShowSeatsModal(false);
    }
  };

  const handleCancelSeat = async (seatId) => {
    if (!window.confirm('Are you sure you want to cancel this user seat? It will remain active until the end of the billing period.')) {
      return;
    }

    try {
      await axios.delete(`${API}/billing/extra-seats/${seatId}`, getAuthHeaders());
      setSuccess('User seat cancelled successfully');
      fetchBillingData();
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to cancel seat');
    }
  };

  const getTierIcon = (tierId) => {
    switch (tierId) {
      case 'starter': return <Zap className="w-6 h-6 text-slate-600" />;
      case 'growth': return <Rocket className="w-6 h-6 text-blue-600" />;
      case 'pro': return <Crown className="w-6 h-6 text-purple-600" />;
      case 'enterprise': return <Building2 className="w-6 h-6 text-amber-600" />;
      default: return <CreditCard className="w-6 h-6 text-slate-600" />;
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'active':
        return <Badge className="bg-green-100 text-green-700">Active</Badge>;
      case 'completed':
        return <Badge className="bg-green-100 text-green-700">Completed</Badge>;
      case 'pending':
        return <Badge className="bg-yellow-100 text-yellow-700">Pending</Badge>;
      case 'failed':
        return <Badge className="bg-red-100 text-red-700">Failed</Badge>;
      case 'cancelled':
        return <Badge className="bg-slate-100 text-slate-700">Cancelled</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading billing information...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Subscription Status Banner */}
        {subscriptionStatus && subscriptionStatus.needs_payment && (
          <Card className={`mb-6 ${
            subscriptionStatus.status === 'inactive' 
              ? 'bg-red-50 border-red-200' 
              : 'bg-yellow-50 border-yellow-200'
          }`}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <AlertCircle className={`w-6 h-6 ${
                    subscriptionStatus.status === 'inactive' 
                      ? 'text-red-600' 
                      : 'text-yellow-600'
                  }`} />
                  <div>
                    <h4 className={`font-semibold ${
                      subscriptionStatus.status === 'inactive' 
                        ? 'text-red-800' 
                        : 'text-yellow-800'
                    }`}>
                      {subscriptionStatus.status === 'inactive' 
                        ? 'Account Suspended' 
                        : 'Payment Overdue'}
                    </h4>
                    <p className={`text-sm ${
                      subscriptionStatus.status === 'inactive' 
                        ? 'text-red-700' 
                        : 'text-yellow-700'
                    }`}>
                      {subscriptionStatus.message}
                      {subscriptionStatus.grace_days_remaining > 0 && (
                        <span className="ml-1 font-medium">
                          ({subscriptionStatus.grace_days_remaining} days remaining)
                        </span>
                      )}
                    </p>
                  </div>
                </div>
                <Button
                  onClick={handleReactivateSubscription}
                  disabled={purchasing === 'reactivate'}
                  className={`${
                    subscriptionStatus.status === 'inactive'
                      ? 'bg-red-600 hover:bg-red-700'
                      : 'bg-yellow-600 hover:bg-yellow-700'
                  } text-white`}
                >
                  {purchasing === 'reactivate' ? (
                    <span className="flex items-center">
                      <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      Processing...
                    </span>
                  ) : (
                    <span className="flex items-center">
                      <CreditCard className="w-4 h-4 mr-2" />
                      {subscriptionStatus.status === 'inactive' ? 'Reactivate Account' : 'Make Payment'}
                    </span>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-800 flex items-center">
            <CreditCard className="w-8 h-8 mr-3 text-blue-600" />
            Accounts & Billing
          </h1>
          <p className="text-slate-600 mt-1">Manage your subscription, add-ons, and billing history</p>
        </div>

        {/* Alerts */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-3">
            <XCircle className="w-5 h-5 text-red-600" />
            <span className="text-red-700">{error}</span>
            <button onClick={() => setError('')} className="ml-auto">
              <XCircle className="w-4 h-4 text-red-600" />
            </button>
          </div>
        )}

        {success && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center space-x-3">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <span className="text-green-700">{success}</span>
            <button onClick={() => setSuccess('')} className="ml-auto">
              <XCircle className="w-4 h-4 text-green-600" />
            </button>
          </div>
        )}

        {/* Tabs */}
        <div className="mb-8 border-b border-slate-200">
          <nav className="flex space-x-8">
            {['overview', 'add-ons', 'users', 'history'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`pb-4 px-1 text-sm font-medium border-b-2 transition-colors capitalize ${
                  activeTab === tab
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-slate-600 hover:text-slate-900 hover:border-slate-300'
                }`}
              >
                {tab === 'add-ons' ? 'Add-ons' : tab}
              </button>
            ))}
          </nav>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && billing && (
          <div className="space-y-6">
            {/* Subscription Summary */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg font-semibold text-slate-700 flex items-center">
                    Current Plan
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center space-x-4 mb-4">
                    {getTierIcon(billing.tier_id)}
                    <div>
                      <p className="text-2xl font-bold text-slate-900">{billing.tier_name}</p>
                      {getStatusBadge(billing.subscription_status)}
                    </div>
                  </div>
                  
                  <div className="space-y-2 text-sm text-slate-600">
                    <div className="flex justify-between">
                      <span>Billing Cycle:</span>
                      <span className="font-medium capitalize">{billing.billing_cycle}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Next Renewal:</span>
                      <span className="font-medium">{formatDate(billing.subscription_end_date)}</span>
                    </div>
                  </div>
                  
                  <Button 
                    className="w-full mt-4 bg-blue-600 hover:bg-blue-700"
                    onClick={() => window.location.href = '/pricing'}
                  >
                    <ArrowUpRight className="w-4 h-4 mr-2" />
                    Change Plan
                  </Button>
                </CardContent>
              </Card>

              <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg font-semibold text-slate-700 flex items-center">
                    Monthly Charges
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-slate-600">Base Subscription</span>
                      <span className="font-semibold">{formatPrice(billing.charges?.base_subscription || 0)}</span>
                    </div>
                    
                    {billing.charges?.extra_users_count > 0 && (
                      <div className="flex justify-between items-center">
                        <span className="text-slate-600">Extra Users ({billing.charges.extra_users_count})</span>
                        <span className="font-semibold">{formatPrice(billing.charges.extra_users_charge)}</span>
                      </div>
                    )}
                    
                    {billing.charges?.addons_charge > 0 && (
                      <div className="flex justify-between items-center">
                        <span className="text-slate-600">Add-ons ({billing.charges.active_addons_count})</span>
                        <span className="font-semibold">{formatPrice(billing.charges.addons_charge)}</span>
                      </div>
                    )}
                    
                    <div className="border-t border-slate-200 pt-3 flex justify-between items-center">
                      <span className="text-lg font-semibold text-slate-800">Total</span>
                      <span className="text-2xl font-bold text-blue-600">
                        {formatPrice(billing.charges?.total_monthly || 0)}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Users Summary */}
            <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg font-semibold text-slate-700 flex items-center">
                  <Users className="w-5 h-5 mr-2 text-purple-600" />
                  User Seats
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-baseline space-x-2">
                      <span className="text-3xl font-bold text-slate-900">{billing.current_users}</span>
                      <span className="text-slate-600">/ {billing.max_users} seats</span>
                    </div>
                    <p className="text-sm text-slate-500 mt-1">
                      {billing.included_users} included • {billing.charges?.extra_users_count || 0} extra purchased
                    </p>
                  </div>
                  <Button
                    onClick={() => setShowSeatsModal(true)}
                    className="bg-purple-600 hover:bg-purple-700"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Add Seats
                  </Button>
                </div>
                
                <div className="w-full bg-slate-200 rounded-full h-3 mt-4">
                  <div 
                    className="bg-purple-600 h-3 rounded-full transition-all"
                    style={{ width: `${(billing.current_users / billing.max_users) * 100}%` }}
                  ></div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Add-ons Tab */}
        {activeTab === 'add-ons' && (
          <div className="space-y-6">
            {/* Active Add-ons */}
            {billing?.active_addons?.length > 0 && (
              <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold text-slate-700">Active Add-ons</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="divide-y divide-slate-200">
                    {billing.active_addons.map((addon) => (
                      <div key={addon.id} className="p-4 flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className="p-2 bg-purple-100 rounded-lg">
                            <Zap className="w-5 h-5 text-purple-600" />
                          </div>
                          <div>
                            <p className="font-medium text-slate-900">{addon.name}</p>
                            <p className="text-sm text-slate-500">
                              {addon.is_recurring 
                                ? `Renews: ${formatDate(addon.expires_date)}`
                                : 'One-time purchase'
                              }
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-4">
                          <span className="font-semibold text-slate-900">
                            {formatPrice(addon.price)}{addon.is_recurring ? '/mo' : ''}
                          </span>
                          {addon.is_recurring && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleCancelAddon(addon.id)}
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
            )}

            {/* Available Add-ons */}
            <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-slate-700">Available Add-ons</CardTitle>
                <CardDescription>Enhance your plan with additional features</CardDescription>
              </CardHeader>
              <CardContent>
                {availableAddons.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {availableAddons.map((addon) => (
                      <div key={addon.id} className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                        <div className="flex justify-between items-start mb-2">
                          <h4 className="font-medium text-slate-900">{addon.name}</h4>
                          <span className="font-semibold text-slate-900">
                            {formatPrice(addon.price_monthly || addon.price_once)}
                            {addon.price_monthly ? '/mo' : ''}
                          </span>
                        </div>
                        <p className="text-sm text-slate-600 mb-3">{addon.description}</p>
                        <Button
                          size="sm"
                          onClick={() => handlePurchaseAddon(addon.id)}
                          disabled={purchasing === addon.id}
                          className="w-full bg-blue-600 hover:bg-blue-700"
                        >
                          {purchasing === addon.id ? (
                            <RefreshCw className="w-4 h-4 animate-spin" />
                          ) : (
                            <>
                              <Plus className="w-4 h-4 mr-2" />
                              Add to Plan
                            </>
                          )}
                        </Button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-slate-500">
                    <Zap className="w-12 h-12 mx-auto mb-3 text-slate-400" />
                    <p>No additional add-ons available for your current plan.</p>
                    <p className="text-sm mt-1">Upgrade your subscription to unlock more features.</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {/* Users Tab */}
        {activeTab === 'users' && (
          <div className="space-y-6">
            <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle className="text-lg font-semibold text-slate-700">Extra User Seats</CardTitle>
                    <CardDescription>Purchased additional user seats</CardDescription>
                  </div>
                  <Button
                    onClick={() => setShowSeatsModal(true)}
                    className="bg-purple-600 hover:bg-purple-700"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Purchase Seats
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {billing?.extra_seats?.length > 0 ? (
                  <div className="divide-y divide-slate-200">
                    {billing.extra_seats.map((seat, index) => (
                      <div key={seat.id} className="py-4 flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center">
                            <Users className="w-5 h-5 text-purple-600" />
                          </div>
                          <div>
                            <p className="font-medium text-slate-900">Extra Seat #{index + 1}</p>
                            <p className="text-sm text-slate-500">
                              {seat.cancelled_at 
                                ? `Cancelled - expires ${formatDate(seat.expires_date)}`
                                : `Renews: ${formatDate(seat.expires_date)}`
                              }
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-4">
                          {seat.is_active && !seat.cancelled_at && (
                            <>
                              <span className="font-semibold text-slate-900">R899/mo</span>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleCancelSeat(seat.id)}
                                className="text-red-600 hover:text-red-700 hover:bg-red-50"
                              >
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            </>
                          )}
                          {seat.cancelled_at && (
                            <Badge className="bg-slate-100 text-slate-600">Cancelled</Badge>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-slate-500">
                    <Users className="w-12 h-12 mx-auto mb-3 text-slate-400" />
                    <p>No extra user seats purchased.</p>
                    <p className="text-sm mt-1">Your plan includes {billing?.included_users} user(s).</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {/* History Tab */}
        {activeTab === 'history' && (
          <div className="space-y-6">
            {/* Statement Download Section */}
            <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-slate-700 flex items-center">
                  <FileText className="w-5 h-5 mr-2 text-purple-600" />
                  Download Statement
                </CardTitle>
                <CardDescription>Generate a billing statement for any period</CardDescription>
              </CardHeader>
              <CardContent>
                <StatementDownload getAuthHeaders={getAuthHeaders} />
              </CardContent>
            </Card>

            {/* Payment History Table */}
            <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-slate-700 flex items-center">
                  <History className="w-5 h-5 mr-2 text-blue-600" />
                  Payment History
                </CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                {history.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-slate-50 border-y border-slate-200">
                        <tr>
                          <th className="text-left py-3 px-4 font-semibold text-slate-700">Date</th>
                          <th className="text-left py-3 px-4 font-semibold text-slate-700">Description</th>
                          <th className="text-center py-3 px-4 font-semibold text-slate-700">Status</th>
                          <th className="text-right py-3 px-4 font-semibold text-slate-700">Amount</th>
                        </tr>
                      </thead>
                      <tbody>
                        {history.map((payment, index) => (
                          <tr key={payment.id} className={index % 2 === 0 ? 'bg-white' : 'bg-slate-50/50'}>
                            <td className="py-3 px-4 text-slate-600">
                              {formatDate(payment.created_at)}
                            </td>
                            <td className="py-3 px-4">
                              <div>
                                <p className="font-medium text-slate-900">
                                  {payment.payment_type === 'subscription' 
                                    ? `${payment.tier_name || 'Subscription'} Plan`
                                    : payment.payment_type === 'addon'
                                      ? `Add-on: ${payment.addon_name || 'Feature'}`
                                      : payment.payment_type === 'extra_seat'
                                        ? `${payment.quantity || 1} Extra User Seat(s)`
                                        : payment.description || payment.payment_type
                                  }
                                </p>
                                {payment.id && (
                                  <p className="text-xs text-slate-500">Ref: {payment.id.substring(0, 8).toUpperCase()}</p>
                                )}
                              </div>
                            </td>
                            <td className="py-3 px-4 text-center">
                              {getStatusBadge(payment.status)}
                            </td>
                            <td className="py-3 px-4 text-right font-semibold text-slate-900">
                              {formatPrice(payment.amount || payment.final_amount || 0)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="text-center py-12 text-slate-500">
                    <History className="w-12 h-12 mx-auto mb-3 text-slate-400" />
                    <p>No payment history yet.</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {/* Purchase Seats Modal */}
        {showSeatsModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <Card className="w-full max-w-md bg-white">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Users className="w-5 h-5 mr-2 text-purple-600" />
                  Purchase Extra User Seats
                </CardTitle>
                <CardDescription>
                  Add more team members to your account
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-slate-700">Number of Seats</label>
                    <div className="flex items-center space-x-4 mt-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setSeatsQuantity(Math.max(1, seatsQuantity - 1))}
                      >
                        -
                      </Button>
                      <span className="text-2xl font-bold text-slate-900 w-12 text-center">
                        {seatsQuantity}
                      </span>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setSeatsQuantity(Math.min(100, seatsQuantity + 1))}
                      >
                        +
                      </Button>
                    </div>
                  </div>
                  
                  <div className="bg-slate-50 p-4 rounded-lg">
                    <div className="flex justify-between items-center">
                      <span className="text-slate-600">Price per seat</span>
                      <span className="font-medium">R899/month</span>
                    </div>
                    <div className="flex justify-between items-center mt-2 pt-2 border-t border-slate-200">
                      <span className="font-semibold text-slate-800">Total</span>
                      <span className="text-xl font-bold text-purple-600">
                        {formatPrice(seatsQuantity * 899)}/month
                      </span>
                    </div>
                  </div>

                  <div className="flex justify-end space-x-3 pt-4">
                    <Button
                      variant="outline"
                      onClick={() => setShowSeatsModal(false)}
                    >
                      Cancel
                    </Button>
                    <Button
                      onClick={handlePurchaseSeats}
                      disabled={purchasing === 'seats'}
                      className="bg-purple-600 hover:bg-purple-700"
                    >
                      {purchasing === 'seats' ? (
                        <RefreshCw className="w-4 h-4 animate-spin mr-2" />
                      ) : (
                        <CreditCard className="w-4 h-4 mr-2" />
                      )}
                      Purchase Seats
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default BillingPage;
