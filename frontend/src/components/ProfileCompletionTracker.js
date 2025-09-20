import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Progress } from "./ui/progress";
import { 
  CheckCircle2, 
  Circle, 
  ChevronDown, 
  ChevronUp, 
  Building2,
  Image,
  Link,
  Users,
  Briefcase,
  Star,
  ArrowRight,
  Target
} from "lucide-react";

const ProfileCompletionTracker = ({ progress, profile, onNavigateToSection, companyForm }) => {
  const [expanded, setExpanded] = useState(true);

  // Define completion requirements with balanced point system
  const completionItems = [
    {
      id: 'basic_info',
      title: 'Company Information',
      description: 'Company name, industry, size, location',
      points: 30,
      completed: companyForm?.company_name && 
                 companyForm?.company_industry && 
                 companyForm?.company_size && 
                 companyForm?.company_location,
      action: 'overview',
      icon: Building2,
      requirements: [
        { field: 'Company Name', completed: !!companyForm?.company_name },
        { field: 'Industry', completed: !!companyForm?.company_industry },
        { field: 'Company Size', completed: !!companyForm?.company_size },
        { field: 'Location', completed: !!companyForm?.company_location }
      ]
    },
    {
      id: 'description',
      title: 'Company Description',
      description: '100+ character compelling description',
      points: 15,
      completed: companyForm?.company_description && companyForm.company_description.length >= 100,
      action: 'overview',
      icon: Building2,
      requirements: [
        { field: 'Description (100+ chars)', completed: companyForm?.company_description && companyForm.company_description.length >= 100 }
      ]
    },
    {
      id: 'branding',
      title: 'Company Branding',
      description: 'Logo and cover images',
      points: 25,
      completed: companyForm?.company_logo_url && companyForm?.company_cover_image_url,
      action: 'branding',
      icon: Image,
      requirements: [
        { field: 'Company Logo', completed: !!companyForm?.company_logo_url },
        { field: 'Cover Image', completed: !!companyForm?.company_cover_image_url }
      ]
    },
    {
      id: 'links',
      title: 'Social Links',
      description: 'Website and LinkedIn profile',
      points: 15,
      completed: companyForm?.company_website && companyForm?.company_linkedin,
      action: 'links',
      icon: Link,
      requirements: [
        { field: 'Company Website', completed: !!companyForm?.company_website },
        { field: 'LinkedIn Profile', completed: !!companyForm?.company_linkedin }
      ]
    },
    {
      id: 'first_job',
      title: 'First Job Posted',
      description: 'Post your first job listing',
      points: 15,
      completed: progress?.first_job_posted,
      action: 'jobs',
      icon: Briefcase,
      requirements: [
        { field: 'First Job Posted', completed: !!progress?.first_job_posted }
      ]
    }
  ];

  const totalPossiblePoints = completionItems.reduce((sum, item) => sum + item.points, 0);
  const earnedPoints = completionItems
    .filter(item => item.completed)
    .reduce((sum, item) => sum + item.points, 0);
  
  const completionPercentage = Math.round((earnedPoints / totalPossiblePoints) * 100);
  const completedItems = completionItems.filter(item => item.completed).length;
  const totalItems = completionItems.length;

  const handleItemClick = (action) => {
    if (onNavigateToSection) {
      onNavigateToSection(action);
    }
  };

  return (
    <Card className="bg-white/90 backdrop-blur-sm border-0 shadow-xl sticky top-4">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Target className="w-5 h-5 text-blue-600" />
            <span className="text-lg">Profile Completion</span>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setExpanded(!expanded)}
            className="p-1"
          >
            {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </Button>
        </CardTitle>
      </CardHeader>
      
      <CardContent className="pt-0">
        {/* Progress Overview */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-slate-700">
              {completedItems}/{totalItems} completed
            </span>
            <Badge className="bg-blue-100 text-blue-800">
              {completionPercentage}%
            </Badge>
          </div>
          <Progress value={completionPercentage} className="h-3" />
          <div className="flex justify-between text-xs text-slate-500 mt-1">
            <span>{earnedPoints} points earned</span>
            <span>{totalPossiblePoints - earnedPoints} points remaining</span>
          </div>
        </div>

        {/* Completion Items */}
        {expanded && (
          <div className="space-y-3">
            {completionItems.map((item) => {
              const IconComponent = item.icon;
              return (
                <div
                  key={item.id}
                  className={`p-3 rounded-lg border transition-all duration-200 ${
                    item.completed 
                      ? 'bg-green-50 border-green-200' 
                      : 'bg-slate-50 border-slate-200 hover:bg-blue-50 hover:border-blue-200 cursor-pointer'
                  }`}
                  onClick={() => !item.completed && handleItemClick(item.action)}
                >
                  <div className="flex items-start space-x-3">
                    <div className={`flex-shrink-0 mt-0.5 ${
                      item.completed ? 'text-green-600' : 'text-slate-400'
                    }`}>
                      {item.completed ? (
                        <CheckCircle2 className="w-5 h-5" />
                      ) : (
                        <Circle className="w-5 h-5" />
                      )}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <IconComponent className="w-4 h-4 text-slate-600" />
                          <h4 className={`font-medium text-sm ${
                            item.completed ? 'text-green-800' : 'text-slate-800'
                          }`}>
                            {item.title}
                          </h4>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge 
                            variant={item.completed ? "default" : "secondary"}
                            className={`text-xs ${
                              item.completed 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-blue-100 text-blue-800'
                            }`}
                          >
                            +{item.points}
                          </Badge>
                          {!item.completed && (
                            <ArrowRight className="w-3 h-3 text-slate-400" />
                          )}
                        </div>
                      </div>
                      
                      <p className={`text-xs mt-1 ${
                        item.completed ? 'text-green-600' : 'text-slate-500'
                      }`}>
                        {item.description}
                      </p>
                      
                      {/* Detailed requirements */}
                      {!item.completed && item.requirements && (
                        <div className="mt-2 space-y-1">
                          {item.requirements.map((req, idx) => (
                            <div key={idx} className="flex items-center space-x-2 text-xs">
                              <div className={`w-2 h-2 rounded-full ${
                                req.completed ? 'bg-green-400' : 'bg-slate-300'
                              }`} />
                              <span className={
                                req.completed ? 'text-green-600 line-through' : 'text-slate-600'
                              }>
                                {req.field}
                              </span>
                            </div>
                          ))}
                        </div>
                      )}
                      
                      {item.completed && (
                        <div className="flex items-center space-x-1 mt-1">
                          <Star className="w-3 h-3 text-green-500 fill-current" />
                          <span className="text-xs text-green-600 font-medium">Completed</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Action Button */}
        {earnedPoints < totalPossiblePoints && (
          <div className="mt-4 pt-4 border-t border-slate-200">
            {completionPercentage === 100 ? (
              <div className="text-center">
                <div className="flex items-center justify-center space-x-2 text-green-600 mb-2">
                  <Star className="w-5 h-5 fill-current" />
                  <span className="font-bold">Profile Complete!</span>
                </div>
                <p className="text-xs text-slate-600">
                  Your profile is optimized to attract top talent
                </p>
              </div>
            ) : (
              <Button
                size="sm"
                className="w-full bg-gradient-to-r from-blue-600 to-slate-700 hover:from-blue-700 hover:to-slate-800"
                onClick={() => {
                  const nextIncomplete = completionItems.find(item => !item.completed);
                  if (nextIncomplete) {
                    handleItemClick(nextIncomplete.action);
                  }
                }}
              >
                <Target className="w-4 h-4 mr-2" />
                Complete Next Step
              </Button>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default ProfileCompletionTracker;