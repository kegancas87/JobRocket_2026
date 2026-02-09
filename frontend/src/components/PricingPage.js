import React, { useState, useEffect } from 'react';
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { 
  Check,
  X,
  Zap,
  Rocket,
  Crown,
  Building2,
  Users,
  Clock,
  CreditCard,
  Star,
  ArrowRight,
  Sparkles,
  Shield,
  Headphones,
  BarChart3,
  Search,
  Mail,
  MessageSquare,
  FileText,
  Bot,
  Palette,
  Code
} from "lucide-react";
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PricingPage = ({ user }) => {
  const [tiers, setTiers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [purchasing, setPurchasing] = useState(null);
  const [billingCycle, setBillingCycle] = useState('monthly');
  const [currentTier, setCurrentTier] = useState(null);

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
    fetchTiers();
    if (user?.account_id) {
      fetchCurrentAccount();
    }
  }, [user]);

  const fetchTiers = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/tiers`);
      setTiers(response.data);
    } catch (error) {
      console.error('Error fetching tiers:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatProfileLevel = (level) => {
    if (!level) return 'Basic';
    return level
      .replace(/_/g, ' ')
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const fetchCurrentAccount = async () => {
    try {
      const response = await axios.get(`${API}/account`, getAuthHeaders());
      setCurrentTier(response.data.tier_id);
    } catch (error) {
      console.error('Error fetching account:', error);
    }
  };

  const handleSubscribe = async (tierId) => {
    if (!user) {
      alert('Please login to subscribe');
      return;
    }
    
    if (user.role !== 'recruiter') {
      alert('Only recruiters can subscribe to plans');
      return;
    }

    try {
      setPurchasing(tierId);
      
      const response = await axios.post(`${API}/payments/subscription`, {
        tier_id: tierId,
        billing_cycle: billingCycle
      }, getAuthHeaders());

      // Build Payfast form and submit
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
      console.error('Error initiating payment:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to initiate payment';
      alert(errorMessage);
    } finally {
      setPurchasing(null);
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-ZA', {
      style: 'currency',
      currency: 'ZAR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(price);
  };

  const getTierIcon = (tierId) => {
    switch (tierId) {
      case 'starter': return <Zap className="w-8 h-8" />;
      case 'growth': return <Rocket className="w-8 h-8" />;
      case 'pro': return <Crown className="w-8 h-8" />;
      case 'enterprise': return <Building2 className="w-8 h-8" />;
      default: return <Star className="w-8 h-8" />;
    }
  };

  const getTierColors = (tierId) => {
    switch (tierId) {
      case 'starter': 
        return {
          gradient: 'from-slate-500 to-slate-700',
          bg: 'bg-slate-50',
          border: 'border-slate-200 hover:border-slate-400',
          icon: 'text-slate-600',
          badge: 'bg-slate-100 text-slate-700'
        };
      case 'growth': 
        return {
          gradient: 'from-blue-500 to-blue-700',
          bg: 'bg-blue-50',
          border: 'border-blue-200 hover:border-blue-400',
          icon: 'text-blue-600',
          badge: 'bg-blue-100 text-blue-700'
        };
      case 'pro': 
        return {
          gradient: 'from-purple-500 to-purple-700',
          bg: 'bg-purple-50',
          border: 'border-purple-200 hover:border-purple-400 ring-2 ring-purple-200',
          icon: 'text-purple-600',
          badge: 'bg-purple-100 text-purple-700'
        };
      case 'enterprise': 
        return {
          gradient: 'from-amber-500 to-orange-600',
          bg: 'bg-amber-50',
          border: 'border-amber-200 hover:border-amber-400',
          icon: 'text-amber-600',
          badge: 'bg-amber-100 text-amber-700'
        };
      default:
        return {
          gradient: 'from-slate-500 to-slate-700',
          bg: 'bg-slate-50',
          border: 'border-slate-200',
          icon: 'text-slate-600',
          badge: 'bg-slate-100 text-slate-700'
        };
    }
  };

  // Feature categories for display
  const featureCategories = {
    'Job Posting': [
      { id: 'JOB_UNLIMITED_POSTS', label: 'Unlimited Job Posts', tiers: ['growth', 'pro', 'enterprise'] },
      { id: 'JOB_30_POSTS', label: '30 Job Posts/month', tiers: ['starter'] },
      { id: 'JOB_TEMPLATES', label: 'Job Templates', tiers: ['growth', 'pro', 'enterprise'] },
      { id: 'JOB_BULK_UPLOAD', label: 'Bulk Job Upload', tiers: ['pro', 'enterprise'] },
    ],
    'Candidate Management': [
      { id: 'CANDIDATE_APPLICANT_INBOX', label: 'Applicant Inbox', tiers: ['starter', 'growth', 'pro', 'enterprise'] },
      { id: 'CANDIDATE_APPLICANT_FILTERING', label: 'Applicant Filtering', tiers: ['growth', 'pro', 'enterprise'] },
      { id: 'CANDIDATE_STATUS_TRACKING', label: 'Status Tracking', tiers: ['growth', 'pro', 'enterprise'] },
      { id: 'CANDIDATE_NOTES_TAGS', label: 'Notes & Tags', tiers: ['growth', 'pro', 'enterprise'], addon: 'starter' },
    ],
    'Talent Pool & AI': [
      { id: 'TALENT_CV_DATABASE', label: 'CV Database Access', tiers: ['growth', 'pro', 'enterprise'] },
      { id: 'TALENT_PASSIVE_SEARCH', label: 'Passive Candidate Search', tiers: ['growth', 'pro', 'enterprise'] },
      { id: 'AI_MATCH_SCORE', label: 'AI Match Score', tiers: ['growth', 'pro', 'enterprise'] },
      { id: 'AI_AUTO_RANKED', label: 'Auto-Ranked Candidates', tiers: ['growth', 'pro', 'enterprise'] },
    ],
    'Distribution': [
      { id: 'DIST_PLATFORM', label: 'Platform Distribution', tiers: ['starter', 'growth', 'pro', 'enterprise'] },
      { id: 'DIST_EMAIL', label: 'Email Distribution', tiers: ['growth', 'pro', 'enterprise'] },
      { id: 'DIST_WHATSAPP', label: 'WhatsApp Distribution', tiers: ['growth', 'pro', 'enterprise'], addon: 'starter' },
      { id: 'DIST_SOCIAL_MEDIA', label: 'Social Media Distribution', tiers: ['growth', 'pro', 'enterprise'], addon: 'starter' },
    ],
    'Analytics & Tools': [
      { id: 'ANALYTICS_JOB_PERFORMANCE', label: 'Job Performance Metrics', tiers: ['growth', 'pro', 'enterprise'] },
      { id: 'ANALYTICS_CONVERSION_RATES', label: 'Conversion Analytics', tiers: ['pro', 'enterprise'] },
      { id: 'TOOLS_CANDIDATE_PIPELINE', label: 'Candidate Pipeline', tiers: ['growth', 'pro', 'enterprise'] },
      { id: 'TOOLS_INTERVIEW_SCHEDULING', label: 'Interview Scheduling', tiers: ['pro', 'enterprise'], addon: 'starter,growth' },
    ],
    'Team & Support': [
      { id: 'ACCOUNT_MULTI_USER_ACCESS', label: 'Multi-User Access', tiers: ['pro', 'enterprise'] },
      { id: 'ACCOUNT_ROLE_BASED_PERMISSIONS', label: 'Role-Based Permissions', tiers: ['enterprise'] },
      { id: 'SUPPORT_PRIORITY', label: 'Priority Support', tiers: ['growth', 'pro', 'enterprise'] },
      { id: 'SUPPORT_DEDICATED_MANAGER', label: 'Dedicated Account Manager', tiers: ['enterprise'] },
    ],
    'Integrations': [
      { id: 'INTEGRATION_ATS_EXPORT', label: 'ATS Export', tiers: ['pro', 'enterprise'], addon: 'growth' },
      { id: 'INTEGRATION_API_ACCESS', label: 'API Access', tiers: ['enterprise'] },
    ],
  };

  const hasFeature = (tierId, featureTiers) => featureTiers.includes(tierId);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading pricing plans...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <Badge variant="outline" className="mb-4 px-4 py-2 text-blue-700 border-blue-300 bg-blue-50">
            🚀 Subscription Plans
          </Badge>
          <h1 className="text-4xl sm:text-5xl font-bold text-slate-800 mb-4">
            Choose Your <span className="text-blue-600">Growth Plan</span>
          </h1>
          <p className="text-lg sm:text-xl text-slate-600 max-w-3xl mx-auto">
            Unlock powerful recruitment tools to find the perfect candidates. 
            All plans include unlimited job posts and 35-day job durations.
          </p>
          
          {/* Current Plan Indicator */}
          {currentTier && (
            <div className="mt-6 inline-flex items-center px-4 py-2 bg-green-50 border border-green-200 rounded-full">
              <Check className="w-5 h-5 text-green-600 mr-2" />
              <span className="text-green-700 font-medium">
                Current Plan: {tiers.find(t => t.id === currentTier)?.name || currentTier}
              </span>
            </div>
          )}
        </div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          {tiers.map((tier) => {
            const colors = getTierColors(tier.id);
            const isPopular = tier.id === 'pro';
            const isCurrent = currentTier === tier.id;
            
            return (
              <Card 
                key={tier.id} 
                className={`relative bg-white/90 backdrop-blur-sm border-2 shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 ${colors.border} ${isCurrent ? 'ring-2 ring-green-400' : ''}`}
              >
                {isPopular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 z-10">
                    <Badge className="bg-gradient-to-r from-purple-500 to-purple-700 text-white px-4 py-1.5 text-sm font-bold shadow-lg">
                      🔥 MOST POPULAR
                    </Badge>
                  </div>
                )}
                
                {isCurrent && (
                  <div className="absolute -top-4 right-4 z-10">
                    <Badge className="bg-green-500 text-white px-3 py-1 text-xs font-bold">
                      CURRENT
                    </Badge>
                  </div>
                )}
                
                <CardHeader className="text-center pb-4 pt-8">
                  <div className={`flex justify-center mb-4 ${colors.icon}`}>
                    {getTierIcon(tier.id)}
                  </div>
                  <CardTitle className="text-2xl font-bold text-slate-800 mb-2">
                    {tier.name}
                  </CardTitle>
                  
                  {/* Price */}
                  <div className="mt-4">
                    <div className="flex items-baseline justify-center">
                      <span className="text-4xl font-bold text-slate-900">
                        {formatPrice(tier.price_monthly)}
                      </span>
                      <span className="text-slate-600 ml-2">/month</span>
                    </div>
                    {tier.id === 'enterprise' && (
                      <p className="text-sm text-slate-500 mt-1">Starting price</p>
                    )}
                  </div>
                  
                  {/* Users */}
                  <div className={`mt-4 inline-flex items-center px-3 py-1.5 rounded-full ${colors.badge}`}>
                    <Users className="w-4 h-4 mr-2" />
                    <span className="font-medium">
                      {tier.included_users} user{tier.included_users > 1 ? 's' : ''} included
                    </span>
                  </div>
                  
                  {tier.extra_user_price > 0 && (
                    <p className="text-xs text-slate-500 mt-2">
                      +{formatPrice(tier.extra_user_price)}/user/month for additional users
                    </p>
                  )}
                </CardHeader>
                
                <CardContent className="pt-4">
                  {/* Key Features */}
                  <div className="space-y-3 mb-6">
                    <div className="flex items-center space-x-3">
                      <Check className="w-5 h-5 text-green-600 flex-shrink-0" />
                      <span className="text-slate-700">Unlimited Job Posts</span>
                    </div>
                    <div className="flex items-center space-x-3">
                      <Check className="w-5 h-5 text-green-600 flex-shrink-0" />
                      <span className="text-slate-700">35-Day Job Duration</span>
                    </div>
                    <div className="flex items-center space-x-3">
                      <Check className="w-5 h-5 text-green-600 flex-shrink-0" />
                      <span className="text-slate-700">{formatProfileLevel(tier.company_profile_level)} Company Profile</span>
                    </div>
                    
                    {tier.id !== 'starter' && (
                      <>
                        <div className="flex items-center space-x-3">
                          <Check className="w-5 h-5 text-green-600 flex-shrink-0" />
                          <span className="text-slate-700">AI Candidate Matching</span>
                        </div>
                        <div className="flex items-center space-x-3">
                          <Check className="w-5 h-5 text-green-600 flex-shrink-0" />
                          <span className="text-slate-700">CV Database Access</span>
                        </div>
                      </>
                    )}
                    
                    {(tier.id === 'pro' || tier.id === 'enterprise') && (
                      <>
                        <div className="flex items-center space-x-3">
                          <Check className="w-5 h-5 text-green-600 flex-shrink-0" />
                          <span className="text-slate-700">Bulk Job Upload</span>
                        </div>
                        <div className="flex items-center space-x-3">
                          <Check className="w-5 h-5 text-green-600 flex-shrink-0" />
                          <span className="text-slate-700">Advanced Analytics</span>
                        </div>
                      </>
                    )}
                    
                    {tier.id === 'enterprise' && (
                      <>
                        <div className="flex items-center space-x-3">
                          <Check className="w-5 h-5 text-green-600 flex-shrink-0" />
                          <span className="text-slate-700">API Access</span>
                        </div>
                        <div className="flex items-center space-x-3">
                          <Check className="w-5 h-5 text-green-600 flex-shrink-0" />
                          <span className="text-slate-700">Dedicated Account Manager</span>
                        </div>
                      </>
                    )}
                  </div>
                  
                  {/* CTA Button */}
                  <Button 
                    onClick={() => handleSubscribe(tier.id)}
                    disabled={purchasing === tier.id || isCurrent}
                    className={`w-full py-3 text-lg font-semibold transition-all duration-200 ${
                      isCurrent 
                        ? 'bg-green-100 text-green-700 cursor-not-allowed'
                        : isPopular
                          ? 'bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 shadow-lg'
                          : `bg-gradient-to-r ${colors.gradient} hover:opacity-90`
                    }`}
                  >
                    {purchasing === tier.id ? (
                      <div className="flex items-center justify-center space-x-2">
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                        <span>Processing...</span>
                      </div>
                    ) : isCurrent ? (
                      <span>Current Plan</span>
                    ) : tier.id === 'enterprise' ? (
                      <div className="flex items-center justify-center space-x-2">
                        <span>Contact Sales</span>
                        <ArrowRight className="w-4 h-4" />
                      </div>
                    ) : (
                      <div className="flex items-center justify-center space-x-2">
                        <CreditCard className="w-5 h-5" />
                        <span>Subscribe Now</span>
                      </div>
                    )}
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Feature Comparison Table */}
        <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-xl border border-slate-200 overflow-hidden">
          <div className="p-6 bg-gradient-to-r from-slate-800 to-slate-900">
            <h2 className="text-2xl font-bold text-white text-center">
              Complete Feature Comparison
            </h2>
            <p className="text-slate-300 text-center mt-2">
              See exactly what's included in each plan
            </p>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="text-left py-4 px-6 font-semibold text-slate-700">Feature</th>
                  {tiers.map(tier => (
                    <th key={tier.id} className="text-center py-4 px-4 font-semibold text-slate-700">
                      {tier.name}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {Object.entries(featureCategories).map(([category, features], catIndex) => (
                  <React.Fragment key={category}>
                    <tr className="bg-slate-100/50">
                      <td colSpan={tiers.length + 1} className="py-3 px-6 font-bold text-slate-800">
                        {category}
                      </td>
                    </tr>
                    {features.map((feature, featureIndex) => (
                      <tr key={feature.id} className={featureIndex % 2 === 0 ? 'bg-white' : 'bg-slate-50/50'}>
                        <td className="py-3 px-6 text-slate-700">{feature.label}</td>
                        {tiers.map(tier => (
                          <td key={tier.id} className="text-center py-3 px-4">
                            {hasFeature(tier.id, feature.tiers) ? (
                              <Check className="w-5 h-5 text-green-600 mx-auto" />
                            ) : feature.addon?.includes(tier.id) ? (
                              <Badge variant="outline" className="text-xs border-blue-300 text-blue-600">
                                Add-on
                              </Badge>
                            ) : (
                              <X className="w-5 h-5 text-slate-300 mx-auto" />
                            )}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-12 text-center">
          <div className="inline-flex items-center space-x-2 px-6 py-3 bg-blue-50 rounded-lg border border-blue-200">
            <Shield className="w-5 h-5 text-blue-600" />
            <span className="text-blue-800 font-medium">
              Secure payments powered by Payfast • Cancel anytime
            </span>
          </div>
          
          <p className="mt-4 text-slate-500 text-sm">
            All prices in South African Rand (ZAR). VAT included where applicable.
          </p>
        </div>
      </div>
    </div>
  );
};

export default PricingPage;
