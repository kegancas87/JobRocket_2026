import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from "./ui/button";
import { Card, CardContent } from "./ui/card";
import { Input } from "./ui/input";
import {
  Rocket, Building2, Users, Briefcase, Target, Mail, Share2,
  ChevronRight, ChevronLeft, Check, X, Award, Zap, Eye,
  Loader2, Plus, Search, Bell, BarChart3, MessageCircle,
  Globe, CheckCircle
} from "lucide-react";
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const STEPS = [
  { id: 0, label: 'Welcome', progress: 0 },
  { id: 1, label: 'Company', progress: 20 },
  { id: 2, label: 'Hiring', progress: 40 },
  { id: 3, label: 'Sourcing', progress: 60 },
  { id: 4, label: 'Activate', progress: 80 },
  { id: 5, label: 'Distribution', progress: 90 },
  { id: 6, label: 'Go Live', progress: 100 },
];

const INDUSTRIES = [
  'Technology', 'Finance & Banking', 'Healthcare', 'Education',
  'Manufacturing', 'Retail', 'Mining', 'Construction',
  'Agriculture', 'Tourism & Hospitality', 'Telecommunications',
  'Media & Entertainment', 'Legal', 'Real Estate', 'Energy',
  'Transportation & Logistics', 'Government', 'Non-Profit', 'Other'
];

const COMPANY_SIZES = [
  '1-10 employees', '11-50 employees', '51-200 employees',
  '201-500 employees', '501-1000 employees', '1000+ employees'
];

const COMMON_ROLES = [
  'Software Developer', 'Data Analyst', 'Marketing Manager', 'Sales Representative',
  'Project Manager', 'Accountant', 'HR Manager', 'Operations Manager',
  'Customer Service', 'Designer', 'Engineer', 'Business Analyst',
  'Admin Assistant', 'Financial Analyst', 'Consultant', 'Mechanic',
  'Electrician', 'Nurse', 'Teacher', 'Driver'
];

const SA_LOCATIONS = [
  'Johannesburg', 'Cape Town', 'Durban', 'Pretoria', 'Port Elizabeth',
  'Bloemfontein', 'East London', 'Polokwane', 'Nelspruit', 'Kimberley',
  'Pietermaritzburg', 'Rustenburg', 'Stellenbosch', 'Sandton', 'Midrand',
  'Remote / National', 'International'
];

const EMPLOYMENT_TYPES = [
  { id: 'permanent', label: 'Permanent' },
  { id: 'contract', label: 'Contract' },
  { id: 'temporary', label: 'Temporary' },
  { id: 'internship', label: 'Internship' },
  { id: 'freelance', label: 'Freelance' },
];

const HIRING_VOLUMES = [
  '1-5 per month', '5-10 per month', '10-25 per month',
  '25-50 per month', '50+ per month'
];

const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return { headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' } };
};

