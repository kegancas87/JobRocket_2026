import React, { useState, useEffect } from 'react';
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { 
  Users,
  User,
  Mail,
  Phone,
  MapPin,
  FileText,
  Eye,
  CheckCircle,
  XCircle,
  Clock,
  MessageSquare,
  Star,
  ExternalLink
} from "lucide-react";
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ApplicationManagement = ({ user }) => {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedApplication, setSelectedApplication] = useState(null);
  const [statusFilter, setStatusFilter] = useState('all');

  const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    return {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    };
  };

  useEffect(() => {
    fetchApplications();
  }, []);

  const fetchApplications = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/applications`, getAuthHeaders());
      setApplications(response.data);
    } catch (error) {
      console.error('Error fetching applications:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateApplicationStatus = async (applicationId, newStatus, notes = '') => {
    try {
      await axios.put(`${API}/applications/${applicationId}/status?status=${newStatus}`, {
        notes
      }, getAuthHeaders());
      
      // Refresh applications
      await fetchApplications();
      
      // Update selected application if viewing
      if (selectedApplication?.application?.id === applicationId) {
        setSelectedApplication(prev => ({
          ...prev,
          application: { ...prev.application, status: newStatus }
        }));
      }
      
    } catch (error) {
      console.error('Error updating application status:', error);
      throw error;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'reviewed': return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'shortlisted': return 'bg-purple-100 text-purple-800 border-purple-300';
      case 'interviewed': return 'bg-indigo-100 text-indigo-800 border-indigo-300';
      case 'offered': return 'bg-green-100 text-green-800 border-green-300';
      case 'rejected': return 'bg-red-100 text-red-800 border-red-300';
      default: return 'bg-slate-100 text-slate-800 border-slate-300';
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const filteredApplications = applications.filter(app => {
    if (statusFilter === 'all') return true;
    return app.application.status === statusFilter;
  });

  const statusCounts = applications.reduce((acc, app) => {
    acc[app.application.status] = (acc[app.application.status] || 0) + 1;
    return acc;
  }, { all: applications.length });

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-800 mb-2">Job Applications</h2>
          <p className="text-slate-600">Manage applications for your job postings</p>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-blue-600">{applications.length}</div>
          <div className="text-sm text-slate-600">Total Applications</div>
        </div>
      </div>

      {/* Status Filters */}
      <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
        <CardContent className="p-6">
          <div className="flex flex-wrap gap-3">
            <Button
              onClick={() => setStatusFilter('all')}
              variant={statusFilter === 'all' ? 'default' : 'outline'}
              size="sm"
            >
              All ({statusCounts.all || 0})
            </Button>
            <Button
              onClick={() => setStatusFilter('pending')}
              variant={statusFilter === 'pending' ? 'default' : 'outline'}
              size="sm"
            >
              Pending ({statusCounts.pending || 0})
            </Button>
            <Button
              onClick={() => setStatusFilter('reviewed')}
              variant={statusFilter === 'reviewed' ? 'default' : 'outline'}
              size="sm"
            >
              Reviewed ({statusCounts.reviewed || 0})
            </Button>
            <Button
              onClick={() => setStatusFilter('shortlisted')}
              variant={statusFilter === 'shortlisted' ? 'default' : 'outline'}
              size="sm"
            >
              Shortlisted ({statusCounts.shortlisted || 0})
            </Button>
            <Button
              onClick={() => setStatusFilter('offered')}
              variant={statusFilter === 'offered' ? 'default' : 'outline'}
              size="sm"
            >
              Offered ({statusCounts.offered || 0})
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Applications List */}
      <div className="space-y-4">
        {filteredApplications.length === 0 ? (
          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
            <CardContent className="p-12 text-center">
              <Users className="w-16 h-16 text-slate-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-slate-800 mb-2">No applications found</h3>
              <p className="text-slate-600">
                {statusFilter === 'all' 
                  ? 'No applications have been received yet'
                  : `No ${statusFilter} applications at the moment`
                }
              </p>
            </CardContent>
          </Card>
        ) : (
          filteredApplications.map(({ application, job }) => {
            // Get applicant data from applicant_snapshot
            const applicant = application.applicant_snapshot || {};
            
            return (
            <Card key={application.id} className="bg-white/80 backdrop-blur-sm border-0 shadow-xl hover:shadow-2xl transition-all duration-300">
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-4 mb-3">
                      <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-slate-600 rounded-full flex items-center justify-center text-white font-semibold">
                        {(applicant.first_name || '?')[0]}{(applicant.last_name || '?')[0]}
                      </div>
                      <div>
                        <h4 className="font-bold text-slate-800 text-lg">
                          {applicant.first_name || 'Unknown'} {applicant.last_name || 'Applicant'}
                        </h4>
                        <p className="text-slate-600 font-medium">{job?.title || 'Unknown Job'}</p>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-slate-600 mb-4">
                      <div className="flex items-center space-x-1">
                        <Mail className="w-4 h-4" />
                        <span>{applicant.email || 'No email'}</span>
                      </div>
                      {applicant.location && (
                        <div className="flex items-center space-x-1">
                          <MapPin className="w-4 h-4" />
                          <span>{applicant.location}</span>
                        </div>
                      )}
                      <div className="flex items-center space-x-1">
                        <Clock className="w-4 h-4" />
                        <span>Applied {formatDate(application.applied_date)}</span>
                      </div>
                    </div>

                    {applicant.skills && applicant.skills.length > 0 && (
                      <div className="mb-4">
                        <p className="text-sm font-medium text-slate-700 mb-2">Skills:</p>
                        <div className="flex flex-wrap gap-1">
                          {applicant.skills.slice(0, 8).map((skill, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {skill}
                            </Badge>
                          ))}
                          {applicant.skills.length > 8 && (
                            <Badge variant="outline" className="text-xs">
                              +{applicant.skills.length - 8} more
                            </Badge>
                          )}
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="flex flex-col items-end space-y-3">
                    <Badge 
                      variant="outline" 
                      className={`px-3 py-1 ${getStatusColor(application.status)}`}
                    >
                      <span className="capitalize font-medium">{application.status}</span>
                    </Badge>
                  </div>
                </div>

                {/* Cover Letter */}
                {application.cover_letter && (
                  <div className="mb-4 p-4 bg-slate-50 rounded-lg">
                    <p className="text-sm font-medium text-slate-700 mb-2">Cover Letter:</p>
                    <p className="text-sm text-slate-600 leading-relaxed">
                      {application.cover_letter}
                    </p>
                  </div>
                )}

                {/* Resume/CV Link */}
                {application.resume_url && (
                  <div className="mb-4">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => window.open(application.resume_url, '_blank')}
                      className="flex items-center space-x-2"
                    >
                      <FileText className="w-4 h-4" />
                      <span>View Resume/CV</span>
                      <ExternalLink className="w-3 h-3" />
                    </Button>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex flex-wrap gap-2 pt-4 border-t border-slate-200">
                  {application.status === 'pending' && (
                    <>
                      <Button
                        size="sm"
                        onClick={() => updateApplicationStatus(application.id, 'reviewed')}
                        className="bg-blue-600 hover:bg-blue-700"
                      >
                        <Eye className="w-4 h-4 mr-2" />
                        Mark as Reviewed
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => updateApplicationStatus(application.id, 'rejected')}
                        className="border-red-300 text-red-600 hover:bg-red-50"
                      >
                        <XCircle className="w-4 h-4 mr-2" />
                        Reject
                      </Button>
                    </>
                  )}
                  
                  {application.status === 'reviewed' && (
                    <>
                      <Button
                        size="sm"
                        onClick={() => updateApplicationStatus(application.id, 'shortlisted')}
                        className="bg-purple-600 hover:bg-purple-700"
                      >
                        <Star className="w-4 h-4 mr-2" />
                        Shortlist
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => updateApplicationStatus(application.id, 'rejected')}
                        className="border-red-300 text-red-600 hover:bg-red-50"
                      >
                        <XCircle className="w-4 h-4 mr-2" />
                        Reject
                      </Button>
                    </>
                  )}
                  
                  {application.status === 'shortlisted' && (
                    <>
                      <Button
                        size="sm"
                        onClick={() => updateApplicationStatus(application.id, 'interviewed')}
                        className="bg-indigo-600 hover:bg-indigo-700"
                      >
                        <MessageSquare className="w-4 h-4 mr-2" />
                        Schedule Interview
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => updateApplicationStatus(application.id, 'rejected')}
                        className="border-red-300 text-red-600 hover:bg-red-50"
                      >
                        <XCircle className="w-4 h-4 mr-2" />
                        Reject
                      </Button>
                    </>
                  )}
                  
                  {application.status === 'interviewed' && (
                    <>
                      <Button
                        size="sm"
                        onClick={() => updateApplicationStatus(application.id, 'offered')}
                        className="bg-green-600 hover:bg-green-700"
                      >
                        <CheckCircle className="w-4 h-4 mr-2" />
                        Make Offer
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => updateApplicationStatus(application.id, 'rejected')}
                        className="border-red-300 text-red-600 hover:bg-red-50"
                      >
                        <XCircle className="w-4 h-4 mr-2" />
                        Reject
                      </Button>
                    </>
                  )}
                </div>

                {/* Recruiter Notes */}
                {application.notes && (
                  <div className="mt-4 pt-4 border-t border-slate-200">
                    <p className="text-sm font-medium text-slate-700 mb-1">Notes:</p>
                    <p className="text-sm text-slate-600 bg-blue-50 p-3 rounded-lg">
                      {application.notes}
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
};

export default ApplicationManagement;