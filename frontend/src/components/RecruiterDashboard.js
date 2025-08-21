import React, { useState, useEffect } from 'react';
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Textarea } from "./ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Label } from "./ui/label";
import TrophyProgress from './TrophyProgress';
import CompanyStructure from './CompanyStructure';
import JobPosting from './JobPosting';
import ApplicationManagement from './ApplicationManagement';
import PackageManagement from './PackageManagement';
import { 
  Building2, 
  Globe, 
  Linkedin, 
  Users, 
  Camera,
  Upload,
  Save,
  Briefcase,
  Plus,
  Star,
  MapPin,
  Calendar,
  Target,
  Zap,
  Image,
  Link,
  Award,
  FileText,
  CreditCard
} from "lucide-react";
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Helper function to get full image URL
const getImageUrl = (imageUrl) => {
  if (!imageUrl) return '';
  if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
    return imageUrl; // Already a full URL
  }
  if (imageUrl.startsWith('/uploads/')) {
    return `${BACKEND_URL}${imageUrl}`; // Prepend backend URL to relative paths
  }
  return imageUrl; // Return as-is for other cases
};

const RecruiterDashboard = ({ user, onUpdateUser }) => {
  const [profile, setProfile] = useState(user);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [progress, setProgress] = useState(user.recruiter_progress || {});
  const [uploadingImage, setUploadingImage] = useState(null);
  
  // Form states
  const [companyForm, setCompanyForm] = useState({
    company_name: user.company_profile?.company_name || '',
    company_description: user.company_profile?.company_description || '',
    company_website: user.company_profile?.company_website || '',
    company_linkedin: user.company_profile?.company_linkedin || '',
    company_size: user.company_profile?.company_size || '',
    company_industry: user.company_profile?.company_industry || '',
    company_location: user.company_profile?.company_location || '',
    company_logo_url: user.company_profile?.company_logo_url || '',
    company_cover_image_url: user.company_profile?.company_cover_image_url || ''
  });

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
      onUpdateUser(response.data);
    } catch (error) {
      console.error('Error fetching user data:', error);
    }
  };

  const handleImageUpload = async (file, imageType) => {
    if (!file) return;

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      alert('Please upload a JPEG, PNG, or WebP image file.');
      return;
    }

    // Validate file size (10MB max)
    if (file.size > 10 * 1024 * 1024) {
      alert('File size must be less than 10MB.');
      return;
    }

    try {
      setUploadingImage(imageType);
      
      const formData = new FormData();
      formData.append('file', file);
      formData.append('image_type', imageType);

      const response = await axios.post(`${API}/upload-image`, formData, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      // Update the appropriate field based on image type
      const fieldMap = {
        'logo': 'company_logo_url',
        'cover': 'company_cover_image_url'
      };

      const fieldName = fieldMap[imageType];
      if (fieldName) {
        setCompanyForm(prev => ({
          ...prev,
          [fieldName]: response.data.file_url
        }));

        // Auto-save the uploaded image
        await updateCompanyProfile({ [fieldName]: response.data.file_url });
      }

    } catch (error) {
      console.error('Error uploading image:', error);
      alert(error.response?.data?.detail || 'Failed to upload image');
    } finally {
      setUploadingImage(null);
    }
  };

  const updateCompanyProfile = async (updates) => {
    try {
      setLoading(true);
      await axios.put(`${API}/profile/company`, updates, getAuthHeaders());
      await fetchCurrentUser();
    } catch (error) {
      console.error('Error updating company profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCompanySubmit = async (e) => {
    e.preventDefault();
    await updateCompanyProfile(companyForm);
  };

  const onProfileComplete = () => {
    // Trigger completion celebration for recruiter
    console.log('Company profile completed! 🚀');
  };

  useEffect(() => {
    fetchCurrentUser();
  }, []);

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

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 relative">
      {/* Background tech grid pattern */}
      <div className="absolute inset-0 opacity-5 tech-grid"></div>
      
      <div className="max-w-7xl mx-auto px-6 lg:px-8 py-8 relative z-10">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-slate-800 mb-2">
                Welcome back, {profile.first_name}! 👔
              </h1>
              <p className="text-slate-600 text-lg">
                Complete your company profile to start attracting top talent
              </p>
            </div>
            <div className="hidden lg:block">
              <TrophyProgress 
                progress={progress} 
                onComplete={onProfileComplete}
                showDetails={false}
                userRole="recruiter"
              />
            </div>
          </div>
        </div>

        {/* Mobile Trophy Progress */}
        <div className="lg:hidden mb-8">
          <TrophyProgress 
            progress={progress} 
            onComplete={onProfileComplete}
            showDetails={false}
            userRole="recruiter"
          />
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar - Company Overview */}
          <div className="lg:col-span-1">
            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
              <CardContent className="p-6">
                <div className="text-center mb-6">
                  <div className="relative inline-block mb-4">
                    <div className="w-24 h-24 bg-gradient-to-br from-blue-100 to-slate-200 rounded-2xl flex items-center justify-center overflow-hidden">
                      {companyForm.company_logo_url ? (
                        <img 
                          src={getImageUrl(companyForm.company_logo_url)} 
                          alt="Company Logo" 
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            e.target.style.display = 'none';
                          }}
                        />
                      ) : (
                        <Building2 className="w-12 h-12 text-slate-400" />
                      )}
                    </div>
                    <Button
                      size="sm"
                      className="absolute -bottom-2 -right-2 w-8 h-8 rounded-full p-0"
                      onClick={() => document.getElementById('logo-upload-overview').click()}
                      disabled={uploadingImage === 'logo'}
                    >
                      {uploadingImage === 'logo' ? (
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      ) : (
                        <Camera className="w-4 h-4" />
                      )}
                    </Button>
                    <input
                      id="logo-upload-overview"
                      type="file"
                      accept="image/*"
                      onChange={(e) => e.target.files[0] && handleImageUpload(e.target.files[0], 'logo')}
                      className="hidden"
                    />
                  </div>
                  <h3 className="font-bold text-slate-800 text-lg">
                    {companyForm.company_name || 'Your Company'}
                  </h3>
                  <p className="text-slate-600 text-sm">Recruiter Dashboard</p>
                  {companyForm.company_location && (
                    <div className="flex items-center justify-center space-x-1 text-slate-500 text-sm mt-2">
                      <MapPin className="w-4 h-4" />
                      <span>{companyForm.company_location}</span>
                    </div>
                  )}
                </div>

                {/* Quick Stats */}
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-600 text-sm">Profile Score</span>
                    <Badge className="bg-blue-100 text-blue-800">
                      {progress.total_points || 0}/100
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-600 text-sm">Company Size</span>
                    <Badge variant="outline">
                      {companyForm.company_size || 'Not set'}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-600 text-sm">Jobs Posted</span>
                    <Badge variant="outline">
                      {progress.first_job_posted ? '1+' : '0'} jobs
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Main Company Profile Tabs */}
          <div className="lg:col-span-3">
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="grid w-full grid-cols-7 bg-white/80 backdrop-blur-sm">
                <TabsTrigger value="overview" className="flex items-center space-x-1">
                  <Building2 className="w-4 h-4" />
                  <span className="hidden sm:inline">Company</span>
                </TabsTrigger>
                <TabsTrigger value="branding" className="flex items-center space-x-1">
                  <Image className="w-4 h-4" />
                  <span className="hidden sm:inline">Branding</span>
                </TabsTrigger>
                <TabsTrigger value="links" className="flex items-center space-x-1">
                  <Link className="w-4 h-4" />
                  <span className="hidden sm:inline">Links</span>
                </TabsTrigger>
                <TabsTrigger value="structure" className="flex items-center space-x-1">
                  <Users className="w-4 h-4" />
                  <span className="hidden sm:inline">Structure</span>
                </TabsTrigger>
                <TabsTrigger value="packages" className="flex items-center space-x-1">
                  <CreditCard className="w-4 h-4" />
                  <span className="hidden sm:inline">Packages</span>
                </TabsTrigger>
                <TabsTrigger value="jobs" className="flex items-center space-x-1">
                  <Briefcase className="w-4 h-4" />
                  <span className="hidden sm:inline">Jobs</span>
                </TabsTrigger>
                <TabsTrigger value="applications" className="flex items-center space-x-1">
                  <FileText className="w-4 h-4" />
                  <span className="hidden sm:inline">Applications</span>
                </TabsTrigger>
              </TabsList>

              {/* Company Overview Tab */}
              <TabsContent value="overview" className="space-y-6 mt-6">
                <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Building2 className="w-5 h-5 text-blue-600" />
                      <span>Company Information</span>
                      {!progress.company_description && (
                        <Badge className="bg-yellow-100 text-yellow-800 text-xs">
                          +20 points (100+ chars)
                        </Badge>
                      )}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <form onSubmit={handleCompanySubmit} className="space-y-6">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-2">
                          <Label htmlFor="company_name">Company Name</Label>
                          <Input
                            id="company_name"
                            value={companyForm.company_name}
                            onChange={(e) => setCompanyForm(prev => ({ ...prev, company_name: e.target.value }))}
                            placeholder="Your Company Name"
                            className="h-12"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="company_location">Location</Label>
                          <Input
                            id="company_location"
                            value={companyForm.company_location}
                            onChange={(e) => setCompanyForm(prev => ({ ...prev, company_location: e.target.value }))}
                            placeholder="City, Province"
                            className="h-12"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="company_industry">Industry</Label>
                          <select 
                            id="company_industry"
                            value={companyForm.company_industry}
                            onChange={(e) => setCompanyForm(prev => ({ ...prev, company_industry: e.target.value }))}
                            className="h-12 w-full px-3 border border-slate-300 rounded-md focus:border-blue-500 focus:ring-blue-500 bg-white"
                          >
                            <option value="">Select industry</option>
                            {industryOptions.map((industry) => (
                              <option key={industry} value={industry}>
                                {industry}
                              </option>
                            ))}
                          </select>
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="company_size">Company Size</Label>
                          {!progress.company_size && (
                            <Badge className="bg-yellow-100 text-yellow-800 text-xs ml-2">
                              +10 points
                            </Badge>
                          )}
                          <select 
                            id="company_size"
                            value={companyForm.company_size}
                            onChange={(e) => setCompanyForm(prev => ({ ...prev, company_size: e.target.value }))}
                            className="h-12 w-full px-3 border border-slate-300 rounded-md focus:border-blue-500 focus:ring-blue-500 bg-white"
                          >
                            <option value="">Select company size</option>
                            {companySizeOptions.map((size) => (
                              <option key={size} value={size}>
                                {size}
                              </option>
                            ))}
                          </select>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="company_description">Company Description (100+ characters for points)</Label>
                        <Textarea
                          id="company_description"
                          value={companyForm.company_description}
                          onChange={(e) => setCompanyForm(prev => ({ ...prev, company_description: e.target.value }))}
                          placeholder="Tell candidates about your company culture, mission, and what makes you unique..."
                          rows={5}
                          className="resize-none"
                        />
                        <div className="text-sm text-slate-500">
                          {companyForm.company_description.length}/100 characters minimum
                        </div>
                      </div>

                      <Button 
                        type="submit" 
                        disabled={loading}
                        className="bg-gradient-to-r from-blue-600 to-slate-700 hover:from-blue-700 hover:to-slate-800"
                      >
                        {loading ? (
                          <div className="flex items-center space-x-2">
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                            <span>Saving...</span>
                          </div>
                        ) : (
                          <div className="flex items-center space-x-2">
                            <Save className="w-4 h-4" />
                            <span>Save Company Info</span>
                          </div>
                        )}
                      </Button>
                    </form>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Branding Tab */}
              <TabsContent value="branding" className="space-y-6 mt-6">
                <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Image className="w-5 h-5 text-blue-600" />
                      <span>Company Branding</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {/* Company Logo */}
                    <div className="space-y-4">
                      <div className="flex items-center space-x-2">
                        <Label htmlFor="company_logo">Company Logo</Label>
                        {!progress.company_logo && (
                          <Badge className="bg-yellow-100 text-yellow-800 text-xs">
                            +15 points
                          </Badge>
                        )}
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className="w-20 h-20 bg-gradient-to-br from-slate-100 to-slate-200 rounded-xl flex items-center justify-center">
                          {companyForm.company_logo_url ? (
                            <img 
                              src={companyForm.company_logo_url} 
                              alt="Company Logo" 
                              className="w-full h-full object-cover rounded-xl"
                            />
                          ) : (
                            <Building2 className="w-10 h-10 text-slate-400" />
                          )}
                        </div>
                        <div className="flex-1 space-y-3">
                          <div className="flex space-x-2">
                            <Input
                              id="company_logo"
                              value={companyForm.company_logo_url}
                              onChange={(e) => setCompanyForm(prev => ({ ...prev, company_logo_url: e.target.value }))}
                              placeholder="Enter logo URL or upload file"
                              className="h-12"
                            />
                            <Button 
                              type="button" 
                              variant="outline"
                              onClick={() => document.getElementById('logo-upload-branding').click()}
                              disabled={uploadingImage === 'logo'}
                            >
                              {uploadingImage === 'logo' ? (
                                <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                              ) : (
                                <Upload className="w-4 h-4" />
                              )}
                            </Button>
                          </div>
                          <Button 
                            type="button" 
                            variant="outline" 
                            onClick={() => updateCompanyProfile({ company_logo_url: companyForm.company_logo_url })}
                            className="w-full"
                          >
                            <Save className="w-4 h-4 mr-2" />
                            Update Logo URL
                          </Button>
                          <input
                            id="logo-upload-branding"
                            type="file"
                            accept="image/*"
                            onChange={(e) => e.target.files[0] && handleImageUpload(e.target.files[0], 'logo')}
                            className="hidden"
                          />
                        </div>
                      </div>
                    </div>

                    {/* Cover Image */}
                    <div className="space-y-4">
                      <div className="flex items-center space-x-2">
                        <Label htmlFor="company_cover">Cover Image</Label>
                        {!progress.cover_image && (
                          <Badge className="bg-yellow-100 text-yellow-800 text-xs">
                            +10 points
                          </Badge>
                        )}
                      </div>
                      <div className="space-y-4">
                        <div className="w-full h-32 bg-gradient-to-r from-slate-100 to-slate-200 rounded-xl overflow-hidden">
                          {companyForm.company_cover_image_url ? (
                            <img 
                              src={companyForm.company_cover_image_url} 
                              alt="Company Cover" 
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center">
                              <Image className="w-12 h-12 text-slate-400" />
                            </div>
                          )}
                        </div>
                        <div className="flex space-x-2">
                          <Input
                            id="company_cover"
                            value={companyForm.company_cover_image_url}
                            onChange={(e) => setCompanyForm(prev => ({ ...prev, company_cover_image_url: e.target.value }))}
                            placeholder="Enter cover image URL or upload file"
                            className="h-12"
                          />
                          <Button 
                            type="button" 
                            variant="outline"
                            onClick={() => document.getElementById('cover-upload-branding').click()}
                            disabled={uploadingImage === 'cover'}
                          >
                            {uploadingImage === 'cover' ? (
                              <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                            ) : (
                              <Upload className="w-4 h-4" />
                            )}
                          </Button>
                        </div>
                        <Button
                          type="button" 
                          variant="outline"
                          onClick={() => updateCompanyProfile({ company_cover_image_url: companyForm.company_cover_image_url })}
                          className="w-full"
                        >
                          <Save className="w-4 h-4 mr-2" />
                          Update Cover Image URL
                        </Button>
                        <input
                          id="cover-upload-branding"
                          type="file"
                          accept="image/*"
                          onChange={(e) => e.target.files[0] && handleImageUpload(e.target.files[0], 'cover')}
                          className="hidden"
                        />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Links Tab */}
              <TabsContent value="links" className="space-y-6 mt-6">
                <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Link className="w-5 h-5 text-blue-600" />
                      <span>Company Links</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="space-y-4">
                      <div className="flex items-center space-x-2">
                        <Label htmlFor="company_website">Website URL</Label>
                        {!progress.website_link && (
                          <Badge className="bg-yellow-100 text-yellow-800 text-xs">
                            +15 points
                          </Badge>
                        )}
                      </div>
                      <div className="relative">
                        <Globe className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
                        <Input
                          id="company_website"
                          value={companyForm.company_website}
                          onChange={(e) => setCompanyForm(prev => ({ ...prev, company_website: e.target.value }))}
                          placeholder="https://yourcompany.com"
                          className="pl-10 h-12"
                        />
                      </div>
                    </div>

                    <div className="space-y-4">
                      <div className="flex items-center space-x-2">
                        <Label htmlFor="company_linkedin">LinkedIn URL</Label>
                        {!progress.linkedin_link && (
                          <Badge className="bg-yellow-100 text-yellow-800 text-xs">
                            +10 points
                          </Badge>
                        )}
                      </div>
                      <div className="relative">
                        <Linkedin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
                        <Input
                          id="company_linkedin"
                          value={companyForm.company_linkedin}
                          onChange={(e) => setCompanyForm(prev => ({ ...prev, company_linkedin: e.target.value }))}
                          placeholder="https://linkedin.com/company/yourcompany"
                          className="pl-10 h-12"
                        />
                      </div>
                    </div>

                    <Button 
                      onClick={() => updateCompanyProfile({
                        company_website: companyForm.company_website,
                        company_linkedin: companyForm.company_linkedin
                      })}
                      className="bg-gradient-to-r from-blue-600 to-slate-700 hover:from-blue-700 hover:to-slate-800"
                    >
                      <Save className="w-4 h-4 mr-2" />
                      Save Links
                    </Button>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Company Structure Tab */}
              <TabsContent value="structure" className="space-y-6 mt-6">
                <CompanyStructure 
                  user={profile} 
                  onUpdateUser={fetchCurrentUser}
                />
              </TabsContent>

              {/* Packages Tab */}
              <TabsContent value="packages" className="space-y-6 mt-6">
                <PackageManagement 
                  user={profile}
                />
              </TabsContent>

              {/* Jobs Tab */}
              <TabsContent value="jobs" className="space-y-6 mt-6">
                <JobPosting 
                  user={profile} 
                  onUpdateUser={fetchCurrentUser}
                />
              </TabsContent>

              {/* Applications Tab */}
              <TabsContent value="applications" className="space-y-6 mt-6">
                <ApplicationManagement 
                  user={profile}
                />
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RecruiterDashboard;