// Progress Bar
const ProgressBar = ({ progress, currentStep }) => (
  <div className="w-full mb-8">
    <div className="flex items-center justify-between mb-2">
      <span className="text-sm font-medium text-slate-600">Account Setup</span>
      <span className="text-sm font-bold text-emerald-600">{progress}%</span>
    </div>
    <div className="w-full bg-slate-200 rounded-full h-3 overflow-hidden">
      <div
        className="h-3 rounded-full transition-all duration-700 ease-out bg-gradient-to-r from-emerald-500 to-teal-500"
        style={{ width: `${progress}%` }}
      />
    </div>
    <div className="flex justify-between mt-3">
      {STEPS.slice(1).map((step) => (
        <div key={step.id} className="flex flex-col items-center" style={{ width: `${100 / 6}%` }}>
          <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold transition-all ${
            currentStep >= step.id ? 'bg-emerald-600 text-white' : 'bg-slate-200 text-slate-500'
          }`}>
            {currentStep > step.id ? <Check className="w-3.5 h-3.5" /> : step.id}
          </div>
          <span className={`text-xs mt-1 hidden sm:block ${currentStep >= step.id ? 'text-emerald-600 font-medium' : 'text-slate-400'}`}>
            {step.label}
          </span>
        </div>
      ))}
    </div>
  </div>
);

// Step 0: Welcome
const WelcomeStep = ({ userName, onNext, onSkip }) => (
  <div className="text-center py-8 max-w-lg mx-auto" data-testid="recruiter-onboarding-welcome">
    <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl flex items-center justify-center shadow-lg">
      <Building2 className="w-10 h-10 text-white" />
    </div>
    <h1 className="text-3xl font-bold text-slate-800 mb-3">
      Welcome to JobRocket{userName ? `, ${userName}` : ''}!
    </h1>
    <p className="text-lg text-slate-600 mb-8 leading-relaxed">
      Let's get you hiring faster. Set up your account in just a few minutes and start finding top talent.
    </p>
    <div className="bg-emerald-50 rounded-xl p-4 mb-8 text-left">
      <p className="text-sm font-medium text-emerald-800 mb-2">Quick setup includes:</p>
      <ul className="space-y-2 text-sm text-emerald-700">
        <li className="flex items-center gap-2"><Check className="w-4 h-4" /> Company profile setup</li>
        <li className="flex items-center gap-2"><Check className="w-4 h-4" /> Hiring preferences & candidate sourcing</li>
        <li className="flex items-center gap-2"><Check className="w-4 h-4" /> Post your first job or browse talent</li>
        <li className="flex items-center gap-2"><Check className="w-4 h-4" /> Distribution & visibility settings</li>
      </ul>
    </div>
    <Button onClick={onNext} className="w-full bg-emerald-600 hover:bg-emerald-700 h-12 text-lg font-semibold" data-testid="setup-account-btn">
      Set up my account <ChevronRight className="w-5 h-5 ml-2" />
    </Button>
    <button onClick={onSkip} className="mt-4 text-sm text-slate-400 hover:text-slate-600 transition-colors" data-testid="skip-recruiter-onboarding-btn">
      Skip for now
    </button>
  </div>
);

// Step 1: Account & Company Basics
const CompanyBasicsStep = ({ data, onChange, account }) => (
  <div data-testid="recruiter-onboarding-step-1">
    <h2 className="text-2xl font-bold text-slate-800 mb-2">Company Basics</h2>
    <p className="text-slate-600 mb-6">Let's set up your company profile</p>
    <div className="space-y-5">
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-2">Company Name</label>
        <div className="relative">
          <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <Input
            value={data.company_name || ''}
            onChange={(e) => onChange({ company_name: e.target.value })}
            placeholder="Your company name"
            className="pl-10 h-12"
            data-testid="company-name-input"
          />
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-2">Company Size</label>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
          {COMPANY_SIZES.map((size) => (
            <button
              key={size}
              onClick={() => onChange({ company_size: size })}
              className={`px-3 py-2.5 rounded-lg text-sm font-medium border transition-all ${
                data.company_size === size
                  ? 'bg-emerald-600 text-white border-emerald-600'
                  : 'bg-white text-slate-700 border-slate-200 hover:border-emerald-300'
              }`}
            >
              {size}
            </button>
          ))}
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-2">Industry</label>
        <select
          value={data.company_industry || ''}
          onChange={(e) => onChange({ company_industry: e.target.value })}
          className="w-full h-12 px-3 border border-slate-200 rounded-lg text-slate-700 focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
          data-testid="company-industry-select"
        >
          <option value="">Select your industry</option>
          {INDUSTRIES.map((ind) => (
            <option key={ind} value={ind}>{ind}</option>
          ))}
        </select>
      </div>
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-2">Company Location</label>
        <Input
          value={data.company_location || ''}
          onChange={(e) => onChange({ company_location: e.target.value })}
          placeholder="e.g. Sandton, Johannesburg"
          className="h-12"
          data-testid="company-location-input"
        />
      </div>
    </div>
  </div>
);

// Step 2: Hiring Preferences
const HiringPreferencesStep = ({ data, onChange }) => {
  const [roleInput, setRoleInput] = useState('');
  const [locInput, setLocInput] = useState('');
  const hiringRoles = data.hiring_roles || [];
  const hiringLocations = data.hiring_locations || [];

  const addRole = (role) => {
    if (role && !hiringRoles.includes(role)) {
      onChange({ hiring_roles: [...hiringRoles, role] });
      setRoleInput('');
    }
  };
  const removeRole = (role) => onChange({ hiring_roles: hiringRoles.filter(r => r !== role) });

  const addLocation = (loc) => {
    if (loc && !hiringLocations.includes(loc)) {
      onChange({ hiring_locations: [...hiringLocations, loc] });
      setLocInput('');
    }
  };
  const removeLocation = (loc) => onChange({ hiring_locations: hiringLocations.filter(l => l !== loc) });

  const roleSuggestions = COMMON_ROLES.filter(r => !hiringRoles.includes(r) && r.toLowerCase().includes(roleInput.toLowerCase())).slice(0, 6);
  const locSuggestions = SA_LOCATIONS.filter(l => !hiringLocations.includes(l) && l.toLowerCase().includes(locInput.toLowerCase())).slice(0, 6);

  return (
    <div data-testid="recruiter-onboarding-step-2">
      <h2 className="text-2xl font-bold text-slate-800 mb-2">Hiring Preferences</h2>
      <p className="text-slate-600 mb-1">Tell us what you're hiring for</p>
      <p className="text-sm text-emerald-600 font-medium mb-6">This helps us surface better candidates</p>
      <div className="space-y-5">
        {/* Roles */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Roles you hire for</label>
          <Input
            value={roleInput}
            onChange={(e) => setRoleInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); addRole(roleInput.trim()); } }}
            placeholder="Type a role and press Enter"
            className="h-12"
            data-testid="hiring-role-input"
          />
          {roleInput && roleSuggestions.length > 0 && (
            <div className="mt-1 bg-white border border-slate-200 rounded-lg shadow-lg max-h-36 overflow-y-auto">
              {roleSuggestions.map((r) => (
                <button key={r} onClick={() => addRole(r)} className="w-full text-left px-3 py-2 hover:bg-emerald-50 text-sm">{r}</button>
              ))}
            </div>
          )}
          {hiringRoles.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-3">
              {hiringRoles.map((role) => (
                <span key={role} className="inline-flex items-center gap-1 bg-emerald-100 text-emerald-800 px-3 py-1.5 rounded-full text-sm font-medium">
                  {role}
                  <button onClick={() => removeRole(role)}><X className="w-3.5 h-3.5 hover:text-red-600" /></button>
                </span>
              ))}
            </div>
          )}
          {hiringRoles.length === 0 && !roleInput && (
            <div className="flex flex-wrap gap-1.5 mt-2">
              {COMMON_ROLES.slice(0, 8).map((r) => (
                <button key={r} onClick={() => addRole(r)} className="px-2.5 py-1 rounded-full text-xs bg-slate-100 text-slate-600 hover:bg-emerald-100 hover:text-emerald-700">+ {r}</button>
              ))}
            </div>
          )}
        </div>

        {/* Locations */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Hiring Locations</label>
          <Input
            value={locInput}
            onChange={(e) => setLocInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); addLocation(locInput.trim()); } }}
            placeholder="Type a city or select below"
            className="h-12"
          />
          {locInput && locSuggestions.length > 0 && (
            <div className="mt-1 bg-white border border-slate-200 rounded-lg shadow-lg max-h-36 overflow-y-auto">
              {locSuggestions.map((l) => (
                <button key={l} onClick={() => addLocation(l)} className="w-full text-left px-3 py-2 hover:bg-emerald-50 text-sm">{l}</button>
              ))}
            </div>
          )}
          {hiringLocations.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-3">
              {hiringLocations.map((loc) => (
                <span key={loc} className="inline-flex items-center gap-1 bg-teal-100 text-teal-800 px-3 py-1.5 rounded-full text-sm font-medium">
                  {loc}
                  <button onClick={() => removeLocation(loc)}><X className="w-3.5 h-3.5 hover:text-red-600" /></button>
                </span>
              ))}
            </div>
          )}
          {hiringLocations.length === 0 && !locInput && (
            <div className="flex flex-wrap gap-1.5 mt-2">
              {SA_LOCATIONS.slice(0, 8).map((l) => (
                <button key={l} onClick={() => addLocation(l)} className="px-2.5 py-1 rounded-full text-xs bg-slate-100 text-slate-600 hover:bg-teal-100 hover:text-teal-700">+ {l}</button>
              ))}
            </div>
          )}
        </div>

        {/* Employment Types */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Employment Types</label>
          <div className="flex flex-wrap gap-2">
            {EMPLOYMENT_TYPES.map((type) => {
              const selected = (data.hiring_employment_types || []).includes(type.id);
              return (
                <button key={type.id} onClick={() => {
                  const current = data.hiring_employment_types || [];
                  onChange({ hiring_employment_types: selected ? current.filter(t => t !== type.id) : [...current, type.id] });
                }} className={`px-4 py-2 rounded-full text-sm font-medium border transition-all ${
                  selected ? 'bg-emerald-600 text-white border-emerald-600' : 'bg-white text-slate-700 border-slate-200 hover:border-emerald-300'
                }`}>
                  {type.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Hiring Volume */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Typical Hiring Volume</label>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {HIRING_VOLUMES.map((vol) => (
              <button key={vol} onClick={() => onChange({ hiring_volume: vol })}
                className={`px-3 py-2.5 rounded-lg text-sm font-medium border transition-all ${
                  data.hiring_volume === vol ? 'bg-emerald-600 text-white border-emerald-600' : 'bg-white text-slate-700 border-slate-200 hover:border-emerald-300'
                }`}>
                {vol}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Step 3: Candidate Access Setup
const CandidateAccessStep = ({ data, onChange }) => {
  const sourcingMethods = data.sourcing_methods || [];
  const toggleMethod = (method) => {
    const updated = sourcingMethods.includes(method) ? sourcingMethods.filter(m => m !== method) : [...sourcingMethods, method];
    onChange({ sourcing_methods: updated });
  };

  return (
    <div data-testid="recruiter-onboarding-step-3">
      <h2 className="text-2xl font-bold text-slate-800 mb-2">Candidate Access Setup</h2>
      <p className="text-slate-600 mb-6">Choose how you want to find candidates</p>
      <div className="space-y-5">
        {/* Sourcing Methods */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-3">Sourcing Methods</label>
          <div className="space-y-3">
            {[
              { id: 'applicants', icon: Briefcase, label: 'Applicant Inbox', desc: 'Receive applications from job seekers' },
              { id: 'talent_pool', icon: Search, label: 'Talent Pool Search', desc: 'Actively search and discover candidates' },
              { id: 'ai_matching', icon: Zap, label: 'AI Matching', desc: 'Get AI-powered candidate recommendations' },
            ].map((method) => (
              <button
                key={method.id}
                onClick={() => toggleMethod(method.id)}
                className={`w-full flex items-center p-4 rounded-xl border-2 transition-all text-left ${
                  sourcingMethods.includes(method.id)
                    ? 'border-emerald-500 bg-emerald-50'
                    : 'border-slate-200 hover:border-emerald-300'
                }`}
              >
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center mr-4 ${
                  sourcingMethods.includes(method.id) ? 'bg-emerald-600 text-white' : 'bg-slate-100 text-slate-500'
                }`}>
                  <method.icon className="w-5 h-5" />
                </div>
                <div className="flex-1">
                  <p className="font-medium text-slate-800">{method.label}</p>
                  <p className="text-sm text-slate-500">{method.desc}</p>
                </div>
                <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                  sourcingMethods.includes(method.id) ? 'border-emerald-600 bg-emerald-600' : 'border-slate-300'
                }`}>
                  {sourcingMethods.includes(method.id) && <Check className="w-4 h-4 text-white" />}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Alerts Toggle */}
        <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
          <div className="flex items-center gap-3">
            <Bell className="w-5 h-5 text-emerald-600" />
            <div>
              <p className="font-medium text-slate-800">Enable Candidate Alerts</p>
              <p className="text-sm text-slate-500">Get notified when matching candidates appear</p>
            </div>
          </div>
          <button
            onClick={() => onChange({ alerts_enabled: !data.alerts_enabled })}
            className={`relative w-12 h-6 rounded-full transition-colors ${data.alerts_enabled ? 'bg-emerald-600' : 'bg-slate-300'}`}
            data-testid="alerts-toggle"
          >
            <span className={`absolute top-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${data.alerts_enabled ? 'translate-x-6' : 'translate-x-0.5'}`} />
          </button>
        </div>

        {/* Match Preferences */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Match Preference</label>
          <div className="grid grid-cols-3 gap-2">
            {['Skills first', 'Experience first', 'Location first'].map((pref) => (
              <button key={pref} onClick={() => onChange({ match_preferences: pref })}
                className={`px-3 py-2.5 rounded-lg text-sm font-medium border transition-all ${
                  data.match_preferences === pref ? 'bg-emerald-600 text-white border-emerald-600' : 'bg-white text-slate-700 border-slate-200 hover:border-emerald-300'
                }`}>
                {pref}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Step 4: Post First Job OR Browse Talent
const ActivateStep = ({ onAction }) => (
  <div className="text-center" data-testid="recruiter-onboarding-step-4">
    <h2 className="text-2xl font-bold text-slate-800 mb-2">Time to Take Action</h2>
    <p className="text-slate-600 mb-2">Choose how you'd like to get started</p>
    <p className="text-sm text-emerald-600 font-medium mb-8">Most recruiters do this within 5 minutes</p>
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-lg mx-auto">
      <button
        onClick={() => onAction('post_job')}
        className="p-6 rounded-xl border-2 border-slate-200 hover:border-emerald-500 hover:bg-emerald-50 transition-all text-center group"
        data-testid="post-first-job-btn"
      >
        <div className="w-14 h-14 mx-auto mb-4 bg-emerald-100 rounded-xl flex items-center justify-center group-hover:bg-emerald-600 transition-colors">
          <Plus className="w-7 h-7 text-emerald-600 group-hover:text-white transition-colors" />
        </div>
        <p className="font-semibold text-slate-800 text-lg mb-1">Post my first job</p>
        <p className="text-sm text-slate-500">Create a listing and start receiving applications</p>
      </button>
      <button
        onClick={() => onAction('browse_talent')}
        className="p-6 rounded-xl border-2 border-slate-200 hover:border-teal-500 hover:bg-teal-50 transition-all text-center group"
        data-testid="browse-talent-btn"
      >
        <div className="w-14 h-14 mx-auto mb-4 bg-teal-100 rounded-xl flex items-center justify-center group-hover:bg-teal-600 transition-colors">
          <Search className="w-7 h-7 text-teal-600 group-hover:text-white transition-colors" />
        </div>
        <p className="font-semibold text-slate-800 text-lg mb-1">Browse candidates</p>
        <p className="text-sm text-slate-500">Search the talent pool for top candidates</p>
      </button>
    </div>
  </div>
);

// Step 5: Distribution & Visibility
const DistributionStep = ({ data, onChange }) => (
  <div data-testid="recruiter-onboarding-step-5">
    <h2 className="text-2xl font-bold text-slate-800 mb-2">Distribution & Visibility</h2>
    <p className="text-slate-600 mb-1">Boost your job visibility with distribution channels</p>
    <p className="text-sm text-emerald-600 font-medium mb-6">Boosted jobs get more applications</p>
    <div className="space-y-3">
      {[
        { key: 'distribution_email', icon: Mail, label: 'Email Distribution', desc: 'Send jobs to matching candidates via email', color: 'blue' },
        { key: 'distribution_whatsapp', icon: MessageCircle, label: 'WhatsApp Distribution', desc: 'Share jobs on WhatsApp channels', color: 'green' },
        { key: 'distribution_social', icon: Globe, label: 'Social Media Distribution', desc: 'Post jobs to social media platforms', color: 'purple' },
      ].map((channel) => (
        <div
          key={channel.key}
          className="flex items-center justify-between p-4 bg-white rounded-xl border border-slate-200"
        >
          <div className="flex items-center gap-4">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
              data[channel.key] ? 'bg-emerald-100 text-emerald-600' : 'bg-slate-100 text-slate-400'
            }`}>
              <channel.icon className="w-5 h-5" />
            </div>
            <div>
              <p className="font-medium text-slate-800">{channel.label}</p>
              <p className="text-sm text-slate-500">{channel.desc}</p>
            </div>
          </div>
          <button
            onClick={() => onChange({ [channel.key]: !data[channel.key] })}
            className={`relative w-12 h-6 rounded-full transition-colors ${data[channel.key] ? 'bg-emerald-600' : 'bg-slate-300'}`}
          >
            <span className={`absolute top-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${data[channel.key] ? 'translate-x-6' : 'translate-x-0.5'}`} />
          </button>
        </div>
      ))}
    </div>
  </div>
);

