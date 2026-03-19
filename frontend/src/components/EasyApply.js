import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Textarea } from "./ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Label } from "./ui/label";
import { Badge } from "./ui/badge";
import { 
  X,
  Send,
  Upload,
  FileText,
  Building2,
  MapPin,
  DollarSign,
  CheckCircle,
  AlertCircle,
  ExternalLink,
  User
} from "lucide-react";
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const EasyApplyModal = ({ job, isOpen, onClose, onSuccess, user }) => {
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1);
  const [applicationData, setApplicationData] = useState({
    cover_letter: '',
    resume_file: null,
    resume_url: '',
    additional_info: ''
  });
  const [uploadedFileName, setUploadedFileName] = useState('');
  const [uploadError, setUploadError] = useState('');

  // Pre-populate form when modal opens and user data is available
  useEffect(() => {
    if (isOpen && user) {
      setApplicationData(prev => ({
        ...prev,
        resume_url: user.resume_url || user.cv_url || '',
        additional_info: user.skills && user.skills.length > 0 
          ? `Skills: ${user.skills.join(', ')}\n\n`
          : ''
      }));
      setUploadedFileName('');
      setUploadError('');
    }
  }, [isOpen, user]);

  const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    return {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    };
  };

  const handleInputChange = (field, value) => {
    setApplicationData(prev => ({ ...prev, [field]: value }));
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    setUploadError('');
    
    if (file) {
      // Validate file type (PDF, DOC, DOCX)
      const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      if (!allowedTypes.includes(file.type)) {
        setUploadError('Please upload a PDF, DOC, or DOCX file');
        return;
      }
      
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        setUploadError('File size must be less than 5MB');
        return;
      }
      
      setApplicationData(prev => ({ ...prev, resume_file: file }));
      setUploadedFileName(file.name);
      
      // Clear the URL field since we're using file upload instead
      setApplicationData(prev => ({ ...prev, resume_url: '' }));
    }
  };

  const removeUploadedFile = () => {
    setApplicationData(prev => ({ ...prev, resume_file: null }));
    setUploadedFileName('');
    setUploadError('');
    // Reset the file input
    const fileInput = document.getElementById('resume_file');
    if (fileInput) fileInput.value = '';
  };

  const handleSubmitApplication = async () => {
    try {
      setLoading(true);
      
      let finalApplicationData = { ...applicationData };
      
      // Handle file upload if a file is selected
      if (applicationData.resume_file) {
        const formData = new FormData();
        formData.append('file', applicationData.resume_file);
        
        try {
          const uploadResponse = await axios.post(
            `${API}/upload-cv`,
            formData,
            {
              headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Content-Type': 'multipart/form-data'
              }
            }
          );
          
          // Use the uploaded file URL instead of the local file
          finalApplicationData.resume_url = uploadResponse.data.file_url;
          // Remove the file object from the data
          delete finalApplicationData.resume_file;
        } catch (uploadError) {
          console.error('File upload error:', uploadError);
          throw new Error(uploadError.response?.data?.detail || 'Failed to upload CV file');
        }
      } else {
        // Remove the file object if no file was uploaded
        delete finalApplicationData.resume_file;
      }

      const response = await axios.post(
        `${API}/jobs/${job.id}/apply`,
        {
          job_id: job.id,
          ...finalApplicationData
        },
        getAuthHeaders()
      );

      setStep(3); // Success step
      if (onSuccess) {
        setTimeout(() => {
          onSuccess(response.data);
          onClose();
        }, 2000);
      }
      
    } catch (error) {
      console.error('Application error:', error);
      alert(error.message || error.response?.data?.detail || 'Failed to submit application');
    } finally {
      setLoading(false);
    }
  };

  const resetModal = () => {
    setStep(1);
    setApplicationData({
      cover_letter: '',
      resume_file: null,
      resume_url: '',
      additional_info: ''
    });
    setUploadedFileName('');
    setUploadError('');
  };

  const handleClose = () => {
    resetModal();
    onClose();
  };

  if (!isOpen || !job) return null;

  // Use createPortal to render modal at document body level
  return ReactDOM.createPortal(
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[9999] flex items-center justify-center p-4" style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0 }}>
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto bg-white shadow-2xl relative">
        <CardHeader className="border-b border-slate-200">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center space-x-2">
              <Send className="w-5 h-5 text-blue-600" />
              <span>Easy Apply</span>
            </CardTitle>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClose}
              className="hover:bg-slate-100"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
          
          {/* Progress indicator */}
          <div className="flex items-center space-x-4 mt-4">
            <div className={`flex items-center space-x-2 ${step >= 1 ? 'text-blue-600' : 'text-slate-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
                step >= 1 ? 'border-blue-600 bg-blue-50' : 'border-slate-300'
              }`}>
                1
              </div>
              <span className="text-sm font-medium">Job Details</span>
            </div>
            <div className={`w-12 h-0.5 ${step >= 2 ? 'bg-blue-600' : 'bg-slate-300'}`}></div>
            <div className={`flex items-center space-x-2 ${step >= 2 ? 'text-blue-600' : 'text-slate-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
                step >= 2 ? 'border-blue-600 bg-blue-50' : 'border-slate-300'
              }`}>
                2
              </div>
              <span className="text-sm font-medium">Application</span>
            </div>
            <div className={`w-12 h-0.5 ${step >= 3 ? 'bg-green-600' : 'bg-slate-300'}`}></div>
            <div className={`flex items-center space-x-2 ${step >= 3 ? 'text-green-600' : 'text-slate-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
                step >= 3 ? 'border-green-600 bg-green-50' : 'border-slate-300'
              }`}>
                {step >= 3 ? <CheckCircle className="w-4 h-4" /> : '3'}
              </div>
              <span className="text-sm font-medium">Complete</span>
            </div>
          </div>
        </CardHeader>

        <CardContent className="p-6">
          {/* Step 1: Job Details */}
          {step === 1 && (
            <div className="space-y-6">
              <div className="text-center">
                <h3 className="text-xl font-bold text-slate-800 mb-2">
                  Apply for this position
                </h3>
                <p className="text-slate-600">
                  Review the job details before submitting your application
                </p>
              </div>

              <div className="bg-slate-50 rounded-xl p-6 space-y-4">
                <h4 className="text-lg font-semibold text-slate-800">{job.title}</h4>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div className="flex items-center space-x-2 text-slate-600">
                    <Building2 className="w-4 h-4" />
                    <span>{job.company_name}</span>
                  </div>
                  <div className="flex items-center space-x-2 text-slate-600">
                    <MapPin className="w-4 h-4" />
                    <span>{job.location}</span>
                  </div>
                  {job.salary && (
                    <div className="flex items-center space-x-2 text-slate-600">
                      <span className="font-semibold">R</span>
                      <span>{job.salary}</span>
                    </div>
                  )}
                </div>

                <div className="flex items-center space-x-2">
                  <Badge variant="outline">{job.job_type}</Badge>
                  <Badge variant="outline">{job.work_type}</Badge>
                  <Badge variant="outline">{job.industry}</Badge>
                </div>

                {job.description && (
                  <div>
                    <p className="text-slate-700 text-sm line-clamp-3">
                      {job.description}
                    </p>
                  </div>
                )}
              </div>

              <div className="flex justify-end space-x-3">
                <Button variant="outline" onClick={handleClose}>
                  Cancel
                </Button>
                <Button onClick={() => setStep(2)}>
                  Continue Application
                </Button>
              </div>
            </div>
          )}

          {/* Step 2: Application Form */}
          {step === 2 && (
            <div className="space-y-6">
              <div className="text-center">
                <h3 className="text-xl font-bold text-slate-800 mb-2">
                  Complete Your Application
                </h3>
                <p className="text-slate-600">
                  Add your cover letter and additional information
                </p>
              </div>

              <form className="space-y-6">
                {/* Pre-populated Profile Information */}
                {user && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h4 className="font-semibold text-blue-900 mb-3 flex items-center">
                      <User className="w-4 h-4 mr-2" />
                      Your Profile Information
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="font-medium text-blue-800">Name:</span>
                        <p className="text-blue-700">{user.first_name} {user.last_name}</p>
                      </div>
                      <div>
                        <span className="font-medium text-blue-800">Email:</span>
                        <p className="text-blue-700">{user.email}</p>
                      </div>
                      {user.location && (
                        <div>
                          <span className="font-medium text-blue-800">Location:</span>
                          <p className="text-blue-700">{user.location}</p>
                        </div>
                      )}
                      {user.phone && (
                        <div>
                          <span className="font-medium text-blue-800">Phone:</span>
                          <p className="text-blue-700">{user.phone}</p>
                        </div>
                      )}
                    </div>
                    
                    {user.skills && user.skills.length > 0 && (
                      <div className="mt-3">
                        <span className="font-medium text-blue-800">Skills:</span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {user.skills.slice(0, 6).map((skill, index) => (
                            <Badge key={index} variant="outline" className="text-xs bg-white border-blue-300 text-blue-700">
                              {skill}
                            </Badge>
                          ))}
                          {user.skills.length > 6 && (
                            <Badge variant="outline" className="text-xs bg-white border-blue-300 text-blue-700">
                              +{user.skills.length - 6} more
                            </Badge>
                          )}
                        </div>
                      </div>
                    )}
                    
                    {(user.resume_url || user.cv_url) && (
                      <div className="mt-3">
                        <span className="font-medium text-blue-800">CV/Resume:</span>
                        <p className="text-blue-700 text-xs truncate">{user.resume_url || user.cv_url}</p>
                      </div>
                    )}
                  </div>
                )}

                <div className="space-y-2">
                  <Label htmlFor="cover_letter">Cover Letter (Optional)</Label>
                  <Textarea
                    id="cover_letter"
                    value={applicationData.cover_letter}
                    onChange={(e) => handleInputChange('cover_letter', e.target.value)}
                    placeholder="Write a brief cover letter explaining why you're interested in this position and how your skills match the requirements..."
                    rows={6}
                    className="resize-none"
                  />
                  <p className="text-sm text-slate-500">
                    {applicationData.cover_letter.length} characters
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="resume_file">Upload Resume/CV</Label>
                  <div className="space-y-3">
                    {/* File Upload Input */}
                    <div className="relative">
                      <input
                        id="resume_file"
                        type="file"
                        accept=".pdf,.doc,.docx"
                        onChange={handleFileUpload}
                        className="hidden"
                      />
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => document.getElementById('resume_file').click()}
                        className="w-full justify-start"
                      >
                        <Upload className="w-4 h-4 mr-2" />
                        {uploadedFileName ? 'Change File' : 'Choose File'}
                      </Button>
                    </div>

                    {/* Uploaded File Display */}
                    {uploadedFileName && (
                      <div className="flex items-center justify-between bg-green-50 border border-green-200 rounded-lg p-3">
                        <div className="flex items-center space-x-2">
                          <FileText className="w-4 h-4 text-green-600" />
                          <span className="text-sm font-medium text-green-800">{uploadedFileName}</span>
                        </div>
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={removeUploadedFile}
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        >
                          <X className="w-4 h-4" />
                        </Button>
                      </div>
                    )}

                    {/* Upload Error */}
                    {uploadError && (
                      <div className="flex items-center space-x-2 text-red-600 bg-red-50 border border-red-200 rounded-lg p-3">
                        <AlertCircle className="w-4 h-4" />
                        <span className="text-sm">{uploadError}</span>
                      </div>
                    )}

                    {/* OR divider */}
                    <div className="relative">
                      <div className="absolute inset-0 flex items-center">
                        <div className="w-full border-t border-slate-200"></div>
                      </div>
                      <div className="relative flex justify-center text-sm">
                        <span className="px-2 bg-white text-slate-500">OR</span>
                      </div>
                    </div>

                    {/* URL Input as fallback */}
                    <div className="relative">
                      <FileText className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
                      <Input
                        id="resume_url"
                        type="url"
                        value={applicationData.resume_url}
                        onChange={(e) => handleInputChange('resume_url', e.target.value)}
                        placeholder="https://your-resume-link.com"
                        className="pl-10"
                        disabled={!!uploadedFileName}
                      />
                    </div>
                  </div>
                  <p className="text-sm text-slate-500">
                    Upload a file (PDF, DOC, DOCX - max 5MB) or provide a link to your resume
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="additional_info">Additional Information (Optional)</Label>
                  <Textarea
                    id="additional_info"
                    value={applicationData.additional_info}
                    onChange={(e) => handleInputChange('additional_info', e.target.value)}
                    placeholder="Any additional information you'd like to share (portfolio links, availability, salary expectations, etc.)..."
                    rows={4}
                    className="resize-none"
                  />
                </div>
              </form>

              <div className="flex justify-between">
                <Button variant="outline" onClick={() => setStep(1)}>
                  Back
                </Button>
                <div className="space-x-3">
                  <Button variant="outline" onClick={handleClose}>
                    Cancel
                  </Button>
                  <Button 
                    onClick={handleSubmitApplication}
                    disabled={loading}
                  >
                    {loading ? (
                      <div className="flex items-center space-x-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        <span>Submitting...</span>
                      </div>
                    ) : (
                      <div className="flex items-center space-x-2">
                        <Send className="w-4 h-4" />
                        <span>Submit Application</span>
                      </div>
                    )}
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* Step 3: Success */}
          {step === 3 && (
            <div className="text-center py-12">
              <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-6" />
              <h3 className="text-2xl font-bold text-slate-800 mb-4">
                Application Submitted Successfully!
              </h3>
              <p className="text-slate-600 mb-6">
                Your application for <strong>{job.title}</strong> at <strong>{job.company_name}</strong> has been submitted.
                You'll receive updates on your application status via email.
              </p>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-left">
                <h4 className="font-semibold text-blue-900 mb-2">What's next?</h4>
                <ul className="text-blue-800 text-sm space-y-1">
                  <li>• The hiring team will review your application</li>
                  <li>• You can track your application status in your profile</li>
                  <li>• We'll notify you of any status updates</li>
                </ul>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>,
    document.body
  );
};

