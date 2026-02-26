import React, { useState, useEffect } from 'react';
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Textarea } from "./ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Switch } from "./ui/switch";
import { Label } from "./ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "./ui/dialog";
import { 
  Briefcase, 
  Search,
  Calendar,
  Users,
  Eye,
  Edit,
  RefreshCw,
  Clock,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Star,
  MessageSquare,
  FileText,
  MapPin,
  Building2,
  DollarSign,
  ChevronRight,
  StickyNote,
  Archive,
  TrendingUp,
  Filter,
  ArrowUpDown,
  User,
  Mail,
  Phone,
  ExternalLink,
  RotateCcw
} from "lucide-react";
import axios from 'axios';
import { useToast } from "../hooks/use-toast";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const JobsDashboard = ({ user }) => {
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [jobs, setJobs] = useState([]);
  const [dashboardStats, setDashboardStats] = useState({
    total_active_jobs: 0,
    total_expired_jobs: 0,
    total_applications_this_month: 0,
    total_interviews: 0
  });
  
  // Filters and search
  const [includeExpired, setIncludeExpired] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('newest');
  
  // Modals
  const [selectedJob, setSelectedJob] = useState(null);
  const [showNotesModal, setShowNotesModal] = useState(false);
  const [showApplicantsModal, setShowApplicantsModal] = useState(false);
  const [showReactivateModal, setShowReactivateModal] = useState(false);
  const [notesText, setNotesText] = useState('');
  const [extensionDays, setExtensionDays] = useState(35);
  const [saving, setSaving] = useState(false);
  
  // Applicants view
  const [applicants, setApplicants] = useState([]);
  const [applicantsLoading, setApplicantsLoading] = useState(false);
  const [applicantStatusFilter, setApplicantStatusFilter] = useState('all');
  const [selectedApplicant, setSelectedApplicant] = useState(null);
  const [showApplicantProfile, setShowApplicantProfile] = useState(false);

  const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    return {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    };
  };

  // Fetch dashboard data
  const fetchDashboard = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      params.append('include_expired', includeExpired);
      if (searchTerm) params.append('search', searchTerm);
      params.append('sort_by', sortBy);
      
      const response = await axios.get(`${API}/jobs/dashboard?${params.toString()}`, getAuthHeaders());
      setJobs(response.data.jobs);
      setDashboardStats(response.data.dashboard_stats);
    } catch (error) {
      console.error('Error fetching dashboard:', error);
      toast({
        title: "Error",
        description: "Failed to load dashboard data",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, [includeExpired, sortBy]);

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      fetchDashboard();
    }, 500);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Fetch applicants for a job
  const fetchApplicants = async (jobId, statusFilter = 'all') => {
    try {
      setApplicantsLoading(true);
      const params = statusFilter !== 'all' ? `?status_filter=${statusFilter}` : '';
      const response = await axios.get(`${API}/jobs/${jobId}/applicants${params}`, getAuthHeaders());
      setApplicants(response.data.applications);
    } catch (error) {
      console.error('Error fetching applicants:', error);
      toast({
        title: "Error",
        description: "Failed to load applicants",
        variant: "destructive",
      });
    } finally {
      setApplicantsLoading(false);
    }
  };

  // Open applicants modal
  const handleViewApplicants = async (job) => {
    setSelectedJob(job);
    setApplicantStatusFilter('all');
    setShowApplicantsModal(true);
    await fetchApplicants(job.id);
  };

  // Open notes modal
  const handleOpenNotes = (job) => {
    setSelectedJob(job);
    setNotesText(job.recruiter_notes || '');
    setShowNotesModal(true);
  };

  // Save notes
  const handleSaveNotes = async () => {
    if (!selectedJob) return;
    try {
      setSaving(true);
      await axios.put(`${API}/jobs/${selectedJob.id}/notes`, { notes: notesText }, getAuthHeaders());
      toast({
        title: "Notes Saved",
        description: "Your notes have been saved successfully.",
        variant: "success",
      });
      setShowNotesModal(false);
      fetchDashboard();
    } catch (error) {
      console.error('Error saving notes:', error);
      toast({
        title: "Error",
        description: "Failed to save notes",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  // Open reactivate modal
  const handleOpenReactivate = (job) => {
    setSelectedJob(job);
    setExtensionDays(35);
    setShowReactivateModal(true);
  };

  // Reactivate job
  const handleReactivateJob = async () => {
    if (!selectedJob) return;
    try {
      setSaving(true);
      await axios.put(`${API}/jobs/${selectedJob.id}/reactivate`, { extension_days: extensionDays }, getAuthHeaders());
      toast({
        title: "Job Reactivated",
        description: `Job listing is now active for ${extensionDays} days.`,
        variant: "success",
      });
      setShowReactivateModal(false);
      fetchDashboard();
    } catch (error) {
      console.error('Error reactivating job:', error);
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to reactivate job",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  // Update application status
  const handleUpdateApplicationStatus = async (applicationId, newStatus) => {
    try {
      await axios.put(`${API}/applications/${applicationId}/status?status=${newStatus}`, {}, getAuthHeaders());
      toast({
        title: "Status Updated",
        description: `Application marked as ${newStatus}.`,
        variant: "success",
      });
      // Refresh applicants list
      if (selectedJob) {
        fetchApplicants(selectedJob.id, applicantStatusFilter);
      }
      // Refresh dashboard to update stats
      fetchDashboard();
    } catch (error) {
      console.error('Error updating status:', error);
      toast({
        title: "Error",
        description: "Failed to update application status",
        variant: "destructive",
      });
    }
  };

  // View applicant profile
  const handleViewApplicantProfile = (applicant) => {
    setSelectedApplicant(applicant);
    setShowApplicantProfile(true);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-ZA', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatDaysUntilExpiry = (days) => {
    if (days < 0) return `Expired ${Math.abs(days)} days ago`;
    if (days === 0) return 'Expires today';
    if (days === 1) return 'Expires tomorrow';
    if (days <= 7) return `Expires in ${days} days`;
    return `Expires in ${Math.ceil(days / 7)} weeks`;
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      pending: { color: 'bg-yellow-100 text-yellow-800 border-yellow-300', label: 'Pending' },
      reviewed: { color: 'bg-blue-100 text-blue-800 border-blue-300', label: 'Reviewed' },
      shortlisted: { color: 'bg-purple-100 text-purple-800 border-purple-300', label: 'Shortlisted' },
      interviewed: { color: 'bg-indigo-100 text-indigo-800 border-indigo-300', label: 'Interviewed' },
      offered: { color: 'bg-green-100 text-green-800 border-green-300', label: 'Offered' },
      rejected: { color: 'bg-red-100 text-red-800 border-red-300', label: 'Rejected' },
      withdrawn: { color: 'bg-slate-100 text-slate-800 border-slate-300', label: 'Withdrawn' }
    };
    const config = statusConfig[status] || statusConfig.pending;
    return <Badge variant="outline" className={`${config.color} capitalize`}>{config.label}</Badge>;
  };

  if (loading && jobs.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6" data-testid="jobs-dashboard">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-800 mb-2">Jobs Dashboard</h1>
          <p className="text-slate-600">Manage your job listings and track applications</p>
        </div>
        <Button
          onClick={fetchDashboard}
          variant="outline"
          className="flex items-center space-x-2"
          data-testid="refresh-dashboard-btn"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </Button>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white border-0 shadow-lg" data-testid="stat-active-jobs">
          <CardContent className="p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-100 text-sm font-medium">Active Jobs</p>
                <p className="text-3xl font-bold">{dashboardStats.total_active_jobs}</p>
              </div>
              <Briefcase className="w-10 h-10 text-blue-200" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-emerald-500 to-emerald-600 text-white border-0 shadow-lg" data-testid="stat-applications">
          <CardContent className="p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-emerald-100 text-sm font-medium">Applications This Month</p>
                <p className="text-3xl font-bold">{dashboardStats.total_applications_this_month}</p>
              </div>
              <Users className="w-10 h-10 text-emerald-200" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white border-0 shadow-lg" data-testid="stat-interviews">
          <CardContent className="p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-100 text-sm font-medium">Interviews</p>
                <p className="text-3xl font-bold">{dashboardStats.total_interviews}</p>
              </div>
              <Calendar className="w-10 h-10 text-purple-200" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-slate-500 to-slate-600 text-white border-0 shadow-lg" data-testid="stat-expired">
          <CardContent className="p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-200 text-sm font-medium">Expired Jobs</p>
                <p className="text-3xl font-bold">{dashboardStats.total_expired_jobs}</p>
              </div>
              <Archive className="w-10 h-10 text-slate-300" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
            {/* Search */}
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
              <Input
                placeholder="Search jobs by title, location..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
                data-testid="search-jobs-input"
              />
            </div>

            {/* Filters */}
            <div className="flex items-center gap-6">
              {/* Sort */}
              <div className="flex items-center gap-2">
                <ArrowUpDown className="w-4 h-4 text-slate-500" />
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="border border-slate-300 rounded-md px-3 py-2 text-sm bg-white"
                  data-testid="sort-select"
                >
                  <option value="newest">Newest First</option>
                  <option value="expiring_soon">Expiring Soon</option>
                  <option value="most_applications">Most Applications</option>
                  <option value="posted_date">Posted Date</option>
                </select>
              </div>

              {/* Show Expired Toggle */}
              <div className="flex items-center gap-2">
                <Switch
                  id="show-expired"
                  checked={includeExpired}
                  onCheckedChange={setIncludeExpired}
                  data-testid="show-expired-toggle"
                />
                <Label htmlFor="show-expired" className="text-sm text-slate-600">
                  Show Expired
                </Label>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Jobs List */}
      <div className="space-y-4">
        {jobs.length === 0 ? (
          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
            <CardContent className="p-12 text-center">
              <Briefcase className="w-16 h-16 text-slate-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-slate-800 mb-2">No jobs found</h3>
              <p className="text-slate-600">
                {searchTerm ? 'Try adjusting your search terms' : 'Create your first job posting to get started'}
              </p>
            </CardContent>
          </Card>
        ) : (
          jobs.map((job) => (
            <Card 
              key={job.id} 
              className={`bg-white/80 backdrop-blur-sm border-0 shadow-xl hover:shadow-2xl transition-all duration-300 ${job.is_expired ? 'opacity-75' : ''}`}
              data-testid={`job-card-${job.id}`}
            >
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  {/* Job Info */}
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <h3 className="text-xl font-bold text-slate-800">{job.title}</h3>
                      
                      {/* Status Badges */}
                      {job.is_expired && (
                        <Badge variant="outline" className="bg-red-100 text-red-800 border-red-300">
                          Expired
                        </Badge>
                      )}
                      {job.is_expiring_soon && !job.is_expired && (
                        <Badge variant="outline" className="bg-orange-100 text-orange-800 border-orange-300">
                          <AlertTriangle className="w-3 h-3 mr-1" />
                          Expiring Soon
                        </Badge>
                      )}
                      {job.recruiter_notes && (
                        <Badge variant="outline" className="bg-slate-100 text-slate-700 border-slate-300">
                          <StickyNote className="w-3 h-3 mr-1" />
                          Has Notes
                        </Badge>
                      )}
                    </div>

                    {/* Job Details */}
                    <div className="flex flex-wrap items-center gap-4 text-sm text-slate-600 mb-4">
                      <div className="flex items-center gap-1">
                        <MapPin className="w-4 h-4" />
                        <span>{job.location}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Building2 className="w-4 h-4" />
                        <span>{job.job_type}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <DollarSign className="w-4 h-4" />
                        <span>{job.salary || 'Salary not disclosed'}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        <span>Posted {formatDate(job.posted_date)}</span>
                      </div>
                    </div>

                    {/* Expiry Info */}
                    <div className={`inline-flex items-center gap-1 text-sm px-2 py-1 rounded-md ${
                      job.is_expired 
                        ? 'bg-red-50 text-red-700' 
                        : job.is_expiring_soon 
                          ? 'bg-orange-50 text-orange-700'
                          : 'bg-green-50 text-green-700'
                    }`}>
                      <Clock className="w-4 h-4" />
                      <span>{formatDaysUntilExpiry(job.days_until_expiry)}</span>
                    </div>

                    {/* Activity Indicators */}
                    <div className="flex flex-wrap items-center gap-3 mt-4 pt-4 border-t border-slate-200">
                      <div className="flex items-center gap-2 px-3 py-1.5 bg-blue-50 rounded-lg" data-testid={`job-${job.id}-applications`}>
                        <Users className="w-4 h-4 text-blue-600" />
                        <span className="text-sm font-medium text-blue-800">{job.stats.total_applications} Applications</span>
                      </div>
                      
                      {job.stats.shortlisted > 0 && (
                        <div className="flex items-center gap-2 px-3 py-1.5 bg-purple-50 rounded-lg">
                          <Star className="w-4 h-4 text-purple-600" />
                          <span className="text-sm font-medium text-purple-800">{job.stats.shortlisted} Shortlisted</span>
                        </div>
                      )}
                      
                      {job.stats.interviewed > 0 && (
                        <div className="flex items-center gap-2 px-3 py-1.5 bg-indigo-50 rounded-lg">
                          <MessageSquare className="w-4 h-4 text-indigo-600" />
                          <span className="text-sm font-medium text-indigo-800">{job.stats.interviewed} Interviews</span>
                        </div>
                      )}
                      
                      {job.stats.offered > 0 && (
                        <div className="flex items-center gap-2 px-3 py-1.5 bg-green-50 rounded-lg">
                          <CheckCircle className="w-4 h-4 text-green-600" />
                          <span className="text-sm font-medium text-green-800">{job.stats.offered} Offers</span>
                        </div>
                      )}
                      
                      {job.stats.pending > 0 && (
                        <div className="flex items-center gap-2 px-3 py-1.5 bg-yellow-50 rounded-lg">
                          <Clock className="w-4 h-4 text-yellow-600" />
                          <span className="text-sm font-medium text-yellow-800">{job.stats.pending} Pending</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex flex-col gap-2 ml-4">
                    <Button
                      size="sm"
                      onClick={() => handleViewApplicants(job)}
                      className="bg-blue-600 hover:bg-blue-700"
                      data-testid={`view-applicants-${job.id}`}
                    >
                      <Eye className="w-4 h-4 mr-2" />
                      View Applicants
                    </Button>
                    
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleOpenNotes(job)}
                      data-testid={`add-notes-${job.id}`}
                    >
                      <StickyNote className="w-4 h-4 mr-2" />
                      {job.recruiter_notes ? 'Edit Notes' : 'Add Notes'}
                    </Button>
                    
                    {job.is_expired && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleOpenReactivate(job)}
                        className="border-green-500 text-green-700 hover:bg-green-50"
                        data-testid={`reactivate-${job.id}`}
                      >
                        <RotateCcw className="w-4 h-4 mr-2" />
                        Reactivate
                      </Button>
                    )}
                    
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => window.location.href = `/my-jobs?edit=${job.id}`}
                    >
                      <Edit className="w-4 h-4 mr-2" />
                      Edit Job
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Notes Modal */}
      <Dialog open={showNotesModal} onOpenChange={setShowNotesModal}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle className="text-xl font-bold text-slate-800">
              Notes for: {selectedJob?.title}
            </DialogTitle>
          </DialogHeader>
          
          <div className="py-4">
            <Textarea
              value={notesText}
              onChange={(e) => setNotesText(e.target.value)}
              placeholder="Add your notes about this job... (e.g., hiring status, internal feedback, priorities)"
              rows={6}
              className="resize-none"
              data-testid="notes-textarea"
            />
            <p className="text-xs text-slate-500 mt-2">
              Notes are private and visible only to your team
            </p>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowNotesModal(false)}>
              Cancel
            </Button>
            <Button 
              onClick={handleSaveNotes} 
              disabled={saving}
              className="bg-blue-600 hover:bg-blue-700"
              data-testid="save-notes-btn"
            >
              {saving ? 'Saving...' : 'Save Notes'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Reactivate Modal */}
      <Dialog open={showReactivateModal} onOpenChange={setShowReactivateModal}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="text-xl font-bold text-slate-800">
              Reactivate Job Listing
            </DialogTitle>
          </DialogHeader>
          
          <div className="py-4 space-y-4">
            <p className="text-slate-600">
              Reactivate "{selectedJob?.title}" and make it visible to job seekers again.
            </p>
            
            <div className="space-y-2">
              <Label>Extension Period</Label>
              <select
                value={extensionDays}
                onChange={(e) => setExtensionDays(parseInt(e.target.value))}
                className="w-full border border-slate-300 rounded-md px-3 py-2"
                data-testid="extension-days-select"
              >
                <option value={7}>7 days</option>
                <option value={14}>14 days</option>
                <option value={21}>21 days</option>
                <option value={30}>30 days</option>
                <option value={35}>35 days (Standard)</option>
                <option value={60}>60 days</option>
              </select>
              <p className="text-xs text-slate-500">
                The job will be active for this many days from today
              </p>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowReactivateModal(false)}>
              Cancel
            </Button>
            <Button 
              onClick={handleReactivateJob} 
              disabled={saving}
              className="bg-green-600 hover:bg-green-700"
              data-testid="confirm-reactivate-btn"
            >
              {saving ? 'Reactivating...' : 'Reactivate Job'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Applicants Modal (Pipeline View) */}
      <Dialog open={showApplicantsModal} onOpenChange={setShowApplicantsModal}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-xl font-bold text-slate-800">
              Applicants for: {selectedJob?.title}
            </DialogTitle>
          </DialogHeader>
          
          <div className="py-4">
            {/* Status Filter */}
            <div className="flex flex-wrap gap-2 mb-6">
              {['all', 'pending', 'reviewed', 'shortlisted', 'interviewed', 'offered', 'rejected'].map((status) => (
                <Button
                  key={status}
                  size="sm"
                  variant={applicantStatusFilter === status ? 'default' : 'outline'}
                  onClick={() => {
                    setApplicantStatusFilter(status);
                    if (selectedJob) fetchApplicants(selectedJob.id, status);
                  }}
                  className="capitalize"
                >
                  {status === 'all' ? 'All' : status}
                </Button>
              ))}
            </div>

            {/* Applicants List */}
            {applicantsLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            ) : applicants.length === 0 ? (
              <div className="text-center py-8">
                <Users className="w-12 h-12 text-slate-300 mx-auto mb-4" />
                <p className="text-slate-600">No applicants found</p>
              </div>
            ) : (
              <div className="space-y-4">
                {applicants.map((app) => {
                  const applicant = app.applicant_snapshot || app.applicant_profile || {};
                  
                  return (
                    <Card key={app.id} className="border border-slate-200" data-testid={`applicant-card-${app.id}`}>
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex items-start gap-4">
                            {/* Avatar */}
                            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-slate-600 rounded-full flex items-center justify-center text-white font-semibold">
                              {(applicant.first_name || '?')[0]}{(applicant.last_name || '?')[0]}
                            </div>
                            
                            {/* Info */}
                            <div>
                              <div className="flex items-center gap-3 mb-2">
                                <h4 className="font-bold text-slate-800">
                                  {applicant.first_name || 'Unknown'} {applicant.last_name || 'Applicant'}
                                </h4>
                                {getStatusBadge(app.status)}
                              </div>
                              
                              <div className="flex flex-wrap items-center gap-4 text-sm text-slate-600 mb-3">
                                <div className="flex items-center gap-1">
                                  <Mail className="w-4 h-4" />
                                  <span>{applicant.email || 'No email'}</span>
                                </div>
                                {applicant.location && (
                                  <div className="flex items-center gap-1">
                                    <MapPin className="w-4 h-4" />
                                    <span>{applicant.location}</span>
                                  </div>
                                )}
                                <div className="flex items-center gap-1">
                                  <Clock className="w-4 h-4" />
                                  <span>Applied {formatDate(app.applied_date)}</span>
                                </div>
                              </div>

                              {/* Skills */}
                              {applicant.skills && applicant.skills.length > 0 && (
                                <div className="flex flex-wrap gap-1 mb-3">
                                  {applicant.skills.slice(0, 5).map((skill, idx) => (
                                    <Badge key={idx} variant="outline" className="text-xs">
                                      {skill}
                                    </Badge>
                                  ))}
                                  {applicant.skills.length > 5 && (
                                    <Badge variant="outline" className="text-xs">
                                      +{applicant.skills.length - 5} more
                                    </Badge>
                                  )}
                                </div>
                              )}

                              {/* Cover Letter Preview */}
                              {app.cover_letter && (
                                <p className="text-sm text-slate-600 line-clamp-2 mb-3">
                                  {app.cover_letter}
                                </p>
                              )}
                            </div>
                          </div>

                          {/* Actions */}
                          <div className="flex flex-col gap-2">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleViewApplicantProfile(app)}
                              data-testid={`view-profile-${app.id}`}
                            >
                              <User className="w-4 h-4 mr-1" />
                              View Profile
                            </Button>
                            
                            {app.resume_url && (
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => window.open(`${BACKEND_URL}${app.resume_url}`, '_blank')}
                              >
                                <FileText className="w-4 h-4 mr-1" />
                                Resume
                              </Button>
                            )}
                          </div>
                        </div>

                        {/* Status Action Buttons */}
                        <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-slate-200">
                          {app.status === 'pending' && (
                            <>
                              <Button size="sm" onClick={() => handleUpdateApplicationStatus(app.id, 'reviewed')} className="bg-blue-600 hover:bg-blue-700">
                                <Eye className="w-4 h-4 mr-1" /> Mark Reviewed
                              </Button>
                              <Button size="sm" variant="outline" onClick={() => handleUpdateApplicationStatus(app.id, 'rejected')} className="text-red-600 border-red-300 hover:bg-red-50">
                                <XCircle className="w-4 h-4 mr-1" /> Reject
                              </Button>
                            </>
                          )}
                          {app.status === 'reviewed' && (
                            <>
                              <Button size="sm" onClick={() => handleUpdateApplicationStatus(app.id, 'shortlisted')} className="bg-purple-600 hover:bg-purple-700">
                                <Star className="w-4 h-4 mr-1" /> Shortlist
                              </Button>
                              <Button size="sm" variant="outline" onClick={() => handleUpdateApplicationStatus(app.id, 'rejected')} className="text-red-600 border-red-300 hover:bg-red-50">
                                <XCircle className="w-4 h-4 mr-1" /> Reject
                              </Button>
                            </>
                          )}
                          {app.status === 'shortlisted' && (
                            <>
                              <Button size="sm" onClick={() => handleUpdateApplicationStatus(app.id, 'interviewed')} className="bg-indigo-600 hover:bg-indigo-700">
                                <MessageSquare className="w-4 h-4 mr-1" /> Schedule Interview
                              </Button>
                              <Button size="sm" variant="outline" onClick={() => handleUpdateApplicationStatus(app.id, 'rejected')} className="text-red-600 border-red-300 hover:bg-red-50">
                                <XCircle className="w-4 h-4 mr-1" /> Reject
                              </Button>
                            </>
                          )}
                          {app.status === 'interviewed' && (
                            <>
                              <Button size="sm" onClick={() => handleUpdateApplicationStatus(app.id, 'offered')} className="bg-green-600 hover:bg-green-700">
                                <CheckCircle className="w-4 h-4 mr-1" /> Make Offer
                              </Button>
                              <Button size="sm" variant="outline" onClick={() => handleUpdateApplicationStatus(app.id, 'rejected')} className="text-red-600 border-red-300 hover:bg-red-50">
                                <XCircle className="w-4 h-4 mr-1" /> Reject
                              </Button>
                            </>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* Applicant Profile Modal */}
      <Dialog open={showApplicantProfile} onOpenChange={setShowApplicantProfile}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-xl font-bold text-slate-800">
              Applicant Profile
            </DialogTitle>
          </DialogHeader>
          
          {selectedApplicant && (
            <div className="py-4 space-y-6">
              {/* Header */}
              <div className="flex items-start gap-4">
                <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-slate-600 rounded-full flex items-center justify-center text-white text-2xl font-bold">
                  {(selectedApplicant.applicant_snapshot?.first_name || selectedApplicant.applicant_profile?.first_name || '?')[0]}
                  {(selectedApplicant.applicant_snapshot?.last_name || selectedApplicant.applicant_profile?.last_name || '?')[0]}
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-slate-800">
                    {selectedApplicant.applicant_snapshot?.first_name || selectedApplicant.applicant_profile?.first_name || 'Unknown'}{' '}
                    {selectedApplicant.applicant_snapshot?.last_name || selectedApplicant.applicant_profile?.last_name || 'Applicant'}
                  </h2>
                  <div className="flex items-center gap-2 mt-2">
                    {getStatusBadge(selectedApplicant.status)}
                    <span className="text-slate-500">Applied {formatDate(selectedApplicant.applied_date)}</span>
                  </div>
                </div>
              </div>

              {/* Contact Info */}
              <div className="grid grid-cols-2 gap-4 p-4 bg-slate-50 rounded-lg">
                <div className="flex items-center gap-2">
                  <Mail className="w-5 h-5 text-slate-500" />
                  <span>{selectedApplicant.applicant_snapshot?.email || selectedApplicant.applicant_profile?.email || 'N/A'}</span>
                </div>
                <div className="flex items-center gap-2">
                  <MapPin className="w-5 h-5 text-slate-500" />
                  <span>{selectedApplicant.applicant_snapshot?.location || selectedApplicant.applicant_profile?.location || 'N/A'}</span>
                </div>
              </div>

              {/* About */}
              {(selectedApplicant.applicant_snapshot?.about_me || selectedApplicant.applicant_profile?.about_me) && (
                <div>
                  <h3 className="font-semibold text-slate-800 mb-2">About</h3>
                  <p className="text-slate-600">
                    {selectedApplicant.applicant_snapshot?.about_me || selectedApplicant.applicant_profile?.about_me}
                  </p>
                </div>
              )}

              {/* Skills */}
              {(selectedApplicant.applicant_snapshot?.skills?.length > 0 || selectedApplicant.applicant_profile?.skills?.length > 0) && (
                <div>
                  <h3 className="font-semibold text-slate-800 mb-2">Skills</h3>
                  <div className="flex flex-wrap gap-2">
                    {(selectedApplicant.applicant_snapshot?.skills || selectedApplicant.applicant_profile?.skills || []).map((skill, idx) => (
                      <Badge key={idx} variant="outline">{skill}</Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Cover Letter */}
              {selectedApplicant.cover_letter && (
                <div>
                  <h3 className="font-semibold text-slate-800 mb-2">Cover Letter</h3>
                  <div className="p-4 bg-slate-50 rounded-lg">
                    <p className="text-slate-600 whitespace-pre-wrap">{selectedApplicant.cover_letter}</p>
                  </div>
                </div>
              )}

              {/* Resume Link */}
              {selectedApplicant.resume_url && (
                <Button
                  variant="outline"
                  onClick={() => window.open(`${BACKEND_URL}${selectedApplicant.resume_url}`, '_blank')}
                  className="w-full"
                >
                  <FileText className="w-4 h-4 mr-2" />
                  View Resume / CV
                  <ExternalLink className="w-4 h-4 ml-2" />
                </Button>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default JobsDashboard;