// Step 6: Go Live
const GoLiveStep = () => (
  <div className="text-center py-4" data-testid="recruiter-onboarding-step-6">
    <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-emerald-400 to-teal-600 rounded-2xl flex items-center justify-center shadow-lg">
      <Rocket className="w-10 h-10 text-white" />
    </div>
    <h2 className="text-2xl font-bold text-slate-800 mb-3">Everything looks great!</h2>
    <p className="text-slate-600 mb-6">Your account is ready. Click below to go live and start hiring.</p>
    <div className="grid grid-cols-3 gap-3 max-w-sm mx-auto mb-6">
      {[
        { icon: Building2, label: 'Company Live', color: 'text-emerald-600 bg-emerald-50' },
        { icon: Target, label: 'Sourcing Ready', color: 'text-teal-600 bg-teal-50' },
        { icon: BarChart3, label: 'Dashboard Ready', color: 'text-blue-600 bg-blue-50' },
      ].map((item) => (
        <div key={item.label} className={`p-3 rounded-xl ${item.color}`}>
          <item.icon className="w-6 h-6 mx-auto mb-1" />
          <p className="text-xs font-medium">{item.label}</p>
        </div>
      ))}
    </div>
  </div>
);

// Confetti
const Confetti = () => {
  const colors = ['#10B981', '#14B8A6', '#3B82F6', '#F59E0B', '#8B5CF6', '#EC4899'];
  return (
    <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden">
      {Array.from({ length: 60 }).map((_, i) => (
        <div key={i} className="absolute" style={{
          left: `${Math.random() * 100}%`, top: `-${Math.random() * 20}%`,
          width: `${6 + Math.random() * 8}px`, height: `${6 + Math.random() * 8}px`,
          backgroundColor: colors[i % colors.length],
          borderRadius: Math.random() > 0.5 ? '50%' : '2px',
          animation: `confetti-fall ${2 + Math.random() * 3}s ease-in forwards`,
          animationDelay: `${Math.random() * 1.5}s`,
        }} />
      ))}
      <style>{`@keyframes confetti-fall { 0% { transform: translateY(0) rotate(0deg); opacity: 1; } 100% { transform: translateY(100vh) rotate(720deg); opacity: 0; } }`}</style>
    </div>
  );
};

