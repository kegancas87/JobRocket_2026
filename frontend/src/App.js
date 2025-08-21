import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import { LoginPage, RegisterPage } from "./components/AuthPages";
import ProfileDashboard from "./components/ProfileDashboard";
import RecruiterDashboard from "./components/RecruiterDashboard";
import AdminDashboard from "./components/AdminDashboard";
import InvitationPage from "./components/InvitationPage";
import PricingPage from "./components/PricingPage";
import MyApplications from "./components/MyApplications";
import ApplicationManagement from "./components/ApplicationManagement";
import JobPosting from "./components/JobPosting";
import PackageManagement from "./components/PackageManagement";
import NotificationsPage from "./components/NotificationsPage";
import { ApplyButton } from "./components/EasyApply";
import JobDetailsModal from "./components/JobDetailsModal";
import Navigation from "./components/Navigation";
import Footer from "./components/Footer";
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import { Card, CardContent, CardHeader } from "./components/ui/card";
import { Badge } from "./components/ui/badge";
import { Separator } from "./components/ui/separator";
import { 
  Search, 
  MapPin, 
  Heart, 
  User, 
  ChevronDown,
  Calendar,
  Home,
  Briefcase,
  Building2,
  Filter,
  Rocket,
  Star,
  Clock,
  DollarSign,
  Users,
  Zap,
  Settings,
  LogOut
} from "lucide-react";

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

