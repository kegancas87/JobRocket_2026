import React, { useState, useEffect } from 'react';
import { Trophy, Rocket, Star, Sparkles, Zap } from 'lucide-react';

const TrophyProgress = ({ progress, showDetails = false, onComplete, userRole = 'job_seeker' }) => {
  const [animateComplete, setAnimateComplete] = useState(false);
  const [showRocket, setShowRocket] = useState(false);
  
  const totalPoints = progress?.total_points || 0;
  const percentage = Math.min((totalPoints / 100) * 100, 100);
  const isComplete = totalPoints >= 100;
  
  const jobSeekerTasks = [
    { key: 'profile_picture', label: 'Add Profile Picture', points: 5, completed: progress?.profile_picture },
    { key: 'about_me', label: 'Write About Me (50+ chars)', points: 10, completed: progress?.about_me },
    { key: 'work_history', label: 'Add Work Experience', points: 10, completed: progress?.work_history },
    { key: 'skills', label: 'Add 5+ Skills', points: 20, completed: progress?.skills },
    { key: 'education', label: 'Add Education with Document', points: 10, completed: progress?.education },
    { key: 'achievements', label: 'Add Achievements', points: 10, completed: progress?.achievements },
    { key: 'intro_video', label: 'Upload Intro Video', points: 20, completed: progress?.intro_video },
    { key: 'job_applications', label: 'Apply to 5 Jobs', points: 10, completed: (progress?.job_applications || 0) >= 5 },
    { key: 'email_alerts', label: 'Setup Email Alerts', points: 5, completed: progress?.email_alerts }
  ];

  const recruiterTasks = [
    { key: 'company_logo', label: 'Add Company Logo', points: 15, completed: progress?.company_logo },
    { key: 'cover_image', label: 'Add Cover Image', points: 10, completed: progress?.cover_image },
    { key: 'company_description', label: 'Company Description (100+ chars)', points: 20, completed: progress?.company_description },
    { key: 'company_size', label: 'Set Company Size', points: 10, completed: progress?.company_size },
    { key: 'website_link', label: 'Add Website Link', points: 15, completed: progress?.website_link },
    { key: 'linkedin_link', label: 'Add LinkedIn Link', points: 10, completed: progress?.linkedin_link },
    { key: 'first_job_posted', label: 'Post First Job', points: 20, completed: progress?.first_job_posted }
  ];

  const tasks = userRole === 'recruiter' ? recruiterTasks : jobSeekerTasks;

  useEffect(() => {
    if (isComplete && !animateComplete) {
      setAnimateComplete(true);
      setTimeout(() => {
        setShowRocket(true);
        if (onComplete) onComplete();
      }, 500);
    }
  }, [isComplete, animateComplete, onComplete]);

  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-3xl shadow-xl p-8 border border-slate-200/50">
      <div className="text-center mb-8">
        <h3 className="text-2xl font-bold text-slate-800 mb-2">
          {userRole === 'recruiter' ? 'Company Profile Completion' : 'Profile Completion'}
        </h3>
        <p className="text-slate-600">
          {userRole === 'recruiter' 
            ? 'Complete your company profile to attract top talent' 
            : 'Complete your profile to unlock all features'
          }
        </p>
      </div>

      {/* Trophy with Progress Circle */}
      <div className="flex justify-center mb-8">
        <div className="relative">
          {/* Progress Circle */}
          <svg className="w-32 h-32 transform -rotate-90" viewBox="0 0 120 120">
            {/* Background circle */}
            <circle
              cx="60"
              cy="60"
              r="50"
              stroke="rgb(226, 232, 240)"
              strokeWidth="8"
              fill="none"
            />
            {/* Progress circle */}
            <circle
              cx="60"
              cy="60"
              r="50"
              stroke={isComplete ? "url(#goldGradient)" : "url(#blueGradient)"}
              strokeWidth="8"
              fill="none"
              strokeLinecap="round"
              strokeDasharray={`${2 * Math.PI * 50}`}
              strokeDashoffset={`${2 * Math.PI * 50 * (1 - percentage / 100)}`}
              className="transition-all duration-1000 ease-out"
            />
            {/* Gradient definitions */}
            <defs>
              <linearGradient id="blueGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#3b82f6" />
                <stop offset="100%" stopColor="#1e40af" />
              </linearGradient>
              <linearGradient id="goldGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#fbbf24" />
                <stop offset="100%" stopColor="#f59e0b" />
              </linearGradient>
            </defs>
          </svg>
          
          {/* Trophy Icon */}
          <div 
            className={`absolute inset-0 flex items-center justify-center transition-all duration-1000 ${
              isComplete ? 'text-yellow-500 scale-110' : 'text-slate-400'
            }`}
          >
            <Trophy 
              className={`w-16 h-16 ${animateComplete ? 'animate-bounce' : ''}`}
              fill={isComplete ? "currentColor" : "none"}
            />
          </div>
          
          {/* Rocket Launch Animation */}
          {showRocket && (
            <div className="absolute -top-8 left-1/2 transform -translate-x-1/2">
              <Rocket className="w-8 h-8 text-blue-600 animate-rocket-launch" />
            </div>
          )}
          
          {/* Sparkles for completion */}
          {isComplete && (
            <>
              <Sparkles className="absolute -top-2 -right-2 w-6 h-6 text-yellow-400 animate-sparkle" />
              <Star className="absolute -bottom-2 -left-2 w-5 h-5 text-yellow-400 animate-sparkle animation-delay-300" />
              <Zap className="absolute top-1/2 -right-4 w-5 h-5 text-blue-400 animate-sparkle animation-delay-600" />
            </>
          )}
        </div>
      </div>

      {/* Progress Stats */}
      <div className="text-center mb-8">
        <div className="text-4xl font-black mb-2">
          <span className={isComplete ? 'text-yellow-600' : 'text-blue-600'}>
            {totalPoints}
          </span>
          <span className="text-slate-400 text-2xl"> / 100</span>
        </div>
        <div className="text-lg font-semibold text-slate-700">
          {isComplete ? '🚀 Profile Complete!' : `${100 - totalPoints} points to go`}
        </div>
        {isComplete && (
          <div className="text-yellow-600 font-medium mt-2 animate-pulse">
            {userRole === 'recruiter' ? '✨ Ready to hire top talent! ✨' : '✨ Career rocket launched! ✨'}
          </div>
        )}
      </div>

      {/* Task List (if showDetails is true) */}
      {showDetails && (
        <div className="space-y-4">
          <h4 className="text-lg font-bold text-slate-800 mb-4">Completion Tasks</h4>
          {tasks.map((task) => (
            <div
              key={task.key}
              className={`flex items-center justify-between p-4 rounded-xl transition-all ${
                task.completed
                  ? 'bg-green-50 border border-green-200'
                  : 'bg-slate-50 border border-slate-200 hover:bg-slate-100'
              }`}
            >
              <div className="flex items-center space-x-3">
                <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                  task.completed
                    ? 'bg-green-500 text-white'
                    : 'bg-slate-300 text-slate-600'
                }`}>
                  {task.completed ? '✓' : '○'}
                </div>
                <span className={`font-medium ${
                  task.completed ? 'text-green-800' : 'text-slate-700'
                }`}>
                  {task.label}
                </span>
              </div>
              <div className={`text-sm font-bold px-3 py-1 rounded-full ${
                task.completed
                  ? 'bg-green-200 text-green-800'
                  : 'bg-slate-200 text-slate-600'
              }`}>
                +{task.points}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default TrophyProgress;