// Apply Button Component
const ApplyButton = ({ job, user, onApplicationSuccess }) => {
  const [showEasyApply, setShowEasyApply] = useState(false);
  const [hasApplied, setHasApplied] = useState(false);
  const [applicationDate, setApplicationDate] = useState(null);
  const [checkingStatus, setCheckingStatus] = useState(true);

  // Check if user has already applied to this job
  useEffect(() => {
    const checkApplicationStatus = async () => {
      if (!user || !job?.id) {
        setCheckingStatus(false);
        return;
      }

      try {
        const token = localStorage.getItem('token');
        if (!token) {
          setCheckingStatus(false);
          return;
        }

        const response = await axios.get(
          `${API}/jobs/${job.id}/application-status`,
          {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        );

        if (response.data.has_applied) {
          setHasApplied(true);
          setApplicationDate(response.data.applied_date);
        }
      } catch (error) {
        // If endpoint doesn't exist or error, assume not applied
        console.log('Could not check application status:', error.message);
      } finally {
        setCheckingStatus(false);
      }
    };

    checkApplicationStatus();
  }, [job?.id, user]);

  // Check if job uses external application
  const hasExternalApplication = job.application_url && job.application_url.trim() !== '';

  const handleExternalApply = (e) => {
    e.stopPropagation();
    if (job.application_url) {
      // Log the external application click (optional analytics)
      console.log(`External application clicked for job: ${job.title}`);
      
      // Open external application URL in new tab
      window.open(job.application_url, '_blank', 'noopener,noreferrer');
    }
  };

  const handleEasyApplySuccess = (applicationData) => {
    setHasApplied(true);
    setApplicationDate(new Date().toISOString());
    if (onApplicationSuccess) {
      onApplicationSuccess(applicationData);
    }
  };

  const formatAppliedDate = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    const now = new Date();
    const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString('en-ZA', { day: 'numeric', month: 'short' });
  };

  // If user has already applied, show "Applied" badge
  if (hasApplied) {
    return (
      <div 
        className="flex items-center space-x-2 bg-emerald-100 text-emerald-700 px-3 sm:px-4 py-2 rounded-full font-semibold text-sm"
        onClick={(e) => e.stopPropagation()}
      >
        <CheckCircle className="w-4 h-4" />
        <span>Applied</span>
        {applicationDate && (
          <span className="text-emerald-600 text-xs hidden sm:inline">
            • {formatAppliedDate(applicationDate)}
          </span>
        )}
      </div>
    );
  }

  // Show loading state while checking
  if (checkingStatus) {
    return (
      <Button
        disabled
        className="bg-slate-200 text-slate-500 cursor-wait"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="w-4 h-4 border-2 border-slate-400 border-t-transparent rounded-full animate-spin mr-2" />
        Loading...
      </Button>
    );
  }

  // For external applications, redirect to company website
  if (hasExternalApplication) {
    return (
      <Button
        onClick={handleExternalApply}
        className="bg-gradient-to-r from-blue-600 to-slate-700 hover:from-blue-700 hover:to-slate-800"
      >
        <ExternalLink className="w-4 h-4 mr-2" />
        <span className="hidden sm:inline">Apply on Website</span>
        <span className="sm:hidden">Apply</span>
      </Button>
    );
  }

  // For Easy Apply jobs, show the modal
  return (
    <>
      <Button
        onClick={(e) => {
          e.stopPropagation();
          setShowEasyApply(true);
        }}
        className="bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700"
      >
        <Send className="w-4 h-4 mr-2" />
        Easy Apply
      </Button>

      <EasyApplyModal
        job={job}
        user={user}
        isOpen={showEasyApply}
        onClose={() => setShowEasyApply(false)}
        onSuccess={handleEasyApplySuccess}
      />
    </>
  );
};

export { EasyApplyModal, ApplyButton };