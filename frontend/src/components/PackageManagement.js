import React, { useState, useEffect } from 'react';
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { 
  Package,
  CreditCard,
  Clock,
  Zap,
  Crown,
  CheckCircle,
  AlertCircle,
  Plus,
  Calendar,
  Infinity
} from "lucide-react";
import axios from 'axios';
import PricingPage from './PricingPage';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PackageManagement = ({ user }) => {
  const [userPackages, setUserPackages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showPricing, setShowPricing] = useState(false);

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
    fetchUserPackages();
  }, []);

  const fetchUserPackages = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/my-packages`, getAuthHeaders());
      setUserPackages(response.data);
    } catch (error) {
      console.error('Error fetching user packages:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getPackageIcon = (packageType) => {
    switch (packageType) {
      case 'two_listings': return <Zap className="w-6 h-6 text-blue-600" />;
      case 'five_listings': return <Package className="w-6 h-6 text-purple-600" />;
      case 'unlimited_listings': return <Crown className="w-6 h-6 text-yellow-600" />;
      default: return <Package className="w-6 h-6 text-slate-600" />;
    }
  };

  const getStatusColor = (userPackage, isExpired) => {
    if (isExpired) return 'bg-red-100 text-red-800 border-red-300';
    if (userPackage.subscription_status === 'active') return 'bg-green-100 text-green-800 border-green-300';
    if (userPackage.job_listings_remaining === 0) return 'bg-gray-100 text-gray-800 border-gray-300';
    return 'bg-blue-100 text-blue-800 border-blue-300';
  };

  const getTotalCredits = () => {
    let jobListings = 0;
    let hasUnlimited = false;
    
    userPackages.forEach(({ user_package, is_expired }) => {
      if (!is_expired && user_package.is_active) {
        if (user_package.job_listings_remaining === null) {
          hasUnlimited = true;
        } else if (user_package.job_listings_remaining > 0) {
          jobListings += user_package.job_listings_remaining;
        }
      }
    });
    
    return { jobListings, hasUnlimited };
  };

  const credits = getTotalCredits();

  if (showPricing) {
    return <PricingPage user={user} onClose={() => setShowPricing(false)} />;
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-800 mb-2">My Packages</h2>
          <p className="text-slate-600">Manage your Job Rocket packages and credits</p>
        </div>
        <Button
          onClick={() => setShowPricing(true)}
          className="bg-gradient-to-r from-blue-600 to-slate-700 hover:from-blue-700 hover:to-slate-800"
        >
          <Plus className="w-4 h-4 mr-2" />
          Buy More Credits
        </Button>
      </div>

      {/* Credit Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="bg-gradient-to-br from-blue-50 to-slate-50 border-0 shadow-xl">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center space-x-2 text-blue-800">
              <Zap className="w-5 h-5" />
              <span>Job Listing Credits</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-slate-800 mb-2">
              {credits.hasUnlimited ? (
                <div className="flex items-center space-x-2">
                  <Infinity className="w-8 h-8 text-blue-600" />
                  <span>Unlimited</span>
                </div>
              ) : (
                credits.jobListings
              )}
            </div>
            <p className="text-slate-600">
              {credits.hasUnlimited ? 'Unlimited job postings available' : 'Job postings remaining'}
            </p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-50 to-slate-50 border-0 shadow-xl">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center space-x-2 text-green-800">
              <CreditCard className="w-5 h-5" />
              <span>Package Status</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-slate-800 mb-2">
              {userPackages.length}
            </div>
            <p className="text-slate-600">Active packages purchased</p>
          </CardContent>
        </Card>
      </div>

      {/* Packages List */}
      <div className="space-y-4">
        {userPackages.length === 0 ? (
          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
            <CardContent className="p-12 text-center">
              <Package className="w-16 h-16 text-slate-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-slate-800 mb-2">No packages purchased</h3>
              <p className="text-slate-600 mb-6">
                Purchase a package to start posting jobs and accessing premium features
              </p>
              <Button
                onClick={() => setShowPricing(true)}
                className="bg-gradient-to-r from-blue-600 to-slate-700 hover:from-blue-700 hover:to-slate-800"
              >
                <Plus className="w-4 h-4 mr-2" />
                View Packages
              </Button>
            </CardContent>
          </Card>
        ) : (
          userPackages.map(({ user_package, package: pkg, is_expired }) => (
            <Card key={user_package.id} className="bg-white/80 backdrop-blur-sm border-0 shadow-xl hover:shadow-2xl transition-all duration-300">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-4 flex-1">
                    <div className="flex-shrink-0">
                      {getPackageIcon(pkg.package_type)}
                    </div>
                    
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h4 className="font-bold text-slate-800 text-lg">{pkg.name}</h4>
                        <Badge 
                          variant="outline" 
                          className={`${getStatusColor(user_package, is_expired)}`}
                        >
                          {is_expired ? 'Expired' : 
                           user_package.subscription_status === 'active' ? 'Active Subscription' :
                           user_package.job_listings_remaining === 0 ? 'Used Up' : 'Active'}
                        </Badge>
                      </div>
                      
                      <p className="text-slate-600 mb-4">{pkg.description}</p>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                        <div>
                          <span className="font-medium text-slate-700">Job Listings:</span>
                          <p className="text-slate-600">
                            {user_package.job_listings_remaining === null ? 'Unlimited' :
                             `${user_package.job_listings_remaining} remaining`}
                          </p>
                        </div>
                        
                        <div>
                          <span className="font-medium text-slate-700">Purchased:</span>
                          <p className="text-slate-600">{formatDate(user_package.purchased_date)}</p>
                        </div>
                        
                        {user_package.expiry_date && (
                          <div>
                            <span className="font-medium text-slate-700">
                              {is_expired ? 'Expired:' : 'Expires:'}
                            </span>
                            <p className={`${is_expired ? 'text-red-600' : 'text-slate-600'}`}>
                              {formatDate(user_package.expiry_date)}
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex flex-col items-end space-y-2">
                    <div className="text-right">
                      <div className="text-2xl font-bold text-slate-800">
                        R{pkg.price.toLocaleString('en-ZA')}
                      </div>
                      <div className="text-sm text-slate-500">
                        {pkg.is_subscription ? 'per month' : 'one-time'}
                      </div>
                    </div>
                    
                    {is_expired && pkg.is_subscription && (
                      <Button size="sm" variant="outline">
                        <Calendar className="w-4 h-4 mr-2" />
                        Renew
                      </Button>
                    )}
                  </div>
                </div>
                
                {/* Progress bar for limited packages */}
                {user_package.job_listings_remaining !== null && pkg.job_listings_included && (
                  <div className="mt-4 pt-4 border-t border-slate-200">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-slate-700">Usage Progress</span>
                      <span className="text-sm text-slate-600">
                        {pkg.job_listings_included - user_package.job_listings_remaining} of {pkg.job_listings_included} used
                      </span>
                    </div>
                    <div className="w-full bg-slate-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ 
                          width: `${((pkg.job_listings_included - user_package.job_listings_remaining) / pkg.job_listings_included) * 100}%` 
                        }}
                      ></div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {userPackages.length > 0 && (
        <div className="text-center">
          <Button
            onClick={() => setShowPricing(true)}
            variant="outline"
            className="border-blue-300 text-blue-600 hover:bg-blue-50"
          >
            <Plus className="w-4 h-4 mr-2" />
            Purchase Additional Packages
          </Button>
        </div>
      )}
    </div>
  );
};

export default PackageManagement;