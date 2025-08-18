import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import { LoginPage, RegisterPage } from "./components/AuthPages";
import ProfileDashboard from "./components/ProfileDashboard";
import RecruiterDashboard from "./components/RecruiterDashboard";
import InvitationPage from "./components/InvitationPage";
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
  LogOut
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const JobCard = ({ job, onSave, onApply }) => {
  const formatPostedDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return '1 day ago';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 14) return '1 week ago';
    return `${Math.ceil(diffDays / 7)} weeks ago`;
  };

  const formatSalary = (salaryMin, salaryMax, currency = 'ZAR') => {
    if (!salaryMin && !salaryMax) return null;
    if (salaryMin && salaryMax) {
      return `${currency} ${salaryMin.toLocaleString()} - ${salaryMax.toLocaleString()}`;
    }
    if (salaryMin) return `${currency} ${salaryMin.toLocaleString()}+`;
    return `Up to ${currency} ${salaryMax.toLocaleString()}`;
  };

  return (
    <Card className="group cursor-pointer hover:shadow-2xl transition-all duration-500 bg-white/80 backdrop-blur-sm border-0 hover:bg-white/90 relative overflow-hidden rocket-card">
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
                src={job.logo_url} 
                alt={`${job.company_name} logo`}
                className="w-full h-full object-cover"
                onError={(e) => {
                  e.target.src = 'https://images.unsplash.com/photo-1606211105533-0439bfecce21?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzZ8MHwxfHNlYXJjaHw0fHxtb2Rlcm4lMjB0ZWNobm9sb2d5fGVufDB8fHx8MTc1NTM1MzYzMXww&ixlib=rb-4.1.0&q=85&w=80&h=80';
                }}
              />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between mb-3">
                <h3 className="text-2xl font-bold text-slate-800 group-hover:text-blue-700 transition-colors leading-tight">
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
              
              {formatSalary(job.salary_min, job.salary_max, job.salary_currency) && (
                <div className="flex items-center space-x-2 text-emerald-700 font-bold mb-4 bg-emerald-50 px-3 py-2 rounded-lg w-fit">
                  <DollarSign className="w-4 h-4" />
                  <span>{formatSalary(job.salary_min, job.salary_max, job.salary_currency)}</span>
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
                  {job.is_remote && (
                    <Badge className="bg-blue-100 text-blue-700 hover:bg-blue-200 px-3 py-1 font-medium border-0">
                      <Zap className="w-3 h-3 mr-1" />
                      Remote
                    </Badge>
                  )}
                  {job.is_hybrid && (
                    <Badge className="bg-purple-100 text-purple-700 hover:bg-purple-200 px-3 py-1 font-medium border-0">
                      Hybrid
                    </Badge>
                  )}
                  <Badge variant="outline" className="border-slate-300 text-slate-600 px-3 py-1 font-medium">
                    {job.experience_level}
                  </Badge>
                </div>
                <Button
                  onClick={(e) => {
                    e.stopPropagation();
                    onApply(job.id);
                  }}
                  className="bg-gradient-to-r from-blue-600 to-slate-700 hover:from-blue-700 hover:to-slate-800"
                >
                  <Rocket className="w-4 h-4 mr-2" />
                  Quick Apply
                </Button>
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
      
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-lg shadow-xl border-b border-slate-200/50 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            <div className="flex items-center space-x-8">
              <div className="flex items-center space-x-3">
                <div className="bg-gradient-to-br from-blue-600 to-slate-700 text-white p-3 rounded-2xl shadow-lg">
                  <Rocket className="w-8 h-8" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-slate-800 bg-clip-text text-transparent">
                    Job Rocket
                  </h1>
                  <p className="text-xs text-slate-500 font-medium">LAUNCH YOUR CAREER</p>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-6">
              <Button variant="ghost" className="text-blue-700 hover:text-blue-800 hover:bg-blue-50 font-semibold px-6">
                For Recruiters
              </Button>
              <Button variant="ghost" className="flex items-center space-x-2 hover:bg-slate-50 font-semibold px-6">
                <Heart className="w-5 h-5" />
                <span>My Jobs</span>
                <ChevronDown className="w-4 h-4" />
              </Button>
              {user && (
                <div className="flex items-center space-x-4">
                  <Button variant="ghost" className="flex items-center space-x-2 hover:bg-slate-50 font-semibold px-6">
                    <User className="w-5 h-5" />
                    <span>{user.first_name}</span>
                    <ChevronDown className="w-4 h-4" />
                  </Button>
                  <Button 
                    variant="ghost" 
                    onClick={onLogout}
                    className="text-red-600 hover:text-red-700 hover:bg-red-50"
                  >
                    <LogOut className="w-5 h-5" />
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

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
                  onSave={handleSaveJob}
                  onApply={handleApplyToJob}
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
        setCurrentPage('jobs'); // or recruiter dashboard
      }
    } else {
      // For job seekers, check if profile needs completion
      const totalPoints = userData.profile_progress?.total_points || 0;
      if (totalPoints < 50) {
        setCurrentPage('profile');
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
        <Routes>
          <Route path="/" element={
            currentPage === 'profile' ? (
              user.role === 'recruiter' ? (
                <RecruiterDashboard 
                  user={user} 
                  onUpdateUser={handleUpdateUser}
                />
              ) : (
                <ProfileDashboard 
                  user={user} 
                  onUpdateUser={handleUpdateUser}
                />
              )
            ) : (
              <JobListingPage 
                user={user} 
                onLogout={handleLogout}
              />
            )
          } />
          <Route path="/profile" element={
            user.role === 'recruiter' ? (
              <RecruiterDashboard 
                user={user} 
                onUpdateUser={handleUpdateUser}
              />
            ) : (
              <ProfileDashboard 
                user={user} 
                onUpdateUser={handleUpdateUser}
              />
            )
          } />
          <Route path="/jobs" element={
            <JobListingPage 
              user={user} 
              onLogout={handleLogout}
            />
          } />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;