import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Card, CardContent } from "./ui/card";
import { Badge } from "./ui/badge";
import {
  Search,
  MapPin,
  Heart,
  ChevronDown,
  Filter,
  Rocket,
  Star,
  Clock,
  Banknote,
  Building2,
  Zap,
  Lock,
  LogIn,
  UserPlus,
  X,
  Menu,
  Send
} from "lucide-react";
import axios from 'axios';
import Footer from './Footer';
import SEO from './SEO';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const getImageUrl = (imageUrl) => {
  if (!imageUrl) return '';
  if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) return imageUrl;
  if (imageUrl.startsWith('/uploads/')) return `${BACKEND_URL}/api${imageUrl}`;
  if (imageUrl.startsWith('/api/uploads/')) return `${BACKEND_URL}${imageUrl}`;
  return imageUrl;
};

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

// Simplified guest navigation
const GuestNavigation = () => {
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <nav className="bg-white shadow-lg border-b border-slate-200 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <button onClick={() => navigate('/')} className="flex items-center space-x-2">
              <div className="bg-gradient-to-br from-blue-600 to-purple-600 p-2 rounded-lg">
                <Rocket className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Job Rocket
              </span>
            </button>
          </div>

          {/* Desktop buttons */}
          <div className="hidden sm:flex items-center space-x-3">
            <Button
              variant="outline"
              onClick={() => navigate('/')}
              className="border-slate-300 hover:bg-slate-50 font-medium"
              data-testid="guest-nav-login-btn"
            >
              <LogIn className="w-4 h-4 mr-2" />
              Login
            </Button>
            <Button
              onClick={() => navigate('/register')}
              className="bg-gradient-to-r from-blue-600 to-slate-700 hover:from-blue-700 hover:to-slate-800 font-medium"
              data-testid="guest-nav-register-btn"
            >
              <UserPlus className="w-4 h-4 mr-2" />
              Register
            </Button>
          </div>

          {/* Mobile menu button */}
          <div className="sm:hidden flex items-center">
            <Button variant="ghost" size="sm" onClick={() => setMobileOpen(!mobileOpen)}>
              {mobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </Button>
          </div>
        </div>
      </div>

      {mobileOpen && (
        <div className="sm:hidden bg-white border-t border-slate-200 px-4 py-3 space-y-2">
          <Button
            variant="outline"
            onClick={() => navigate('/')}
            className="w-full border-slate-300 hover:bg-slate-50 font-medium"
          >
            <LogIn className="w-4 h-4 mr-2" />
            Login
          </Button>
          <Button
            onClick={() => navigate('/register')}
            className="w-full bg-gradient-to-r from-blue-600 to-slate-700 hover:from-blue-700 hover:to-slate-800 font-medium"
          >
            <UserPlus className="w-4 h-4 mr-2" />
            Register
          </Button>
        </div>
      )}
    </nav>
  );
};

// Login prompt modal
const LoginPromptModal = ({ isOpen, onClose }) => {
  const navigate = useNavigate();

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />

      {/* Modal content */}
      <div className="relative bg-white rounded-2xl shadow-2xl max-w-md w-full p-8 animate-in fade-in zoom-in-95" data-testid="guest-login-prompt-modal">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 transition-colors"
          data-testid="guest-modal-close-btn"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="text-center">
          <div className="mx-auto w-16 h-16 bg-gradient-to-br from-blue-100 to-slate-100 rounded-2xl flex items-center justify-center mb-5">
            <Lock className="w-8 h-8 text-blue-600" />
          </div>

          <h3 className="text-2xl font-bold text-slate-800 mb-2">
            Create an Account to Continue
          </h3>
          <p className="text-slate-600 mb-8 leading-relaxed">
            Register or log in to view full job details, apply to positions, and track your applications.
          </p>

          <div className="space-y-3">
            <Button
              onClick={() => navigate('/register')}
              className="w-full bg-gradient-to-r from-blue-600 to-slate-700 hover:from-blue-700 hover:to-slate-800 h-12 text-lg font-semibold shadow-lg"
              data-testid="guest-modal-register-btn"
            >
              <UserPlus className="w-5 h-5 mr-2" />
              Create Account
            </Button>

            <Button
              variant="outline"
              onClick={() => navigate('/')}
              className="w-full h-12 border-slate-300 hover:bg-slate-50 font-medium text-lg"
              data-testid="guest-modal-login-btn"
            >
              <LogIn className="w-5 h-5 mr-2" />
              Sign In
            </Button>
          </div>

          <p className="text-xs text-slate-400 mt-5">
            It only takes a minute to get started
          </p>
        </div>
      </div>
    </div>
  );
};

