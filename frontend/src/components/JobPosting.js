import React, { useState, useEffect, useRef } from 'react';
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Textarea } from "./ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Label } from "./ui/label";
import { Badge } from "./ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "./ui/dialog";
import { 
  Briefcase, 
  Plus, 
  Upload,
  FileText,
  Building2,
  MapPin,
  DollarSign,
  Clock,
  Users,
  Eye,
  Edit,
  Trash,
  Download,
  AlertCircle,
  CheckCircle,
  X,
  Save
} from "lucide-react";
import axios from 'axios';
import { useToast } from "../hooks/use-toast";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const JobPosting = ({ user, onUpdateUser }) => {
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState('single');
  const [jobsTab, setJobsTab] = useState('active');
  const [loading, setLoading] = useState(false);
  const [companies, setCompanies] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [archivedJobs, setArchivedJobs] = useState([]);
  const [showJobsList, setShowJobsList] = useState(false);
  const [userPackages, setUserPackages] = useState([]);
  const [editingJob, setEditingJob] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  
  // Single job form
  const [jobForm, setJobForm] = useState({
    title: '',
    location: '',
    salary: '',
    job_type: 'Permanent',
    work_type: 'Onsite',
    industry: '',
    description: '',
    experience: '',
    qualifications: '',
    company_id: '',
    application_url: '',
    application_email: ''
  });

  // Bulk upload
  const [bulkFile, setBulkFile] = useState(null);
  const [bulkCompanyId, setBulkCompanyId] = useState('');
  const [bulkResults, setBulkResults] = useState(null);
  const fileInputRef = useRef(null);

  const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    return {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    };
  };

  const getMultipartAuthHeaders = () => {
    const token = localStorage.getItem('token');
    return {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    };
  };

  useEffect(() => {
    fetchCompanies();
    fetchJobs();
    fetchUserPackages();
  }, []);

  const fetchCompanies = async () => {
    try {
      const response = await axios.get(`${API}/companies`, getAuthHeaders());
      setCompanies(response.data);
      
      // Set default company
      const defaultCompany = response.data.find(c => c.is_default);
      if (defaultCompany) {
        setJobForm(prev => ({ ...prev, company_id: defaultCompany.id }));
        setBulkCompanyId(defaultCompany.id);
      }
    } catch (error) {
      console.error('Error fetching companies:', error);
    }
  };

  const fetchJobs = async () => {
    try {
      // Fetch active jobs
      const response = await axios.get(`${API}/jobs?include_archived=false`, getAuthHeaders());
      setJobs(response.data);
      
      // Fetch archived jobs
      const archivedResponse = await axios.get(`${API}/jobs/archived`, getAuthHeaders());
      setArchivedJobs(archivedResponse.data);
    } catch (error) {
      console.error('Error fetching jobs:', error);
    }
  };

  const fetchUserPackages = async () => {
    try {
      const response = await axios.get(`${API}/my-packages`, getAuthHeaders());
      setUserPackages(response.data);
    } catch (error) {
      console.error('Error fetching packages:', error);
    }
  };

  const handleJobFormChange = (field, value) => {
    setJobForm(prev => ({ ...prev, [field]: value }));
  };

  const getTotalCredits = () => {
    let jobListings = 0;
    let hasUnlimited = false;
    
    userPackages.forEach(({ user_package, is_expired }) => {
      if (!is_expired && user_package.is_active) {
        if (user_package.job_listings_remaining === null) {
          hasUnlimited = true;
        } else if (user_package.job_listings_remaining > 0) {
          jobListings += user_package.job_listings_remaining;
        }
      }
    });
    
    return { jobListings, hasUnlimited };
  };

  const handleSingleJobSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      await axios.post(`${API}/jobs`, jobForm, getAuthHeaders());
      
      toast({
        title: "Job Posted Successfully",
        description: "Your job listing is now live and visible to job seekers.",
        variant: "success",
      });
      
      // Reset form
      setJobForm({
        title: '',
        location: '',
        salary: '',
        job_type: 'Permanent',
        work_type: 'Onsite',
        industry: '',
        description: '',
        experience: '',
        qualifications: '',
        company_id: companies.find(c => c.is_default)?.id || '',
        application_url: '',
        application_email: ''
      });
      
      // Refresh jobs list and user progress
      await fetchJobs();
      await fetchUserPackages(); // Refresh packages to update credit count
      if (onUpdateUser) onUpdateUser();
      
    } catch (error) {
      console.error('Error posting job:', error);
      if (error.response?.status === 402) {
        toast({
          title: "No Credits Available",
          description: "Please purchase a package to post jobs.",
          variant: "destructive",
        });
      } else {
        toast({
          title: "Failed to Post Job",
          description: error.response?.data?.detail || "Something went wrong. Please try again.",
          variant: "destructive",
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file type
      const allowedTypes = [
        'text/csv',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      ];
      
      if (!allowedTypes.includes(file.type)) {
        toast({
          title: "Invalid File Type",
          description: "Please select a CSV or Excel file.",
          variant: "destructive",
        });
        return;
      }
      
      setBulkFile(file);
      setBulkResults(null);
    }
  };

  const handleBulkUpload = async (e) => {
    e.preventDefault();
    
    if (!bulkFile) {
      toast({
        title: "No File Selected",
        description: "Please select a file to upload.",
        variant: "warning",
      });
      return;
    }

    try {
      setLoading(true);
      const formData = new FormData();
      formData.append('file', bulkFile);
      if (bulkCompanyId) {
        formData.append('company_id', bulkCompanyId);
      }

      const response = await axios.post(`${API}/jobs/bulk`, formData, getMultipartAuthHeaders());
      
      setBulkResults(response.data);
      setBulkFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      
      // Refresh jobs list and user progress
      await fetchJobs();
      if (onUpdateUser) onUpdateUser();
      
    } catch (error) {
      console.error('Error uploading jobs:', error);
      setBulkResults({
        message: 'Upload failed',
        jobs_created: 0,
        total_rows: 0,
        errors: [error.response?.data?.detail || 'Failed to upload jobs']
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRepostJob = async (jobId) => {
    try {
      setLoading(true);
      await axios.put(`${API}/jobs/${jobId}/repost`, {}, getAuthHeaders());
      
      toast({
        title: "Job Reposted Successfully",
        description: "Your job listing is now visible to job seekers for another 35 days.",
        variant: "success",
      });
      
      // Refresh jobs
      await fetchJobs();
      
    } catch (error) {
      console.error('Error reposting job:', error);
      toast({
        title: "Failed to Repost Job",
        description: error.response?.data?.detail || "Something went wrong. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const downloadTemplate = () => {
    const template = `title,location,salary,job_type,work_type,industry,description,experience,qualifications,application_url,application_email
Software Engineer,Cape Town,R50000 - R70000,Permanent,Hybrid,Technology,"We are looking for a talented Software Engineer to join our dynamic team...",2-3 years experience in software development,"Degree in Computer Science or related field, Experience with React and Python",https://company.com/apply,careers@company.com
Marketing Manager,Johannesburg,R45000 - R60000,Permanent,Onsite,Marketing,"Join our marketing team as a Marketing Manager...",3-5 years marketing experience,"Marketing degree, Experience with digital marketing campaigns",,marketing@company.com`;
    
    const blob = new Blob([template], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'job_posting_template.csv';
    a.click();
    window.URL.revokeObjectURL(url);
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

  const formatExpiryDate = (expiryDateString) => {
    const expiryDate = new Date(expiryDateString);
    const now = new Date();
    const diffTime = expiryDate - now;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) return 'Expired';
    if (diffDays === 0) return 'Expires today';
    if (diffDays === 1) return 'Expires tomorrow';
    if (diffDays <= 7) return `Expires in ${diffDays} days`;
    return `Expires in ${Math.ceil(diffDays / 7)} weeks`;
  };

  const isJobExpired = (expiryDateString) => {
    return new Date(expiryDateString) <= new Date();
  };

  const handleEditJob = (job) => {
    setEditingJob(job);
    setJobForm({
      title: job.title || '',
      location: job.location || '',
      salary: job.salary || '',
      job_type: job.job_type || 'Permanent',
      work_type: job.work_type || 'Onsite',
      industry: job.industry || '',
      description: job.description || '',
      experience: job.experience || '',
      qualifications: job.qualifications || '',
      company_id: job.company_id || '',
      application_url: job.application_url || '',
      application_email: job.application_email || ''
    });
    setShowEditModal(true);
    setShowJobsList(false);
  };

  const handleUpdateJob = async (e) => {
    e.preventDefault();
    if (!editingJob) return;

    try {
      setLoading(true);
      await axios.put(`${API}/jobs/${editingJob.id}`, jobForm, getAuthHeaders());
      
      toast({
        title: "Job Updated Successfully",
        description: "Your changes have been saved.",
        variant: "success",
      });
      setShowEditModal(false);
      setEditingJob(null);
      
      // Reset form and refresh
      setJobForm({
        title: '',
        location: '',
        salary: '',
        job_type: 'Permanent',
        work_type: 'Onsite',
        industry: '',
        description: '',
        experience: '',
        qualifications: '',
        company_id: companies.find(c => c.is_default)?.id || '',
        application_url: '',
        application_email: ''
      });
      
      await fetchJobs();
      if (onUpdateUser) onUpdateUser();
      
    } catch (error) {
      console.error('Error updating job:', error);
      toast({
        title: "Failed to Update Job",
        description: error.response?.data?.detail || "Something went wrong. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteJob = async (jobId, jobTitle) => {
    if (!window.confirm(`Are you sure you want to delete "${jobTitle}"? This action cannot be undone.`)) {
      return;
    }

    try {
      setLoading(true);
      await axios.delete(`${API}/jobs/${jobId}`, getAuthHeaders());
      
      toast({
        title: "Job Deleted",
        description: "The job listing has been moved to archived.",
        variant: "success",
      });
      await fetchJobs();
      if (onUpdateUser) onUpdateUser();
      
    } catch (error) {
      console.error('Error deleting job:', error);
      toast({
        title: "Failed to Delete Job",
        description: error.response?.data?.detail || "Something went wrong. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCancelEdit = () => {
    setShowEditModal(false);
    setEditingJob(null);
    setJobForm({
      title: '',
      location: '',
      salary: '',
      job_type: 'Permanent',
      work_type: 'Onsite',
      industry: '',
      description: '',
      experience: '',
      qualifications: '',
      company_id: companies.find(c => c.is_default)?.id || '',
      application_url: '',
      application_email: ''
    });
  };

  const jobTypeOptions = ['Permanent', 'Contract'];
  const workTypeOptions = ['Remote', 'Onsite', 'Hybrid'];
  const credits = getTotalCredits();

  return (
    <div className="space-y-6">
      {/* Edit Job Modal */}
      <Dialog open={showEditModal} onOpenChange={setShowEditModal}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-xl font-bold text-slate-800">
              Edit Job: {editingJob?.title}
            </DialogTitle>
          </DialogHeader>
          
          <form onSubmit={handleUpdateJob} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Job Title *</Label>
                <Input
                  value={jobForm.title}
                  onChange={(e) => handleJobFormChange('title', e.target.value)}
                  placeholder="e.g., Software Engineer"
                  required
                />
              </div>
              <div>
                <Label>Location *</Label>
                <Input
                  value={jobForm.location}
                  onChange={(e) => handleJobFormChange('location', e.target.value)}
                  placeholder="e.g., Cape Town, Western Cape"
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Salary *</Label>
                <Input
                  value={jobForm.salary}
                  onChange={(e) => handleJobFormChange('salary', e.target.value)}
                  placeholder="e.g., R50,000 - R70,000"
                  required
                />
              </div>
              <div>
                <Label>Industry *</Label>
                <Input
                  value={jobForm.industry}
                  onChange={(e) => handleJobFormChange('industry', e.target.value)}
                  placeholder="e.g., Technology"
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Job Type *</Label>
                <select
                  value={jobForm.job_type}
                  onChange={(e) => handleJobFormChange('job_type', e.target.value)}
                  className="w-full border border-slate-300 rounded-md px-3 py-2"
                  required
                >
                  {jobTypeOptions.map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>
              <div>
                <Label>Work Type *</Label>
                <select
                  value={jobForm.work_type}
                  onChange={(e) => handleJobFormChange('work_type', e.target.value)}
                  className="w-full border border-slate-300 rounded-md px-3 py-2"
                  required
                >
                  {workTypeOptions.map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <Label>Job Description *</Label>
              <Textarea
                value={jobForm.description}
                onChange={(e) => handleJobFormChange('description', e.target.value)}
                placeholder="Provide a detailed description of the role..."
                rows={4}
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Experience</Label>
                <Input
                  value={jobForm.experience}
                  onChange={(e) => handleJobFormChange('experience', e.target.value)}
                  placeholder="e.g., 2-3 years experience"
                />
              </div>
              <div>
                <Label>Qualifications</Label>
                <Input
                  value={jobForm.qualifications}
                  onChange={(e) => handleJobFormChange('qualifications', e.target.value)}
                  placeholder="e.g., Degree in Computer Science"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Application URL</Label>
                <Input
                  value={jobForm.application_url}
                  onChange={(e) => handleJobFormChange('application_url', e.target.value)}
                  placeholder="https://company.com/apply"
                  type="url"
                />
              </div>
              <div>
                <Label>Application Email</Label>
                <Input
                  value={jobForm.application_email}
                  onChange={(e) => handleJobFormChange('application_email', e.target.value)}
                  placeholder="careers@company.com"
                  type="email"
                />
              </div>
            </div>

            <DialogFooter className="flex justify-end space-x-2 pt-4">
              <Button type="button" variant="outline" onClick={handleCancelEdit} disabled={loading}>
                Cancel
              </Button>
              <Button type="submit" className="bg-blue-600 hover:bg-blue-700" disabled={loading}>
                {loading ? (
                  <span className="flex items-center">
                    <span className="animate-spin mr-2">⏳</span> Saving...
                  </span>
                ) : (
                  <span className="flex items-center">
                    <Save className="w-4 h-4 mr-2" /> Save Changes
                  </span>
                )}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Header with Credits */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-800 mb-2">Job Postings</h2>
          <p className="text-slate-600">Create and manage your job listings</p>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-blue-600">
            {credits.hasUnlimited ? '∞' : credits.jobListings}
          </div>
          <div className="text-sm text-slate-600">
            {credits.hasUnlimited ? 'Unlimited Credits' : 'Job Credits Remaining'}
          </div>
        </div>
      </div>

      {/* Low Credits Warning */}
      {!credits.hasUnlimited && credits.jobListings > 0 && credits.jobListings <= 2 && (
        <Card className="bg-yellow-50 border-yellow-200">
          <CardContent className="p-4">
            <div className="flex items-center space-x-3">
              <AlertCircle className="w-6 h-6 text-yellow-600" />
              <div>
                <h4 className="font-semibold text-yellow-800">Running Low on Credits</h4>
                <p className="text-yellow-700 text-sm">
                  You have {credits.jobListings} job credit{credits.jobListings > 1 ? 's' : ''} remaining.
                  <Button variant="link" className="p-0 h-auto text-yellow-600 underline ml-1">
                    Buy More Credits
                  </Button>
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Jobs List Toggle */}
      <div className="flex items-center justify-between">
        <div></div>
        <Button
          onClick={() => setShowJobsList(!showJobsList)}
          variant="outline"
        >
          <Eye className="w-4 h-4 mr-2" />
          {showJobsList ? 'Hide' : 'View'} Jobs ({jobs.length} active, {archivedJobs.length} archived)
        </Button>
      </div>

      {/* Jobs List */}
      {showJobsList && (
        <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Briefcase className="w-5 h-5 text-blue-600" />
                <span>Your Posted Jobs</span>
              </div>
              <div className="flex items-center space-x-2">
                <Button
                  onClick={() => setJobsTab('active')}
                  variant={jobsTab === 'active' ? 'default' : 'outline'}
                  size="sm"
                >
                  Active ({jobs.length})
                </Button>
                <Button
                  onClick={() => setJobsTab('archived')}
                  variant={jobsTab === 'archived' ? 'default' : 'outline'}
                  size="sm"
                >
                  Archived ({archivedJobs.length})
                </Button>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {jobsTab === 'active' ? (
              jobs.length === 0 ? (
                <div className="text-center py-8">
                  <Briefcase className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-slate-800 mb-2">No active jobs posted</h3>
                  <p className="text-slate-600">Create your first job posting to get started</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {jobs.map((job) => (
                    <div key={job.id} className="border border-slate-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="font-semibold text-slate-800 text-lg">{job.title}</h4>
                          <div className="flex items-center space-x-4 text-sm text-slate-600 mt-2">
                            <div className="flex items-center space-x-1">
                              <Building2 className="w-4 h-4" />
                              <span>{job.company_name}</span>
                            </div>
                            <div className="flex items-center space-x-1">
                              <MapPin className="w-4 h-4" />
                              <span>{job.location}</span>
                            </div>
                            <div className="flex items-center space-x-1">
                              <span className="font-semibold text-slate-600">R</span>
                              <span>{job.salary}</span>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2 mt-3">
                            <Badge variant="outline">{job.job_type}</Badge>
                            <Badge variant="outline">{job.work_type}</Badge>
                            <Badge variant="outline">{job.industry}</Badge>
                            <Badge 
                              variant="outline" 
                              className={isJobExpired(job.expiry_date) ? 'border-red-500 text-red-700' : 'border-green-500 text-green-700'}
                            >
                              {formatExpiryDate(job.expiry_date)}
                            </Badge>
                          </div>
                          <div className="flex items-center justify-between mt-2">
                            <p className="text-sm text-slate-500">
                              Posted: {formatPostedDate(job.posted_date)}
                            </p>
                            <p className="text-xs text-slate-400">
                              Expires: {new Date(job.expiry_date).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                        <div className="flex space-x-2">
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => handleEditJob(job)}
                            disabled={loading}
                            title="Edit job"
                          >
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button 
                            size="sm" 
                            variant="outline" 
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                            onClick={() => handleDeleteJob(job.id, job.title)}
                            disabled={loading}
                            title="Delete job"
                          >
                            <Trash className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )
            ) : (
              archivedJobs.length === 0 ? (
                <div className="text-center py-8">
                  <Clock className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-slate-800 mb-2">No archived jobs</h3>
                  <p className="text-slate-600">Expired jobs will appear here</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {archivedJobs.map((job) => (
                    <div key={job.id} className="border border-slate-200 rounded-lg p-4 bg-slate-50 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2">
                            <h4 className="font-semibold text-slate-700 text-lg">{job.title}</h4>
                            <Badge variant="outline" className="border-red-500 text-red-700 bg-red-50">
                              Expired
                            </Badge>
                          </div>
                          <div className="flex items-center space-x-4 text-sm text-slate-600 mt-2">
                            <div className="flex items-center space-x-1">
                              <Building2 className="w-4 h-4" />
                              <span>{job.company_name}</span>
                            </div>
                            <div className="flex items-center space-x-1">
                              <MapPin className="w-4 h-4" />
                              <span>{job.location}</span>
                            </div>
                            <div className="flex items-center space-x-1">
                              <span className="font-semibold text-slate-600">R</span>
                              <span>{job.salary}</span>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2 mt-3">
                            <Badge variant="outline">{job.job_type}</Badge>
                            <Badge variant="outline">{job.work_type}</Badge>
                            <Badge variant="outline">{job.industry}</Badge>
                          </div>
                          <div className="flex items-center justify-between mt-2">
                            <p className="text-sm text-slate-500">
                              Originally posted: {formatPostedDate(job.posted_date)}
                            </p>
                            <p className="text-xs text-red-500">
                              Expired: {new Date(job.expiry_date).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                        <div className="flex space-x-2">
                          <Button 
                            size="sm" 
                            onClick={() => handleRepostJob(job.id)}
                            disabled={loading}
                            className="bg-blue-600 hover:bg-blue-700 text-white"
                          >
                            <Plus className="w-4 h-4 mr-1" />
                            Repost
                          </Button>
                          <Button 
                            size="sm" 
                            variant="outline" 
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                            onClick={() => handleDeleteJob(job.id, job.title)}
                            disabled={loading}
                            title="Delete job"
                          >
                            <Trash className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )
            )}
          </CardContent>
        </Card>
      )}

      {/* Job Posting Tabs */}
      <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Plus className="w-5 h-5 text-blue-600" />
            <span>Create Job Posting</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-2 bg-slate-100">
              <TabsTrigger value="single" className="flex items-center space-x-2">
                <FileText className="w-4 h-4" />
                <span>Single Job</span>
              </TabsTrigger>
              <TabsTrigger value="bulk" className="flex items-center space-x-2">
                <Upload className="w-4 h-4" />
                <span>Bulk Upload</span>
              </TabsTrigger>
            </TabsList>

            {/* Single Job Posting */}
            <TabsContent value="single" className="space-y-6 mt-6">
              <form onSubmit={handleSingleJobSubmit} className="space-y-6">
                {/* Company Selection */}
                {companies.length > 1 && (
                  <div className="space-y-2">
                    <Label htmlFor="company_select">Company *</Label>
                    <select
                      id="company_select"
                      value={jobForm.company_id}
                      onChange={(e) => handleJobFormChange('company_id', e.target.value)}
                      className="w-full h-12 px-3 border border-slate-300 rounded-md focus:border-blue-500 focus:ring-blue-500 bg-white"
                      required
                    >
                      {companies.map((company) => (
                        <option key={company.id} value={company.id}>
                          {company.name} {company.is_default && '(Default)'}
                        </option>
                      ))}
                    </select>
                  </div>
                )}

                {/* Required Fields Row 1 */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="title">Job Title *</Label>
                    <Input
                      id="title"
                      value={jobForm.title}
                      onChange={(e) => handleJobFormChange('title', e.target.value)}
                      placeholder="e.g., Software Engineer"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="location">Location *</Label>
                    <Input
                      id="location"
                      value={jobForm.location}
                      onChange={(e) => handleJobFormChange('location', e.target.value)}
                      placeholder="e.g., Cape Town, Western Cape"
                      required
                    />
                  </div>
                </div>

                {/* Required Fields Row 2 */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="salary">Salary *</Label>
                    <Input
                      id="salary"
                      value={jobForm.salary}
                      onChange={(e) => handleJobFormChange('salary', e.target.value)}
                      placeholder="e.g., R50,000 - R70,000"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="industry">Industry *</Label>
                    <Input
                      id="industry"
                      value={jobForm.industry}
                      onChange={(e) => handleJobFormChange('industry', e.target.value)}
                      placeholder="e.g., Technology"
                      required
                    />
                  </div>
                </div>

                {/* Required Fields Row 3 */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="job_type">Job Type *</Label>
                    <select
                      id="job_type"
                      value={jobForm.job_type}
                      onChange={(e) => handleJobFormChange('job_type', e.target.value)}
                      className="w-full h-12 px-3 border border-slate-300 rounded-md focus:border-blue-500 focus:ring-blue-500 bg-white"
                      required
                    >
                      {jobTypeOptions.map((type) => (
                        <option key={type} value={type}>{type}</option>
                      ))}
                    </select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="work_type">Work Type *</Label>
                    <select
                      id="work_type"
                      value={jobForm.work_type}
                      onChange={(e) => handleJobFormChange('work_type', e.target.value)}
                      className="w-full h-12 px-3 border border-slate-300 rounded-md focus:border-blue-500 focus:ring-blue-500 bg-white"
                      required
                    >
                      {workTypeOptions.map((type) => (
                        <option key={type} value={type}>{type}</option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Description */}
                <div className="space-y-2">
                  <Label htmlFor="description">Job Description *</Label>
                  <Textarea
                    id="description"
                    value={jobForm.description}
                    onChange={(e) => handleJobFormChange('description', e.target.value)}
                    placeholder="Provide a detailed description of the role, responsibilities, and what you're looking for..."
                    rows={6}
                    className="resize-none"
                    required
                  />
                </div>

                {/* Optional Fields */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="experience">Experience</Label>
                    <Textarea
                      id="experience"
                      value={jobForm.experience}
                      onChange={(e) => handleJobFormChange('experience', e.target.value)}
                      placeholder="e.g., 2-3 years experience in software development"
                      rows={3}
                      className="resize-none"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="qualifications">Qualifications</Label>
                    <Textarea
                      id="qualifications"
                      value={jobForm.qualifications}
                      onChange={(e) => handleJobFormChange('qualifications', e.target.value)}
                      placeholder="e.g., Degree in Computer Science or related field"
                      rows={3}
                      className="resize-none"
                    />
                  </div>
                </div>

                {/* Application Details */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="application_url">Application URL</Label>
                    <Input
                      id="application_url"
                      value={jobForm.application_url}
                      onChange={(e) => handleJobFormChange('application_url', e.target.value)}
                      placeholder="https://company.com/careers/apply"
                      type="url"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="application_email">Application Email</Label>
                    <Input
                      id="application_email"
                      value={jobForm.application_email}
                      onChange={(e) => handleJobFormChange('application_email', e.target.value)}
                      placeholder="careers@company.com"
                      type="email"
                    />
                  </div>
                </div>

                <Button 
                  type="submit" 
                  disabled={loading}
                  className="bg-gradient-to-r from-blue-600 to-slate-700 hover:from-blue-700 hover:to-slate-800 w-full md:w-auto"
                >
                  {loading ? (
                    <div className="flex items-center space-x-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span>Posting Job...</span>
                    </div>
                  ) : (
                    <div className="flex items-center space-x-2">
                      <Plus className="w-4 h-4" />
                      <span>Post Job</span>
                    </div>
                  )}
                </Button>
              </form>
            </TabsContent>

            {/* Bulk Upload */}
            <TabsContent value="bulk" className="space-y-6 mt-6">
              <div className="space-y-6">
                {/* Template Download */}
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex items-start space-x-3">
                    <AlertCircle className="w-5 h-5 text-blue-600 mt-1" />
                    <div>
                      <h4 className="font-semibold text-blue-900">Download Template First</h4>
                      <p className="text-blue-700 mb-3">
                        Use our template to ensure your CSV/Excel file has the correct format and column names.
                      </p>
                      <Button onClick={downloadTemplate} variant="outline" size="sm">
                        <Download className="w-4 h-4 mr-2" />
                        Download Template
                      </Button>
                    </div>
                  </div>
                </div>

                <form onSubmit={handleBulkUpload} className="space-y-6">
                  {/* Company Selection for Bulk */}
                  {companies.length > 1 && (
                    <div className="space-y-2">
                      <Label htmlFor="bulk_company_select">Default Company (Optional)</Label>
                      <select
                        id="bulk_company_select"
                        value={bulkCompanyId}
                        onChange={(e) => setBulkCompanyId(e.target.value)}
                        className="w-full h-12 px-3 border border-slate-300 rounded-md focus:border-blue-500 focus:ring-blue-500 bg-white"
                      >
                        <option value="">Select default company...</option>
                        {companies.map((company) => (
                          <option key={company.id} value={company.id}>
                            {company.name} {company.is_default && '(Default)'}
                          </option>
                        ))}
                      </select>
                      <p className="text-sm text-slate-500">
                        This company will be used for all jobs unless overridden in the CSV file
                      </p>
                    </div>
                  )}

                  {/* File Upload */}
                  <div className="space-y-2">
                    <Label htmlFor="bulk_file">CSV/Excel File</Label>
                    <div className="border-2 border-dashed border-slate-300 rounded-lg p-6 text-center">
                      <Upload className="w-12 h-12 text-slate-400 mx-auto mb-4" />
                      <div>
                        <input
                          ref={fileInputRef}
                          id="bulk_file"
                          type="file"
                          accept=".csv,.xlsx,.xls"
                          onChange={handleFileChange}
                          className="hidden"
                        />
                        <Button
                          type="button"
                          variant="outline"
                          onClick={() => fileInputRef.current?.click()}
                        >
                          Choose File
                        </Button>
                        {bulkFile && (
                          <p className="text-sm text-slate-600 mt-2">
                            Selected: {bulkFile.name}
                          </p>
                        )}
                      </div>
                      <p className="text-sm text-slate-500 mt-2">
                        Accepts CSV, XLS, and XLSX files
                      </p>
                    </div>
                  </div>

                  <Button 
                    type="submit" 
                    disabled={loading || !bulkFile}
                    className="bg-gradient-to-r from-blue-600 to-slate-700 hover:from-blue-700 hover:to-slate-800"
                  >
                    {loading ? (
                      <div className="flex items-center space-x-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        <span>Uploading...</span>
                      </div>
                    ) : (
                      <div className="flex items-center space-x-2">
                        <Upload className="w-4 h-4" />
                        <span>Upload Jobs</span>
                      </div>
                    )}
                  </Button>
                </form>

                {/* Bulk Upload Results */}
                {bulkResults && (
                  <Card className="bg-white border-0 shadow-lg">
                    <CardHeader>
                      <CardTitle className="flex items-center space-x-2">
                        {bulkResults.errors.length === 0 ? (
                          <CheckCircle className="w-5 h-5 text-green-600" />
                        ) : (
                          <AlertCircle className="w-5 h-5 text-yellow-600" />
                        )}
                        <span>Upload Results</span>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div className="grid grid-cols-3 gap-4 text-center">
                          <div className="p-4 bg-green-50 rounded-lg">
                            <p className="text-2xl font-bold text-green-700">{bulkResults.jobs_created}</p>
                            <p className="text-sm text-green-600">Jobs Created</p>
                          </div>
                          <div className="p-4 bg-blue-50 rounded-lg">
                            <p className="text-2xl font-bold text-blue-700">{bulkResults.total_rows}</p>
                            <p className="text-sm text-blue-600">Total Rows</p>
                          </div>
                          <div className="p-4 bg-red-50 rounded-lg">
                            <p className="text-2xl font-bold text-red-700">{bulkResults.errors.length}</p>
                            <p className="text-sm text-red-600">Errors</p>
                          </div>
                        </div>

                        {bulkResults.errors.length > 0 && (
                          <div className="space-y-2">
                            <h4 className="font-semibold text-slate-800">Errors:</h4>
                            <div className="max-h-40 overflow-y-auto space-y-1">
                              {bulkResults.errors.map((error, index) => (
                                <div key={index} className="text-sm text-red-600 bg-red-50 p-2 rounded">
                                  {error}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        <Button
                          onClick={() => setBulkResults(null)}
                          variant="outline"
                          size="sm"
                        >
                          <X className="w-4 h-4 mr-2" />
                          Close Results
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};

export default JobPosting;