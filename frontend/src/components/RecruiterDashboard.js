import React, { useState, useEffect } from 'react';
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Textarea } from "./ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Label } from "./ui/label";
import CompanyStructure from './CompanyStructure';
import JobPosting from './JobPosting';
import ApplicationManagement from './ApplicationManagement';
import PackageManagement from './PackageManagement';
import { 
  Building2, 
  Globe, 
  Linkedin, 
  Users, 
  Upload,
  Save,
  Briefcase,
  MapPin,
  Image,
  Link,
  FileText,
  CreditCard,
  Check,
  ChevronRight,
  Loader2,
  Edit2,
  X,
  Trash2
} from "lucide-react";
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Helper function to get full image URL
const getImageUrl = (imageUrl) => {
  if (!imageUrl) return '';
  if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
    return imageUrl;
  }
  if (imageUrl.startsWith('/uploads/')) {
    return `${BACKEND_URL}/api${imageUrl}`;
  }
  if (imageUrl.startsWith('/api/uploads/')) {
    return `${BACKEND_URL}${imageUrl}`;
  }
  return imageUrl;
};

const RecruiterDashboard = ({ user, onUpdateUser }) => {
  const [profile, setProfile] = useState(user);
  const [loading, setLoading] = useState(false);
  const [activeStep, setActiveStep] = useState(0);
  const [progress, setProgress] = useState(user.recruiter_progress || {});
  const [uploadingImage, setUploadingImage] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  
  // Form states - get data from account (which stores company info)
  const [companyForm, setCompanyForm] = useState({
    company_name: user.account?.name || user.company_profile?.company_name || '',
    company_description: user.account?.company_description || user.company_profile?.company_description || '',
    company_website: user.account?.company_website || user.company_profile?.company_website || '',
    company_linkedin: user.account?.company_linkedin || user.company_profile?.company_linkedin || '',
    company_size: user.account?.company_size || user.company_profile?.company_size || '',
    company_industry: user.account?.company_industry || user.company_profile?.company_industry || '',
    company_location: user.account?.company_location || user.company_profile?.company_location || '',
    company_logo_url: user.account?.company_logo_url || user.company_profile?.company_logo_url || '',
    company_cover_image_url: user.account?.company_cover_image_url || user.company_profile?.company_cover_image_url || ''
  });

  // Original form values for cancel functionality
  const [originalForm, setOriginalForm] = useState({...companyForm});

  // Fetch full user data with account info on mount
  useEffect(() => {
    fetchCurrentUser();
    // eslint-disable-next-line
  }, []);

  // Steps configuration
  const steps = [
    { 
      id: 'company', 
      label: 'Company Info', 
      icon: Building2,
      isComplete: progress.company_description && progress.company_size
    },
    { 
      id: 'branding', 
      label: 'Branding', 
      icon: Image,
      isComplete: progress.company_logo
    },
    { 
      id: 'links', 
      label: 'Links', 
      icon: Link,
      isComplete: progress.company_website
    },
    { 
      id: 'structure', 
      label: 'Structure', 
      icon: Users,
      isComplete: false
    }
  ];

  const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    return {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    };
  };

  const fetchCurrentUser = async () => {
    try {
      const response = await axios.get(`${API}/auth/me`, getAuthHeaders());
      setProfile(response.data);
      setProgress(response.data.recruiter_progress || {});
      
      // Update form with latest data from server
      const account = response.data.account || {};
      const newFormData = {
        company_name: account.name || '',
        company_description: account.company_description || '',
        company_website: account.company_website || '',
        company_linkedin: account.company_linkedin || '',
        company_size: account.company_size || '',
        company_industry: account.company_industry || '',
        company_location: account.company_location || '',
        company_logo_url: account.company_logo_url || '',
        company_cover_image_url: account.company_cover_image_url || ''
      };
      setCompanyForm(newFormData);
      setOriginalForm(newFormData);
      setIsEditing(false);
      
      onUpdateUser(response.data);
    } catch (error) {
      console.error('Error fetching user data:', error);
    }
  };

  const handleImageUpload = async (file, imageType) => {
    if (!file) return;
    
    const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      alert('Please upload a valid image file (JPG, PNG, GIF, or WebP)');
      return;
    }

    const maxSize = 5 * 1024 * 1024;
    if (file.size > maxSize) {
      alert('Image must be smaller than 5MB');
      return;
    }

    setUploadingImage(imageType);
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const token = localStorage.getItem('token');
      const endpoint = imageType === 'logo' ? '/uploads/company-logo' : '/uploads/company-cover';
      
      const response = await axios.post(`${API}${endpoint}`, formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });
      
      const fieldName = imageType === 'logo' ? 'company_logo_url' : 'company_cover_image_url';
      setCompanyForm(prev => ({
        ...prev,
        [fieldName]: response.data.url
      }));
      
      await fetchCurrentUser();
    } catch (error) {
      console.error(`Error uploading ${imageType}:`, error);
      alert(`Failed to upload ${imageType}. Please try again.`);
    } finally {
      setUploadingImage(null);
    }
  };

  const handleCompanySubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      // Update the account with company profile data
      await axios.put(`${API}/account`, {
        name: companyForm.company_name,
        company_description: companyForm.company_description,
        company_website: companyForm.company_website,
        company_linkedin: companyForm.company_linkedin,
        company_size: companyForm.company_size,
        company_industry: companyForm.company_industry,
        company_location: companyForm.company_location,
        company_logo_url: companyForm.company_logo_url,
        company_cover_image_url: companyForm.company_cover_image_url
      }, getAuthHeaders());
      await fetchCurrentUser();
      setIsEditing(false);
      setOriginalForm({...companyForm});
    } catch (error) {
      console.error('Error updating company profile:', error);
      alert(error.response?.data?.detail || 'Failed to update company profile');
    } finally {
      setLoading(false);
    }
  };

  const onProfileComplete = async () => {
    await fetchCurrentUser();
  };

  const companySizeOptions = [
    "1-10 employees",
    "11-50 employees",
    "51-200 employees",
    "201-500 employees",
    "501-1000 employees",
    "1000+ employees"
  ];

  const industryOptions = [
    "Technology",
    "Healthcare",
    "Finance",
    "Education",
    "Retail",
    "Manufacturing",
    "Consulting",
    "Media & Entertainment",
    "Real Estate",
    "Non-profit",
    "Other"
  ];

  // Calculate overall progress percentage
  const completedSteps = steps.filter(s => s.isComplete).length;
  const progressPercentage = Math.round((progress.total_points || 0));

  // Render step content
  const renderStepContent = () => {
    switch(steps[activeStep].id) {
      case 'company':
        // Check if company info has any data saved
        const hasCompanyData = companyForm.company_name || companyForm.company_description || companyForm.company_industry;
        
        // If there's data and not editing, show the view mode
        if (hasCompanyData && !isEditing) {
          return (
            <div className="space-y-8">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-semibold text-slate-800 mb-2">Company Info</h2>
                  <p className="text-slate-500">Your company information</p>
                </div>
                <Button 
                  onClick={() => {
                    setOriginalForm({...companyForm});
                    setIsEditing(true);
                  }}
                  variant="outline"
                  className="flex items-center gap-2"
                >
                  <Edit2 className="w-4 h-4" />
                  Edit Company Info
                </Button>
              </div>
              
              {/* Display saved company info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="p-4 bg-slate-50 rounded-lg">
                    <label className="text-xs font-medium text-slate-500 uppercase tracking-wider">Company Name</label>
                    <p className="text-lg font-medium text-slate-800 mt-1">{companyForm.company_name || 'Not set'}</p>
                  </div>
                  
                  <div className="p-4 bg-slate-50 rounded-lg">
                    <label className="text-xs font-medium text-slate-500 uppercase tracking-wider">Industry</label>
                    <p className="text-lg font-medium text-slate-800 mt-1">{companyForm.company_industry || 'Not set'}</p>
                  </div>
                  
                  <div className="p-4 bg-slate-50 rounded-lg">
                    <label className="text-xs font-medium text-slate-500 uppercase tracking-wider">Location</label>
                    <p className="text-lg font-medium text-slate-800 mt-1">{companyForm.company_location || 'Not set'}</p>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <div className="p-4 bg-slate-50 rounded-lg">
                    <label className="text-xs font-medium text-slate-500 uppercase tracking-wider">Company Size</label>
                    <p className="text-lg font-medium text-slate-800 mt-1">{companyForm.company_size || 'Not set'}</p>
                  </div>
                  
                  <div className="p-4 bg-slate-50 rounded-lg h-full">
                    <label className="text-xs font-medium text-slate-500 uppercase tracking-wider">Description</label>
                    <p className="text-slate-700 mt-1 whitespace-pre-wrap">
                      {companyForm.company_description || 'No description added yet'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="flex items-center gap-4 pt-4 border-t border-slate-200">
                <Button 
                  variant="outline"
                  onClick={() => setActiveStep(1)}
                  className="flex items-center gap-2"
                >
                  Next: Branding
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
            </div>
          );
        }
        
        // Edit mode / Initial setup
        return (
          <div className="space-y-8">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-semibold text-slate-800 mb-2">
                  {isEditing ? 'Edit Company Info' : 'Company Info'}
                </h2>
                <p className="text-slate-500">Tell candidates about your company</p>
              </div>
              {isEditing && (
                <Button 
                  variant="ghost"
                  onClick={() => {
                    setCompanyForm({...originalForm});
                    setIsEditing(false);
                  }}
                  className="text-slate-600"
                >
                  <X className="w-4 h-4 mr-2" />
                  Cancel
                </Button>
              )}
            </div>
            
            <form onSubmit={handleCompanySubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="company_name" className="text-sm font-medium text-slate-700">
                      Company Name
                    </Label>
                    {companyForm.company_name && (
                      <button 
                        type="button"
                        onClick={() => setCompanyForm(prev => ({ ...prev, company_name: '' }))}
                        className="text-xs text-red-500 hover:text-red-700"
                      >
                        Clear
                      </button>
                    )}
                  </div>
                  <Input
                    id="company_name"
                    value={companyForm.company_name}
                    onChange={(e) => setCompanyForm(prev => ({ ...prev, company_name: e.target.value }))}
                    placeholder="Your Company Name"
                    className="h-12 bg-white border-slate-200 focus:border-blue-500 focus:ring-blue-500/20"
                  />
                </div>
                
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="company_industry" className="text-sm font-medium text-slate-700">
                      Industry
                    </Label>
                    <div className="flex items-center gap-2">
                      {companyForm.company_industry && (
                        <button 
                          type="button"
                          onClick={() => setCompanyForm(prev => ({ ...prev, company_industry: '' }))}
                          className="text-xs text-red-500 hover:text-red-700"
                        >
                          Clear
                        </button>
                      )}
                      {!progress.company_industry && (
                        <span className="text-xs text-emerald-600 font-medium">earn 20 pts</span>
                      )}
                    </div>
                  </div>
                  <select 
                    id="company_industry"
                    value={companyForm.company_industry}
                    onChange={(e) => setCompanyForm(prev => ({ ...prev, company_industry: e.target.value }))}
                    className="h-12 w-full px-4 border border-slate-200 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 bg-white text-slate-700"
                  >
                    <option value="">Select Industry</option>
                    {industryOptions.map((industry) => (
                      <option key={industry} value={industry}>{industry}</option>
                    ))}
                  </select>
                </div>
                
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="company_location" className="text-sm font-medium text-slate-700">
                      Location
                    </Label>
                    {companyForm.company_location && (
                      <button 
                        type="button"
                        onClick={() => setCompanyForm(prev => ({ ...prev, company_location: '' }))}
                        className="text-xs text-red-500 hover:text-red-700"
                      >
                        Clear
                      </button>
                    )}
                  </div>
                  <Input
                    id="company_location"
                    value={companyForm.company_location}
                    onChange={(e) => setCompanyForm(prev => ({ ...prev, company_location: e.target.value }))}
                    placeholder="City, Province"
                    className="h-12 bg-white border-slate-200 focus:border-blue-500 focus:ring-blue-500/20"
                  />
                </div>
                
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="company_size" className="text-sm font-medium text-slate-700">
                      Company Size
                    </Label>
                    <div className="flex items-center gap-2">
                      {companyForm.company_size && (
                        <button 
                          type="button"
                          onClick={() => setCompanyForm(prev => ({ ...prev, company_size: '' }))}
                          className="text-xs text-red-500 hover:text-red-700"
                        >
                          Clear
                        </button>
                      )}
                      {!progress.company_size && (
                        <span className="text-xs text-emerald-600 font-medium">earn 10 pts</span>
                      )}
                    </div>
                  </div>
                  <select 
                    id="company_size"
                    value={companyForm.company_size}
                    onChange={(e) => setCompanyForm(prev => ({ ...prev, company_size: e.target.value }))}
                    className="h-12 w-full px-4 border border-slate-200 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 bg-white text-slate-700"
                  >
                    <option value="">Select company size</option>
                    {companySizeOptions.map((size) => (
                      <option key={size} value={size}>{size}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="company_description" className="text-sm font-medium text-slate-700">
                    Company Description <span className="text-slate-400 font-normal">(100+ chars)</span>
                  </Label>
                  <div className="flex items-center gap-2">
                    {companyForm.company_description && (
                      <button 
                        type="button"
                        onClick={() => setCompanyForm(prev => ({ ...prev, company_description: '' }))}
                        className="text-xs text-red-500 hover:text-red-700"
                      >
                        Clear
                      </button>
                    )}
                    {!progress.company_description && (
                      <span className="text-xs text-emerald-600 font-medium">earn 30 pts on completion</span>
                    )}
                  </div>
                </div>
                <Textarea
                  id="company_description"
                  value={companyForm.company_description}
                  onChange={(e) => setCompanyForm(prev => ({ ...prev, company_description: e.target.value }))}
                  placeholder="Tell candidates about your company, culture, mission, and what makes you unique..."
                  rows={6}
                  className="resize-none bg-white border-slate-200 focus:border-blue-500 focus:ring-blue-500/20"
                />
                <div className="flex justify-between text-sm">
                  <span className={`${companyForm.company_description.length >= 100 ? 'text-emerald-600' : 'text-slate-400'}`}>
                    {companyForm.company_description.length}/100 characters minimum
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between gap-4 pt-4 border-t border-slate-200">
                {!isEditing && (
                  <Button 
                    type="button" 
                    variant="outline"
                    onClick={() => setActiveStep(prev => Math.min(prev + 1, steps.length - 1))}
                    className="px-6"
                  >
                    Skip for Now
                  </Button>
                )}
                <div className="flex items-center gap-3 ml-auto">
                  {isEditing && (
                    <Button 
                      type="button" 
                      variant="outline"
                      onClick={() => {
                        setCompanyForm({...originalForm});
                        setIsEditing(false);
                      }}
                      className="px-6"
                    >
                      Cancel
                    </Button>
                  )}
                  <Button 
                    type="submit" 
                    disabled={loading}
                    className="bg-blue-600 hover:bg-blue-700 px-8 h-11"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Saving...
                      </>
                    ) : (
                      <>
                        <Save className="w-4 h-4 mr-2" />
                        {isEditing ? 'Save Changes' : 'Save Company Info'}
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </form>
          </div>
        );

      case 'branding':
        return (
          <div className="space-y-8">
            <div>
              <h2 className="text-2xl font-semibold text-slate-800 mb-2">Company Branding</h2>
              <p className="text-slate-500">Upload your logo and cover image to stand out</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {/* Logo Upload */}
              <Card className="border border-slate-200 shadow-sm">
                <CardHeader className="pb-4">
                  <CardTitle className="text-base font-medium flex items-center justify-between">
                    <span>Company Logo</span>
                    {!progress.company_logo && (
                      <span className="text-xs text-emerald-600 font-medium">+15 pts</span>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-col items-center">
                    <div className="w-32 h-32 bg-slate-100 rounded-xl flex items-center justify-center overflow-hidden mb-4 border-2 border-dashed border-slate-300">
                      {companyForm.company_logo_url ? (
                        <img 
                          src={getImageUrl(companyForm.company_logo_url)} 
                          alt="Logo" 
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <Building2 className="w-12 h-12 text-slate-400" />
                      )}
                    </div>
                    <input
                      id="logo-upload"
                      type="file"
                      accept="image/*"
                      onChange={(e) => e.target.files[0] && handleImageUpload(e.target.files[0], 'logo')}
                      className="hidden"
                    />
                    <Button
                      variant="outline"
                      onClick={() => document.getElementById('logo-upload').click()}
                      disabled={uploadingImage === 'logo'}
                      className="w-full"
                    >
                      {uploadingImage === 'logo' ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Uploading...
                        </>
                      ) : (
                        <>
                          <Upload className="w-4 h-4 mr-2" />
                          {companyForm.company_logo_url ? 'Change Logo' : 'Upload Logo'}
                        </>
                      )}
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Cover Image Upload */}
              <Card className="border border-slate-200 shadow-sm">
                <CardHeader className="pb-4">
                  <CardTitle className="text-base font-medium flex items-center justify-between">
                    <span>Cover Image</span>
                    {!progress.company_cover && (
                      <span className="text-xs text-emerald-600 font-medium">+10 pts</span>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-col items-center">
                    <div className="w-full h-32 bg-slate-100 rounded-xl flex items-center justify-center overflow-hidden mb-4 border-2 border-dashed border-slate-300">
                      {companyForm.company_cover_image_url ? (
                        <img 
                          src={getImageUrl(companyForm.company_cover_image_url)} 
                          alt="Cover" 
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <Image className="w-12 h-12 text-slate-400" />
                      )}
                    </div>
                    <input
                      id="cover-upload"
                      type="file"
                      accept="image/*"
                      onChange={(e) => e.target.files[0] && handleImageUpload(e.target.files[0], 'cover')}
                      className="hidden"
                    />
                    <Button
                      variant="outline"
                      onClick={() => document.getElementById('cover-upload').click()}
                      disabled={uploadingImage === 'cover'}
                      className="w-full"
                    >
                      {uploadingImage === 'cover' ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Uploading...
                        </>
                      ) : (
                        <>
                          <Upload className="w-4 h-4 mr-2" />
                          {companyForm.company_cover_image_url ? 'Change Cover' : 'Upload Cover'}
                        </>
                      )}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="flex justify-end pt-4">
              <Button 
                onClick={() => setActiveStep(prev => Math.min(prev + 1, steps.length - 1))}
                className="bg-blue-600 hover:bg-blue-700 px-8"
              >
                Continue
                <ChevronRight className="w-4 h-4 ml-2" />
              </Button>
            </div>
          </div>
        );

      case 'links':
        // Check if links have any data saved
        const hasLinksData = companyForm.company_website || companyForm.company_linkedin;
        
        // If there's data and not editing, show the view mode
        if (hasLinksData && !isEditing) {
          return (
            <div className="space-y-8">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-semibold text-slate-800 mb-2">Company Links</h2>
                  <p className="text-slate-500">Your company's online presence</p>
                </div>
                <Button 
                  onClick={() => {
                    setOriginalForm({...companyForm});
                    setIsEditing(true);
                  }}
                  variant="outline"
                  className="flex items-center gap-2"
                >
                  <Edit2 className="w-4 h-4" />
                  Edit Links
                </Button>
              </div>
              
              {/* Display saved links */}
              <div className="space-y-4">
                {companyForm.company_website && (
                  <div className="p-4 bg-slate-50 rounded-lg">
                    <label className="text-xs font-medium text-slate-500 uppercase tracking-wider flex items-center">
                      <Globe className="w-3 h-3 mr-1" />
                      Website
                    </label>
                    <a 
                      href={companyForm.company_website} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-lg font-medium text-blue-600 hover:text-blue-700 hover:underline mt-1 block"
                    >
                      {companyForm.company_website}
                    </a>
                  </div>
                )}
                
                {companyForm.company_linkedin && (
                  <div className="p-4 bg-slate-50 rounded-lg">
                    <label className="text-xs font-medium text-slate-500 uppercase tracking-wider flex items-center">
                      <Linkedin className="w-3 h-3 mr-1" />
                      LinkedIn
                    </label>
                    <a 
                      href={companyForm.company_linkedin} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-lg font-medium text-blue-600 hover:text-blue-700 hover:underline mt-1 block"
                    >
                      {companyForm.company_linkedin}
                    </a>
                  </div>
                )}
                
                {!companyForm.company_website && (
                  <div className="p-4 bg-slate-50 rounded-lg">
                    <label className="text-xs font-medium text-slate-500 uppercase tracking-wider flex items-center">
                      <Globe className="w-3 h-3 mr-1" />
                      Website
                    </label>
                    <p className="text-slate-400 mt-1">Not set</p>
                  </div>
                )}
                
                {!companyForm.company_linkedin && (
                  <div className="p-4 bg-slate-50 rounded-lg">
                    <label className="text-xs font-medium text-slate-500 uppercase tracking-wider flex items-center">
                      <Linkedin className="w-3 h-3 mr-1" />
                      LinkedIn
                    </label>
                    <p className="text-slate-400 mt-1">Not set</p>
                  </div>
                )}
              </div>

              {/* Quick Actions */}
              <div className="flex items-center gap-4 pt-4 border-t border-slate-200">
                <Button 
                  variant="outline"
                  onClick={() => setActiveStep(3)}
                  className="flex items-center gap-2"
                >
                  Next: Structure
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
            </div>
          );
        }
        
        // Edit mode / Initial setup
        return (
          <div className="space-y-8">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-semibold text-slate-800 mb-2">
                  {isEditing ? 'Edit Company Links' : 'Company Links'}
                </h2>
                <p className="text-slate-500">Add your website and social profiles</p>
              </div>
              {isEditing && (
                <Button 
                  variant="ghost"
                  onClick={() => {
                    setCompanyForm({...originalForm});
                    setIsEditing(false);
                  }}
                  className="text-slate-600"
                >
                  <X className="w-4 h-4 mr-2" />
                  Cancel
                </Button>
              )}
            </div>
            
            <form onSubmit={handleCompanySubmit} className="space-y-6">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="company_website" className="text-sm font-medium text-slate-700 flex items-center">
                    <Globe className="w-4 h-4 mr-2 text-slate-400" />
                    Company Website
                  </Label>
                  <div className="flex items-center gap-2">
                    {companyForm.company_website && (
                      <button 
                        type="button"
                        onClick={() => setCompanyForm(prev => ({ ...prev, company_website: '' }))}
                        className="text-xs text-red-500 hover:text-red-700"
                      >
                        Clear
                      </button>
                    )}
                    {!progress.company_website && (
                      <span className="text-xs text-emerald-600 font-medium">+10 pts</span>
                    )}
                  </div>
                </div>
                <Input
                  id="company_website"
                  type="url"
                  value={companyForm.company_website}
                  onChange={(e) => setCompanyForm(prev => ({ ...prev, company_website: e.target.value }))}
                  placeholder="https://www.yourcompany.com"
                  className="h-12 bg-white border-slate-200"
                />
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="company_linkedin" className="text-sm font-medium text-slate-700 flex items-center">
                    <Linkedin className="w-4 h-4 mr-2 text-slate-400" />
                    LinkedIn Page
                  </Label>
                  <div className="flex items-center gap-2">
                    {companyForm.company_linkedin && (
                      <button 
                        type="button"
                        onClick={() => setCompanyForm(prev => ({ ...prev, company_linkedin: '' }))}
                        className="text-xs text-red-500 hover:text-red-700"
                      >
                        Clear
                      </button>
                    )}
                    {!progress.company_linkedin && (
                      <span className="text-xs text-emerald-600 font-medium">+5 pts</span>
                    )}
                  </div>
                </div>
                <Input
                  id="company_linkedin"
                  type="url"
                  value={companyForm.company_linkedin}
                  onChange={(e) => setCompanyForm(prev => ({ ...prev, company_linkedin: e.target.value }))}
                  placeholder="https://linkedin.com/company/yourcompany"
                  className="h-12 bg-white border-slate-200"
                />
              </div>

              <div className="flex items-center justify-between gap-4 pt-4 border-t border-slate-200">
                {!isEditing && (
                  <Button 
                    type="button" 
                    variant="outline"
                    onClick={() => setActiveStep(prev => Math.min(prev + 1, steps.length - 1))}
                    className="px-6"
                  >
                    Skip for Now
                  </Button>
                )}
                <div className="flex items-center gap-3 ml-auto">
                  {isEditing && (
                    <Button 
                      type="button" 
                      variant="outline"
                      onClick={() => {
                        setCompanyForm({...originalForm});
                        setIsEditing(false);
                      }}
                      className="px-6"
                    >
                      Cancel
                    </Button>
                  )}
                  <Button 
                    type="submit" 
                    disabled={loading}
                    className="bg-blue-600 hover:bg-blue-700 px-8"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Saving...
                      </>
                    ) : (
                      <>
                        <Save className="w-4 h-4 mr-2" />
                        {isEditing ? 'Save Changes' : 'Save Links'}
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </form>
          </div>
        );

      case 'structure':
        return (
          <div className="space-y-8">
            <div>
              <h2 className="text-2xl font-semibold text-slate-800 mb-2">Company Structure</h2>
              <p className="text-slate-500">Manage your team and hierarchy</p>
            </div>
            <CompanyStructure user={profile} onUpdate={fetchCurrentUser} />
          </div>
        );

      case 'packages':
        return (
          <div className="space-y-8">
            <div>
              <h2 className="text-2xl font-semibold text-slate-800 mb-2">Packages & Credits</h2>
              <p className="text-slate-500">Manage your subscription and credits</p>
            </div>
            <PackageManagement 
              user={profile}
              onUpdate={fetchCurrentUser}
              showFullManagement={true}
            />
          </div>
        );

      case 'jobs':
        return (
          <div className="space-y-8">
            <div>
              <h2 className="text-2xl font-semibold text-slate-800 mb-2">Job Listings</h2>
              <p className="text-slate-500">Create and manage your job postings</p>
            </div>
            <JobPosting 
              user={profile}
              onUpdate={fetchCurrentUser}
            />
          </div>
        );

      case 'applications':
        return (
          <div className="space-y-8">
            <div>
              <h2 className="text-2xl font-semibold text-slate-800 mb-2">Applications</h2>
              <p className="text-slate-500">Review and manage candidate applications</p>
            </div>
            <ApplicationManagement 
              user={profile}
              onUpdate={fetchCurrentUser}
            />
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Compact Header with Progress Bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-2xl font-semibold text-slate-800">
                Set Up Your Company Profile to Attract Talent
              </h1>
            </div>
            <div className="hidden sm:flex items-center gap-3">
              <span className="text-sm text-slate-500">Profile Score</span>
              <div className="flex items-center gap-2">
                <div className="w-32 h-2 bg-slate-200 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-blue-500 to-emerald-500 rounded-full transition-all duration-500"
                    style={{ width: `${progressPercentage}%` }}
                  />
                </div>
                <span className="text-sm font-semibold text-slate-700">{progressPercentage}/100</span>
              </div>
            </div>
          </div>
          
          {/* Mobile Progress */}
          <div className="sm:hidden mb-4">
            <div className="flex items-center gap-2">
              <div className="flex-1 h-2 bg-slate-200 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-blue-500 to-emerald-500 rounded-full transition-all duration-500"
                  style={{ width: `${progressPercentage}%` }}
                />
              </div>
              <span className="text-sm font-semibold text-slate-700">{progressPercentage}/100</span>
            </div>
          </div>
        </div>

        {/* Two Column Layout */}
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Left Sidebar - Navigation & Context */}
          <div className="lg:w-72 flex-shrink-0">
            {/* Company Card */}
            <Card className="bg-white border-0 shadow-sm mb-6">
              <CardContent className="p-6">
                <div className="text-center mb-4">
                  <div className="relative inline-block mb-3">
                    <div className="w-20 h-20 bg-slate-100 rounded-2xl flex items-center justify-center overflow-hidden">
                      {companyForm.company_logo_url ? (
                        <img 
                          src={getImageUrl(companyForm.company_logo_url)} 
                          alt="Logo" 
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <Building2 className="w-10 h-10 text-slate-400" />
                      )}
                    </div>
                  </div>
                  <h3 className="font-semibold text-slate-800">
                    {companyForm.company_name || 'Your Company'}
                  </h3>
                  <p className="text-sm text-slate-500">Recruiter Dashboard</p>
                </div>

                <div className="space-y-3 text-sm">
                  <div className="flex justify-between items-center py-2 border-b border-slate-100">
                    <span className="text-slate-500">Profile Score</span>
                    <span className="font-semibold text-slate-700">{progressPercentage}/100</span>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-slate-100">
                    <span className="text-slate-500">Company Size</span>
                    <span className="text-slate-700">{companyForm.company_size || 'Not set'}</span>
                  </div>
                  <div className="flex justify-between items-center py-2">
                    <span className="text-slate-500">Jobs Posted</span>
                    <span className="text-slate-700">{progress.first_job_posted ? '1+' : '0'} jobs</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Vertical Stepper */}
            <Card className="bg-white border-0 shadow-sm">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-slate-500 uppercase tracking-wider">
                  Profile Completion
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-0">
                <nav className="space-y-1">
                  {steps.map((step, index) => {
                    const Icon = step.icon;
                    const isActive = index === activeStep;
                    const isPast = index < activeStep;
                    
                    return (
                      <button
                        key={step.id}
                        onClick={() => setActiveStep(index)}
                        className={`w-full flex items-center gap-3 px-3 py-3 rounded-lg text-left transition-all ${
                          isActive 
                            ? 'bg-blue-50 text-blue-700' 
                            : 'hover:bg-slate-50 text-slate-600'
                        }`}
                      >
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                          step.isComplete
                            ? 'bg-emerald-100 text-emerald-600'
                            : isActive
                              ? 'bg-blue-100 text-blue-600'
                              : 'bg-slate-100 text-slate-400'
                        }`}>
                          {step.isComplete ? (
                            <Check className="w-4 h-4" />
                          ) : (
                            <span className="text-xs font-semibold">{index + 1}</span>
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className={`text-sm font-medium truncate ${
                            isActive ? 'text-blue-700' : 'text-slate-700'
                          }`}>
                            {step.label}
                          </p>
                          <p className="text-xs text-slate-400">
                            {step.isComplete ? 'Complete' : isActive ? 'In Progress' : 'Next'}
                          </p>
                        </div>
                        {step.isComplete && (
                          <Check className="w-4 h-4 text-emerald-500 flex-shrink-0" />
                        )}
                      </button>
                    );
                  })}
                </nav>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Main Content Area */}
          <div className="flex-1 min-w-0">
            <Card className="bg-white border-0 shadow-sm">
              <CardContent className="p-8">
                {renderStepContent()}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RecruiterDashboard;
