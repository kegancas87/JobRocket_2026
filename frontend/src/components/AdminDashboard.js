import React, { useState, useEffect } from "react";
import axios from "axios";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Separator } from "./ui/separator";
import { 
  Plus, 
  Edit2, 
  Trash2, 
  ToggleLeft, 
  ToggleRight,
  TrendingUp,
  Users,
  DollarSign,
  ShoppingCart,
  Calendar,
  Settings,
  BarChart3,
  LogOut,
  Check,
  X
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminDashboard = ({ user, onLogout, onNavigateToJobs }) => {
  const [activeTab, setActiveTab] = useState('discount-codes');
  const [discountCodes, setDiscountCodes] = useState([]);
  const [usageStats, setUsageStats] = useState({});
  const [loading, setLoading] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingCode, setEditingCode] = useState(null);
  const [formData, setFormData] = useState({
    code: '',
    name: '',
    description: '',
    discount_type: 'percentage',
    discount_value: '',
    minimum_amount: '',
    maximum_discount: '',
    usage_limit: '',
    user_limit: '',
    valid_until: '',
    applicable_packages: []
  });

  const packageTypes = [
    'two_listings',
    'five_listings', 
    'unlimited_listings',
    'cv_search_10',
    'cv_search_20',
    'cv_search_unlimited'
  ];

  useEffect(() => {
    if (activeTab === 'discount-codes') {
      loadDiscountCodes();
    } else if (activeTab === 'statistics') {
      loadUsageStats();
    }
  }, [activeTab]);

  const getAuthHeaders = () => ({
    'Authorization': `Bearer ${localStorage.getItem('token')}`,
    'Content-Type': 'application/json'
  });

  const loadDiscountCodes = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/admin/discount-codes`, {
        headers: getAuthHeaders()
      });
      setDiscountCodes(response.data);
    } catch (error) {
      console.error('Error loading discount codes:', error);
    }
    setLoading(false);
  };

  const loadUsageStats = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/admin/discount-codes/stats/usage`, {
        headers: getAuthHeaders()
      });
      setUsageStats(response.data);
    } catch (error) {
      console.error('Error loading usage stats:', error);
    }
    setLoading(false);
  };

  const resetForm = () => {
    setFormData({
      code: '',
      name: '',
      description: '',
      discount_type: 'percentage',
      discount_value: '',
      minimum_amount: '',
      maximum_discount: '',
      usage_limit: '',
      user_limit: '',
      valid_until: '',
      applicable_packages: []
    });
    setShowCreateForm(false);
    setEditingCode(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      // Prepare data
      const submitData = {
        ...formData,
        discount_value: parseFloat(formData.discount_value),
        minimum_amount: formData.minimum_amount ? parseFloat(formData.minimum_amount) : null,
        maximum_discount: formData.maximum_discount ? parseFloat(formData.maximum_discount) : null,
        usage_limit: formData.usage_limit ? parseInt(formData.usage_limit) : null,
        user_limit: formData.user_limit ? parseInt(formData.user_limit) : null,
        valid_until: formData.valid_until ? new Date(formData.valid_until).toISOString() : null,
        applicable_packages: formData.applicable_packages.length > 0 ? formData.applicable_packages : null
      };

      if (editingCode) {
        // Update existing code
        await axios.put(`${API}/admin/discount-codes/${editingCode.id}`, submitData, {
          headers: getAuthHeaders()
        });
      } else {
        // Create new code
        await axios.post(`${API}/admin/discount-codes`, submitData, {
          headers: getAuthHeaders()
        });
      }
      
      resetForm();
      loadDiscountCodes();
    } catch (error) {
      console.error('Error saving discount code:', error);
      alert(error.response?.data?.detail || 'Error saving discount code');
    }
    setLoading(false);
  };

  const handleEdit = (code) => {
    setEditingCode(code);
    setFormData({
      code: code.code,
      name: code.name,
      description: code.description || '',
      discount_type: code.discount_type,
      discount_value: code.discount_value.toString(),
      minimum_amount: code.minimum_amount?.toString() || '',
      maximum_discount: code.maximum_discount?.toString() || '',
      usage_limit: code.usage_limit?.toString() || '',
      user_limit: code.user_limit?.toString() || '',
      valid_until: code.valid_until ? new Date(code.valid_until).toISOString().split('T')[0] : '',
      applicable_packages: code.applicable_packages || []
    });
    setShowCreateForm(true);
  };

  const handleDeactivate = async (codeId) => {
    if (window.confirm('Are you sure you want to deactivate this discount code?')) {
      try {
        await axios.post(`${API}/admin/discount-codes/${codeId}/deactivate`, {}, {
          headers: getAuthHeaders()
        });
        loadDiscountCodes();
      } catch (error) {
        console.error('Error deactivating discount code:', error);
        alert('Error deactivating discount code');
      }
    }
  };

  const handleDelete = async (codeId) => {
    if (window.confirm('Are you sure you want to delete this discount code? This action cannot be undone.')) {
      try {
        await axios.delete(`${API}/admin/discount-codes/${codeId}`, {
          headers: getAuthHeaders()
        });
        loadDiscountCodes();
      } catch (error) {
        console.error('Error deleting discount code:', error);
        alert('Error deleting discount code');
      }
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'No expiry';
    return new Date(dateString).toLocaleDateString();
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-ZA', {
      style: 'currency',
      currency: 'ZAR'
    }).format(amount);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <div className="bg-slate-800/50 backdrop-blur border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <Settings className="w-8 h-8 text-blue-400" />
              <div>
                <h1 className="text-2xl font-bold text-white">Admin Dashboard</h1>
                <p className="text-slate-400">Manage Job Rocket Platform</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-slate-300">Welcome, {user.first_name}</span>
              <Button 
                variant="outline" 
                onClick={onLogout}
                className="border-slate-600 text-slate-300 hover:bg-slate-700"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Navigation Tabs */}
        <div className="flex space-x-1 mb-8">
          <Button
            variant={activeTab === 'discount-codes' ? 'default' : 'outline'}
            onClick={() => setActiveTab('discount-codes')}
            className={activeTab === 'discount-codes' ? 'bg-blue-600 text-white' : 'border-slate-600 text-slate-300'}
          >
            <ShoppingCart className="w-4 h-4 mr-2" />
            Discount Codes
          </Button>
          <Button
            variant={activeTab === 'statistics' ? 'default' : 'outline'}
            onClick={() => setActiveTab('statistics')}
            className={activeTab === 'statistics' ? 'bg-blue-600 text-white' : 'border-slate-600 text-slate-300'}
          >
            <BarChart3 className="w-4 h-4 mr-2" />
            Statistics
          </Button>
        </div>

        {/* Discount Codes Tab */}
        {activeTab === 'discount-codes' && (
          <div className="space-y-6">
            {/* Create/Edit Form */}
            {showCreateForm && (
              <Card className="bg-slate-800/50 backdrop-blur border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center justify-between">
                    {editingCode ? 'Edit Discount Code' : 'Create New Discount Code'}
                    <Button 
                      variant="outline" 
                      onClick={resetForm}
                      className="border-slate-600 text-slate-300"
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">Code *</label>
                      <Input
                        value={formData.code}
                        onChange={(e) => setFormData({...formData, code: e.target.value.toUpperCase()})}
                        placeholder="SAVE20"
                        required
                        disabled={editingCode}
                        className="bg-slate-700/50 border-slate-600 text-white"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">Name *</label>
                      <Input
                        value={formData.name}
                        onChange={(e) => setFormData({...formData, name: e.target.value})}
                        placeholder="20% Off Discount"
                        required
                        className="bg-slate-700/50 border-slate-600 text-white"
                      />
                    </div>

                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-slate-300 mb-2">Description</label>
                      <Input
                        value={formData.description}
                        onChange={(e) => setFormData({...formData, description: e.target.value})}
                        placeholder="Save 20% on all packages"
                        className="bg-slate-700/50 border-slate-600 text-white"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">Discount Type *</label>
                      <select
                        value={formData.discount_type}
                        onChange={(e) => setFormData({...formData, discount_type: e.target.value})}
                        className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600 rounded-md text-white"
                        required
                      >
                        <option value="percentage">Percentage</option>
                        <option value="fixed_amount">Fixed Amount (ZAR)</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        Discount Value * {formData.discount_type === 'percentage' ? '(%)' : '(ZAR)'}
                      </label>
                      <Input
                        type="number"
                        step="0.01"
                        value={formData.discount_value}
                        onChange={(e) => setFormData({...formData, discount_value: e.target.value})}
                        placeholder={formData.discount_type === 'percentage' ? '20' : '500'}
                        required
                        className="bg-slate-700/50 border-slate-600 text-white"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">Minimum Amount (ZAR)</label>
                      <Input
                        type="number"
                        step="0.01"
                        value={formData.minimum_amount}
                        onChange={(e) => setFormData({...formData, minimum_amount: e.target.value})}
                        placeholder="1000"
                        className="bg-slate-700/50 border-slate-600 text-white"
                      />
                    </div>

                    {formData.discount_type === 'percentage' && (
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">Maximum Discount (ZAR)</label>
                        <Input
                          type="number"
                          step="0.01"
                          value={formData.maximum_discount}
                          onChange={(e) => setFormData({...formData, maximum_discount: e.target.value})}
                          placeholder="1000"
                          className="bg-slate-700/50 border-slate-600 text-white"
                        />
                      </div>
                    )}

                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">Usage Limit</label>
                      <Input
                        type="number"
                        value={formData.usage_limit}
                        onChange={(e) => setFormData({...formData, usage_limit: e.target.value})}
                        placeholder="100"
                        className="bg-slate-700/50 border-slate-600 text-white"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">User Limit</label>
                      <Input
                        type="number"
                        value={formData.user_limit}
                        onChange={(e) => setFormData({...formData, user_limit: e.target.value})}
                        placeholder="1"
                        className="bg-slate-700/50 border-slate-600 text-white"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">Valid Until</label>
                      <Input
                        type="date"
                        value={formData.valid_until}
                        onChange={(e) => setFormData({...formData, valid_until: e.target.value})}
                        className="bg-slate-700/50 border-slate-600 text-white"
                      />
                    </div>

                    <div className="md:col-span-2 flex justify-end space-x-4">
                      <Button 
                        type="button" 
                        variant="outline" 
                        onClick={resetForm}
                        className="border-slate-600 text-slate-300"
                      >
                        Cancel
                      </Button>
                      <Button 
                        type="submit" 
                        disabled={loading}
                        className="bg-blue-600 hover:bg-blue-700 text-white"
                      >
                        <Check className="w-4 h-4 mr-2" />
                        {editingCode ? 'Update' : 'Create'} Discount Code
                      </Button>
                    </div>
                  </form>
                </CardContent>
              </Card>
            )}

            {/* Discount Codes List */}
            <Card className="bg-slate-800/50 backdrop-blur border-slate-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center justify-between">
                  <span>Discount Codes</span>
                  <Button 
                    onClick={() => setShowCreateForm(true)}
                    className="bg-green-600 hover:bg-green-700 text-white"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    New Code
                  </Button>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="text-center text-slate-400 py-8">Loading...</div>
                ) : discountCodes.length === 0 ? (
                  <div className="text-center text-slate-400 py-8">No discount codes created yet</div>
                ) : (
                  <div className="space-y-4">
                    {discountCodes.map((code) => (
                      <div key={code.id} className="bg-slate-700/30 rounded-lg p-4 border border-slate-600">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-3 mb-2">
                              <Badge 
                                variant={code.status === 'active' ? 'default' : 'secondary'}
                                className={code.status === 'active' ? 'bg-green-600 text-white' : 'bg-slate-500 text-white'}
                              >
                                {code.code}
                              </Badge>
                              <span className="text-white font-medium">{code.name}</span>
                              <Badge variant="outline" className="border-slate-500 text-slate-300">
                                {code.status}
                              </Badge>
                            </div>
                            
                            {code.description && (
                              <p className="text-slate-400 text-sm mb-2">{code.description}</p>
                            )}
                            
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                              <div>
                                <span className="text-slate-500">Discount:</span>
                                <div className="text-slate-300">
                                  {code.discount_type === 'percentage' 
                                    ? `${code.discount_value}%` 
                                    : formatCurrency(code.discount_value)
                                  }
                                </div>
                              </div>
                              
                              <div>
                                <span className="text-slate-500">Usage:</span>
                                <div className="text-slate-300">
                                  {code.usage_count} / {code.usage_limit || '∞'}
                                </div>
                              </div>
                              
                              <div>
                                <span className="text-slate-500">Valid Until:</span>
                                <div className="text-slate-300">{formatDate(code.valid_until)}</div>
                              </div>
                              
                              <div>
                                <span className="text-slate-500">Minimum:</span>
                                <div className="text-slate-300">
                                  {code.minimum_amount ? formatCurrency(code.minimum_amount) : 'None'}
                                </div>
                              </div>
                            </div>
                          </div>
                          
                          <div className="flex items-center space-x-2 ml-4">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleEdit(code)}
                              className="border-slate-600 text-slate-300 hover:bg-slate-700"
                            >
                              <Edit2 className="w-4 h-4" />
                            </Button>
                            
                            {code.status === 'active' && (
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleDeactivate(code.id)}
                                className="border-yellow-600 text-yellow-400 hover:bg-yellow-600 hover:text-white"
                              >
                                <ToggleLeft className="w-4 h-4" />
                              </Button>
                            )}
                            
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleDelete(code.id)}
                              className="border-red-600 text-red-400 hover:bg-red-600 hover:text-white"
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {/* Statistics Tab */}
        {activeTab === 'statistics' && (
          <div className="space-y-6">
            {/* Overview Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <Card className="bg-slate-800/50 backdrop-blur border-slate-700">
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <ShoppingCart className="w-8 h-8 text-blue-400" />
                    <div className="ml-4">
                      <p className="text-sm font-medium text-slate-400">Total Codes</p>
                      <p className="text-2xl font-bold text-white">{usageStats.total_codes || 0}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-slate-800/50 backdrop-blur border-slate-700">
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <TrendingUp className="w-8 h-8 text-green-400" />
                    <div className="ml-4">
                      <p className="text-sm font-medium text-slate-400">Active Codes</p>
                      <p className="text-2xl font-bold text-white">{usageStats.active_codes || 0}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-slate-800/50 backdrop-blur border-slate-700">
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <Users className="w-8 h-8 text-purple-400" />
                    <div className="ml-4">
                      <p className="text-sm font-medium text-slate-400">Total Uses</p>
                      <p className="text-2xl font-bold text-white">{usageStats.total_transactions_with_discounts || 0}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-slate-800/50 backdrop-blur border-slate-700">
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <DollarSign className="w-8 h-8 text-yellow-400" />
                    <div className="ml-4">
                      <p className="text-sm font-medium text-slate-400">Total Savings</p>
                      <p className="text-2xl font-bold text-white">
                        {formatCurrency(usageStats.total_savings || 0)}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Usage Details */}
            {usageStats.code_usage && usageStats.code_usage.length > 0 && (
              <Card className="bg-slate-800/50 backdrop-blur border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">Code Usage Details</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {usageStats.code_usage.map((usage, index) => (
                      <div key={index} className="bg-slate-700/30 rounded-lg p-4 border border-slate-600">
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          <div>
                            <span className="text-slate-500">Code:</span>
                            <div className="text-white font-medium">{usage._id}</div>
                          </div>
                          <div>
                            <span className="text-slate-500">Uses:</span>
                            <div className="text-slate-300">{usage.usage_count}</div>
                          </div>
                          <div>
                            <span className="text-slate-500">Total Savings:</span>
                            <div className="text-green-400">{formatCurrency(usage.total_discount_amount)}</div>
                          </div>
                          <div>
                            <span className="text-slate-500">Revenue Impact:</span>
                            <div className="text-slate-300">{formatCurrency(usage.total_final_amount)}</div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;