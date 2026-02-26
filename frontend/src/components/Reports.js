import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Badge } from "./ui/badge";
import { 
  Clock,
  TrendingUp,
  Users,
  Download,
  RefreshCw,
  Calendar,
  Filter,
  ChevronDown,
  ChevronUp,
  AlertTriangle,
  CheckCircle,
  ArrowRight,
  Briefcase,
  UserCheck,
  FileText
} from "lucide-react";
import axios from 'axios';
import { useToast } from "../hooks/use-toast";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Reports = ({ user }) => {
  const { toast } = useToast();
  const [activeReport, setActiveReport] = useState('time-to-fill');
  const [loading, setLoading] = useState(false);
  const [reportData, setReportData] = useState(null);
  
  // Filters
  const [startDate, setStartDate] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() - 90);
    return d.toISOString().split('T')[0];
  });
  const [endDate, setEndDate] = useState(() => new Date().toISOString().split('T')[0]);
  const [showFilters, setShowFilters] = useState(false);

  const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    return {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    };
  };

  const fetchReport = async (reportType) => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);
      if (reportType === 'time-to-fill') params.append('include_open', 'true');
      
      const response = await axios.get(
        `${API}/reports/${reportType}?${params.toString()}`,
        getAuthHeaders()
      );
      setReportData(response.data);
    } catch (error) {
      console.error('Error fetching report:', error);
      toast({
        title: "Error",
        description: "Failed to load report data",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReport(activeReport);
  }, [activeReport]);

  const handleExportCSV = async () => {
    try {
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);
      
      const response = await axios.get(
        `${API}/reports/export/${activeReport}?${params.toString()}`,
        {
          ...getAuthHeaders(),
          responseType: 'blob'
        }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${activeReport}_${new Date().toISOString().split('T')[0]}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast({
        title: "Export Complete",
        description: "Report downloaded successfully",
      });
    } catch (error) {
      console.error('Export error:', error);
      toast({
        title: "Export Failed",
        description: "Could not export report",
        variant: "destructive",
      });
    }
  };

  const handleApplyFilters = () => {
    fetchReport(activeReport);
  };

  const reportTabs = [
    { id: 'time-to-fill', label: 'Time to Fill', icon: Clock },
    { id: 'pipeline-conversion', label: 'Pipeline Conversion', icon: TrendingUp },
    { id: 'recruiter-workload', label: 'Recruiter Workload', icon: Users },
  ];

  return (
    <div className="space-y-6 p-6" data-testid="reports-page">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-800 mb-2">Reports</h1>
          <p className="text-slate-600">Operational insights for your recruitment activities</p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={handleExportCSV}
            disabled={loading || !reportData}
            data-testid="export-csv-btn"
          >
            <Download className="w-4 h-4 mr-2" />
            Export CSV
          </Button>
          <Button
            onClick={() => fetchReport(activeReport)}
            disabled={loading}
            data-testid="refresh-report-btn"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Report Tabs */}
      <div className="flex flex-wrap gap-2 border-b border-slate-200 pb-4">
        {reportTabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <Button
              key={tab.id}
              variant={activeReport === tab.id ? 'default' : 'outline'}
              onClick={() => setActiveReport(tab.id)}
              className={activeReport === tab.id ? 'bg-blue-600 hover:bg-blue-700' : ''}
              data-testid={`tab-${tab.id}`}
            >
              <Icon className="w-4 h-4 mr-2" />
              {tab.label}
            </Button>
          );
        })}
      </div>

      {/* Filters */}
      <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
        <CardHeader 
          className="cursor-pointer flex flex-row items-center justify-between py-3"
          onClick={() => setShowFilters(!showFilters)}
        >
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-600" />
            <span className="font-medium text-slate-700">Filters</span>
          </div>
          {showFilters ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </CardHeader>
        {showFilters && (
          <CardContent className="pt-0">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="text-sm font-medium text-slate-600 mb-1 block">Start Date</label>
                <Input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  data-testid="filter-start-date"
                />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-600 mb-1 block">End Date</label>
                <Input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  data-testid="filter-end-date"
                />
              </div>
              <div className="flex items-end">
                <Button onClick={handleApplyFilters} className="w-full sm:w-auto">
                  Apply Filters
                </Button>
              </div>
            </div>
          </CardContent>
        )}
      </Card>

      {/* Report Content */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-slate-600">Loading report...</p>
          </div>
        </div>
      ) : reportData ? (
        <>
          {activeReport === 'time-to-fill' && <TimeToFillReport data={reportData} />}
          {activeReport === 'pipeline-conversion' && <PipelineConversionReport data={reportData} />}
          {activeReport === 'recruiter-workload' && <RecruiterWorkloadReport data={reportData} />}
        </>
      ) : (
        <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
          <CardContent className="p-12 text-center">
            <FileText className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-600">No report data available</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};


// Time to Fill Report Component
const TimeToFillReport = ({ data }) => {
  const { summary = {}, data: jobs = [] } = data || {};
  
  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white border-0 shadow-lg">
          <CardContent className="p-4">
            <p className="text-blue-100 text-xs font-medium">Total Jobs</p>
            <p className="text-2xl font-bold">{summary.total_jobs || 0}</p>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-emerald-500 to-emerald-600 text-white border-0 shadow-lg">
          <CardContent className="p-4">
            <p className="text-emerald-100 text-xs font-medium">Filled</p>
            <p className="text-2xl font-bold">{summary.filled_jobs || 0}</p>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-amber-500 to-amber-600 text-white border-0 shadow-lg">
          <CardContent className="p-4">
            <p className="text-amber-100 text-xs font-medium">Open</p>
            <p className="text-2xl font-bold">{summary.open_jobs || 0}</p>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white border-0 shadow-lg">
          <CardContent className="p-4">
            <p className="text-purple-100 text-xs font-medium">Avg Days to Fill</p>
            <p className="text-2xl font-bold">{summary.average_days_to_fill || 0}</p>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-slate-500 to-slate-600 text-white border-0 shadow-lg">
          <CardContent className="p-4">
            <p className="text-slate-200 text-xs font-medium">Median Days</p>
            <p className="text-2xl font-bold">{summary.median_days_to_fill || 0}</p>
          </CardContent>
        </Card>
      </div>

      {/* Jobs Table */}
      <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-slate-800">Job Details</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-200">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-600">Job Title</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-600">Recruiter</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-600">Open Date</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-600">Fill Date</th>
                  <th className="text-center py-3 px-4 text-sm font-semibold text-slate-600">Days</th>
                  <th className="text-center py-3 px-4 text-sm font-semibold text-slate-600">Status</th>
                </tr>
              </thead>
              <tbody>
                {jobs.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="text-center py-8 text-slate-500">No jobs found in selected date range</td>
                  </tr>
                ) : (
                  jobs.map((job, idx) => (
                    <tr key={job.job_id} className={idx % 2 === 0 ? 'bg-slate-50' : ''}>
                      <td className="py-3 px-4">
                        <p className="font-medium text-slate-800">{job.job_title}</p>
                        <p className="text-xs text-slate-500">{job.company_name}</p>
                      </td>
                      <td className="py-3 px-4 text-sm text-slate-600">{job.recruiter_name}</td>
                      <td className="py-3 px-4 text-sm text-slate-600">
                        {job.job_open_date ? new Date(job.job_open_date).toLocaleDateString() : '-'}
                      </td>
                      <td className="py-3 px-4 text-sm text-slate-600">
                        {job.offer_accepted_date ? new Date(job.offer_accepted_date).toLocaleDateString() : '-'}
                      </td>
                      <td className="py-3 px-4 text-center">
                        <span className={`font-semibold ${job.days_to_fill > 30 ? 'text-red-600' : job.days_to_fill > 14 ? 'text-amber-600' : 'text-emerald-600'}`}>
                          {job.days_to_fill}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-center">
                        <Badge variant={job.is_filled ? 'default' : 'outline'} className={job.is_filled ? 'bg-emerald-100 text-emerald-800' : ''}>
                          {job.status}
                        </Badge>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};


// Pipeline Conversion Report Component
const PipelineConversionReport = ({ data }) => {
  const { summary = {}, pipeline_stages = [], job_breakdown = [] } = data || {};
  
  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white border-0 shadow-lg">
          <CardContent className="p-4">
            <p className="text-blue-100 text-xs font-medium">Total Applications</p>
            <p className="text-2xl font-bold">{summary.total_applications || 0}</p>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-emerald-500 to-emerald-600 text-white border-0 shadow-lg">
          <CardContent className="p-4">
            <p className="text-emerald-100 text-xs font-medium">Conversion to Offer</p>
            <p className="text-2xl font-bold">{summary.overall_conversion_to_offer || 0}%</p>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-red-500 to-red-600 text-white border-0 shadow-lg">
          <CardContent className="p-4">
            <p className="text-red-100 text-xs font-medium">Rejected</p>
            <p className="text-2xl font-bold">{summary.rejected || 0}</p>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-slate-500 to-slate-600 text-white border-0 shadow-lg">
          <CardContent className="p-4">
            <p className="text-slate-200 text-xs font-medium">Withdrawn</p>
            <p className="text-2xl font-bold">{summary.withdrawn || 0}</p>
          </CardContent>
        </Card>
      </div>

      {/* Pipeline Funnel */}
      <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-slate-800">Pipeline Stages</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {pipeline_stages.length === 0 ? (
              <p className="text-slate-500 text-center py-8">No pipeline data available</p>
            ) : (
              pipeline_stages.map((stage, idx) => {
                const widthPercent = stage.cumulative_count > 0 
                  ? (stage.cumulative_count / (pipeline_stages[0]?.cumulative_count || 1)) * 100
                  : 0;
                
                return (
                  <div key={stage.stage} className="relative">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-slate-800">{stage.stage_label}</span>
                        <Badge variant="outline" className="text-xs">{stage.count}</Badge>
                      </div>
                      <div className="flex items-center gap-4 text-sm">
                        <span className="text-emerald-600 font-medium">{stage.conversion_rate}% conversion</span>
                        {stage.drop_off_rate > 0 && (
                          <span className="text-red-500">{stage.drop_off_rate}% drop-off</span>
                        )}
                      </div>
                    </div>
                    <div className="h-8 bg-slate-100 rounded-lg overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg transition-all duration-500 flex items-center justify-end pr-3"
                        style={{ width: `${Math.max(widthPercent, 5)}%` }}
                      >
                        <span className="text-white text-xs font-medium">{stage.cumulative_count}</span>
                      </div>
                    </div>
                    {idx < pipeline_stages.length - 1 && (
                      <div className="flex justify-center my-2">
                        <ArrowRight className="w-4 h-4 text-slate-400 rotate-90" />
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </CardContent>
      </Card>

      {/* Job Breakdown */}
      {job_breakdown && job_breakdown.length > 0 && (
        <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
          <CardHeader>
            <CardTitle className="text-lg font-semibold text-slate-800">By Job</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-200">
                    <th className="text-left py-3 px-4 text-sm font-semibold text-slate-600">Job</th>
                    <th className="text-center py-3 px-4 text-sm font-semibold text-slate-600">Total</th>
                    <th className="text-center py-3 px-4 text-sm font-semibold text-slate-600">Pending</th>
                    <th className="text-center py-3 px-4 text-sm font-semibold text-slate-600">Reviewed</th>
                    <th className="text-center py-3 px-4 text-sm font-semibold text-slate-600">Shortlisted</th>
                    <th className="text-center py-3 px-4 text-sm font-semibold text-slate-600">Interviewed</th>
                    <th className="text-center py-3 px-4 text-sm font-semibold text-slate-600">Offered</th>
                  </tr>
                </thead>
                <tbody>
                  {job_breakdown.map((job, idx) => (
                    <tr key={job.job_id} className={idx % 2 === 0 ? 'bg-slate-50' : ''}>
                      <td className="py-3 px-4 font-medium text-slate-800">{job.job_title}</td>
                      <td className="py-3 px-4 text-center font-semibold text-blue-600">{job.total_applications}</td>
                      <td className="py-3 px-4 text-center text-slate-600">{job.stages?.pending || 0}</td>
                      <td className="py-3 px-4 text-center text-slate-600">{job.stages?.reviewed || 0}</td>
                      <td className="py-3 px-4 text-center text-slate-600">{job.stages?.shortlisted || 0}</td>
                      <td className="py-3 px-4 text-center text-slate-600">{job.stages?.interviewed || 0}</td>
                      <td className="py-3 px-4 text-center text-emerald-600 font-medium">{job.stages?.offered || 0}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};


// Recruiter Workload Report Component
const RecruiterWorkloadReport = ({ data }) => {
  const { summary, data: recruiters } = data;
  
  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white border-0 shadow-lg">
          <CardContent className="p-4">
            <p className="text-blue-100 text-xs font-medium">Total Recruiters</p>
            <p className="text-2xl font-bold">{summary.total_recruiters}</p>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-emerald-500 to-emerald-600 text-white border-0 shadow-lg">
          <CardContent className="p-4">
            <p className="text-emerald-100 text-xs font-medium">Active Jobs</p>
            <p className="text-2xl font-bold">{summary.total_active_jobs}</p>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white border-0 shadow-lg">
          <CardContent className="p-4">
            <p className="text-purple-100 text-xs font-medium">Active Candidates</p>
            <p className="text-2xl font-bold">{summary.total_active_candidates}</p>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-red-500 to-red-600 text-white border-0 shadow-lg">
          <CardContent className="p-4">
            <p className="text-red-100 text-xs font-medium">Overdue Tasks</p>
            <p className="text-2xl font-bold">{summary.total_overdue_tasks}</p>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-amber-500 to-amber-600 text-white border-0 shadow-lg">
          <CardContent className="p-4">
            <p className="text-amber-100 text-xs font-medium">With Overdue</p>
            <p className="text-2xl font-bold">{summary.recruiters_with_overdue}</p>
          </CardContent>
        </Card>
      </div>

      {/* Recruiter Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {recruiters.length === 0 ? (
          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg col-span-2">
            <CardContent className="p-12 text-center">
              <Users className="w-16 h-16 text-slate-300 mx-auto mb-4" />
              <p className="text-slate-600">No recruiters found</p>
            </CardContent>
          </Card>
        ) : (
          recruiters.map((recruiter) => (
            <Card 
              key={recruiter.recruiter_id} 
              className={`bg-white/80 backdrop-blur-sm border-0 shadow-xl ${recruiter.has_overdue ? 'ring-2 ring-red-200' : ''}`}
            >
              <CardContent className="p-5">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold">
                      {recruiter.recruiter_name.split(' ').map(n => n[0]).join('')}
                    </div>
                    <div>
                      <p className="font-semibold text-slate-800">{recruiter.recruiter_name}</p>
                      <p className="text-xs text-slate-500">{recruiter.email}</p>
                    </div>
                  </div>
                  {recruiter.has_overdue && (
                    <Badge variant="outline" className="bg-red-100 text-red-800 border-red-300">
                      <AlertTriangle className="w-3 h-3 mr-1" />
                      Overdue
                    </Badge>
                  )}
                </div>

                <div className="grid grid-cols-3 gap-3">
                  <div className="bg-slate-50 rounded-lg p-3 text-center">
                    <Briefcase className="w-4 h-4 text-blue-600 mx-auto mb-1" />
                    <p className="text-lg font-bold text-slate-800">{recruiter.metrics.active_jobs}</p>
                    <p className="text-xs text-slate-500">Active Jobs</p>
                  </div>
                  <div className="bg-slate-50 rounded-lg p-3 text-center">
                    <UserCheck className="w-4 h-4 text-emerald-600 mx-auto mb-1" />
                    <p className="text-lg font-bold text-slate-800">{recruiter.metrics.active_candidates}</p>
                    <p className="text-xs text-slate-500">Candidates</p>
                  </div>
                  <div className="bg-slate-50 rounded-lg p-3 text-center">
                    <Calendar className="w-4 h-4 text-purple-600 mx-auto mb-1" />
                    <p className="text-lg font-bold text-slate-800">{recruiter.metrics.interviews_scheduled}</p>
                    <p className="text-xs text-slate-500">Interviews</p>
                  </div>
                </div>

                <div className="flex items-center justify-between mt-4 pt-4 border-t border-slate-200">
                  <div className="flex items-center gap-4 text-sm">
                    <span className="text-slate-600">
                      <span className="font-medium text-blue-600">{recruiter.metrics.new_applications}</span> new apps
                    </span>
                    <span className="text-slate-600">
                      <span className={`font-medium ${recruiter.metrics.overdue_reviews > 0 ? 'text-red-600' : 'text-emerald-600'}`}>
                        {recruiter.metrics.overdue_reviews}
                      </span> overdue
                    </span>
                    <span className="text-slate-600">
                      <span className="font-medium text-amber-600">{recruiter.metrics.offers_pending}</span> offers pending
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
};

export default Reports;
