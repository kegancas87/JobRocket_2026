import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
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
  Filter
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Mock data for job listings
const mockJobs = [
  {
    id: "1",
    title: "R & D Manager / Workshop",
    company: "ESG Recruitment",
    location: "JHB - Eastern Suburbs",
    description: "Experience as a R & D Manager / Workshop * 5 - 8 years experience in R & D Management / workshop more",
    postedDate: "1 day ago",
    logo: "https://images.unsplash.com/photo-1496200186974-4293800e2c20?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODF8MHwxfHNlYXJjaHwxfHxjb21wYW55JTIwbG9nb3N8ZW58MHx8fHwxNzU1MzUzMDk0fDA&ixlib=rb-4.1.0&q=85",
    type: "Full-time",
    remote: false,
    saved: false
  },
  {
    id: "2",
    title: "Senior Site Manager (Construction)",
    company: "R & D Contracting",
    location: "Johannesburg / Durban",
    salary: "R18000 + R3000 KPA On Success 3 Month Probation",
    description: "R & D Contracting",
    postedDate: "5 days ago",
    logo: "https://images.unsplash.com/photo-1621831337128-35676ca30868?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHw0fHxvZmZpY2UlMjBidWlsZGluZ3N8ZW58MHx8fHwxNzU1MzUzMDk5fDA&ixlib=rb-4.1.0&q=85",
    type: "Full-time",
    remote: false,
    saved: false
  },
  {
    id: "3",
    title: "Principal Development Engineer (Software)",
    company: "E and D Recruiters",
    location: "Somerset West",
    description: "E and D Recruiters",
    postedDate: "1 day ago",
    logo: "https://images.unsplash.com/photo-1712159018726-4564d92f3ec2?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHw0fHx0ZWNoJTIwY29tcGFuaWVzfGVufDB8fHx8MTc1NTM1MzEwNHww&ixlib=rb-4.1.0&q=85",
    type: "Full-time",
    remote: true,
    saved: false
  },
  {
    id: "4",
    title: "Electrical Engineer: Renewable Energy PrEng",
    company: "Green Energy Solutions",
    location: "Cape Town",
    description: "Leading renewable energy company seeking experienced Electrical Engineer",
    postedDate: "3 days ago",
    logo: "https://images.unsplash.com/photo-1608145390633-195fd7d33de2?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHwzfHx0ZWNoJTIwY29tcGFuaWVzfGVufDB8fHx8MTc1NTM1MzEwNHww&ixlib=rb-4.1.0&q=85",
    type: "Full-time",
    remote: false,
    saved: false
  }
];

const JobCard = ({ job, onSave }) => (
  <Card className="group cursor-pointer hover:shadow-lg transition-all duration-300 border-l-4 border-l-teal-500 hover:border-l-teal-600">
    <CardContent className="p-6">
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-4 flex-1">
          <div className="w-16 h-16 rounded-lg overflow-hidden bg-gray-100 flex-shrink-0">
            <img 
              src={job.logo} 
              alt={`${job.company} logo`}
              className="w-full h-full object-cover"
            />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="text-xl font-semibold text-gray-900 mb-2 group-hover:text-teal-700 transition-colors">
              {job.title}
            </h3>
            <div className="flex items-center space-x-4 text-sm text-gray-600 mb-3">
              <div className="flex items-center space-x-1">
                <Building2 className="w-4 h-4" />
                <span>{job.company}</span>
              </div>
              <div className="flex items-center space-x-1">
                <MapPin className="w-4 h-4" />
                <span>{job.location}</span>
              </div>
            </div>
            {job.salary && (
              <div className="text-sm font-medium text-red-600 mb-2">
                {job.salary}
              </div>
            )}
            <p className="text-gray-700 text-sm mb-3 line-clamp-2">
              {job.description}
            </p>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Badge variant="secondary" className="text-xs">
                  {job.type}
                </Badge>
                {job.remote && (
                  <Badge variant="outline" className="text-xs">
                    Remote
                  </Badge>
                )}
              </div>
              <span className="text-xs text-gray-500">{job.postedDate}</span>
            </div>
          </div>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={(e) => {
            e.stopPropagation();
            onSave(job.id);
          }}
          className="ml-4 hover:bg-red-50 hover:text-red-600"
        >
          <Heart className={`w-5 h-5 ${job.saved ? 'fill-red-500 text-red-500' : ''}`} />
        </Button>
      </div>
    </CardContent>
  </Card>
);

const FilterSection = ({ title, children, defaultExpanded = true }) => {
  const [expanded, setExpanded] = useState(defaultExpanded);
  
  return (
    <div className="border-b pb-4 mb-6">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center justify-between w-full text-left text-lg font-medium text-gray-900 mb-3"
      >
        {title}
        <ChevronDown className={`w-5 h-5 transition-transform ${expanded ? 'rotate-180' : ''}`} />
      </button>
      {expanded && <div className="space-y-2">{children}</div>}
    </div>
  );
};

