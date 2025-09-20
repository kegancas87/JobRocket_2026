import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate, useParams } from "react-router-dom";
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
  Banknote,
  Users,
  Zap,
  Settings,
  LogOut,
  ExternalLink,
  ArrowRight,
  Mail,
  FileText,
  AlertCircle
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
    return `${BACKEND_URL}/api${imageUrl}`; // Convert old URLs to new API path
  }
  if (imageUrl.startsWith('/api/uploads/')) {
    return `${BACKEND_URL}${imageUrl}`; // New API URLs
  }
  return imageUrl; // Return as-is for other cases
};

// Helper function to format posted date
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

const CVSearchPage = ({ user }) => {
  const [searchCriteria, setSearchCriteria] = useState({
    position: '',
    location: '',
    skills: ''
  });
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [remainingSearches, setRemainingSearches] = useState(null);
  const [error, setError] = useState('');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setSearchCriteria(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const params = new URLSearchParams();
      if (searchCriteria.position) params.append('position', searchCriteria.position);
      if (searchCriteria.location) params.append('location', searchCriteria.location);
      if (searchCriteria.skills) params.append('skills', searchCriteria.skills);

      const response = await axios.get(`${API}/cv-search?${params.toString()}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });

      setSearchResults(response.data.results);
      setRemainingSearches(response.data.remaining_searches);
      setHasSearched(true);
    } catch (error) {
      console.error('CV search error:', error);
      if (error.response?.status === 402) {
        setError('No CV search credits available. Please purchase a CV search package.');
      } else {
        setError(error.response?.data?.detail || 'An error occurred while searching CVs');
      }
      setSearchResults([]);
    }
    setLoading(false);
  };

  const getExperienceYears = (experience) => {
    if (!experience || experience.length === 0) return 'No experience listed';
    
    // Calculate total experience from all positions
    let totalMonths = 0;
    experience.forEach(exp => {
      if (exp.start_date && exp.end_date) {
        const start = new Date(exp.start_date);
        const end = new Date(exp.end_date);
        const diffMonths = (end.getFullYear() - start.getFullYear()) * 12 + (end.getMonth() - start.getMonth());
        totalMonths += diffMonths;
      }
    });
    
    if (totalMonths < 12) return `${totalMonths} months`;
    const years = Math.floor(totalMonths / 12);
    const months = totalMonths % 12;
    return months > 0 ? `${years}.${months} years` : `${years} years`;
  };

  if (user?.role !== 'recruiter') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-slate-800 mb-4">Access Denied</h1>
          <p className="text-slate-600">Only recruiters can access CV search functionality.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-slate-800 mb-2">CV Search</h1>
            <p className="text-slate-600">Search and discover talented candidates for your open positions</p>
            {remainingSearches !== null && (
              <div className="mt-4">
                <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                  {remainingSearches === 'unlimited' ? 'Unlimited searches' : `${remainingSearches} searches remaining`}
                </span>
              </div>
            )}
          </div>

          {/* Search Form */}
          <div className="bg-white rounded-2xl shadow-xl p-6 mb-8">
            <form onSubmit={handleSearch} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <label htmlFor="position" className="block text-sm font-medium text-slate-700 mb-2">
                    Position / Job Title
                  </label>
                  <input
                    type="text"
                    id="position"
                    name="position"
                    value={searchCriteria.position}
                    onChange={handleInputChange}
                    placeholder="e.g. Software Developer, Marketing Manager"
                    className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label htmlFor="location" className="block text-sm font-medium text-slate-700 mb-2">
                    Location
                  </label>
                  <input
                    type="text"
                    id="location"
                    name="location"
                    value={searchCriteria.location}
                    onChange={handleInputChange}
                    placeholder="e.g. Cape Town, Johannesburg"
                    className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label htmlFor="skills" className="block text-sm font-medium text-slate-700 mb-2">
                    Skills
                  </label>
                  <input
                    type="text"
                    id="skills"
                    name="skills"
                    value={searchCriteria.skills}
                    onChange={handleInputChange}
                    placeholder="e.g. JavaScript, Python, Marketing"
                    className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <p className="text-xs text-slate-500 mt-1">Separate multiple skills with commas</p>
                </div>
              </div>

              <div className="flex justify-center">
                <button
                  type="submit"
                  disabled={loading || (!searchCriteria.position && !searchCriteria.location && !searchCriteria.skills)}
                  className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors font-medium flex items-center space-x-2"
                >
                  {loading ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      <span>Searching...</span>
                    </>
                  ) : (
                    <>
                      <Search className="w-5 h-5" />
                      <span>Search CVs</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
              <div className="flex items-center space-x-2">
                <AlertCircle className="w-5 h-5 text-red-500" />
                <p className="text-red-700">{error}</p>
              </div>
              {error.includes('purchase') && (
                <div className="mt-3">
                  <button
                    onClick={() => window.location.href = '/pricing'}
                    className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors text-sm"
                  >
                    View CV Search Packages
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Search Results */}
          {hasSearched && (
            <div className="bg-white rounded-2xl shadow-xl p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-slate-800">
                  Search Results ({searchResults.length})
                </h2>
                {searchResults.length > 0 && (
                  <p className="text-slate-600 text-sm">
                    Showing top {searchResults.length} candidates
                  </p>
                )}
              </div>

              {searchResults.length === 0 ? (
                <div className="text-center py-12">
                  <Users className="w-16 h-16 mx-auto text-slate-300 mb-4" />
                  <h3 className="text-lg font-medium text-slate-800 mb-2">No candidates found</h3>
                  <p className="text-slate-600">Try adjusting your search criteria or using different keywords.</p>
                </div>
              ) : (
                <div className="space-y-6">
                  {searchResults.map((candidate) => (
                    <div key={candidate.id} className="border border-slate-200 rounded-xl p-6 hover:shadow-md transition-shadow">
                      <div className="flex items-start space-x-6">
                        {/* Profile Picture */}
                        <div className="w-16 h-16 rounded-full overflow-hidden bg-gradient-to-br from-slate-200 to-slate-300 flex-shrink-0">
                          <img
                            src={getImageUrl(candidate.profile_picture_url) || `https://ui-avatars.com/api/?name=${candidate.first_name}+${candidate.last_name}&background=3b82f6&color=fff`}
                            alt={`${candidate.first_name} ${candidate.last_name}`}
                            className="w-full h-full object-cover"
                            onError={(e) => {
                              e.target.src = `https://ui-avatars.com/api/?name=${candidate.first_name}+${candidate.last_name}&background=3b82f6&color=fff`;
                            }}
                          />
                        </div>

                        {/* Candidate Info */}
                        <div className="flex-1">
                          <div className="flex items-start justify-between mb-4">
                            <div>
                              <h3 className="text-xl font-bold text-slate-800 mb-1">
                                {candidate.first_name} {candidate.last_name}
                              </h3>
                              {candidate.desired_job_title && (
                                <p className="text-blue-600 font-medium mb-2">{candidate.desired_job_title}</p>
                              )}
                              <div className="flex flex-wrap items-center gap-4 text-sm text-slate-600">
                                {candidate.location && (
                                  <div className="flex items-center space-x-1">
                                    <MapPin className="w-4 h-4" />
                                    <span>{candidate.location}</span>
                                  </div>
                                )}
                                {candidate.experience && (
                                  <div className="flex items-center space-x-1">
                                    <Briefcase className="w-4 h-4" />
                                    <span>{getExperienceYears(candidate.experience)}</span>
                                  </div>
                                )}
                                <div className="flex items-center space-x-1">
                                  <User className="w-4 h-4" />
                                  <span>{candidate.profile_completeness}% profile complete</span>
                                </div>
                              </div>
                            </div>
                            <div className="flex space-x-2">
                              {candidate.resume_url && (
                                <a
                                  href={getImageUrl(candidate.resume_url)}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="bg-slate-100 text-slate-700 px-4 py-2 rounded-lg hover:bg-slate-200 transition-colors text-sm flex items-center space-x-2"
                                >
                                  <FileText className="w-4 h-4" />
                                  <span>View CV</span>
                                </a>
                              )}
                              <button
                                onClick={() => window.location.href = `mailto:${candidate.email}`}
                                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm flex items-center space-x-2"
                              >
                                <Mail className="w-4 h-4" />
                                <span>Contact</span>
                              </button>
                            </div>
                          </div>

                          {/* Skills */}
                          {candidate.skills && candidate.skills.length > 0 && (
                            <div className="mb-4">
                              <h4 className="text-sm font-medium text-slate-700 mb-2">Skills</h4>
                              <div className="flex flex-wrap gap-2">
                                {candidate.skills.slice(0, 8).map((skill, index) => (
                                  <span
                                    key={index}
                                    className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm"
                                  >
                                    {skill}
                                  </span>
                                ))}
                                {candidate.skills.length > 8 && (
                                  <span className="text-slate-500 text-sm">+{candidate.skills.length - 8} more</span>
                                )}
                              </div>
                            </div>
                          )}

                          {/* Latest Experience */}
                          {candidate.experience && candidate.experience.length > 0 && (
                            <div>
                              <h4 className="text-sm font-medium text-slate-700 mb-2">Latest Experience</h4>
                              <div className="text-sm text-slate-600">
                                <p className="font-medium">{candidate.experience[0].job_title}</p>
                                <p>{candidate.experience[0].company}</p>
                                <p>{candidate.experience[0].start_date} - {candidate.experience[0].end_date || 'Present'}</p>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const CompanyProfileWrapper = () => {
  const { companyId } = useParams();
  return <CompanyProfilePage companyId={companyId} />;
};

const CompanyProfilePage = ({ companyId }) => {
  const [company, setCompany] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchCompanyProfile();
    fetchCompanyJobs();
  }, [companyId]);
  
  const fetchCompanyProfile = async () => {
    try {
      const response = await axios.get(`${API}/public/company/${companyId}`);
      setCompany(response.data);
    } catch (error) {
      console.error('Error fetching company profile:', error);
    }
  };
  
  const fetchCompanyJobs = async () => {
    try {
      const response = await axios.get(`${API}/public/company/${companyId}/jobs`);
      setJobs(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching company jobs:', error);
      setLoading(false);
    }
  };
  
  const formatJobPostedDate = (dateString) => {
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

  const isValidDescription = (description) => {
    if (!description || description.trim().length === 0) return false;
    
    // Check if description is just repeated characters (like "mmmmm...")
    const firstChar = description.trim().charAt(0);
    const isRepeatedChar = description.trim().split('').every(char => char === firstChar);
    
    if (isRepeatedChar) return false;
    
    // Check if description is too short or looks like test data
    if (description.trim().length < 10) return false;
    
    return true;
  };
  
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  if (!company) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-slate-800 mb-4">Company Not Found</h1>
          <p className="text-slate-600">The company profile you're looking for doesn't exist.</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Cover Image Section */}
      <div className="relative h-64 bg-gradient-to-r from-blue-600 to-slate-700 overflow-hidden">
        {company.company_cover_image_url && (
          <img 
            src={getImageUrl(company.company_cover_image_url)} 
            alt="Company cover"
            className="w-full h-full object-cover"
          />
        )}
        <div className="absolute inset-0 bg-black bg-opacity-40"></div>
      </div>
      
      {/* Company Info Section */}
      <div className="relative px-4 sm:px-6 lg:px-8 -mt-20">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-2xl shadow-xl p-6 sm:p-8">
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-6 mb-8">
              {/* Company Logo */}
              <div className="w-24 h-24 rounded-2xl overflow-hidden bg-gradient-to-br from-slate-100 to-slate-200 flex-shrink-0 shadow-lg ring-4 ring-white">
                <img 
                  src={getImageUrl(company.company_logo_url) || 'https://customer-assets.emergentagent.com/job_career-launchpad-16/artifacts/a6w1unn9_Leonardo_Phoenix_A_modern_sleek_logo_featuring_a_stylized_rock_2.jpg'} 
                  alt={`${company.company_name} logo`}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    e.target.src = 'https://customer-assets.emergentagent.com/job_career-launchpad-16/artifacts/a6w1unn9_Leonardo_Phoenix_A_modern_sleek_logo_featuring_a_stylized_rock_2.jpg';
                  }}
                />
              </div>
              
              {/* Company Details */}
              <div className="flex-1">
                <h1 className="text-3xl font-bold text-slate-800 mb-2">{company.company_name}</h1>
                <div className="flex flex-wrap items-center gap-4 text-slate-600 mb-4">
                  {company.company_location && (
                    <div className="flex items-center space-x-2">
                      <MapPin className="w-5 h-5" />
                      <span>{company.company_location}</span>
                    </div>
                  )}
                  {company.company_size && (
                    <div className="flex items-center space-x-2">
                      <Users className="w-5 h-5" />
                      <span>{company.company_size}</span>
                    </div>
                  )}
                  {company.company_industry && (
                    <div className="flex items-center space-x-2">
                      <Building2 className="w-5 h-5" />
                      <span>{company.company_industry}</span>
                    </div>
                  )}
                </div>
                
                <div className="flex items-center gap-4">
                  <div className="bg-blue-100 text-blue-800 px-4 py-2 rounded-full font-semibold">
                    {company.active_jobs_count} Active Jobs
                  </div>
                  {company.company_website && (
                    <a 
                      href={company.company_website} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 font-medium"
                    >
                      <ExternalLink className="w-5 h-5" />
                      <span>Website</span>
                    </a>
                  )}
                  {company.company_linkedin && (
                    <a 
                      href={company.company_linkedin} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 font-medium"
                    >
                      <ExternalLink className="w-5 h-5" />
                      <span>LinkedIn</span>
                    </a>
                  )}
                </div>
              </div>
            </div>
            
            {/* Company Description */}
            <div className="mb-8">
              <h2 className="text-xl font-bold text-slate-800 mb-4">About Us</h2>
              {company.company_description && isValidDescription(company.company_description) ? (
                <p className="text-slate-600 leading-relaxed">{company.company_description}</p>
              ) : (
                <div className="text-slate-600 leading-relaxed">
                  <p className="mb-4">
                    <strong>{company.company_name}</strong> is a leading company in the {company.company_industry || 'professional services'} industry, 
                    based in {company.company_location || 'South Africa'}.
                  </p>
                  {company.company_size && (
                    <p className="mb-4">
                      We are a {company.company_size} organization committed to excellence and innovation in our field.
                    </p>
                  )}
                  <p className="mb-4">
                    With {company.active_jobs_count} active job opportunities, we're always looking for talented individuals to join our growing team.
                  </p>
                  {(company.company_website || company.company_linkedin) && (
                    <p>
                      Learn more about our company culture and opportunities by visiting our 
                      {company.company_website && (
                        <>
                          {' '}
                          <a href={company.company_website} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                            website
                          </a>
                        </>
                      )}
                      {company.company_website && company.company_linkedin && ' or '}
                      {company.company_linkedin && (
                        <>
                          <a href={company.company_linkedin} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                            LinkedIn page
                          </a>
                        </>
                      )}.
                    </p>
                  )}
                </div>
              )}
            </div>
            
            {/* Jobs Section */}
            <div>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-slate-800">Open Positions ({jobs.length})</h2>
                {jobs.length > 0 && (
                  <button 
                    onClick={() => window.location.href = `/jobs?company=${companyId}`}
                    className="text-blue-600 hover:text-blue-700 font-medium flex items-center space-x-2"
                  >
                    <span>View All Jobs</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                )}
              </div>
              
              {jobs.length === 0 ? (
                <div className="text-center py-8 text-slate-500">
                  <Briefcase className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>No active job openings at the moment.</p>
                </div>
              ) : (
                <div className="max-h-96 overflow-y-auto space-y-4 pr-2">
                  {jobs.slice(0, 10).map((job) => (
                    <div key={job.id} className="border border-slate-200 rounded-xl p-4 hover:shadow-md transition-shadow bg-white">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="font-bold text-slate-800 mb-2 text-lg">{job.title}</h3>
                          <div className="flex flex-wrap items-center gap-4 text-sm text-slate-600 mb-3">
                            <div className="flex items-center space-x-1">
                              <MapPin className="w-4 h-4" />
                              <span>{job.location}</span>
                            </div>
                            <div className="flex items-center space-x-1">
                              <Briefcase className="w-4 h-4" />
                              <span>{job.job_type}</span>
                            </div>
                            <div className="flex items-center space-x-1">
                              <Clock className="w-4 h-4" />
                              <span>{formatJobPostedDate(job.posted_date)}</span>
                            </div>
                          </div>
                          {job.salary && (
                            <div className="text-green-600 font-semibold mb-2 text-lg">
                              R{job.salary}
                            </div>
                          )}
                          {job.description && (
                            <p className="text-slate-600 text-sm mb-3 line-clamp-2">
                              {job.description.length > 100 ? `${job.description.substring(0, 100)}...` : job.description}
                            </p>
                          )}
                        </div>
                        <button 
                          onClick={() => window.location.href = `/jobs?search=${encodeURIComponent(job.title)}`}
                          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors ml-4 flex-shrink-0"
                        >
                          View Job
                        </button>
                      </div>
                    </div>
                  ))}
                  {jobs.length > 10 && (
                    <div className="text-center py-4">
                      <button 
                        onClick={() => window.location.href = `/jobs?company=${companyId}`}
                        className="text-blue-600 hover:text-blue-700 font-medium"
                      >
                        View {jobs.length - 10} More Jobs →
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const JobCard = ({ job, user, onSave, onApply, onJobClick }) => {
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
                  onClick={handleJobTitleClick}
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
                  <span 
                    className="font-medium hover:text-blue-600 cursor-pointer transition-colors hover:underline truncate"
                    onClick={(e) => {
                      e.stopPropagation();
                      window.location.href = `/company/${job.company_id}`;
                    }}
                  >
                    {job.company_name}
                  </span>
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
                <div className="flex items-center space-x-2 text-emerald-700 font-bold mb-4 bg-emerald-50 px-3 py-2 rounded-lg w-fit">
                  <Banknote className="w-4 h-4" />
                  <span>{job.salary}</span>
                </div>
              )}
              
              <p className="text-slate-700 mb-6 leading-relaxed line-clamp-2">
                {job.description}
              </p>
              
              <div className="flex items-center justify-between">
                <div className="flex flex-wrap items-center gap-3">
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
                <div className="flex items-center space-x-2 ml-4">
                  <ApplyButton 
                    job={job}
                    user={user}
                    onApplicationSuccess={(applicationData) => {
                      console.log('Application submitted:', applicationData);
                    }}
                  />
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      onSave && onSave(job.id);
                    }}
                    className="hover:bg-red-50 hover:text-red-600 rounded-full p-2 transition-all duration-300"
                  >
                    <Heart className={`w-5 h-5 ${job.saved ? 'fill-red-500 text-red-500' : 'text-slate-400'}`} />
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

const JobListingPage = ({ user, onLogout }) => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [location, setLocation] = useState("");
  const [filters, setFilters] = useState({
    datePosted: {
      newJobs: false,
      lastWeek: false
    },
    workFromHome: {
      partiallyRemote: false,
      fullyRemote: false
    },
    applicationMethod: {
      onCompanyWebsite: false,
      easyApply: false
    },
    functions: {
      engineering: false,
      production: false,
      itTelecom: false,
      salesPurchasing: false,
      accounting: false,
      banking: false
    }
  });

  // Handle filter changes
  const handleFilterChange = (category, filterKey, value) => {
    setFilters(prevFilters => ({
      ...prevFilters,
      [category]: {
        ...prevFilters[category],
        [filterKey]: value
      }
    }));
  };
  
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
    // Search and location filters
    const matchesSearch = job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         job.company_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         job.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesLocation = !location || job.location.toLowerCase().includes(location.toLowerCase());
    
    // Date Posted filters
    let matchesDatePosted = true;
    if (filters.datePosted.newJobs || filters.datePosted.lastWeek) {
      const jobDate = new Date(job.posted_date);
      const now = new Date();
      const daysDiff = Math.floor((now - jobDate) / (1000 * 60 * 60 * 24));
      
      if (filters.datePosted.newJobs && daysDiff > 1) {
        matchesDatePosted = false;
      }
      if (filters.datePosted.lastWeek && daysDiff > 7) {
        matchesDatePosted = false;
      }
    }
    
    // Work From Home filters
    let matchesWorkFromHome = true;
    if (filters.workFromHome.partiallyRemote || filters.workFromHome.fullyRemote) {
      const workType = job.work_type?.toLowerCase() || '';
      matchesWorkFromHome = false;
      
      if (filters.workFromHome.partiallyRemote && (workType.includes('hybrid') || workType.includes('partial'))) {
        matchesWorkFromHome = true;
      }
      if (filters.workFromHome.fullyRemote && workType.includes('remote')) {
        matchesWorkFromHome = true;
      }
    }
    
    // Application Method filters (assuming Easy Apply is available for all jobs)
    let matchesApplicationMethod = true;
    if (filters.applicationMethod.onCompanyWebsite || filters.applicationMethod.easyApply) {
      matchesApplicationMethod = false;
      
      if (filters.applicationMethod.easyApply) {
        matchesApplicationMethod = true; // All jobs have Easy Apply
      }
      if (filters.applicationMethod.onCompanyWebsite && job.external_url) {
        matchesApplicationMethod = true;
      }
    }
    
    // Functions/Industry filters
    let matchesFunctions = true;
    const hasAnyFunctionFilter = Object.values(filters.functions).some(val => val);
    if (hasAnyFunctionFilter) {
      const jobIndustry = job.industry?.toLowerCase() || '';
      const jobTitle = job.title?.toLowerCase() || '';
      matchesFunctions = false;
      
      if (filters.functions.engineering && (
        jobIndustry.includes('technology') || 
        jobIndustry.includes('engineering') || 
        jobTitle.includes('engineer') || 
        jobTitle.includes('developer') || 
        jobTitle.includes('technical')
      )) {
        matchesFunctions = true;
      }
      if (filters.functions.production && (
        jobIndustry.includes('manufacturing') || 
        jobIndustry.includes('production') ||
        jobTitle.includes('production') ||
        jobTitle.includes('manufacturing')
      )) {
        matchesFunctions = true;
      }
      if (filters.functions.it && (
        jobIndustry.includes('technology') || 
        jobIndustry.includes('software') || 
        jobIndustry.includes('it') ||
        jobTitle.includes('it ') ||
        jobTitle.includes('software')
      )) {
        matchesFunctions = true;
      }
      if (filters.functions.sales && (
        jobIndustry.includes('sales') || 
        jobTitle.includes('sales') ||
        jobTitle.includes('marketing')
      )) {
        matchesFunctions = true;
      }
      if (filters.functions.accounting && (
        jobIndustry.includes('finance') || 
        jobIndustry.includes('accounting') ||
        jobTitle.includes('accountant') ||
        jobTitle.includes('finance')
      )) {
        matchesFunctions = true;
      }
      if (filters.functions.banking && (
        jobIndustry.includes('banking') || 
        jobIndustry.includes('financial') ||
        jobTitle.includes('bank') ||
        jobTitle.includes('financial')
      )) {
        matchesFunctions = true;
      }
    }
    
    return matchesSearch && matchesLocation && matchesDatePosted && matchesWorkFromHome && matchesApplicationMethod && matchesFunctions;
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
          
          <div className="flex flex-col sm:flex-row gap-4 max-w-4xl mx-auto">
            <div className="relative flex-1">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5 sm:w-6 sm:h-6" />
              <Input
                type="text"
                placeholder="Job title, keywords"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 sm:pl-12 h-12 sm:h-16 text-base sm:text-lg font-medium bg-white/90 backdrop-blur-sm border-0 shadow-2xl rounded-2xl focus:ring-4 focus:ring-blue-500/30 focus:bg-white transition-all"
              />
            </div>
            <div className="relative flex-1">
              <MapPin className="absolute left-4 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5 sm:w-6 sm:h-6" />
              <Input
                type="text"
                placeholder="City, province"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="pl-10 sm:pl-12 h-12 sm:h-16 text-base sm:text-lg font-medium bg-white/90 backdrop-blur-sm border-0 shadow-2xl rounded-2xl focus:ring-4 focus:ring-blue-500/30 focus:bg-white transition-all"
              />
            </div>
            <Button className="bg-gradient-to-r from-blue-600 to-slate-700 hover:from-blue-700 hover:to-slate-800 h-12 sm:h-16 px-6 sm:px-12 text-base sm:text-lg font-bold shadow-2xl rounded-2xl hover:shadow-3xl transform hover:scale-105 transition-all duration-300 whitespace-nowrap">
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
                    functions: { engineering: false, production: false, it: false, sales: false, accounting: false, banking: false }
                  })}
                  className="text-slate-500 hover:text-slate-700"
                >
                  Clear All
                </Button>
              </div>

              <FilterSection title="Date Posted" defaultExpanded={true}>
                <FilterOption 
                  label="New jobs" 
                  count={jobs.filter(job => {
                    const daysDiff = Math.floor((new Date() - new Date(job.posted_date)) / (1000 * 60 * 60 * 24));
                    return daysDiff <= 1;
                  }).length}
                  selected={filters.datePosted.newJobs}
                  onChange={(checked) => handleFilterChange('datePosted', 'newJobs', checked)}
                />
                <FilterOption 
                  label="Last week" 
                  count={jobs.filter(job => {
                    const daysDiff = Math.floor((new Date() - new Date(job.posted_date)) / (1000 * 60 * 60 * 24));
                    return daysDiff <= 7;
                  }).length}
                  selected={filters.datePosted.lastWeek}
                  onChange={(checked) => handleFilterChange('datePosted', 'lastWeek', checked)}
                />
              </FilterSection>

              <FilterSection title="Work From Home" defaultExpanded={true}>
                <FilterOption 
                  label="Partially remote" 
                  count={jobs.filter(job => job.work_type?.toLowerCase().includes('hybrid')).length}
                  selected={filters.workFromHome.partiallyRemote}
                  onChange={(checked) => handleFilterChange('workFromHome', 'partiallyRemote', checked)}
                />
                <FilterOption 
                  label="Fully remote" 
                  count={jobs.filter(job => job.work_type?.toLowerCase().includes('remote')).length}
                  selected={filters.workFromHome.fullyRemote}
                  onChange={(checked) => handleFilterChange('workFromHome', 'fullyRemote', checked)}
                />
              </FilterSection>

              <FilterSection title="Application Method" defaultExpanded={true}>
                <FilterOption 
                  label="On company website" 
                  count={jobs.filter(job => job.external_url).length}
                  selected={filters.applicationMethod.onCompanyWebsite}
                  onChange={(checked) => handleFilterChange('applicationMethod', 'onCompanyWebsite', checked)}
                />
                <FilterOption 
                  label="Easy Apply" 
                  count={jobs.length}
                  selected={filters.applicationMethod.easyApply}
                  onChange={(checked) => handleFilterChange('applicationMethod', 'easyApply', checked)}
                />
              </FilterSection>

              <FilterSection title="Functions" defaultExpanded={true}>
                <FilterOption 
                  label="Engineering, Technical" 
                  count={jobs.filter(job => {
                    const industry = job.industry?.toLowerCase() || '';
                    const title = job.title?.toLowerCase() || '';
                    return industry.includes('technology') || industry.includes('engineering') || 
                           title.includes('engineer') || title.includes('developer') || title.includes('technical');
                  }).length}
                  selected={filters.functions.engineering}
                  onChange={(checked) => handleFilterChange('functions', 'engineering', checked)}
                />
                <FilterOption 
                  label="Production & Manufacturing" 
                  count={jobs.filter(job => {
                    const industry = job.industry?.toLowerCase() || '';
                    const title = job.title?.toLowerCase() || '';
                    return industry.includes('manufacturing') || industry.includes('production') ||
                           title.includes('production') || title.includes('manufacturing');
                  }).length}
                  selected={filters.functions.production}
                  onChange={(checked) => handleFilterChange('functions', 'production', checked)}
                />
                <FilterOption 
                  label="IT & Telecommunications" 
                  count={jobs.filter(job => {
                    const industry = job.industry?.toLowerCase() || '';
                    const title = job.title?.toLowerCase() || '';
                    return industry.includes('technology') || industry.includes('software') || 
                           industry.includes('it') || title.includes('it ') || title.includes('software');
                  }).length}
                  selected={filters.functions.it}
                  onChange={(checked) => handleFilterChange('functions', 'it', checked)}
                />
                <FilterOption 
                  label="Sales & Purchasing" 
                  count={jobs.filter(job => {
                    const industry = job.industry?.toLowerCase() || '';
                    const title = job.title?.toLowerCase() || '';
                    return industry.includes('sales') || title.includes('sales') || title.includes('marketing');
                  }).length}
                  selected={filters.functions.sales}
                  onChange={(checked) => handleFilterChange('functions', 'sales', checked)}
                />
                <FilterOption 
                  label="Accounting, Auditing" 
                  count={jobs.filter(job => {
                    const industry = job.industry?.toLowerCase() || '';
                    const title = job.title?.toLowerCase() || '';
                    return industry.includes('finance') || industry.includes('accounting') ||
                           title.includes('accountant') || title.includes('finance');
                  }).length}
                  selected={filters.functions.accounting}
                  onChange={(checked) => handleFilterChange('functions', 'accounting', checked)}
                />
                <FilterOption 
                  label="Banking, Finance" 
                  count={jobs.filter(job => {
                    const industry = job.industry?.toLowerCase() || '';
                    const title = job.title?.toLowerCase() || '';
                    return industry.includes('banking') || industry.includes('financial') ||
                           title.includes('bank') || title.includes('financial');
                  }).length}
                  selected={filters.functions.banking}
                  onChange={(checked) => handleFilterChange('functions', 'banking', checked)}
                />
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

            <div className="grid grid-cols-1 gap-6 lg:gap-8">
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
            <Route path="/jobs" element={
              <JobListingPage 
                user={null} 
                onLogout={handleLogout}
              />
            } />
            <Route path="/company/:companyId" element={
              <CompanyProfileWrapper />
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

              <Route path="/company/:companyId" element={
                <CompanyProfileWrapper />
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

              <Route path="/cv-search" element={
                user.role === 'recruiter' ? (
                  <CVSearchPage user={user} />
                ) : (
                  <Navigate to="/" replace />
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