// Completion screen
const CompletionScreen = ({ onFinish }) => (
  <div className="text-center py-8 max-w-lg mx-auto" data-testid="recruiter-onboarding-complete">
    <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-emerald-400 to-teal-600 rounded-2xl flex items-center justify-center shadow-lg">
      <CheckCircle className="w-10 h-10 text-white" />
    </div>
    <h1 className="text-3xl font-bold text-slate-800 mb-3">You're ready to hire!</h1>
    <p className="text-lg text-slate-600 mb-8">Your account is live. Head to your dashboard to start finding talent.</p>
    <div className="bg-slate-50 rounded-xl p-4 mb-8 text-left space-y-3">
      <p className="text-sm font-medium text-slate-700">Next steps:</p>
      {[
        { icon: Users, label: 'Add team members to collaborate' },
        { icon: BarChart3, label: 'Explore your dashboard & analytics' },
      ].map((item) => (
        <div key={item.label} className="flex items-center gap-3 text-sm text-slate-600">
          <item.icon className="w-4 h-4 text-emerald-600" />
          <span>{item.label}</span>
        </div>
      ))}
    </div>
    <Button onClick={onFinish} className="w-full bg-emerald-600 hover:bg-emerald-700 h-12 text-lg font-semibold" data-testid="go-to-dashboard-btn">
      Go to Dashboard <ChevronRight className="w-5 h-5 ml-2" />
    </Button>
  </div>
);

