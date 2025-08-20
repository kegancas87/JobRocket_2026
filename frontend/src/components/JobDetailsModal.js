import React from 'react';
import { 
  X, 
  Building2, 
  MapPin, 
  Clock, 
  DollarSign, 
  Users, 
  Calendar,
  Star,
  Briefcase,
  GraduationCap,
  CheckCircle,
  ExternalLink
} from 'lucide-react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { ApplyButton } from './EasyApply';

const JobDetailsModal = ({ job, user, isOpen, onClose, onApplicationSuccess }) => {
  if (!isOpen || !job) return null;

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

  const formatDescription = (description) => {
    // Split by line breaks and convert to paragraphs
    return description.split('\n').map((paragraph, index) => {
      if (paragraph.trim() === '') return null;
      
      // Handle headers (lines with **text**)
      if (paragraph.includes('**')) {
        const headerMatch = paragraph.match(/\*\*(.*?)\*\*/);
        if (headerMatch) {
          return (
            <h3 key={index} className="text-lg font-semibold text-slate-800 mt-6 mb-3 first:mt-0">
              {headerMatch[1]}
            </h3>
          );
        }
      }
      
      // Handle bullet points (lines starting with -)
      if (paragraph.trim().startsWith('-')) {
        return (
          <li key={index} className="ml-4 mb-1 text-slate-700">
            {paragraph.trim().substring(1).trim()}
          </li>
        );
      }
      
      // Regular paragraphs
      return (
        <p key={index} className="text-slate-700 mb-3 leading-relaxed">
          {paragraph.trim()}
        </p>
      );
    }).filter(Boolean);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-slate-50 to-blue-50 p-6 border-b border-slate-200">
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-4">
              <div className="w-16 h-16 rounded-xl overflow-hidden bg-gradient-to-br from-slate-100 to-slate-200 flex-shrink-0 shadow-lg">
                <img 
                  src={job.logo_url} 
                  alt={`${job.company_name} logo`}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    e.target.src = 'https://images.unsplash.com/photo-1606211105533-0439bfecce21?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzZ8MHwxfHNlYXJjaHw0fHxtb2Rlcm4lMjB0ZWNobm9sb2d5fGVufDB8fHx8MTc1NTM1MzYzMXww&ixlib=rb-4.1.0&q=85&w=80&h=80';
                  }}
                />
              </div>
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-2">
                  <h2 className="text-2xl font-bold text-slate-800">{job.title}</h2>
                  {job.featured && (
                    <div className="flex items-center space-x-1 bg-gradient-to-r from-blue-600 to-slate-700 text-white px-3 py-1 rounded-full text-xs font-semibold">
                      <Star className="w-3 h-3 fill-current" />
                      <span>Featured</span>
                    </div>
                  )}
                </div>
                <div className="flex items-center space-x-6 text-slate-600">
                  <div className="flex items-center space-x-2">
                    <Building2 className="w-4 h-4" />
                    <span className="font-medium">{job.company_name}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <MapPin className="w-4 h-4" />
                    <span>{job.location}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Clock className="w-4 h-4" />
                    <span className="text-sm">{formatPostedDate(job.posted_date)}</span>
                  </div>
                </div>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="hover:bg-slate-100"
            >
              <X className="w-5 h-5" />
            </Button>
          </div>
        </div>

        {/* Content */}
        <div className="flex">
          {/* Main Content */}
          <div className="flex-1 p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
            {/* Job Meta Info */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              {job.salary && (
                <div className="bg-emerald-50 p-4 rounded-lg">
                  <div className="flex items-center space-x-2 text-emerald-700 mb-1">
                    <DollarSign className="w-4 h-4" />
                    <span className="font-medium">Salary</span>
                  </div>
                  <p className="font-bold text-emerald-800">{job.salary}</p>
                </div>
              )}
              
              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="flex items-center space-x-2 text-blue-700 mb-1">
                  <Briefcase className="w-4 h-4" />
                  <span className="font-medium">Job Type</span>
                </div>
                <p className="font-bold text-blue-800">{job.job_type}</p>
              </div>
              
              <div className="bg-purple-50 p-4 rounded-lg">
                <div className="flex items-center space-x-2 text-purple-700 mb-1">
                  <Users className="w-4 h-4" />
                  <span className="font-medium">Work Type</span>
                </div>
                <p className="font-bold text-purple-800">{job.work_type}</p>
              </div>
              
              {job.experience && (
                <div className="bg-orange-50 p-4 rounded-lg">
                  <div className="flex items-center space-x-2 text-orange-700 mb-1">
                    <GraduationCap className="w-4 h-4" />
                    <span className="font-medium">Experience</span>
                  </div>
                  <p className="font-bold text-orange-800">{job.experience}</p>
                </div>
              )}
            </div>

            {/* Job Description */}
            <div className="mb-6">
              <h3 className="text-xl font-bold text-slate-800 mb-4">Job Description</h3>
              <div className="prose prose-slate max-w-none">
                {formatDescription(job.description)}
              </div>
            </div>

            {/* Qualifications */}
            {job.qualifications && (
              <div className="mb-6">
                <h3 className="text-xl font-bold text-slate-800 mb-4">Qualifications</h3>
                <div className="bg-slate-50 p-4 rounded-lg">
                  <p className="text-slate-700 leading-relaxed">{job.qualifications}</p>
                </div>
              </div>
            )}

            {/* Tags */}
            <div className="mb-6">
              <h3 className="text-xl font-bold text-slate-800 mb-4">Tags</h3>
              <div className="flex flex-wrap gap-2">
                <Badge variant="secondary" className="bg-slate-100 text-slate-700">
                  {job.job_type}
                </Badge>
                <Badge className={`border-0 ${
                  job.work_type === 'Remote' ? 'bg-blue-100 text-blue-700' :
                  job.work_type === 'Hybrid' ? 'bg-purple-100 text-purple-700' :
                  'bg-green-100 text-green-700'
                }`}>
                  {job.work_type}
                </Badge>
                <Badge variant="outline" className="border-slate-300 text-slate-600">
                  {job.industry}
                </Badge>
                {job.featured && (
                  <Badge className="bg-gradient-to-r from-blue-600 to-slate-700 text-white">
                    <Star className="w-3 h-3 mr-1" />
                    Featured
                  </Badge>
                )}
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="w-80 bg-slate-50 p-6 border-l border-slate-200">
            <div className="sticky top-6">
              {/* Apply Button */}
              <div className="mb-6">
                <ApplyButton 
                  job={job}
                  user={user}
                  onApplicationSuccess={onApplicationSuccess}
                />
              </div>

              <Separator className="my-6" />

              {/* Company Info */}
              <div className="mb-6">
                <h4 className="font-bold text-slate-800 mb-3">About {job.company_name}</h4>
                <div className="space-y-3">
                  <div className="flex items-center space-x-3">
                    <Building2 className="w-4 h-4 text-slate-500" />
                    <span className="text-slate-700 text-sm">{job.company_name}</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <MapPin className="w-4 h-4 text-slate-500" />
                    <span className="text-slate-700 text-sm">{job.location}</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <Calendar className="w-4 h-4 text-slate-500" />
                    <span className="text-slate-700 text-sm">Posted {formatPostedDate(job.posted_date)}</span>
                  </div>
                </div>
              </div>

              {/* External Application Link */}
              {job.external_application_link && (
                <div className="mb-6">
                  <Button
                    variant="outline"
                    className="w-full"
                    onClick={() => window.open(job.external_application_link, '_blank')}
                  >
                    <ExternalLink className="w-4 h-4 mr-2" />
                    Apply on Company Website
                  </Button>
                </div>
              )}

              {/* Job Stats */}
              <div className="bg-white p-4 rounded-lg border border-slate-200">
                <h4 className="font-bold text-slate-800 mb-3">Job Statistics</h4>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-600">Applications:</span>
                    <span className="text-slate-800 font-medium">{job.application_count || 0}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-600">Views:</span>
                    <span className="text-slate-800 font-medium">{job.view_count || 0}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-600">Job ID:</span>
                    <span className="text-slate-800 font-medium text-xs">{job.id?.substring(0, 8)}...</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default JobDetailsModal;