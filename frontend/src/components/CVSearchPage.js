import React, { useState, useEffect } from 'react';
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { 
  Search,
  User,
  MapPin,
  Mail,
  Phone,
  Briefcase,
  DollarSign,
  Calendar,
  FileText,
  Eye,
  EyeOff,
  Lock,
  Unlock,
  Filter,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  ArrowUpRight,
  Zap,
  Clock,
  Download
} from "lucide-react";
import axios from 'axios';
import { useToast } from "../hooks/use-toast";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CVSearchPage = ({ user }) => {
  const { toast } = useToast();
  const [accessInfo, setAccessInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [revealing, setRevealing] = useState(null);
  const [showFilters, setShowFilters] = useState(true);
  const [hasSearched, setHasSearched] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const [totalResults, setTotalResults] = useState(0);
  
  // Search criteria
  const [searchCriteria, setSearchCriteria] = useState({
    q: '',
    skills: '',
    location: '',
    experience_min: '',
    experience_max: '',
    industry: '',
    salary_min: '',
    salary_max: '',
    availability: ''
  });

  const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    return {
      headers: { 'Authorization': `Bearer ${token}` }
    };
  };

  // Check CV search access on mount
  useEffect(() => {
    const checkAccess = async () => {
      try {
        const response = await axios.get(`${API}/cv-search/access`, getAuthHeaders());
        setAccessInfo(response.data);
      } catch (error) {
        console.error('Error checking CV search access:', error);
        if (error.response?.status === 403) {
          setAccessInfo({ has_access: false, upgrade_required: true });
        }
      } finally {
        setLoading(false);
      }
    };
    
    if (user?.role === 'recruiter') {
      checkAccess();
    } else {
      setLoading(false);
    }
  }, [user]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setSearchCriteria(prev => ({ ...prev, [name]: value }));
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setSearching(true);
    
    try {
      const params = new URLSearchParams();
      Object.entries(searchCriteria).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });

      const response = await axios.get(`${API}/cv-search?${params.toString()}`, getAuthHeaders());
      
      setSearchResults(response.data.candidates || []);
      setTotalResults(response.data.total || 0);
      setHasSearched(true);
      
      // Update access info with latest reveals count
      if (accessInfo) {
        setAccessInfo(prev => ({
          ...prev,
          searches_this_month: response.data.searches_this_month
        }));
      }
      
    } catch (error) {
      console.error('CV search error:', error);
      
      if (error.response?.status === 403) {
        const detail = error.response.data?.detail;
        if (detail?.error === 'upgrade_required') {
          toast({
            title: "Upgrade Required",
            description: detail.message || "CV Search requires a Growth plan or higher.",
            variant: "destructive",
          });
        }
      } else {
        toast({
          title: "Search Failed",
          description: error.response?.data?.detail || "An error occurred while searching.",
          variant: "destructive",
        });
      }
      setSearchResults([]);
    } finally {
      setSearching(false);
    }
  };

  const handleRevealContact = async (candidateId) => {
    setRevealing(candidateId);
    
    try {
      const response = await axios.post(`${API}/cv-search/reveal/${candidateId}`, {}, getAuthHeaders());
      
      if (response.data.success) {
        // Update the candidate in results with revealed contact info
        setSearchResults(prev => prev.map(c => 
          c.id === candidateId 
            ? { 
                ...c, 
                ...response.data.candidate,
                contact_revealed: true 
              }
            : c
        ));
        
        // Update access info
        if (accessInfo) {
          setAccessInfo(prev => ({
            ...prev,
            contact_reveals_used: response.data.reveals_used,
            contact_reveals_remaining: response.data.reveals_remaining
          }));
        }
        
        toast({
          title: response.data.already_revealed ? "Contact Already Revealed" : "Contact Revealed",
          description: response.data.already_revealed 
            ? "You've already revealed this contact."
            : `${response.data.reveals_remaining} reveals remaining this month.`,
          variant: "success",
        });
      }
    } catch (error) {
      console.error('Error revealing contact:', error);
      
      if (error.response?.status === 402) {
        const detail = error.response.data?.detail;
        toast({
          title: "Reveal Limit Reached",
          description: detail?.message || "You have used all your contact reveals for this month.",
          variant: "destructive",
        });
      } else {
        toast({
          title: "Reveal Failed",
          description: error.response?.data?.detail || "Failed to reveal contact.",
          variant: "destructive",
        });
      }
    } finally {
      setRevealing(null);
    }
  };

  const clearFilters = () => {
    setSearchCriteria({
      q: '',
      skills: '',
      location: '',
      experience_min: '',
      experience_max: '',
      industry: '',
      salary_min: '',
      salary_max: '',
      availability: ''
    });
  };

  // Non-recruiter access denied
  if (user?.role !== 'recruiter') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <Card className="max-w-md">
          <CardContent className="pt-6 text-center">
            <Lock className="w-12 h-12 mx-auto mb-4 text-slate-400" />
            <h2 className="text-xl font-bold text-slate-800 mb-2">Access Denied</h2>
            <p className="text-slate-600">Only recruiters can access CV search functionality.</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Starter tier - no access
  if (accessInfo?.upgrade_required || !accessInfo?.has_access) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="container mx-auto px-4 py-12">
          <div className="max-w-2xl mx-auto">
            <Card className="shadow-xl border-0 overflow-hidden">
              <div className="bg-gradient-to-r from-blue-600 to-slate-700 p-8 text-white text-center">
                <Lock className="w-16 h-16 mx-auto mb-4 opacity-80" />
                <h1 className="text-3xl font-bold mb-2">Upgrade to Growth</h1>
                <p className="text-blue-100">Unlock access to our CV database and find your perfect candidates</p>
              </div>
              
              <CardContent className="p-8">
                <div className="space-y-4 mb-8">
                  <h3 className="font-semibold text-slate-800">CV Search includes:</h3>
                  <ul className="space-y-3">
                    {[
                      "Access to thousands of active job seekers",
                      "Search by skills, location, experience & more",
                      "1,500 contact reveals per month",
                      "Passive candidate sourcing",
                      "Skills matching"
                    ].map((feature, i) => (
                      <li key={i} className="flex items-center text-slate-600">
                        <div className="w-5 h-5 rounded-full bg-green-100 flex items-center justify-center mr-3">
                          <Zap className="w-3 h-3 text-green-600" />
                        </div>
                        {feature}
                      </li>
                    ))}
                  </ul>
                </div>
                
                <div className="flex flex-col sm:flex-row gap-4">
                  <Button 
                    onClick={() => window.location.href = '/pricing'}
                    className="flex-1 bg-blue-600 hover:bg-blue-700"
                  >
                    <ArrowUpRight className="w-4 h-4 mr-2" />
                    Upgrade to Growth
                  </Button>
                  <Button 
                    variant="outline"
                    onClick={() => window.location.href = '/recruiter'}
                    className="flex-1"
                  >
                    Back to Dashboard
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
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
            <div className="flex flex-col md:flex-row md:items-center md:justify-between">
              <div>
                <h1 className="text-3xl font-bold text-slate-800 mb-2">CV Search</h1>
                <p className="text-slate-600">Search and discover talented candidates for your open positions</p>
              </div>
              
              {/* Usage Stats */}
              <div className="mt-4 md:mt-0 flex flex-wrap gap-3">
                <Badge variant="outline" className="px-3 py-1.5 bg-white">
                  <Eye className="w-4 h-4 mr-1.5 text-blue-600" />
                  <span className="font-medium">{accessInfo?.contact_reveals_remaining?.toLocaleString()}</span>
                  <span className="text-slate-500 ml-1">reveals left</span>
                </Badge>
                <Badge variant="outline" className="px-3 py-1.5 bg-white">
                  <Search className="w-4 h-4 mr-1.5 text-slate-600" />
                  <span className="font-medium">{accessInfo?.searches_this_month?.toLocaleString() || 0}</span>
                  <span className="text-slate-500 ml-1">searches</span>
                </Badge>
                <Badge className="px-3 py-1.5 bg-blue-100 text-blue-800 border-0">
                  {accessInfo?.tier_name} Plan
                </Badge>
              </div>
            </div>
          </div>

          {/* Search Form */}
          <Card className="shadow-xl border-0 mb-8">
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg flex items-center">
                  <Filter className="w-5 h-5 mr-2 text-blue-600" />
                  Search Filters
                </CardTitle>
                <div className="flex items-center gap-2">
                  <Button variant="ghost" size="sm" onClick={clearFilters}>
                    Clear All
                  </Button>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={() => setShowFilters(!showFilters)}
                  >
                    {showFilters ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </Button>
                </div>
              </div>
            </CardHeader>
            
            {showFilters && (
              <CardContent>
                <form onSubmit={handleSearch} className="space-y-6">
                  {/* Primary Search */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1.5">
                        Keywords
                      </label>
                      <Input
                        name="q"
                        value={searchCriteria.q}
                        onChange={handleInputChange}
                        placeholder="Job title, name, or keywords..."
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1.5">
                        Skills
                      </label>
                      <Input
                        name="skills"
                        value={searchCriteria.skills}
                        onChange={handleInputChange}
                        placeholder="JavaScript, Python, React..."
                      />
                      <p className="text-xs text-slate-500 mt-1">Separate with commas</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1.5">
                        Location
                      </label>
                      <Input
                        name="location"
                        value={searchCriteria.location}
                        onChange={handleInputChange}
                        placeholder="Cape Town, Johannesburg..."
                      />
                    </div>
                  </div>

                  {/* Advanced Filters */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1.5">
                        Industry
                      </label>
                      <Input
                        name="industry"
                        value={searchCriteria.industry}
                        onChange={handleInputChange}
                        placeholder="Technology, Finance..."
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1.5">
                        Min Experience (years)
                      </label>
                      <Input
                        type="number"
                        name="experience_min"
                        value={searchCriteria.experience_min}
                        onChange={handleInputChange}
                        placeholder="0"
                        min="0"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1.5">
                        Max Experience (years)
                      </label>
                      <Input
                        type="number"
                        name="experience_max"
                        value={searchCriteria.experience_max}
                        onChange={handleInputChange}
                        placeholder="20"
                        min="0"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1.5">
                        Availability
                      </label>
                      <select
                        name="availability"
                        value={searchCriteria.availability}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="">Any</option>
                        <option value="immediately">Immediately</option>
                        <option value="2_weeks">2 Weeks Notice</option>
                        <option value="1_month">1 Month Notice</option>
                        <option value="3_months">3+ Months Notice</option>
                      </select>
                    </div>
                  </div>

                  {/* Salary Range */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1.5">
                        Min Salary Expectation (ZAR/month)
                      </label>
                      <Input
                        type="number"
                        name="salary_min"
                        value={searchCriteria.salary_min}
                        onChange={handleInputChange}
                        placeholder="30000"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1.5">
                        Max Salary Expectation (ZAR/month)
                      </label>
                      <Input
                        type="number"
                        name="salary_max"
                        value={searchCriteria.salary_max}
                        onChange={handleInputChange}
                        placeholder="100000"
                      />
                    </div>
                  </div>

                  <div className="flex justify-center pt-4">
                    <Button
                      type="submit"
                      disabled={searching}
                      className="px-8 bg-blue-600 hover:bg-blue-700"
                    >
                      {searching ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                          Searching...
                        </>
                      ) : (
                        <>
                          <Search className="w-4 h-4 mr-2" />
                          Search CVs
                        </>
                      )}
                    </Button>
                  </div>
                </form>
              </CardContent>
            )}
          </Card>

          {/* Results */}
          {hasSearched && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-slate-800">
                  {totalResults.toLocaleString()} Candidates Found
                </h2>
              </div>

              {searchResults.length === 0 ? (
                <Card className="shadow-lg border-0">
                  <CardContent className="py-12 text-center">
                    <User className="w-16 h-16 mx-auto mb-4 text-slate-300" />
                    <h3 className="text-lg font-medium text-slate-700 mb-2">No candidates found</h3>
                    <p className="text-slate-500">Try adjusting your search filters</p>
                  </CardContent>
                </Card>
              ) : (
                <div className="grid gap-4">
                  {searchResults.map((candidate) => (
                    <CandidateCard 
                      key={candidate.id} 
                      candidate={candidate}
                      onReveal={handleRevealContact}
                      revealing={revealing === candidate.id}
                    />
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

// Candidate Card Component
const CandidateCard = ({ candidate, onReveal, revealing }) => {
  const isRevealed = candidate.contact_revealed;

  return (
    <Card className="shadow-lg border-0 hover:shadow-xl transition-shadow">
      <CardContent className="p-6">
        <div className="flex flex-col md:flex-row md:items-start gap-6">
          {/* Avatar & Basic Info */}
          <div className="flex-shrink-0">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-slate-600 rounded-full flex items-center justify-center text-white text-xl font-bold">
              {(candidate.first_name?.[0] || '?')}{(candidate.last_name?.[0] || '')}
            </div>
          </div>

          {/* Main Info */}
          <div className="flex-1 min-w-0">
            <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
              <div>
                <h3 className="text-lg font-bold text-slate-800">
                  {candidate.first_name} {candidate.last_name}
                </h3>
                {candidate.headline && (
                  <p className="text-slate-600 mt-0.5">{candidate.headline}</p>
                )}
                
                <div className="flex flex-wrap gap-3 mt-3 text-sm text-slate-600">
                  {candidate.location && (
                    <span className="flex items-center">
                      <MapPin className="w-4 h-4 mr-1 text-slate-400" />
                      {candidate.location}
                    </span>
                  )}
                  {candidate.years_experience && (
                    <span className="flex items-center">
                      <Briefcase className="w-4 h-4 mr-1 text-slate-400" />
                      {candidate.years_experience} years exp.
                    </span>
                  )}
                  {candidate.expected_salary && (
                    <span className="flex items-center">
                      <span className="font-semibold mr-1 text-slate-400">R</span>
                      {candidate.expected_salary.toLocaleString()}/mo
                    </span>
                  )}
                  {candidate.availability_status && (
                    <span className="flex items-center">
                      <Clock className="w-4 h-4 mr-1 text-slate-400" />
                      {candidate.availability_status.replace('_', ' ')}
                    </span>
                  )}
                </div>
              </div>

              {/* Contact Info / Reveal Button */}
              <div className="flex-shrink-0">
                {isRevealed ? (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4 space-y-2">
                    <div className="flex items-center text-green-700">
                      <Unlock className="w-4 h-4 mr-2" />
                      <span className="font-medium text-sm">Contact Revealed</span>
                    </div>
                    {candidate.email && (
                      <a href={`mailto:${candidate.email}`} className="flex items-center text-sm text-slate-700 hover:text-blue-600">
                        <Mail className="w-4 h-4 mr-2 text-slate-400" />
                        {candidate.email}
                      </a>
                    )}
                    {candidate.phone && (
                      <a href={`tel:${candidate.phone}`} className="flex items-center text-sm text-slate-700 hover:text-blue-600">
                        <Phone className="w-4 h-4 mr-2 text-slate-400" />
                        {candidate.phone}
                      </a>
                    )}
                  </div>
                ) : (
                  <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                    <div className="text-sm text-slate-500 mb-3">
                      {candidate.email_masked && (
                        <div className="flex items-center mb-1">
                          <Mail className="w-4 h-4 mr-2 text-slate-400" />
                          <span className="text-slate-400">{candidate.email_masked}</span>
                        </div>
                      )}
                      {candidate.phone_masked && (
                        <div className="flex items-center">
                          <Phone className="w-4 h-4 mr-2 text-slate-400" />
                          <span className="text-slate-400">{candidate.phone_masked}</span>
                        </div>
                      )}
                    </div>
                    <Button
                      onClick={() => onReveal(candidate.id)}
                      disabled={revealing}
                      size="sm"
                      className="w-full bg-blue-600 hover:bg-blue-700"
                    >
                      {revealing ? (
                        <>
                          <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white mr-2"></div>
                          Revealing...
                        </>
                      ) : (
                        <>
                          <Eye className="w-4 h-4 mr-2" />
                          Reveal Contact
                        </>
                      )}
                    </Button>
                  </div>
                )}
              </div>
            </div>

            {/* Skills */}
            {candidate.skills && candidate.skills.length > 0 && (
              <div className="mt-4">
                <div className="flex flex-wrap gap-2">
                  {candidate.skills.slice(0, 10).map((skill, i) => (
                    <Badge key={i} variant="secondary" className="bg-blue-50 text-blue-700 border-0">
                      {skill}
                    </Badge>
                  ))}
                  {candidate.skills.length > 10 && (
                    <Badge variant="outline" className="text-slate-500">
                      +{candidate.skills.length - 10} more
                    </Badge>
                  )}
                </div>
              </div>
            )}

            {/* About */}
            {candidate.about_me && (
              <p className="mt-4 text-sm text-slate-600 line-clamp-2">
                {candidate.about_me}
              </p>
            )}

            {/* Actions */}
            <div className="mt-4 flex gap-3">
              {candidate.cv_url && (
                <Button variant="outline" size="sm" asChild>
                  <a href={`${BACKEND_URL}${candidate.cv_url}`} target="_blank" rel="noopener noreferrer">
                    <FileText className="w-4 h-4 mr-1.5" />
                    View CV
                  </a>
                </Button>
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default CVSearchPage;