// Badge popup
const BadgePopup = ({ badge, onClose }) => {
  const badgeInfo = {
    company_live: { title: 'Company Profile Live', icon: Building2, color: 'from-emerald-500 to-emerald-600' },
    sourcing_ready: { title: 'Sourcing Ready', icon: Target, color: 'from-teal-500 to-teal-600' },
    ready_to_hire: { title: 'Ready to Hire', icon: Rocket, color: 'from-blue-500 to-blue-600' },
  };
  const info = badgeInfo[badge];
  if (!info) return null;
  const Icon = info.icon;

  return (
    <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-white rounded-2xl p-6 text-center shadow-2xl max-w-xs" onClick={e => e.stopPropagation()}>
        <div className={`w-16 h-16 mx-auto mb-4 bg-gradient-to-br ${info.color} rounded-xl flex items-center justify-center`}>
          <Icon className="w-8 h-8 text-white" />
        </div>
        <h3 className="text-lg font-bold text-slate-800 mb-1">Badge Unlocked!</h3>
        <p className="text-slate-600 mb-4">{info.title}</p>
        <Button onClick={onClose} size="sm" className="bg-emerald-600 hover:bg-emerald-700">Continue</Button>
      </div>
    </div>
  );
};

// Main Recruiter Onboarding Wizard
const RecruiterOnboarding = ({ user, onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);
  const [formData, setFormData] = useState({
    company_name: user?.account?.name || '',
    company_size: user?.account?.company_size || '',
    company_industry: user?.account?.company_industry || '',
    company_location: user?.account?.company_location || '',
    hiring_roles: [],
    hiring_locations: [],
    hiring_employment_types: [],
    hiring_volume: '',
    sourcing_methods: ['applicants'],
    alerts_enabled: true,
    match_preferences: 'Skills first',
    action_taken: '',
    distribution_email: true,
    distribution_whatsapp: false,
    distribution_social: false,
  });
  const [saving, setSaving] = useState(false);
  const [showBadge, setShowBadge] = useState(null);
  const [showConfetti, setShowConfetti] = useState(false);
  const [completed, setCompleted] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const loadProgress = async () => {
      try {
        const response = await axios.get(`${API}/onboarding/status`, getAuthHeaders());
        if (response.data.onboarding_step > 0) {
          setCurrentStep(response.data.onboarding_step);
          setProgress(response.data.onboarding_progress);
        }
      } catch { /* ignore */ }
    };
    loadProgress();
  }, []);

  const updateFormData = (updates) => setFormData(prev => ({ ...prev, ...updates }));

  const saveStep = async (step) => {
    setSaving(true);
    try {
      const response = await axios.put(`${API}/onboarding/step/${step}`, formData, getAuthHeaders());
      setProgress(response.data.progress);
      const badges = response.data.badges || [];
      const badgeMap = { 1: 'company_live', 3: 'sourcing_ready', 6: 'ready_to_hire' };
      const expected = badgeMap[step];
      if (expected && badges.includes(expected)) setShowBadge(expected);
      return true;
    } catch (err) {
      console.error('Save error:', err);
      return false;
    } finally {
      setSaving(false);
    }
  };

  const handleNext = async () => {
    if (currentStep === 0) {
      setCurrentStep(1);
      setProgress(STEPS[1].progress);
      return;
    }
    const saved = await saveStep(currentStep);
    if (!saved) return;
    if (currentStep === 6) {
      setShowConfetti(true);
      setCompleted(true);
      setTimeout(() => setShowConfetti(false), 4000);
      const savedUser = JSON.parse(localStorage.getItem('user') || '{}');
      savedUser.onboarding_completed = true;
      savedUser.onboarding_progress = 100;
      localStorage.setItem('user', JSON.stringify(savedUser));
      return;
    }
    setCurrentStep(currentStep + 1);
  };

  const handleBack = () => { if (currentStep > 0) setCurrentStep(currentStep - 1); };

  const handleSkip = async () => {
    try {
      await axios.post(`${API}/onboarding/skip`, {}, getAuthHeaders());
      const savedUser = JSON.parse(localStorage.getItem('user') || '{}');
      savedUser.onboarding_completed = true;
      localStorage.setItem('user', JSON.stringify(savedUser));
      if (onComplete) onComplete();
      else navigate('/');
    } catch { navigate('/'); }
  };

  const handleFinish = () => {
    if (onComplete) onComplete();
    else navigate('/');
  };

  const handleStep4Action = async (action) => {
    updateFormData({ action_taken: action });
    const saved = await saveStep(4);
    if (!saved) return;
    setCurrentStep(5);
  };

  const renderStep = () => {
    switch (currentStep) {
      case 0: return <WelcomeStep userName={user?.first_name} onNext={handleNext} onSkip={handleSkip} />;
      case 1: return <CompanyBasicsStep data={formData} onChange={updateFormData} account={user?.account} />;
      case 2: return <HiringPreferencesStep data={formData} onChange={updateFormData} />;
      case 3: return <CandidateAccessStep data={formData} onChange={updateFormData} />;
      case 4: return <ActivateStep onAction={handleStep4Action} />;
      case 5: return <DistributionStep data={formData} onChange={updateFormData} />;
      case 6: return <GoLiveStep />;
      default: return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-emerald-50/30 to-teal-50/20">
      {showConfetti && <Confetti />}
      {showBadge && <BadgePopup badge={showBadge} onClose={() => setShowBadge(null)} />}

      <div className="max-w-2xl mx-auto px-4 py-8">
        <div className="flex items-center justify-center mb-6">
          <div className="bg-gradient-to-br from-blue-600 to-purple-600 p-2 rounded-lg mr-2">
            <Rocket className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Job Rocket
          </span>
        </div>

        {currentStep > 0 && !completed && (
          <ProgressBar progress={progress} currentStep={currentStep} />
        )}

        <Card className="bg-white/90 backdrop-blur-sm shadow-xl border-0">
          <CardContent className="p-6 sm:p-8">
            {completed ? (
              <CompletionScreen onFinish={handleFinish} />
            ) : (
              <>
                {renderStep()}
                {currentStep > 0 && currentStep !== 4 && (
                  <div className="flex items-center justify-between mt-8 pt-6 border-t border-slate-100">
                    <Button variant="ghost" onClick={handleBack} disabled={saving} data-testid="recruiter-back-btn">
                      <ChevronLeft className="w-4 h-4 mr-1" /> Back
                    </Button>
                    <div className="flex items-center gap-3">
                      {currentStep < 6 && (
                        <button onClick={() => setCurrentStep(currentStep + 1)} className="text-sm text-slate-400 hover:text-slate-600" data-testid="recruiter-skip-step-btn">
                          Skip
                        </button>
                      )}
                      <Button onClick={handleNext} disabled={saving} className="bg-emerald-600 hover:bg-emerald-700 px-6" data-testid="recruiter-next-btn">
                        {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : currentStep === 6 ? (
                          <>Go Live <Rocket className="w-4 h-4 ml-2" /></>
                        ) : (
                          <>Continue <ChevronRight className="w-4 h-4 ml-2" /></>
                        )}
                      </Button>
                    </div>
                  </div>
                )}
              </>
            )}
          </CardContent>
        </Card>

        {currentStep > 0 && !completed && (
          <div className="text-center mt-4">
            <button onClick={handleSkip} className="text-sm text-slate-400 hover:text-slate-600 transition-colors" data-testid="skip-recruiter-all-btn">
              Skip onboarding entirely
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default RecruiterOnboarding;
