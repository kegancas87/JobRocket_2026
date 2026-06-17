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
            <h3 key={index} className="text-base sm:text-lg font-semibold text-slate-800 mt-4 sm:mt-6 mb-2 sm:mb-3 first:mt-0">
              {headerMatch[1]}
            </h3>
          );
        }
      }
      
      // Handle bullet points (lines starting with -)
      if (paragraph.trim().startsWith('-')) {
        return (
          <li key={index} className="ml-4 mb-1 text-sm sm:text-base text-slate-700">
            {paragraph.trim().substring(1).trim()}
          </li>
        );
      }
      
      // Regular paragraphs
      return (
        <p key={index} className="text-sm sm:text-base text-slate-700 mb-2 sm:mb-3 leading-relaxed">
          {paragraph.trim()}
        </p>
      );
    }).filter(Boolean);
  };

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-end sm:items-center justify-center z-50 sm:p-4"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      {/* Modal Container - Full screen on mobile, centered on desktop */}
      <div className="bg-white w-full sm:rounded-xl shadow-2xl sm:max-w-4xl sm:w-full h-[95vh] sm:h-auto sm:max-h-[90vh] overflow-hidden flex flex-col rounded-t-2xl sm:rounded-xl">
        
        {/* Header - Compact on mobile */}
        <div className="bg-gradient-to-r from-slate-50 to-blue-50 p-4 sm:p-6 border-b border-slate-200 flex-shrink-0">
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-start space-x-3 sm:space-x-4 min-w-0 flex-1">
              {/* Company Logo */}
              <div className="w-12 h-12 sm:w-16 sm:h-16 rounded-xl overflow-hidden bg-gradient-to-br from-blue-100 to-slate-200 flex-shrink-0 shadow-lg flex items-center justify-center">
                {job.logo_url ? (
                  <img 
                    src={job.logo_url} 
                    alt={`${job.company_name} logo`}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.parentElement.innerHTML = `<div class="w-full h-full flex items-center justify-center bg-gradient-to-br from-blue-600 to-slate-700 text-white font-bold text-lg sm:text-xl">${job.company_name?.charAt(0) || 'J'}</div>`;
                    }}
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-blue-600 to-slate-700 text-white font-bold text-lg sm:text-xl">
                    {job.company_name?.charAt(0) || 'J'}
                  </div>
                )}
              </div>
              
              <div className="flex-1 min-w-0">
                {/* Job Title */}
                <div className="flex items-start gap-2 mb-1 sm:mb-2">
                  <h2 className="text-lg sm:text-2xl font-bold text-slate-800 leading-tight line-clamp-2">
                    {job.title}
                  </h2>
                  {job.featured && (
                    <div className="hidden sm:flex items-center space-x-1 bg-gradient-to-r from-blue-600 to-slate-700 text-white px-2 sm:px-3 py-1 rounded-full text-xs font-semibold flex-shrink-0">
                      <Star className="w-3 h-3 fill-current" />
                      <span>Featured</span>
                    </div>
                  )}
                </div>
                
                {/* Company, Location, Time - Stack on mobile */}
                <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-slate-600 text-sm">
                  <div className="flex items-center space-x-1.5">
                    <Building2 className="w-3.5 h-3.5 flex-shrink-0" />
                    <span className="font-medium truncate">{job.company_name}</span>
                  </div>
                  <div className="flex items-center space-x-1.5">
                    <MapPin className="w-3.5 h-3.5 flex-shrink-0" />
                    <span className="truncate">{job.location}</span>
                  </div>
                  <div className="flex items-center space-x-1.5">
                    <Clock className="w-3.5 h-3.5 flex-shrink-0" />
                    <span>{formatPostedDate(job.posted_date)}</span>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Close Button */}
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="hover:bg-slate-100 flex-shrink-0 -mr-2 -mt-1"
            >
              <X className="w-5 h-5" />
            </Button>
          </div>
        </div>

        {/* Scrollable Content Area */}
        <div className="flex-1 overflow-y-auto overscroll-contain">
          {/* Mobile: Apply Button at top */}
          <div className="sm:hidden p-4 bg-white border-b border-slate-100 sticky top-0 z-10">
            <ApplyButton 
              job={job}
              user={user}
              onApplicationSuccess={onApplicationSuccess}
            />
          </div>

          <div className="flex flex-col lg:flex-row">
            {/* Main Content */}
            <div className="flex-1 p-4 sm:p-6">
              {/* Job Meta Info Cards */}
              <div className="grid grid-cols-2 gap-3 sm:gap-4 mb-5 sm:mb-6">
                {job.salary && (
                  <div className="bg-emerald-50 p-3 sm:p-4 rounded-lg">
                    <div className="flex items-center space-x-1.5 sm:space-x-2 text-emerald-700 mb-1">
                      <span className="font-bold text-sm sm:text-base">R</span>
                      <span className="font-medium text-xs sm:text-sm">Salary</span>
                    </div>
                    <p className="font-bold text-emerald-800 text-sm sm:text-base">{job.salary}</p>
                  </div>
                )}
                
                <div className="bg-blue-50 p-3 sm:p-4 rounded-lg">
                  <div className="flex items-center space-x-1.5 sm:space-x-2 text-blue-700 mb-1">
                    <Briefcase className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                    <span className="font-medium text-xs sm:text-sm">Job Type</span>
                  </div>
                  <p className="font-bold text-blue-800 text-sm sm:text-base">{job.job_type || 'Not specified'}</p>
                </div>
                
                <div className="bg-purple-50 p-3 sm:p-4 rounded-lg">
                  <div className="flex items-center space-x-1.5 sm:space-x-2 text-purple-700 mb-1">
                    <Users className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                    <span className="font-medium text-xs sm:text-sm">Work Type</span>
                  </div>
                  <p className="font-bold text-purple-800 text-sm sm:text-base">{job.work_type || 'Not specified'}</p>
                </div>
                
                <div className="bg-orange-50 p-3 sm:p-4 rounded-lg">
                  <div className="flex items-center space-x-1.5 sm:space-x-2 text-orange-700 mb-1">
                    <GraduationCap className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                    <span className="font-medium text-xs sm:text-sm">Experience</span>
                  </div>
                  <p className="font-bold text-orange-800 text-sm sm:text-base">{job.experience || 'Not specified'}</p>
                </div>
              </div>

              {/* Job Description */}
              <div className="mb-5 sm:mb-6">
                <h3 className="text-lg sm:text-xl font-bold text-slate-800 mb-3 sm:mb-4">Job Description</h3>
                <div className="prose prose-slate max-w-none">
                  {formatDescription(job.description)}
                </div>
              </div>

              {/* Qualifications */}
              {job.qualifications && (
                <div className="mb-5 sm:mb-6">
                  <h3 className="text-lg sm:text-xl font-bold text-slate-800 mb-3 sm:mb-4">Qualifications</h3>
                  <div className="bg-slate-50 p-3 sm:p-4 rounded-lg">
                    <p className="text-sm sm:text-base text-slate-700 leading-relaxed">{job.qualifications}</p>
                  </div>
                </div>
              )}

              {/* Tags */}
              <div className="mb-5 sm:mb-6">
                <h3 className="text-lg sm:text-xl font-bold text-slate-800 mb-3 sm:mb-4">Tags</h3>
                <div className="flex flex-wrap gap-2">
                  <Badge variant="secondary" className="bg-slate-100 text-slate-700 text-xs sm:text-sm">
                    {job.job_type}
                  </Badge>
                  <Badge className={`border-0 text-xs sm:text-sm ${
                    job.work_type === 'Remote' ? 'bg-blue-100 text-blue-700' :
                    job.work_type === 'Hybrid' ? 'bg-purple-100 text-purple-700' :
                    'bg-green-100 text-green-700'
                  }`}>
                    {job.work_type}
                  </Badge>
                  <Badge variant="outline" className="border-slate-300 text-slate-600 text-xs sm:text-sm">
                    {job.industry}
                  </Badge>
                  {job.featured && (
                    <Badge className="bg-gradient-to-r from-blue-600 to-slate-700 text-white text-xs sm:text-sm">
                      <Star className="w-3 h-3 mr-1" />
                      Featured
                    </Badge>
                  )}
                </div>
              </div>

              {/* Mobile: Company Info & Stats */}
              <div className="lg:hidden space-y-4 mb-6">
                <Separator />
                
                {/* Company Info */}
                <div>
                  <h4 className="font-bold text-slate-800 mb-3">About {job.company_name}</h4>
                  <div className="space-y-2">
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
                  <Button
                    variant="outline"
                    className="w-full"
                    onClick={() => window.open(job.external_application_link, '_blank')}
                  >
                    <ExternalLink className="w-4 h-4 mr-2" />
                    Apply on Company Website
                  </Button>
                )}

                {/* Job Stats */}
                <div className="bg-slate-50 p-4 rounded-lg">
                  <h4 className="font-bold text-slate-800 mb-3">Job Statistics</h4>
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                      <p className="text-lg font-bold text-slate-800">{job.application_count || 0}</p>
                      <p className="text-xs text-slate-600">Applications</p>
                    </div>
                    <div>
                      <p className="text-lg font-bold text-slate-800">{job.view_count || 0}</p>
                      <p className="text-xs text-slate-600">Views</p>
                    </div>
                    <div>
                      <p className="text-xs font-medium text-slate-800 truncate">{job.id?.substring(0, 8)}...</p>
                      <p className="text-xs text-slate-600">Job ID</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Desktop Sidebar - Hidden on mobile */}
            <div className="hidden lg:block w-80 bg-slate-50 p-6 border-l border-slate-200">
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

        {/* Mobile: Fixed Bottom Apply Button */}
        <div className="sm:hidden p-4 bg-white border-t border-slate-200 flex-shrink-0 safe-area-inset-bottom">
          <ApplyButton 
            job={job}
            user={user}
            onApplicationSuccess={onApplicationSuccess}
          />
        </div>
      </div>
    </div>
  );
};

export default JobDetailsModal;