// Guest job card — same visual layout, locked interactions
const GuestJobCard = ({ job, onLockedAction }) => {
  const formatSalary = (salaryMin, salaryMax, currency = 'ZAR') => {
    if (!salaryMin && !salaryMax) return null;
    if (salaryMin && salaryMax) return `${currency} ${salaryMin.toLocaleString()} - ${salaryMax.toLocaleString()}`;
    if (salaryMin) return `${currency} ${salaryMin.toLocaleString()}+`;
    return `Up to ${currency} ${salaryMax.toLocaleString()}`;
  };

  return (
    <Card
      className="group cursor-pointer hover:shadow-2xl transition-all duration-500 bg-white/80 backdrop-blur-sm border-0 hover:bg-white/90 relative overflow-hidden rocket-card"
      onClick={onLockedAction}
      data-testid="guest-job-card"
    >
      <div className="absolute inset-0 opacity-5 tech-grid"></div>
      {job.featured && (
        <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-transparent to-slate-500/10 pointer-events-none"></div>
      )}

      <CardContent className="p-3 sm:p-4 lg:p-6 relative z-10">
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-3 sm:space-x-4 flex-1 min-w-0">
            <div className="w-12 h-12 sm:w-16 sm:h-16 lg:w-20 lg:h-20 rounded-xl sm:rounded-2xl overflow-hidden bg-gradient-to-br from-slate-100 to-slate-200 flex-shrink-0 shadow-lg ring-2 ring-slate-200/50">
              <img
                src={getImageUrl(job.logo_url) || 'https://customer-assets.emergentagent.com/job_career-launchpad-16/artifacts/a6w1unn9_Leonardo_Phoenix_A_modern_sleek_logo_featuring_a_stylized_rock_2.jpg'}
                alt={`${job.company_name} logo`}
                className="w-full h-full object-cover"
                onError={(e) => {
                  e.target.src = 'https://customer-assets.emergentagent.com/job_career-launchpad-16/artifacts/a6w1unn9_Leonardo_Phoenix_A_modern_sleek_logo_featuring_a_stylized_rock_2.jpg';
                }}
              />
            </div>
            <div className="flex-1 min-w-0 overflow-hidden">
              <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between mb-2 sm:mb-3">
                <h3
                  className="text-lg sm:text-xl lg:text-2xl font-bold text-slate-800 group-hover:text-blue-700 transition-colors leading-tight cursor-pointer hover:underline pr-2 truncate"
                  onClick={(e) => { e.stopPropagation(); onLockedAction(); }}
                >
                  {job.title}
                </h3>
                {job.featured && (
                  <div className="flex items-center space-x-1 bg-gradient-to-r from-blue-600 to-slate-700 text-white px-2 sm:px-3 py-1 rounded-full text-xs font-semibold flex-shrink-0 mt-1 sm:mt-0">
                    <Star className="w-3 h-3 fill-current" />
                    <span className="hidden sm:inline">Featured</span>
                  </div>
                )}
              </div>

              <div className="flex flex-col sm:flex-row sm:flex-wrap sm:items-center gap-2 sm:gap-4 text-slate-600 mb-3 sm:mb-4">
                <div className="flex items-center space-x-2 min-w-0">
                  <Building2 className="w-4 h-4 text-slate-500 flex-shrink-0" />
                  <span className="font-medium truncate">{job.company_name}</span>
                </div>
                <div className="flex items-center space-x-2 min-w-0">
                  <MapPin className="w-4 h-4 text-slate-500 flex-shrink-0" />
                  <span className="truncate">{job.location}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Clock className="w-4 h-4 text-slate-500 flex-shrink-0" />
                  <span className="text-sm">{formatPostedDate(job.posted_date)}</span>
                </div>
              </div>

              {job.salary && (
                <div className="flex items-center space-x-2 text-emerald-700 font-bold mb-3 sm:mb-4 bg-emerald-50 px-2 sm:px-3 py-1 sm:py-2 rounded-lg w-fit">
                  <Banknote className="w-4 h-4 flex-shrink-0" />
                  <span className="text-sm sm:text-base">{job.salary}</span>
                </div>
              )}

              <p className="text-slate-700 mb-4 sm:mb-6 leading-relaxed line-clamp-2 text-sm sm:text-base">
                {job.description}
              </p>

              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                <div className="flex flex-wrap items-center gap-2">
                  <Badge variant="secondary" className="bg-slate-100 text-slate-700 hover:bg-slate-200 px-2 sm:px-3 py-1 font-medium text-xs sm:text-sm">
                    {job.job_type}
                  </Badge>
                  <Badge className={`px-2 sm:px-3 py-1 font-medium border-0 text-xs sm:text-sm ${
                    job.work_type === 'Remote' ? 'bg-blue-100 text-blue-700 hover:bg-blue-200' :
                    job.work_type === 'Hybrid' ? 'bg-purple-100 text-purple-700 hover:bg-purple-200' :
                    'bg-green-100 text-green-700 hover:bg-green-200'
                  }`}>
                    {job.work_type === 'Remote' && <Zap className="w-3 h-3 mr-1" />}
                    {job.work_type}
                  </Badge>
                  <Badge variant="outline" className="border-slate-300 text-slate-600 px-2 sm:px-3 py-1 font-medium text-xs sm:text-sm">
                    {job.industry}
                  </Badge>
                </div>
                <div className="flex items-center space-x-2 justify-end">
                  <Button
                    onClick={(e) => { e.stopPropagation(); onLockedAction(); }}
                    className="bg-gradient-to-r from-slate-400 to-slate-500 hover:from-blue-600 hover:to-slate-700 transition-all"
                    data-testid="guest-apply-btn"
                  >
                    <Lock className="w-4 h-4 mr-2" />
                    <span className="hidden sm:inline">Sign In to Apply</span>
                    <span className="sm:hidden">Apply</span>
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => { e.stopPropagation(); onLockedAction(); }}
                    className="hover:bg-red-50 hover:text-red-600 rounded-full p-2 transition-all duration-300 flex-shrink-0"
                    data-testid="guest-save-btn"
                  >
                    <Heart className="w-4 h-4 sm:w-5 sm:h-5 text-slate-400" />
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// Filter section (same as main app)
const GuestFilterSection = ({ title, children, defaultExpanded = true }) => {
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

const GuestFilterOption = ({ label, count, selected, onChange }) => (
  <label className="flex items-center justify-between cursor-pointer hover:bg-slate-50 p-3 rounded-xl transition-all duration-200">
    <div className="flex items-center space-x-3">
      <input
        type="checkbox"
        checked={selected || false}
        onChange={(e) => onChange(e.target.checked)}
        className="w-5 h-5 rounded border-2 border-slate-300 text-blue-600 focus:ring-blue-500 focus:ring-2"
      />
      <span className="font-medium text-slate-700">{label}</span>
    </div>
    {count !== undefined && (
      <span className="text-xs text-slate-500 bg-slate-100 px-2 py-1 rounded-full font-semibold">
        {count}
      </span>
    )}
  </label>
);

// Main Guest Job Listings Page
const GuestJobListings = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchInput, setSearchInput] = useState("");
  const [locationInput, setLocationInput] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [location, setLocation] = useState("");
  const [visibleCount, setVisibleCount] = useState(30);
  const [showLoginPrompt, setShowLoginPrompt] = useState(false);
  const [filters, setFilters] = useState({
    datePosted: { newJobs: false, lastWeek: false },
    workFromHome: { partiallyRemote: false, fullyRemote: false },
    applicationMethod: { onCompanyWebsite: false, easyApply: false },
    functions: { engineering: false, production: false, itTelecom: false, salesPurchasing: false, accounting: false, banking: false }
  });

  const handleFilterChange = (category, filterKey, value) => {
    setFilters(prev => ({
      ...prev,
      [category]: { ...prev[category], [filterKey]: value }
    }));
  };

  const fetchJobs = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);
      if (location) params.append('location', location);
      const response = await axios.get(`${API}/public/jobs?${params.toString()}`);
      setJobs(response.data.jobs || response.data);
    } catch (error) {
      console.error('Error fetching jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchJobs(); }, []);

  // Re-fetch when search terms change via button
  useEffect(() => { fetchJobs(); }, [searchTerm, location]);

  const handleSearch = () => {
    setSearchTerm(searchInput);
    setLocation(locationInput);
    setVisibleCount(30);
  };

  const handleSearchKeyPress = (e) => {
    if (e.key === 'Enter') handleSearch();
  };

  const handleLoadMore = () => setVisibleCount(prev => prev + 30);

  const filteredJobs = jobs.filter(job => {
    const title = job.title?.toLowerCase() || '';
    const companyName = job.company_name?.toLowerCase() || '';
    const description = job.description?.toLowerCase() || '';
    const jobLocation = job.location?.toLowerCase() || '';
    const searchLower = searchTerm.toLowerCase();
    const locationLower = location.toLowerCase();

    const matchesSearch = !searchTerm || title.includes(searchLower) || companyName.includes(searchLower) || description.includes(searchLower);
    const matchesLocation = !location || jobLocation.includes(locationLower);

    let matchesDatePosted = true;
    if (filters.datePosted.newJobs || filters.datePosted.lastWeek) {
      const jobDate = new Date(job.posted_date);
      const now = new Date();
      const daysDiff = Math.floor((now - jobDate) / (1000 * 60 * 60 * 24));
      if (filters.datePosted.newJobs && daysDiff > 1) matchesDatePosted = false;
      if (filters.datePosted.lastWeek && daysDiff > 7) matchesDatePosted = false;
    }

    let matchesWorkFromHome = true;
    if (filters.workFromHome.partiallyRemote || filters.workFromHome.fullyRemote) {
      const workType = job.work_type?.toLowerCase() || '';
      matchesWorkFromHome = false;
      if (filters.workFromHome.partiallyRemote && (workType.includes('hybrid') || workType.includes('partial'))) matchesWorkFromHome = true;
      if (filters.workFromHome.fullyRemote && workType.includes('remote')) matchesWorkFromHome = true;
    }

    let matchesApplicationMethod = true;
    if (filters.applicationMethod.onCompanyWebsite || filters.applicationMethod.easyApply) {
      matchesApplicationMethod = false;
      if (filters.applicationMethod.easyApply) matchesApplicationMethod = true;
      if (filters.applicationMethod.onCompanyWebsite && job.external_url) matchesApplicationMethod = true;
    }

    let matchesFunctions = true;
    const hasAnyFunctionFilter = Object.values(filters.functions).some(val => val);
    if (hasAnyFunctionFilter) {
      const jobIndustry = job.industry?.toLowerCase() || '';
      const jobTitle = job.title?.toLowerCase() || '';
      matchesFunctions = false;
      if (filters.functions.engineering && (jobIndustry.includes('technology') || jobIndustry.includes('engineering') || jobTitle.includes('engineer') || jobTitle.includes('developer') || jobTitle.includes('technical'))) matchesFunctions = true;
      if (filters.functions.production && (jobIndustry.includes('manufacturing') || jobIndustry.includes('production') || jobTitle.includes('production') || jobTitle.includes('manufacturing'))) matchesFunctions = true;
      if (filters.functions.itTelecom && (jobIndustry.includes('technology') || jobIndustry.includes('software') || jobIndustry.includes('it') || jobTitle.includes('it ') || jobTitle.includes('software'))) matchesFunctions = true;
      if (filters.functions.salesPurchasing && (jobIndustry.includes('sales') || jobTitle.includes('sales') || jobTitle.includes('marketing'))) matchesFunctions = true;
      if (filters.functions.accounting && (jobIndustry.includes('finance') || jobIndustry.includes('accounting') || jobTitle.includes('accountant') || jobTitle.includes('finance'))) matchesFunctions = true;
      if (filters.functions.banking && (jobIndustry.includes('banking') || jobIndustry.includes('financial') || jobTitle.includes('bank') || jobTitle.includes('financial'))) matchesFunctions = true;
    }

    return matchesSearch && matchesLocation && matchesDatePosted && matchesWorkFromHome && matchesApplicationMethod && matchesFunctions;
  });

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col">
        <GuestNavigation />
        <div className="flex-1 bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 flex items-center justify-center relative overflow-hidden">
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
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      <SEO 
        title="Browse Jobs in South Africa"
        description="Search and browse thousands of job opportunities across South Africa. Find jobs in Johannesburg, Cape Town, Durban and more. IT, finance, engineering, healthcare and all industries."
        keywords="jobs South Africa, job search, careers, employment, vacancies, hiring, Johannesburg jobs, Cape Town jobs, Durban jobs, remote jobs SA, IT jobs, finance jobs, engineering jobs"
        canonicalPath="/browse-jobs"
        jsonLd={{
          "@context": "https://schema.org",
          "@type": "ItemList",
          "name": "Job Listings in South Africa",
          "description": "Browse latest job opportunities in South Africa",
          "numberOfItems": jobs.length,
          "itemListElement": jobs.slice(0, 10).map((job, i) => ({
            "@type": "ListItem",
            "position": i + 1,
            "item": {
              "@type": "JobPosting",
              "title": job.title,
              "description": (job.description || '').substring(0, 200),
              "datePosted": job.posted_date,
              "jobLocation": {
                "@type": "Place",
                "address": { "@type": "PostalAddress", "addressLocality": job.location || "South Africa", "addressCountry": "ZA" }
              },
              "hiringOrganization": {
                "@type": "Organization",
                "name": job.company_name || "Company"
              }
            }
          }))
        }}
      />
      <GuestNavigation />

      <div className="flex-1 bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 relative">
        <div className="absolute inset-0 opacity-5 tech-grid"></div>

        {/* Guest banner */}
        <div className="bg-gradient-to-r from-amber-50 to-orange-50 border-b border-amber-200">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex items-center justify-center gap-2 text-sm text-amber-800">
            <Lock className="w-4 h-4 flex-shrink-0" />
            <span className="font-medium">You are browsing as a guest.</span>
            <span className="hidden sm:inline">Register to view full details and apply.</span>
          </div>
        </div>

        {/* Hero Search Section */}
        <div
          className="relative py-20 overflow-hidden"
          style={{
            backgroundImage: `linear-gradient(135deg, rgba(15, 23, 42, 0.85), rgba(30, 64, 175, 0.8)), url('https://images.unsplash.com/photo-1541185933-ef5d8ed016c2?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwyfHxyb2NrZXQlMjBsYXVuY2h8ZW58MHx8fHwxNzU1MzUzNjI2fDA&ixlib=rb-4.1.0&q=85')`,
            backgroundSize: 'cover',
            backgroundPosition: 'top center'
          }}
        >
          <div className="absolute inset-0 overflow-hidden">
            <div className="stars"></div>
          </div>

          <div className="max-w-5xl mx-auto px-6 lg:px-8 text-center relative z-10">
            <div className="mb-8">
              <h2 className="text-4xl sm:text-5xl lg:text-6xl font-black text-white mb-4 tracking-tight">
                Browse
                <span className="bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent block">
                  Open Positions
                </span>
              </h2>
              <p className="text-lg sm:text-xl text-slate-300 max-w-2xl mx-auto leading-relaxed">
                Preview available opportunities across South Africa — create an account to apply
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 max-w-4xl mx-auto">
              <div className="relative flex-1">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5 sm:w-6 sm:h-6" />
                <Input
                  type="text"
                  placeholder="Job title, keywords"
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                  onKeyPress={handleSearchKeyPress}
                  className="pl-10 sm:pl-12 h-12 sm:h-16 text-base sm:text-lg font-medium bg-white/90 backdrop-blur-sm border-0 shadow-2xl rounded-2xl focus:ring-4 focus:ring-blue-500/30 focus:bg-white transition-all"
                  data-testid="guest-search-input"
                />
              </div>
              <div className="relative flex-1">
                <MapPin className="absolute left-4 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5 sm:w-6 sm:h-6" />
                <Input
                  type="text"
                  placeholder="City, province"
                  value={locationInput}
                  onChange={(e) => setLocationInput(e.target.value)}
                  onKeyPress={handleSearchKeyPress}
                  className="pl-10 sm:pl-12 h-12 sm:h-16 text-base sm:text-lg font-medium bg-white/90 backdrop-blur-sm border-0 shadow-2xl rounded-2xl focus:ring-4 focus:ring-blue-500/30 focus:bg-white transition-all"
                  data-testid="guest-location-input"
                />
              </div>
              <Button
                onClick={handleSearch}
                className="bg-gradient-to-r from-blue-600 to-slate-700 hover:from-blue-700 hover:to-slate-800 h-12 sm:h-16 px-6 sm:px-12 text-base sm:text-lg font-bold shadow-2xl rounded-2xl hover:shadow-3xl transform hover:scale-105 transition-all duration-300 whitespace-nowrap"
                data-testid="guest-search-btn"
              >
                <Rocket className="w-5 h-5 sm:w-6 sm:h-6 mr-2 sm:mr-3" />
                <span className="hidden sm:inline">Launch Search</span>
                <span className="sm:hidden">Search</span>
              </Button>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12 relative z-10">
          <div className="flex flex-col lg:flex-row gap-6 lg:gap-8">
            {/* Filters Sidebar */}
            <div className="w-full lg:w-80 lg:flex-shrink-0">
              <div className="bg-white/80 backdrop-blur-sm rounded-3xl shadow-xl p-4 sm:p-8 lg:sticky lg:top-32 border border-slate-200/50">
                <div className="flex items-center justify-between mb-6 lg:mb-8">
                  <div className="flex items-center space-x-3">
                    <Filter className="w-5 h-5 sm:w-6 sm:h-6 text-blue-600" />
                    <h3 className="text-xl sm:text-2xl font-bold text-slate-800">Filters</h3>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setFilters({
                      datePosted: { newJobs: false, lastWeek: false },
                      workFromHome: { partiallyRemote: false, fullyRemote: false },
                      applicationMethod: { onCompanyWebsite: false, easyApply: false },
                      functions: { engineering: false, production: false, itTelecom: false, salesPurchasing: false, accounting: false, banking: false }
                    })}
                    className="text-slate-500 hover:text-slate-700"
                  >
                    Clear All
                  </Button>
                </div>

                <GuestFilterSection title="Date Posted" defaultExpanded={true}>
                  <GuestFilterOption
                    label="New jobs"
                    count={jobs.filter(job => { const d = Math.floor((new Date() - new Date(job.posted_date)) / (1000*60*60*24)); return d <= 1; }).length}
                    selected={filters.datePosted.newJobs}
                    onChange={(checked) => handleFilterChange('datePosted', 'newJobs', checked)}
                  />
                  <GuestFilterOption
                    label="Last week"
                    count={jobs.filter(job => { const d = Math.floor((new Date() - new Date(job.posted_date)) / (1000*60*60*24)); return d <= 7; }).length}
                    selected={filters.datePosted.lastWeek}
                    onChange={(checked) => handleFilterChange('datePosted', 'lastWeek', checked)}
                  />
                </GuestFilterSection>

                <GuestFilterSection title="Work From Home" defaultExpanded={true}>
                  <GuestFilterOption
                    label="Partially remote"
                    count={jobs.filter(job => job.work_type?.toLowerCase().includes('hybrid')).length}
                    selected={filters.workFromHome.partiallyRemote}
                    onChange={(checked) => handleFilterChange('workFromHome', 'partiallyRemote', checked)}
                  />
                  <GuestFilterOption
                    label="Fully remote"
                    count={jobs.filter(job => job.work_type?.toLowerCase().includes('remote')).length}
                    selected={filters.workFromHome.fullyRemote}
                    onChange={(checked) => handleFilterChange('workFromHome', 'fullyRemote', checked)}
                  />
                </GuestFilterSection>

                <GuestFilterSection title="Application Method" defaultExpanded={true}>
                  <GuestFilterOption
                    label="On company website"
                    count={jobs.filter(job => job.external_url).length}
                    selected={filters.applicationMethod.onCompanyWebsite}
                    onChange={(checked) => handleFilterChange('applicationMethod', 'onCompanyWebsite', checked)}
                  />
                  <GuestFilterOption
                    label="Easy Apply"
                    count={jobs.length}
                    selected={filters.applicationMethod.easyApply}
                    onChange={(checked) => handleFilterChange('applicationMethod', 'easyApply', checked)}
                  />
                </GuestFilterSection>

                <GuestFilterSection title="Functions" defaultExpanded={true}>
                  <GuestFilterOption
                    label="Engineering, Technical"
                    count={jobs.filter(job => { const i = job.industry?.toLowerCase() || ''; const t = job.title?.toLowerCase() || ''; return i.includes('technology') || i.includes('engineering') || t.includes('engineer') || t.includes('developer') || t.includes('technical'); }).length}
                    selected={filters.functions.engineering}
                    onChange={(checked) => handleFilterChange('functions', 'engineering', checked)}
                  />
                  <GuestFilterOption
                    label="Production & Manufacturing"
                    count={jobs.filter(job => { const i = job.industry?.toLowerCase() || ''; const t = job.title?.toLowerCase() || ''; return i.includes('manufacturing') || i.includes('production') || t.includes('production') || t.includes('manufacturing'); }).length}
                    selected={filters.functions.production}
                    onChange={(checked) => handleFilterChange('functions', 'production', checked)}
                  />
                  <GuestFilterOption
                    label="IT & Telecommunications"
                    count={jobs.filter(job => { const i = job.industry?.toLowerCase() || ''; const t = job.title?.toLowerCase() || ''; return i.includes('technology') || i.includes('software') || i.includes('it') || t.includes('it ') || t.includes('software'); }).length}
                    selected={filters.functions.itTelecom}
                    onChange={(checked) => handleFilterChange('functions', 'itTelecom', checked)}
                  />
                  <GuestFilterOption
                    label="Sales & Purchasing"
                    count={jobs.filter(job => { const i = job.industry?.toLowerCase() || ''; const t = job.title?.toLowerCase() || ''; return i.includes('sales') || t.includes('sales') || t.includes('marketing'); }).length}
                    selected={filters.functions.salesPurchasing}
                    onChange={(checked) => handleFilterChange('functions', 'salesPurchasing', checked)}
                  />
                  <GuestFilterOption
                    label="Accounting, Auditing"
                    count={jobs.filter(job => { const i = job.industry?.toLowerCase() || ''; const t = job.title?.toLowerCase() || ''; return i.includes('finance') || i.includes('accounting') || t.includes('accountant') || t.includes('finance'); }).length}
                    selected={filters.functions.accounting}
                    onChange={(checked) => handleFilterChange('functions', 'accounting', checked)}
                  />
                  <GuestFilterOption
                    label="Banking, Finance"
                    count={jobs.filter(job => { const i = job.industry?.toLowerCase() || ''; const t = job.title?.toLowerCase() || ''; return i.includes('banking') || i.includes('financial') || t.includes('bank') || t.includes('financial'); }).length}
                    selected={filters.functions.banking}
                    onChange={(checked) => handleFilterChange('functions', 'banking', checked)}
                  />
                </GuestFilterSection>
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

              <div className="grid grid-cols-1 gap-6 lg:gap-8">
                {filteredJobs.slice(0, visibleCount).map((job) => (
                  <GuestJobCard
                    key={job.id}
                    job={job}
                    onLockedAction={() => setShowLoginPrompt(true)}
                  />
                ))}
              </div>

              {filteredJobs.length > visibleCount && (
                <div className="flex justify-center mt-10">
                  <Button
                    onClick={handleLoadMore}
                    variant="outline"
                    className="px-8 py-3 text-lg font-semibold border-2 border-blue-600 text-blue-600 hover:bg-blue-50 rounded-xl transition-all duration-200"
                    data-testid="guest-load-more-btn"
                  >
                    View More
                  </Button>
                </div>
              )}

              {filteredJobs.length > 0 && filteredJobs.length <= visibleCount && filteredJobs.length > 30 && (
                <div className="text-center mt-8 text-slate-500">
                  All {filteredJobs.length} jobs loaded
                </div>
              )}

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
                      setSearchInput("");
                      setLocationInput("");
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

      <Footer />

      {/* Login prompt modal */}
      <LoginPromptModal
        isOpen={showLoginPrompt}
        onClose={() => setShowLoginPrompt(false)}
      />
    </div>
  );
};

export default GuestJobListings;
