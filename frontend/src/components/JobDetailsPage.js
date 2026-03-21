import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Separator } from "./ui/separator";
import { 
  MapPin, 
  Calendar, 
  Briefcase, 
  Building2, 
  Clock, 
  ChevronLeft,
  Share2,
  Heart,
  ExternalLink,
  CheckCircle,
  User,
  Mail,
  Phone,
  FileText,
  Upload,
  Loader2
} from "lucide-react";
import { Input } from "./ui/input";
import { Textarea } from "./ui/textarea";
import { Label } from "./ui/label";
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const JobDetailsPage = ({ user }) => {
  const { jobId } = useParams();
  const navigate = useNavigate();
  
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [applying, setApplying] = useState(false);
  const [applied, setApplied] = useState(false);
  const [showApplicationForm, setShowApplicationForm] = useState(false);
  
  // Application form state
  const [applicationData, setApplicationData] = useState({
    cover_letter: '',
    resume_file: null,
    resume_url: '',
    additional_info: ''
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

  const getUploadHeaders = () => {
    const token = localStorage.getItem('token');
    return {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    };
  };

  useEffect(() => {
    fetchJobDetails();
    if (user) {
      checkIfApplied();
      // Pre-fill user info
      setApplicationData(prev => ({
        ...prev,
        resume_url: user.resume_url || user.cv_url || '',
        additional_info: `Skills: ${(user.skills || []).join(', ')}\n\n`
      }));
    }
  }, [jobId, user]);

  const fetchJobDetails = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/public/jobs/${jobId}`);
      setJob(response.data);
    } catch (err) {
      console.error('Error fetching job details:', err);
      setError('Job not found or has been removed.');
    } finally {
      setLoading(false);
    }
  };

  const checkIfApplied = async () => {
    try {
      const response = await axios.get(`${API}/applications`, getAuthHeaders());
      const hasApplied = response.data.some(app => app.application?.job_id === jobId);
      setApplied(hasApplied);
    } catch (err) {
      console.error('Error checking application status:', err);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      if (!allowedTypes.includes(file.type)) {
        alert('Please upload a PDF, DOC, or DOCX file');
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        alert('File size must be less than 5MB');
        return;
      }
      setApplicationData(prev => ({ ...prev, resume_file: file }));
    }
  };

  const handleSubmitApplication = async (e) => {
    e.preventDefault();
    if (!user) {
      navigate('/login');
      return;
    }

    setApplying(true);
    try {
      let finalApplicationData = { ...applicationData };

      // Handle file upload if a file is selected
      if (applicationData.resume_file) {
        const formData = new FormData();
        formData.append('file', applicationData.resume_file);
        
        try {
          const uploadResponse = await axios.post(
            `${API}/uploads/cv`,
            formData,
            getUploadHeaders()
          );
          finalApplicationData.resume_url = uploadResponse.data.url;
          delete finalApplicationData.resume_file;
        } catch (uploadError) {
          console.error('File upload error:', uploadError);
          throw new Error(uploadError.response?.data?.detail || 'Failed to upload CV file');
        }
      } else {
        delete finalApplicationData.resume_file;
      }

      await axios.post(
        `${API}/jobs/${job.id}/apply`,
        {
          job_id: job.id,
          ...finalApplicationData
        },
        getAuthHeaders()
      );

      setApplied(true);
      setShowApplicationForm(false);
      alert('Application submitted successfully!');
    } catch (err) {
      console.error('Error submitting application:', err);
      alert(err.message || err.response?.data?.detail || 'Failed to submit application');
    } finally {
      setApplying(false);
    }
  };

  const handleShare = async () => {
    const url = window.location.href;
    if (navigator.share) {
      try {
        await navigator.share({
          title: `${job.title} at ${job.company_name}`,
          text: `Check out this job opportunity: ${job.title}`,
          url: url
        });
      } catch (err) {
        console.log('Share cancelled');
      }
    } else {
      navigator.clipboard.writeText(url);
      alert('Link copied to clipboard!');
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    return date.toLocaleDateString('en-ZA', { day: 'numeric', month: 'short', year: 'numeric' });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-slate-600">Loading job details...</p>
        </div>
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 flex items-center justify-center">
        <Card className="max-w-md w-full mx-4">
          <CardContent className="pt-6 text-center">
            <Briefcase className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-slate-800 mb-2">Job Not Found</h2>
            <p className="text-slate-600 mb-6">{error || 'This job listing may have been removed or is no longer available.'}</p>
            <Button onClick={() => navigate('/jobs')} className="bg-blue-600 hover:bg-blue-700">
              <ChevronLeft className="w-4 h-4 mr-2" />
              Browse All Jobs
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Back Button */}
        <Button 
          variant="ghost" 
          onClick={() => navigate('/jobs')}
          className="mb-6 text-slate-600 hover:text-slate-800"
        >
          <ChevronLeft className="w-4 h-4 mr-1" />
          Back to Jobs
        </Button>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Job Header Card */}
            <Card className="bg-white shadow-lg border-0">
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-4">
                    <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-700 rounded-xl flex items-center justify-center text-white text-2xl font-bold shadow-lg">
                      {job.company_name?.charAt(0) || 'J'}
                    </div>
                    <div>
                      <h1 className="text-2xl font-bold text-slate-800">{job.title}</h1>
                      <p className="text-lg text-slate-600">{job.company_name}</p>
                    </div>
                  </div>
                  <Button variant="ghost" size="icon" onClick={handleShare} title="Share this job">
                    <Share2 className="w-5 h-5 text-slate-500" />
                  </Button>
                </div>

                {/* Job Meta Info */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  <div className="flex items-center text-slate-600">
                    <MapPin className="w-4 h-4 mr-2 text-blue-500" />
                    <span className="text-sm">{job.location}</span>
                  </div>
                  {job.salary && (
                    <div className="flex items-center text-slate-600">
                      <span className="font-semibold mr-1 text-blue-500">R</span>
                      <span className="text-sm">{job.salary}</span>
                    </div>
                  )}
                  <div className="flex items-center text-slate-600">
                    <Briefcase className="w-4 h-4 mr-2 text-blue-500" />
                    <span className="text-sm">{job.job_type || 'Not specified'}</span>
                  </div>
                  <div className="flex items-center text-slate-600">
                    <Calendar className="w-4 h-4 mr-2 text-blue-500" />
                    <span className="text-sm">Posted {formatDate(job.posted_date)}</span>
                  </div>
                </div>

                {/* Tags */}
                <div className="flex flex-wrap gap-2 mb-6">
                  {job.job_type && (
                    <Badge variant="secondary" className="bg-blue-100 text-blue-700">
                      {job.job_type}
                    </Badge>
                  )}
                  {job.work_type && (
                    <Badge variant="secondary" className={
                      job.work_type === 'Remote' ? 'bg-green-100 text-green-700' :
                      job.work_type === 'Hybrid' ? 'bg-purple-100 text-purple-700' :
                      'bg-orange-100 text-orange-700'
                    }>
                      {job.work_type}
                    </Badge>
                  )}
                  {job.industry && (
                    <Badge variant="secondary" className="bg-slate-100 text-slate-700">
                      {job.industry}
                    </Badge>
                  )}
                </div>

                {/* Apply Button (Mobile) */}
                <div className="lg:hidden">
                  {applied ? (
                    <Button disabled className="w-full bg-green-600">
                      <CheckCircle className="w-4 h-4 mr-2" />
                      Already Applied
                    </Button>
                  ) : user ? (
                    <Button 
                      onClick={() => setShowApplicationForm(!showApplicationForm)} 
                      className="w-full bg-blue-600 hover:bg-blue-700"
                    >
                      {showApplicationForm ? 'Hide Application Form' : 'Apply Now'}
                    </Button>
                  ) : (
                    <Button 
                      onClick={() => navigate('/login')} 
                      className="w-full bg-blue-600 hover:bg-blue-700"
                    >
                      Login to Apply
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Job Description */}
            <Card className="bg-white shadow-lg border-0">
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-slate-800">Job Description</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="prose prose-slate max-w-none">
                  <p className="text-slate-700 whitespace-pre-wrap leading-relaxed">{job.description}</p>
                </div>

                {job.experience && (
                  <>
                    <Separator className="my-6" />
                    <h3 className="font-semibold text-slate-800 mb-3">Experience Required</h3>
                    <p className="text-slate-700">{job.experience}</p>
                  </>
                )}

                {job.qualifications && (
                  <>
                    <Separator className="my-6" />
                    <h3 className="font-semibold text-slate-800 mb-3">Qualifications</h3>
                    <p className="text-slate-700 whitespace-pre-wrap">{job.qualifications}</p>
                  </>
                )}
              </CardContent>
            </Card>

            {/* Application Form (shown when Apply Now is clicked) */}
            {showApplicationForm && user && !applied && (
              <Card className="bg-white shadow-lg border-0">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold text-slate-800">Submit Your Application</CardTitle>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSubmitApplication} className="space-y-6">
                    {/* User Info Display */}
                    <div className="bg-slate-50 p-4 rounded-lg">
                      <h4 className="font-medium text-slate-700 mb-3">Your Information</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                        <div className="flex items-center text-slate-600">
                          <User className="w-4 h-4 mr-2" />
                          {user.first_name} {user.last_name}
                        </div>
                        <div className="flex items-center text-slate-600">
                          <Mail className="w-4 h-4 mr-2" />
                          {user.email}
                        </div>
                        {user.phone && (
                          <div className="flex items-center text-slate-600">
                            <Phone className="w-4 h-4 mr-2" />
                            {user.phone}
                          </div>
                        )}
                        {user.location && (
                          <div className="flex items-center text-slate-600">
                            <MapPin className="w-4 h-4 mr-2" />
                            {user.location}
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Cover Letter */}
                    <div>
                      <Label htmlFor="cover_letter">Cover Letter (Optional)</Label>
                      <Textarea
                        id="cover_letter"
                        value={applicationData.cover_letter}
                        onChange={(e) => setApplicationData(prev => ({ ...prev, cover_letter: e.target.value }))}
                        placeholder="Write a brief cover letter explaining why you're interested in this position..."
                        className="mt-1 min-h-[120px]"
                      />
                    </div>

                    {/* Resume Upload */}
                    <div>
                      <Label htmlFor="resume_file">Upload Resume/CV</Label>
                      <div className="mt-1 flex items-center space-x-4">
                        <input
                          type="file"
                          id="resume_file"
                          accept=".pdf,.doc,.docx"
                          onChange={handleFileChange}
                          className="hidden"
                        />
                        <Button
                          type="button"
                          variant="outline"
                          onClick={() => document.getElementById('resume_file').click()}
                        >
                          <Upload className="w-4 h-4 mr-2" />
                          {applicationData.resume_file ? 'Change File' : 'Choose File'}
                        </Button>
                        {applicationData.resume_file && (
                          <span className="text-sm text-slate-600 flex items-center">
                            <FileText className="w-4 h-4 mr-1" />
                            {applicationData.resume_file.name}
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-slate-500 mt-1">PDF, DOC, DOCX - Max 5MB</p>
                    </div>

                    {/* Additional Info */}
                    <div>
                      <Label htmlFor="additional_info">Additional Information (Optional)</Label>
                      <Textarea
                        id="additional_info"
                        value={applicationData.additional_info}
                        onChange={(e) => setApplicationData(prev => ({ ...prev, additional_info: e.target.value }))}
                        placeholder="Any additional information you'd like to share..."
                        className="mt-1"
                      />
                    </div>

                    {/* Submit Button */}
                    <div className="flex space-x-3">
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => setShowApplicationForm(false)}
                        className="flex-1"
                      >
                        Cancel
                      </Button>
                      <Button
                        type="submit"
                        disabled={applying}
                        className="flex-1 bg-blue-600 hover:bg-blue-700"
                      >
                        {applying ? (
                          <>
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            Submitting...
                          </>
                        ) : (
                          'Submit Application'
                        )}
                      </Button>
                    </div>
                  </form>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Apply Card */}
            <Card className="bg-white shadow-lg border-0 sticky top-6">
              <CardContent className="p-6">
                <h3 className="font-semibold text-slate-800 mb-4">Apply for this position</h3>
                
                {applied ? (
                  <div className="text-center py-4">
                    <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-3" />
                    <p className="text-green-700 font-medium">You've applied for this job</p>
                    <p className="text-sm text-slate-500 mt-1">Good luck with your application!</p>
                    <Link to="/my-applications">
                      <Button variant="outline" className="mt-4 w-full">
                        View My Applications
                      </Button>
                    </Link>
                  </div>
                ) : user ? (
                  <>
                    <Button 
                      onClick={() => setShowApplicationForm(!showApplicationForm)} 
                      className="w-full bg-blue-600 hover:bg-blue-700 mb-3"
                    >
                      {showApplicationForm ? 'Hide Form' : 'Apply Now'}
                    </Button>
                    <p className="text-xs text-slate-500 text-center">
                      Your profile information will be shared with the employer
                    </p>
                  </>
                ) : (
                  <>
                    <Button 
                      onClick={() => navigate('/login')} 
                      className="w-full bg-blue-600 hover:bg-blue-700 mb-3"
                    >
                      Login to Apply
                    </Button>
                    <p className="text-xs text-slate-500 text-center">
                      Don't have an account?{' '}
                      <Link to="/register" className="text-blue-600 hover:underline">
                        Register here
                      </Link>
                    </p>
                  </>
                )}

                <Separator className="my-4" />

                <Button variant="outline" onClick={handleShare} className="w-full">
                  <Share2 className="w-4 h-4 mr-2" />
                  Share this Job
                </Button>
              </CardContent>
            </Card>

            {/* Company Info */}
            <Card className="bg-white shadow-lg border-0">
              <CardContent className="p-6">
                <h3 className="font-semibold text-slate-800 mb-4">About the Company</h3>
                <div className="flex items-center space-x-3 mb-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-700 rounded-lg flex items-center justify-center text-white text-lg font-bold">
                    {job.company_name?.charAt(0) || 'C'}
                  </div>
                  <div>
                    <p className="font-medium text-slate-800">{job.company_name}</p>
                    <p className="text-sm text-slate-500">{job.industry || 'Industry not specified'}</p>
                  </div>
                </div>
                {job.application_url && (
                  <a 
                    href={job.application_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-sm text-blue-600 hover:underline flex items-center"
                  >
                    Visit Company Website
                    <ExternalLink className="w-3 h-3 ml-1" />
                  </a>
                )}
              </CardContent>
            </Card>

            {/* Job Stats */}
            <Card className="bg-white shadow-lg border-0">
              <CardContent className="p-6">
                <h3 className="font-semibold text-slate-800 mb-4">Job Details</h3>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Posted</span>
                    <span className="text-slate-800">{formatDate(job.posted_date)}</span>
                  </div>
                  {job.expiry_date && (
                    <div className="flex justify-between">
                      <span className="text-slate-500">Expires</span>
                      <span className="text-slate-800">{formatDate(job.expiry_date)}</span>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span className="text-slate-500">Job Type</span>
                    <span className="text-slate-800">{job.job_type || 'Not specified'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Work Type</span>
                    <span className="text-slate-800">{job.work_type || 'Not specified'}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default JobDetailsPage;
