import React, { useState, useEffect } from 'react';
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { 
  Briefcase,
  Building2,
  MapPin,
  Clock,
  Eye,
  CheckCircle,
  XCircle,
  Calendar,
  MessageSquare,
  Undo2
} from "lucide-react";
import axios from 'axios';
import { useToast } from "../hooks/use-toast";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const MyApplications = ({ user }) => {
  const { toast } = useToast();
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [withdrawing, setWithdrawing] = useState(null);

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

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return '1 day ago';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 14) return '1 week ago';
    if (diffDays < 30) return `${Math.ceil(diffDays / 7)} weeks ago`;
    return `${Math.ceil(diffDays / 30)} months ago`;
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'reviewed': return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'shortlisted': return 'bg-purple-100 text-purple-800 border-purple-300';
      case 'interviewed': return 'bg-indigo-100 text-indigo-800 border-indigo-300';
      case 'offered': return 'bg-green-100 text-green-800 border-green-300';
      case 'rejected': return 'bg-red-100 text-red-800 border-red-300';
      case 'withdrawn': return 'bg-gray-100 text-gray-800 border-gray-300';
      default: return 'bg-slate-100 text-slate-800 border-slate-300';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending': return <Clock className="w-4 h-4" />;
      case 'reviewed': return <Eye className="w-4 h-4" />;
      case 'shortlisted': return <CheckCircle className="w-4 h-4" />;
      case 'interviewed': return <MessageSquare className="w-4 h-4" />;
      case 'offered': return <CheckCircle className="w-4 h-4" />;
      case 'rejected': return <XCircle className="w-4 h-4" />;
      case 'withdrawn': return <Undo2 className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  const handleWithdraw = async (applicationId, jobTitle) => {
    if (!window.confirm(`Are you sure you want to withdraw your application for "${jobTitle}"? This action cannot be undone.`)) {
      return;
    }

    try {
      setWithdrawing(applicationId);
      await axios.put(`${API}/applications/${applicationId}/withdraw`, {}, getAuthHeaders());
      
      toast({
        title: "Application Withdrawn",
        description: `Your application for "${jobTitle}" has been withdrawn.`,
        variant: "success",
      });
      
      // Refresh applications
      await fetchApplications();
      
    } catch (error) {
      console.error('Error withdrawing application:', error);
      toast({
        title: "Failed to Withdraw",
        description: error.response?.data?.detail || "Something went wrong. Please try again.",
        variant: "destructive",
      });
    } finally {
      setWithdrawing(null);
    }
  };

  const canWithdraw = (status) => {
    return !['withdrawn', 'rejected', 'offered'].includes(status);
  };

  const filteredApplications = applications.filter(app => {
    if (filter === 'all') return true;
    return app.application.status === filter;
  });

  const statusCounts = applications.reduce((acc, app) => {
    acc[app.application.status] = (acc[app.application.status] || 0) + 1;
    return acc;
  }, {});

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-800 mb-2">My Applications</h2>
          <p className="text-slate-600">Track the status of your job applications</p>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-blue-600">{applications.length}</div>
          <div className="text-sm text-slate-600">Total Applications</div>
        </div>
      </div>

      {/* Status Filter */}
      <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
        <CardContent className="p-6">
          <div className="flex flex-wrap gap-3">
            <Button
              onClick={() => setFilter('all')}
              variant={filter === 'all' ? 'default' : 'outline'}
              size="sm"
            >
              All ({applications.length})
            </Button>
            {Object.entries(statusCounts).map(([status, count]) => (
              <Button
                key={status}
                onClick={() => setFilter(status)}
                variant={filter === status ? 'default' : 'outline'}
                size="sm"
                className="capitalize"
              >
                {status} ({count})
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Applications List */}
      <div className="space-y-4">
        {filteredApplications.length === 0 ? (
          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
            <CardContent className="p-12 text-center">
              <Briefcase className="w-16 h-16 text-slate-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-slate-800 mb-2">
                {filter === 'all' ? 'No applications yet' : `No ${filter} applications`}
              </h3>
              <p className="text-slate-600">
                {filter === 'all' 
                  ? 'Start applying to jobs to see your applications here'
                  : `You don't have any ${filter} applications at the moment`
                }
              </p>
            </CardContent>
          </Card>
        ) : (
          filteredApplications.map(({ application, job }) => (
            <Card key={application.id} className="bg-white/80 backdrop-blur-sm border-0 shadow-xl hover:shadow-2xl transition-all duration-300">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-start space-x-4">
                      <div className="flex-1">
                        <h4 className="font-bold text-slate-800 text-lg mb-2">{job.title}</h4>
                        
                        <div className="flex items-center space-x-4 text-sm text-slate-600 mb-3">
                          <div className="flex items-center space-x-1">
                            <Building2 className="w-4 h-4" />
                            <span>{job.company_name}</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <MapPin className="w-4 h-4" />
                            <span>{job.location}</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <Calendar className="w-4 h-4" />
                            <span>Applied {formatDate(application.applied_date)}</span>
                          </div>
                        </div>

                        <div className="flex items-center space-x-3 mb-4">
                          <Badge variant="outline">{job.job_type}</Badge>
                          <Badge variant="outline">{job.work_type}</Badge>
                          <Badge variant="outline">{job.industry}</Badge>
                        </div>

                        {application.cover_letter && (
                          <div className="mt-4 p-4 bg-slate-50 rounded-lg">
                            <p className="text-sm text-slate-700 font-medium mb-2">Your Cover Letter:</p>
                            <p className="text-sm text-slate-600 line-clamp-3">
                              {application.cover_letter}
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-col items-end space-y-3">
                    <Badge 
                      variant="outline" 
                      className={`flex items-center space-x-1 px-3 py-1 ${getStatusColor(application.status)}`}
                    >
                      {getStatusIcon(application.status)}
                      <span className="capitalize font-medium">{application.status}</span>
                    </Badge>

                    {application.last_updated !== application.applied_date && (
                      <p className="text-xs text-slate-500">
                        Updated {formatDate(application.last_updated)}
                      </p>
                    )}
                  </div>
                </div>

                {application.notes && (
                  <div className="mt-4 pt-4 border-t border-slate-200">
                    <p className="text-sm text-slate-700 font-medium mb-1">Recruiter Notes:</p>
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

export default MyApplications;