const FilterOption = ({ label, count, selected, onChange }) => (
  <label className="flex items-center justify-between cursor-pointer hover:bg-gray-50 p-2 rounded">
    <div className="flex items-center space-x-2">
      <input
        type="checkbox"
        checked={selected}
        onChange={onChange}
        className="rounded border-gray-300 text-teal-600 focus:ring-teal-500"
      />
      <span className="text-sm text-gray-700">{label}</span>
    </div>
    {count && <span className="text-xs text-gray-500 bg-gray-200 px-2 py-1 rounded">{count}</span>}
  </label>
);

const JobListingPage = () => {
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

  // Fetch jobs from API
  const fetchJobs = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);
      if (location) params.append('location', location);
      
      const response = await axios.get(`${API}/jobs?${params.toString()}`);
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

  const filteredJobs = jobs.filter(job => {
    const matchesSearch = job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         job.company.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesLocation = !location || job.location.toLowerCase().includes(location.toLowerCase());
    return matchesSearch && matchesLocation;
  });

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-8">
              <div className="flex items-center space-x-2">
                <div className="bg-teal-600 text-white p-2 rounded-lg">
                  <Briefcase className="w-6 h-6" />
                </div>
                <h1 className="text-2xl font-bold text-gray-900">Job Rocket</h1>
              </div>
            </div>
            <div className="flex items-center space-x-6">
              <Button variant="ghost" className="text-teal-600 hover:text-teal-700">
                For recruiters
              </Button>
              <Button variant="ghost" className="flex items-center space-x-1">
                <Heart className="w-4 h-4" />
                <span>My jobs</span>
                <ChevronDown className="w-4 h-4" />
              </Button>
              <Button variant="ghost" className="flex items-center space-x-1">
                <User className="w-4 h-4" />
                <span>Kegan</span>
                <ChevronDown className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Search Section */}
      <div 
        className="relative bg-gradient-to-r from-teal-50 to-blue-50 py-16"
        style={{
          backgroundImage: `linear-gradient(rgba(20, 184, 166, 0.1), rgba(59, 130, 246, 0.1)), url('https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHwyfHxvZmZpY2UlMjBidWlsZGluZ3N8ZW58MHx8fHwxNzU1MzUzMDk5fDA&ixlib=rb-4.1.0&q=85')`,
          backgroundSize: 'cover',
          backgroundPosition: 'center'
        }}
      >
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold text-gray-900 mb-8">
            Find Your Dream Job
          </h2>
          <div className="flex flex-col sm:flex-row gap-4 max-w-3xl mx-auto">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <Input
                type="text"
                placeholder="Job title, keywords, or company"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 h-12 text-lg"
              />
            </div>
            <div className="relative flex-1">
              <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <Input
                type="text"
                placeholder="City, district or province"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="pl-10 h-12 text-lg"
              />
            </div>
            <Button className="bg-teal-600 hover:bg-teal-700 h-12 px-8 text-lg font-medium">
              Find Jobs
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-8">
          {/* Filters Sidebar */}
          <div className="w-80 flex-shrink-0">
            <div className="bg-white rounded-lg shadow-sm p-6 sticky top-4">
              <div className="flex items-center space-x-2 mb-6">
                <Filter className="w-5 h-5 text-gray-600" />
                <h3 className="text-lg font-semibold text-gray-900">Filters</h3>
              </div>

              <FilterSection title="Date posted" defaultExpanded={true}>
                <FilterOption label="New jobs" count="14" />
                <FilterOption label="Last week" count="147" />
              </FilterSection>

              <FilterSection title="Work from home options" defaultExpanded={true}>
                <FilterOption label="Partially remote" count="17" />
                <FilterOption label="Fully remote" count="4" />
              </FilterSection>

              <FilterSection title="Application method" defaultExpanded={true}>
                <FilterOption label="On company website" count="220" />
                <FilterOption label="Easy Apply" count="130" />
              </FilterSection>

              <FilterSection title="Functions" defaultExpanded={true}>
                <FilterOption label="Engineering, Technical" count="100" />
                <FilterOption label="Production & Manufacturing" />
                <FilterOption label="IT & Telecommunications" count="47" />
                <FilterOption label="Sales & Purchasing" count="36" />
                <FilterOption label="Accounting, Auditing" count="33" />
                <FilterOption label="Banking, Finance, Insurance, Stockbroking" count="26" />
              </FilterSection>
            </div>
          </div>

          {/* Job Listings */}
          <div className="flex-1">
            <div className="mb-6 flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">
                {filteredJobs.length} results for {searchTerm || "all jobs"}
              </h2>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">Relevance</span>
                <ChevronDown className="w-4 h-4 text-gray-600" />
              </div>
            </div>

            <div className="space-y-4">
              {filteredJobs.map((job) => (
                <JobCard key={job.id} job={job} onSave={handleSaveJob} />
              ))}
            </div>

            {filteredJobs.length === 0 && (
              <div className="text-center py-16">
                <div className="text-gray-400 mb-4">
                  <Search className="w-16 h-16 mx-auto" />
                </div>
                <h3 className="text-xl font-medium text-gray-900 mb-2">No jobs found</h3>
                <p className="text-gray-600">Try adjusting your search criteria or filters</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<JobListingPage />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;