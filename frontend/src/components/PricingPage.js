import React, { useState, useEffect } from 'react';
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { 
  Check,
  Zap,
  Crown,
  Rocket,
  Search,
  Users,
  Clock,
  CreditCard,
  Star,
  ArrowRight,
  Sparkles,
  Tag,
  AlertCircle,
  CheckCircle,
  X
} from "lucide-react";
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PricingPage = ({ user, onClose }) => {
  const [packages, setPackages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [purchasing, setPurchasing] = useState(null);
  const [selectedPackage, setSelectedPackage] = useState(null);
  const [discountCode, setDiscountCode] = useState('');
  const [discountValidation, setDiscountValidation] = useState(null);
  const [validatingDiscount, setValidatingDiscount] = useState(false);
  const [showCheckout, setShowCheckout] = useState(false);

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
    fetchPackages();
  }, []);

  const fetchPackages = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/packages`, getAuthHeaders());
      setPackages(response.data);
    } catch (error) {
      console.error('Error fetching packages:', error);
    } finally {
      setLoading(false);
    }
  };

  const validateDiscountCode = async (code, packageType) => {
    if (!code.trim()) {
      setDiscountValidation(null);
      return;
    }

    setValidatingDiscount(true);
    try {
      const response = await axios.post(`${API}/discount-codes/validate`, {
        code: code.trim(),
        package_type: packageType
      });
      
      setDiscountValidation({
        valid: true,
        ...response.data
      });
    } catch (error) {
      setDiscountValidation({
        valid: false,
        error: error.response?.data?.error || 'Invalid discount code'
      });
    } finally {
      setValidatingDiscount(false);
    }
  };

  const handleDiscountCodeChange = (value) => {
    setDiscountCode(value);
    
    // Clear previous validation
    setDiscountValidation(null);
    
    // Validate after a short delay
    if (selectedPackage && value.trim()) {
      const timeoutId = setTimeout(() => {
        validateDiscountCode(value, selectedPackage.package_type);
      }, 500);
      
      return () => clearTimeout(timeoutId);
    }
  };

  const handleSelectPackage = (pkg) => {
    setSelectedPackage(pkg);
    setShowCheckout(true);
    setDiscountCode('');
    setDiscountValidation(null);
  };


  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-ZA', {
      style: 'currency',
      currency: 'ZAR'
    }).format(amount);
  };

  const closeCheckout = () => {
    setShowCheckout(false);
    setSelectedPackage(null);
    setDiscountCode('');
    setDiscountValidation(null);
  };

  const handlePurchase = async (packageType) => {
    try {
      setPurchasing(packageType);
      
      // If we have a selected package from checkout modal, use that instead
      const targetPackage = selectedPackage || packages.find(p => p.package_type === packageType);
      if (!targetPackage) return;
      
      const payload = {
        package_type: targetPackage.package_type
      };
      
      // Add discount code if applied
      if (discountCode.trim()) {
        payload.discount_code = discountCode.trim();
      }
      
      const response = await axios.post(`${API}/payments/initiate`, payload, getAuthHeaders());

      // Redirect to payment URL
      window.location.href = response.data.payment_url;
      
    } catch (error) {
      console.error('Error initiating payment:', error);
      alert(error.response?.data?.detail || 'Failed to initiate payment');
    } finally {
      setPurchasing(null);
    }
  };

  const getPackageIcon = (packageType) => {
    switch (packageType) {
      case 'two_listings': return <Zap className="w-8 h-8 text-blue-600" />;
      case 'five_listings': return <Rocket className="w-8 h-8 text-purple-600" />;
      case 'unlimited_listings': return <Crown className="w-8 h-8 text-yellow-600" />;
      case 'cv_search_10': return <Search className="w-8 h-8 text-green-600" />;
      case 'cv_search_20': return <Users className="w-8 h-8 text-indigo-600" />;
      case 'cv_search_unlimited': return <Sparkles className="w-8 h-8 text-pink-600" />;
      default: return <Star className="w-8 h-8 text-slate-600" />;
    }
  };

  const getPackageColor = (packageType) => {
    switch (packageType) {
      case 'two_listings': return 'border-blue-200 hover:border-blue-300';
      case 'five_listings': return 'border-purple-200 hover:border-purple-300';
      case 'unlimited_listings': return 'border-yellow-200 hover:border-yellow-300 ring-2 ring-yellow-200';
      case 'cv_search_10': return 'border-green-200 hover:border-green-300';
      case 'cv_search_20': return 'border-indigo-200 hover:border-indigo-300';
      case 'cv_search_unlimited': return 'border-pink-200 hover:border-pink-300';
      default: return 'border-slate-200 hover:border-slate-300';
    }
  };

  const formatPrice = (price) => {
    return `R${price.toLocaleString('en-ZA')}`;
  };

  const getPackageFeatures = (pkg) => {
    const features = [];
    
    if (pkg.job_listings_included) {
      if (pkg.job_listings_included === 1) {
        features.push('1 Job Listing');
      } else {
        features.push(`${pkg.job_listings_included} Job Listings`);
      }
    } else if (pkg.job_listings_included === null && pkg.package_type === 'unlimited_listings') {
      features.push('Unlimited Job Listings');
    }
    
    if (pkg.job_expiry_days) {
      features.push(`Jobs expire in ${pkg.job_expiry_days} days`);
    }
    
    if (pkg.cv_searches_included) {
      features.push(`${pkg.cv_searches_included} CV Searches${pkg.is_subscription ? '/month' : ''}`);
    } else if (pkg.cv_searches_included === null && pkg.package_type.includes('cv_search')) {
      features.push('Unlimited CV Searches');
    }
    
    if (!pkg.is_subscription && pkg.job_listings_included) {
      features.push('No expiry - use anytime');
    }
    
    if (pkg.is_subscription) {
      features.push('Monthly billing');
      features.push('Cancel anytime');
    }
    
    return features;
  };

  const isPopular = (packageType) => {
    return packageType === 'unlimited_listings';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading packages...</p>
        </div>
      </div>
    );
  }

  // Separate job listing packages from CV search packages
  const jobPackages = packages.filter(pkg => 
    ['two_listings', 'five_listings', 'unlimited_listings'].includes(pkg.package_type)
  );
  
  const cvPackages = packages.filter(pkg => 
    pkg.package_type.includes('cv_search')
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
      <div className="max-w-7xl mx-auto px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="text-center mb-16">
          <Badge variant="outline" className="mb-4 px-4 py-2 text-blue-700 border-blue-300 bg-blue-50">
            🚀 Innovative Hiring Solutions
          </Badge>
          <h1 className="text-5xl font-bold text-slate-800 mb-6">
            Choose Your <span className="text-blue-600">Job Rocket</span> Package
          </h1>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto leading-relaxed">
            We're rocking the recruitment industry with game-changing packages designed for modern hiring teams. 
            Get the tools you need to find top talent faster.
          </p>
        </div>

        {/* Job Listing Packages */}
        <div className="mb-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-slate-800 mb-4">Job Listing Packages</h2>
            <p className="text-lg text-slate-600">Post jobs and reach qualified candidates</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {jobPackages.map((pkg) => (
              <Card 
                key={pkg.id} 
                className={`relative bg-white/90 backdrop-blur-sm border-2 shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2 ${getPackageColor(pkg.package_type)}`}
              >
                {isPopular(pkg.package_type) && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <Badge className="bg-gradient-to-r from-yellow-400 to-orange-500 text-white px-6 py-2 text-sm font-bold shadow-lg">
                      🔥 MOST POPULAR
                    </Badge>
                  </div>
                )}
                
                <CardHeader className="text-center pb-2">
                  <div className="flex justify-center mb-4">
                    {getPackageIcon(pkg.package_type)}
                  </div>
                  <CardTitle className="text-2xl font-bold text-slate-800 mb-2">
                    {pkg.name}
                  </CardTitle>
                  <p className="text-slate-600 text-sm mb-6">{pkg.description}</p>
                  
                  <div className="space-y-2">
                    <div className="text-4xl font-bold text-slate-800">
                      {formatPrice(pkg.price)}
                    </div>
                    <div className="text-slate-600">
                      {pkg.is_subscription ? 'per month' : 'one-time payment'}
                    </div>
                  </div>
                </CardHeader>
                
                <CardContent className="pt-6">
                  <div className="space-y-4 mb-8">
                    {getPackageFeatures(pkg).map((feature, index) => (
                      <div key={index} className="flex items-center space-x-3">
                        <Check className="w-5 h-5 text-green-600 flex-shrink-0" />
                        <span className="text-slate-700">{feature}</span>
                      </div>
                    ))}
                  </div>
                  
                  <Button 
                    onClick={() => handlePurchase(pkg.package_type)}
                    disabled={purchasing === pkg.package_type}
                    className={`w-full py-3 text-lg font-semibold transition-all duration-200 ${
                      isPopular(pkg.package_type)
                        ? 'bg-gradient-to-r from-yellow-500 to-orange-600 hover:from-yellow-600 hover:to-orange-700 shadow-lg'
                        : 'bg-gradient-to-r from-blue-600 to-slate-700 hover:from-blue-700 hover:to-slate-800'
                    }`}
                  >
                    {purchasing === pkg.package_type ? (
                      <div className="flex items-center space-x-2">
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                        <span>Processing...</span>
                      </div>
                    ) : (
                      <div className="flex items-center justify-center space-x-2">
                        <CreditCard className="w-5 h-5" />
                        <span>Purchase Now</span>
                        <ArrowRight className="w-4 h-4" />
                      </div>
                    )}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* CV Search Packages */}
        <div className="mb-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-slate-800 mb-4">CV Search Packages</h2>
            <p className="text-lg text-slate-600">Find candidates actively (Coming Soon)</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {cvPackages.map((pkg) => (
              <Card 
                key={pkg.id} 
                className={`relative bg-white/60 backdrop-blur-sm border-2 shadow-xl opacity-75 ${getPackageColor(pkg.package_type)}`}
              >
                <div className="absolute inset-0 bg-slate-100/50 rounded-lg flex items-center justify-center">
                  <Badge variant="outline" className="px-4 py-2 text-slate-600 border-slate-400 bg-white/80">
                    Coming Soon
                  </Badge>
                </div>
                
                <CardHeader className="text-center pb-2">
                  <div className="flex justify-center mb-4">
                    {getPackageIcon(pkg.package_type)}
                  </div>
                  <CardTitle className="text-2xl font-bold text-slate-800 mb-2">
                    {pkg.name}
                  </CardTitle>
                  <p className="text-slate-600 text-sm mb-6">{pkg.description}</p>
                  
                  <div className="space-y-2">
                    <div className="text-4xl font-bold text-slate-800">
                      {formatPrice(pkg.price)}
                    </div>
                    <div className="text-slate-600">
                      {pkg.is_subscription ? 'per month' : 'one-time payment'}
                    </div>
                  </div>
                </CardHeader>
                
                <CardContent className="pt-6">
                  <div className="space-y-4 mb-8">
                    {getPackageFeatures(pkg).map((feature, index) => (
                      <div key={index} className="flex items-center space-x-3">
                        <Check className="w-5 h-5 text-green-600 flex-shrink-0" />
                        <span className="text-slate-700">{feature}</span>
                      </div>
                    ))}
                  </div>
                  
                  <Button 
                    disabled
                    className="w-full py-3 text-lg font-semibold bg-slate-400 cursor-not-allowed"
                  >
                    Coming Soon
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="text-center">
          <div className="inline-flex items-center space-x-2 px-6 py-3 bg-blue-50 rounded-lg border border-blue-200">
            <Clock className="w-5 h-5 text-blue-600" />
            <span className="text-blue-800 font-medium">
              Secure payments powered by Payfast
            </span>
          </div>
        </div>
      </div>

      {/* Checkout Modal */}
      {showCheckout && selectedPackage && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-screen overflow-y-auto">
            <div className="p-6">
              {/* Header */}
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-slate-900">Complete Purchase</h3>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={closeCheckout}
                  className="text-slate-400 hover:text-slate-600"
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>

              {/* Package Details */}
              <div className="bg-slate-50 rounded-lg p-4 mb-6">
                <h4 className="font-medium text-slate-900 mb-2">{selectedPackage.name}</h4>
                <p className="text-slate-600 text-sm mb-3">{selectedPackage.description}</p>
                
                <div className="flex items-center justify-between">
                  <span className="text-slate-700">Package Price:</span>
                  <span className="font-medium text-slate-900">
                    {formatCurrency(selectedPackage.price)}
                  </span>
                </div>
              </div>

              {/* Discount Code Section */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Discount Code (Optional)
                </label>
                <div className="flex space-x-2">
                  <div className="flex-1 relative">
                    <Tag className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
                    <Input
                      value={discountCode}
                      onChange={(e) => handleDiscountCodeChange(e.target.value)}
                      placeholder="Enter discount code"
                      className="pl-10"
                    />
                  </div>
                </div>
                
                {/* Discount Validation Feedback */}
                {validatingDiscount && (
                  <div className="mt-2 flex items-center text-sm text-slate-500">
                    <div className="animate-spin rounded-full h-3 w-3 border-b border-slate-400 mr-2"></div>
                    Validating code...
                  </div>
                )}
                
                {discountValidation && (
                  <div className="mt-2">
                    {discountValidation.valid ? (
                      <div className="flex items-start space-x-2 p-3 bg-green-50 border border-green-200 rounded-md">
                        <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                        <div className="flex-1">
                          <p className="text-sm font-medium text-green-800">
                            {discountValidation.discount_details.name}
                          </p>
                          <p className="text-xs text-green-600">
                            {discountValidation.discount_details.description}
                          </p>
                          <div className="mt-2 text-xs text-green-700">
                            Discount: {formatCurrency(discountValidation.discount_amount)}
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="flex items-center space-x-2 p-3 bg-red-50 border border-red-200 rounded-md">
                        <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0" />
                        <p className="text-sm text-red-800">{discountValidation.error}</p>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Price Summary */}
              <div className="bg-slate-50 rounded-lg p-4 mb-6">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-600">Subtotal:</span>
                    <span className="text-slate-900">
                      {formatCurrency(discountValidation?.original_price || selectedPackage.price)}
                    </span>
                  </div>
                  
                  {discountValidation?.valid && (
                    <div className="flex items-center justify-between text-green-600">
                      <span>Discount ({discountValidation.discount_details.code}):</span>
                      <span>-{formatCurrency(discountValidation.discount_amount)}</span>
                    </div>
                  )}
                  
                  <Separator />
                  
                  <div className="flex items-center justify-between font-medium text-lg">
                    <span className="text-slate-900">Total:</span>
                    <span className="text-blue-600">
                      {formatCurrency(discountValidation?.final_price || selectedPackage.price)}
                    </span>
                  </div>
                </div>
              </div>

              {/* Payment Button */}
              <div className="space-y-3">
                <Button
                  onClick={() => handlePurchase(selectedPackage.package_type)}
                  disabled={purchasing === selectedPackage.package_type}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                  size="lg"
                >
                  {purchasing === selectedPackage.package_type ? (
                    <div className="flex items-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b border-white mr-2"></div>
                      Processing...
                    </div>
                  ) : (
                    <div className="flex items-center">
                      <CreditCard className="w-4 h-4 mr-2" />
                      Pay {formatCurrency(discountValidation?.final_price || selectedPackage.price)}
                    </div>
                  )}
                </Button>
                
                <p className="text-xs text-slate-500 text-center">
                  You will be redirected to Payfast to complete your payment securely.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PricingPage;