const JobCard = ({ job, user, onSave, onApply, onJobClick }) => {
  const formatPostedDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return '1 day ago';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 14) return '1 week ago';
    if (diffDays < 30) return `${Math.ceil(diffDays / 7)} weeks ago`;
    if (diffDays < 60) return '1 month ago';
    return `${Math.ceil(diffDays / 30)} months ago`;
  };

  const formatSalary = (salaryMin, salaryMax, currency = 'ZAR') => {
    if (!salaryMin && !salaryMax) return null;
    if (salaryMin && salaryMax) {
      return `${currency} ${salaryMin.toLocaleString()} - ${salaryMax.toLocaleString()}`;
    }
    if (salaryMin) return `${currency} ${salaryMin.toLocaleString()}+`;
    return `Up to ${currency} ${salaryMax.toLocaleString()}`;
  };

  const handleCardClick = () => {
    if (onJobClick) {
      onJobClick(job);
    }
  };

  const handleJobTitleClick = (e) => {
    e.stopPropagation();
    if (onJobClick) {
      onJobClick(job);
    }
  };

  return (
    <Card 
      className="group cursor-pointer hover:shadow-2xl transition-all duration-500 bg-white/80 backdrop-blur-sm border-0 hover:bg-white/90 relative overflow-hidden rocket-card"
      onClick={handleCardClick}
    >
      {/* Subtle tech grid pattern overlay */}
      <div className="absolute inset-0 opacity-5 tech-grid"></div>
      
      {/* Featured job glow effect */}
      {job.featured && (
        <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-transparent to-slate-500/10 pointer-events-none"></div>
      )}
      
      <CardContent className="p-8 relative z-10">
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-6 flex-1">
            <div className="w-20 h-20 rounded-2xl overflow-hidden bg-gradient-to-br from-slate-100 to-slate-200 flex-shrink-0 shadow-lg ring-2 ring-slate-200/50">
              <img 
                src={getImageUrl(job.logo_url)} 
                alt={`${job.company_name} logo`}
                className="w-full h-full object-cover"
                onError={(e) => {
                  e.target.src = 'https://images.unsplash.com/photo-1606211105533-0439bfecce21?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzZ8MHwxfHNlYXJjaHw0fHxtb2Rlcm4lMjB0ZWNobm9sb2d5fGVufDB8fHx8MTc1NTM1MzYzMXww&ixlib=rb-4.1.0&q=85&w=80&h=80';
                }}
              />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between mb-3">
                <h3 
                  className="text-2xl font-bold text-slate-800 group-hover:text-blue-700 transition-colors leading-tight cursor-pointer hover:underline"
                  onClick={handleJobTitleClick}
                >
                  {job.title}
                </h3>
                {job.featured && (
                  <div className="flex items-center space-x-1 bg-gradient-to-r from-blue-600 to-slate-700 text-white px-3 py-1 rounded-full text-xs font-semibold">
                    <Star className="w-3 h-3 fill-current" />
                    <span>Featured</span>
                  </div>
                )}
              </div>
              
              <div className="flex items-center space-x-6 text-slate-600 mb-4">
                <div className="flex items-center space-x-2">
                  <Building2 className="w-5 h-5 text-slate-500" />
                  <span className="font-medium">{job.company_name}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <MapPin className="w-5 h-5 text-slate-500" />
                  <span>{job.location}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Clock className="w-4 h-4 text-slate-500" />
                  <span className="text-sm">{formatPostedDate(job.posted_date)}</span>
                </div>
              </div>
              
              {job.salary && (
                <div className="flex items-center space-x-2 text-emerald-700 font-bold mb-4 bg-emerald-50 px-3 py-2 rounded-lg w-fit">
                  <DollarSign className="w-4 h-4" />
                  <span>{job.salary}</span>
                </div>
              )}
              
              <p className="text-slate-700 mb-6 leading-relaxed line-clamp-2">
                {job.description}
              </p>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Badge variant="secondary" className="bg-slate-100 text-slate-700 hover:bg-slate-200 px-3 py-1 font-medium">
                    {job.job_type}
                  </Badge>
                  <Badge className={`px-3 py-1 font-medium border-0 ${
                    job.work_type === 'Remote' ? 'bg-blue-100 text-blue-700 hover:bg-blue-200' :
                    job.work_type === 'Hybrid' ? 'bg-purple-100 text-purple-700 hover:bg-purple-200' :
                    'bg-green-100 text-green-700 hover:bg-green-200'
                  }`}>
                    {job.work_type === 'Remote' && <Zap className="w-3 h-3 mr-1" />}
                    {job.work_type}
                  </Badge>
                  <Badge variant="outline" className="border-slate-300 text-slate-600 px-3 py-1 font-medium">
                    {job.industry}
                  </Badge>
                </div>
                <ApplyButton 
                  job={job}
                  user={user}
                  onApplicationSuccess={(applicationData) => {
                    console.log('Application submitted:', applicationData);
                    // You can add any success handling here
                  }}
                />
              </div>
            </div>
          </div>
          <Button
            variant="ghost"
            size="lg"
            onClick={(e) => {
              e.stopPropagation();
              onSave(job.id);
            }}
            className="ml-6 hover:bg-red-50 hover:text-red-600 rounded-full p-3 transition-all duration-300"
          >
            <Heart className={`w-6 h-6 ${job.saved ? 'fill-red-500 text-red-500' : 'text-slate-400'}`} />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

const FilterSection = ({ title, children, defaultExpanded = true }) => {
  const [expanded, setExpanded] = useState(defaultExpanded);
  
  return (
    <div className="border-b border-slate-200 pb-6 mb-6">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center justify-between w-full text-left text-lg font-bold text-slate-800 mb-4 hover:text-blue-700 transition-colors"
      >
        {title}
        <ChevronDown className={`w-5 h-5 transition-transform duration-300 ${expanded ? 'rotate-180' : ''}`} />
      </button>
      {expanded && <div className="space-y-3">{children}</div>}
    </div>
  );
};

const FilterOption = ({ label, count, selected, onChange }) => (
  <label className="flex items-center justify-between cursor-pointer hover:bg-slate-50 p-3 rounded-xl transition-all duration-200">
    <div className="flex items-center space-x-3">
      <input
        type="checkbox"
        checked={selected}
        onChange={onChange}
        className="w-5 h-5 rounded border-2 border-slate-300 text-blue-600 focus:ring-blue-500 focus:ring-2"
      />
      <span className="font-medium text-slate-700">{label}</span>
    </div>
    {count && (
      <span className="text-xs text-slate-500 bg-slate-100 px-2 py-1 rounded-full font-semibold">
        {count}
      </span>
    )}
  </label>
);

const JobListingPage = ({ user, onLogout }) => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [location, setLocation] = useState("");
  const [filters, setFilters] = useState({
    datePosted: { newJobs: false, lastWeek: false },
    workFromHome: { partiallyRemote: false, fullyRemote: false },
    applicationMethod: { onCompanyWebsite: false, easyApply: false },
    functions: {
      engineering: false,
      production: false,
      itTelecom: false,
      salesPurchasing: false,
      accounting: false,
      banking: false
    }
  });
  
  // Job details modal state
  const [selectedJob, setSelectedJob] = useState(null);
  const [showJobDetails, setShowJobDetails] = useState(false);

  const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    return {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    };
  };

  // Fetch jobs from API
  const fetchJobs = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);
      if (location) params.append('location', location);
      
      const response = await axios.get(`${API}/public/jobs?${params.toString()}`);
      setJobs(response.data);
    } catch (error) {
      console.error('Error fetching jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      fetchJobs();
    }, 500);
    return () => clearTimeout(timeoutId);
  }, [searchTerm, location]);

  const handleSaveJob = (jobId) => {
    setJobs(jobs.map(job => 
      job.id === jobId ? { ...job, saved: !job.saved } : job
    ));
  };

  const handleApplyToJob = async (jobId) => {
    try {
      await axios.post(`${API}/profile/job-application/${jobId}`, {}, getAuthHeaders());
      // Show success message or redirect to application
      console.log('Job application tracked!');
    } catch (error) {
      console.error('Error applying to job:', error);
    }
  };

  const handleJobClick = (job) => {
    setSelectedJob(job);
    setShowJobDetails(true);
  };

  const handleCloseJobDetails = () => {
    setShowJobDetails(false);
    setSelectedJob(null);
  };

  const handleApplicationSuccess = (applicationData) => {
    console.log('Application submitted:', applicationData);
    // You can add any success handling here
    handleCloseJobDetails();
  };

  const filteredJobs = jobs.filter(job => {
    const matchesSearch = job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         job.company_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesLocation = !location || job.location.toLowerCase().includes(location.toLowerCase());
    return matchesSearch && matchesLocation;
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 flex items-center justify-center relative overflow-hidden">
        {/* Background tech pattern */}
        <div className="absolute inset-0 opacity-5 tech-grid"></div>
        
        <div className="text-center relative z-10">
          <div className="relative mb-8">
            <div className="animate-spin rounded-full h-24 w-24 border-4 border-slate-200 border-t-blue-600 mx-auto"></div>
            <Rocket className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-8 h-8 text-blue-600" />
          </div>
          <h3 className="text-2xl font-bold text-slate-800 mb-2">Job Rocket Loading...</h3>
          <p className="text-slate-600">Searching the galaxy for amazing opportunities</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 relative">
      {/* Background tech grid pattern */}
      <div className="absolute inset-0 opacity-5 tech-grid"></div>
      
      {/* Hero Search Section */}
      <div 
        className="relative py-24 overflow-hidden"
        style={{
          backgroundImage: `linear-gradient(135deg, rgba(15, 23, 42, 0.8), rgba(30, 64, 175, 0.7)), url('https://images.unsplash.com/photo-1541185933-ef5d8ed016c2?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwyfHxyb2NrZXQlMjBsYXVuY2h8ZW58MHx8fHwxNzU1MzUzNjI2fDA&ixlib=rb-4.1.0&q=85')`,
          backgroundSize: 'cover',
          backgroundPosition: 'center'
        }}
      >
        {/* Animated particles/stars effect */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="stars"></div>
        </div>
        
        <div className="max-w-5xl mx-auto px-6 lg:px-8 text-center relative z-10">
          <div className="mb-8">
            <h2 className="text-6xl font-black text-white mb-4 tracking-tight">
              Launch Your 
              <span className="bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent block">
                Dream Career
              </span>
            </h2>
            <p className="text-xl text-slate-300 max-w-2xl mx-auto leading-relaxed">
              Discover opportunities that propel your career to new heights with South Africa's most innovative job platform
            </p>
          </div>
          
          <div className="flex flex-col lg:flex-row gap-4 max-w-4xl mx-auto">
            <div className="relative flex-1">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-slate-400 w-6 h-6" />
              <Input
                type="text"
                placeholder="Job title, keywords, or company"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-12 h-16 text-lg font-medium bg-white/90 backdrop-blur-sm border-0 shadow-2xl rounded-2xl focus:ring-4 focus:ring-blue-500/30 focus:bg-white transition-all"
              />
            </div>
            <div className="relative flex-1">
              <MapPin className="absolute left-4 top-1/2 transform -translate-y-1/2 text-slate-400 w-6 h-6" />
              <Input
                type="text"
                placeholder="City, province, or remote"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="pl-12 h-16 text-lg font-medium bg-white/90 backdrop-blur-sm border-0 shadow-2xl rounded-2xl focus:ring-4 focus:ring-blue-500/30 focus:bg-white transition-all"
              />
            </div>
            <Button className="bg-gradient-to-r from-blue-600 to-slate-700 hover:from-blue-700 hover:to-slate-800 h-16 px-12 text-lg font-bold shadow-2xl rounded-2xl hover:shadow-3xl transform hover:scale-105 transition-all duration-300">
              <Rocket className="w-6 h-6 mr-3" />
              Launch Search
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 lg:px-8 py-12 relative z-10">
        <div className="flex gap-12">
          {/* Filters Sidebar */}
          <div className="w-96 flex-shrink-0">
            <div className="bg-white/80 backdrop-blur-sm rounded-3xl shadow-xl p-8 sticky top-32 border border-slate-200/50">
              <div className="flex items-center space-x-3 mb-8">
                <Filter className="w-6 h-6 text-blue-600" />
                <h3 className="text-2xl font-bold text-slate-800">Filters</h3>
              </div>

              <FilterSection title="Date Posted" defaultExpanded={true}>
                <FilterOption label="New jobs" count="14" />
                <FilterOption label="Last week" count="147" />
              </FilterSection>

              <FilterSection title="Work From Home" defaultExpanded={true}>
                <FilterOption label="Partially remote" count="17" />
                <FilterOption label="Fully remote" count="4" />
              </FilterSection>

              <FilterSection title="Application Method" defaultExpanded={true}>
                <FilterOption label="On company website" count="220" />
                <FilterOption label="Easy Apply" count="130" />
              </FilterSection>

              <FilterSection title="Functions" defaultExpanded={true}>
                <FilterOption label="Engineering, Technical" count="100" />
                <FilterOption label="Production & Manufacturing" />
                <FilterOption label="IT & Telecommunications" count="47" />
                <FilterOption label="Sales & Purchasing" count="36" />
                <FilterOption label="Accounting, Auditing" count="33" />
                <FilterOption label="Banking, Finance" count="26" />
              </FilterSection>
            </div>
          </div>

          {/* Job Listings */}
          <div className="flex-1">
            <div className="mb-8 flex items-center justify-between">
              <div>
                <h2 className="text-4xl font-bold text-slate-800 mb-2">
                  {filteredJobs.length} Opportunities Found
                </h2>
                <p className="text-slate-600 text-lg">
                  {searchTerm || location ? `Results for ${searchTerm || 'all jobs'}${location ? ` in ${location}` : ''}` : 'All active positions'}
                </p>
              </div>
              <div className="flex items-center space-x-3">
                <span className="text-slate-600 font-medium">Sort by:</span>
                <Button variant="outline" className="flex items-center space-x-2 border-slate-300 hover:bg-slate-50">
                  <span>Relevance</span>
                  <ChevronDown className="w-4 h-4" />
                </Button>
              </div>
            </div>

            <div className="space-y-6">
              {filteredJobs.map((job) => (
                <JobCard 
                  key={job.id} 
                  job={job} 
                  user={user}
                  onSave={handleSaveJob}
                  onApply={handleApplyToJob}
                  onJobClick={handleJobClick}
                />
              ))}
            </div>

            {filteredJobs.length === 0 && (
              <div className="text-center py-24">
                <div className="mb-8">
                  <div className="w-32 h-32 bg-gradient-to-br from-slate-100 to-slate-200 rounded-full flex items-center justify-center mx-auto mb-6">
                    <Search className="w-16 h-16 text-slate-400" />
                  </div>
                  <h3 className="text-3xl font-bold text-slate-800 mb-4">No Jobs Found</h3>
                  <p className="text-xl text-slate-600 max-w-md mx-auto">
                    Try adjusting your search criteria or explore different keywords
                  </p>
                </div>
                <Button 
                  onClick={() => {
                    setSearchTerm("");
                    setLocation("");
                  }}
                  className="bg-gradient-to-r from-blue-600 to-slate-700 hover:from-blue-700 hover:to-slate-800 px-8 py-3 text-lg font-semibold"
                >
                  View All Jobs
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Job Details Modal */}
      <JobDetailsModal
        job={selectedJob}
        user={user}
        isOpen={showJobDetails}
        onClose={handleCloseJobDetails}
        onApplicationSuccess={handleApplicationSuccess}
      />
    </div>
  );
};

function App() {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authPage, setAuthPage] = useState('login'); // 'login' or 'register'
  const [currentPage, setCurrentPage] = useState('jobs'); // 'jobs' or 'profile'
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');
    
    if (token && savedUser) {
      setUser(JSON.parse(savedUser));
      setIsAuthenticated(true);
    }
    setLoading(false);
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
    setIsAuthenticated(true);
    
    // Role-based routing after login
    if (userData.role === 'recruiter') {
      // For recruiters, check if company profile needs completion
      const totalPoints = userData.recruiter_progress?.total_points || 0;
      if (totalPoints < 50) {
        setCurrentPage('profile');
      } else {
        setCurrentPage('dashboard');
      }
    } else {
      // For job seekers and admins, check if profile needs completion
      const totalPoints = userData.job_seeker_progress?.total_points || 0;
      if (totalPoints < 100 && userData.role !== 'admin') {
        setCurrentPage('profile');
      } else {
        setCurrentPage('dashboard');
      }
    }
  };

  const handleRegister = (userData) => {
    setUser(userData);
    setIsAuthenticated(true);
    setCurrentPage('profile'); // Always go to profile after registration
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    setIsAuthenticated(false);
    setCurrentPage('jobs');
  };

  const handleUpdateUser = (updatedUser) => {
    setUser(updatedUser);
    localStorage.setItem('user', JSON.stringify(updatedUser));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-24 w-24 border-4 border-slate-200 border-t-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading Job Rocket...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="App">
        <BrowserRouter>
          <Routes>
            <Route path="/invitation/:token" element={
              <InvitationPage onLogin={handleLogin} />
            } />
            <Route path="*" element={
              authPage === 'login' ? (
                <LoginPage 
                  onLogin={handleLogin}
                  onSwitchToRegister={() => setAuthPage('register')}
                />
              ) : (
                <RegisterPage 
                  onRegister={handleRegister}
                  onSwitchToLogin={() => setAuthPage('login')}
                />
              )
            } />
          </Routes>
        </BrowserRouter>
      </div>
    );
  }

  return (
    <div className="App">
      <BrowserRouter>
        <div className="min-h-screen flex flex-col">
          <Navigation user={user} onLogout={handleLogout} />
          
          <main className="flex-1">
            <Routes>
              <Route path="/" element={
                user.role === 'recruiter' ? (
                  <RecruiterDashboard 
                    user={user} 
                    onUpdateUser={handleUpdateUser}
                  />
                ) : user.role === 'admin' ? (
                  <AdminDashboard 
                    user={user}
                    onLogout={handleLogout}
                  />
                ) : (
                  currentPage === 'profile' ? (
                    <ProfileDashboard 
                      user={user} 
                      onUpdateUser={handleUpdateUser}
                      onLogout={handleLogout}
                    />
                  ) : (
                    <JobListingPage 
                      user={user} 
                      onLogout={handleLogout}
                    />
                  )
                )
              } />
              
              <Route path="/jobs" element={
                <JobListingPage 
                  user={user} 
                  onLogout={handleLogout}
                />
              } />
              
              <Route path="/profile" element={
                user.role === 'recruiter' ? (
                  <RecruiterDashboard 
                    user={user} 
                    onUpdateUser={handleUpdateUser}
                  />
                ) : user.role === 'admin' ? (
                  <AdminDashboard 
                    user={user}
                    onLogout={handleLogout}
                  />
                ) : (
                  <ProfileDashboard 
                    user={user} 
                    onUpdateUser={handleUpdateUser}
                    onLogout={handleLogout}
                  />
                )
              } />

              <Route path="/my-applications" element={
                user.role === 'job_seeker' ? (
                  <MyApplications 
                    user={user}
                  />
                ) : (
                  <Navigate to="/" replace />
                )
              } />

              <Route path="/applications" element={
                user.role === 'recruiter' ? (
                  <ApplicationManagement 
                    user={user}
                  />
                ) : (
                  <Navigate to="/" replace />
                )
              } />

              <Route path="/my-jobs" element={
                user.role === 'recruiter' ? (
                  <JobPosting 
                    user={user}
                  />
                ) : (
                  <Navigate to="/" replace />
                )
              } />

              <Route path="/pricing" element={
                <PricingPage 
                  user={user}
                />
              } />

              <Route path="/packages" element={
                user.role === 'recruiter' ? (
                  <PackageManagement 
                    user={user}
                  />
                ) : (
                  <Navigate to="/" replace />
                )
              } />

              <Route path="/notifications" element={
                <NotificationsPage 
                  user={user}
                />
              } />
              
              <Route path="/admin" element={
                user && user.role === 'admin' ? (
                  <AdminDashboard 
                    user={user}
                    onLogout={handleLogout}
                  />
                ) : (
                  <div className="min-h-screen bg-slate-50 flex items-center justify-center">
                    <div className="text-center">
                      <h1 className="text-2xl font-bold text-slate-900 mb-4">Access Denied</h1>
                      <p className="text-slate-600 mb-4">You need admin privileges to access this page.</p>
                      <Button onClick={() => window.location.href = '/'} className="bg-blue-600 hover:bg-blue-700">
                        Return to Home
                      </Button>
                    </div>
                  </div>
                )
              } />
              
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
          
          <Footer user={user} />
        </div>
      </BrowserRouter>
    </div>
  );
}

export default App;