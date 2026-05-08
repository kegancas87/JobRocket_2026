import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from "./ui/button";
import { Card, CardContent } from "./ui/card";
import { Badge } from "./ui/badge";
import { Input } from "./ui/input";
import {
  Rocket, MapPin, Briefcase, Star, Upload, FileText, User,
  ChevronRight, ChevronLeft, Check, X, Award, Zap, Eye,
  Loader2, Plus, Trash2, Clock, Calendar, Link2
} from "lucide-react";
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const STEPS = [
  { id: 0, label: 'Welcome', progress: 0 },
  { id: 1, label: 'Location', progress: 15 },
  { id: 2, label: 'Professional', progress: 35 },
  { id: 3, label: 'Skills', progress: 55 },
  { id: 4, label: 'CV Upload', progress: 75 },
  { id: 5, label: 'Experience', progress: 90 },
  { id: 6, label: 'Profile Boost', progress: 100 },
];

const INDUSTRIES = [
  'Technology', 'Finance & Banking', 'Healthcare', 'Education',
  'Manufacturing', 'Retail', 'Mining', 'Construction',
  'Agriculture', 'Tourism & Hospitality', 'Telecommunications',
  'Media & Entertainment', 'Legal', 'Real Estate', 'Energy',
  'Transportation & Logistics', 'Government', 'Non-Profit', 'Other'
];

const EXPERIENCE_LEVELS = [
  '0-1 years', '1-2 years', '2-3 years', '3-5 years',
  '5-7 years', '7-10 years', '10-15 years', '15+ years'
];

const SENIORITY_LEVELS = [
  'Entry Level', 'Junior', 'Mid Level', 'Senior', 'Lead', 'Executive'
];

const EMPLOYMENT_TYPES = [
  { id: 'permanent', label: 'Permanent' },
  { id: 'contract', label: 'Contract' },
  { id: 'remote', label: 'Remote' },
  { id: 'part-time', label: 'Part-time' },
  { id: 'freelance', label: 'Freelance' },
];

const POPULAR_SKILLS = [
  'JavaScript', 'Python', 'React', 'Node.js', 'SQL', 'Excel',
  'Project Management', 'Data Analysis', 'Marketing', 'Sales',
  'Customer Service', 'Communication', 'Leadership', 'Teamwork',
  'Problem Solving', 'Java', 'C#', 'AWS', 'Docker', 'Machine Learning',
  'Figma', 'Photoshop', 'SEO', 'Content Writing', 'Accounting',
  'Financial Analysis', 'HR Management', 'Supply Chain', 'Logistics',
  'AutoCAD', 'Electrical Engineering', 'Mechanical Engineering'
];

const STRENGTHS = [
  'Analytical Thinking', 'Creative Problem Solving', 'Team Leadership',
  'Strategic Planning', 'Communication', 'Adaptability', 'Attention to Detail',
  'Time Management', 'Critical Thinking', 'Collaboration',
  'Negotiation', 'Decision Making', 'Innovation', 'Mentoring',
  'Conflict Resolution', 'Resilience'
];

const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return { headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' } };
};

const getUploadHeaders = () => {
  const token = localStorage.getItem('token');
  return { headers: { Authorization: `Bearer ${token}` } };
};

// ProgressBar component
const ProgressBar = ({ progress, currentStep }) => (
  <div className="w-full mb-8">
    <div className="flex items-center justify-between mb-2">
      <span className="text-sm font-medium text-slate-600">Profile Completion</span>
      <span className="text-sm font-bold text-blue-600">{progress}%</span>
    </div>
    <div className="w-full bg-slate-200 rounded-full h-3 overflow-hidden">
      <div
        className="h-3 rounded-full transition-all duration-700 ease-out bg-gradient-to-r from-blue-500 to-blue-600"
        style={{ width: `${progress}%` }}
      />
    </div>
    {/* Step indicators */}
    <div className="flex justify-between mt-3">
      {STEPS.slice(1).map((step) => (
        <div key={step.id} className="flex flex-col items-center" style={{ width: `${100 / 6}%` }}>
          <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold transition-all ${
            currentStep >= step.id
              ? 'bg-blue-600 text-white'
              : 'bg-slate-200 text-slate-500'
          }`}>
            {currentStep > step.id ? <Check className="w-3.5 h-3.5" /> : step.id}
          </div>
          <span className={`text-xs mt-1 hidden sm:block ${currentStep >= step.id ? 'text-blue-600 font-medium' : 'text-slate-400'}`}>
            {step.label}
          </span>
        </div>
      ))}
    </div>
  </div>
);

// Step 0: Welcome
const WelcomeStep = ({ userName, onNext, onSkip }) => (
  <div className="text-center py-8 max-w-lg mx-auto" data-testid="onboarding-welcome">
    <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-blue-500 to-blue-700 rounded-2xl flex items-center justify-center shadow-lg">
      <Rocket className="w-10 h-10 text-white" />
    </div>
    <h1 className="text-3xl font-bold text-slate-800 mb-3">
      Welcome to JobRocket{userName ? `, ${userName}` : ''}!
    </h1>
    <p className="text-lg text-slate-600 mb-8 leading-relaxed">
      Let's get you noticed by recruiters. Complete your profile to boost your visibility and land your dream job.
    </p>
    <div className="bg-blue-50 rounded-xl p-4 mb-8 text-left">
      <p className="text-sm font-medium text-blue-800 mb-2">What you'll set up:</p>
      <ul className="space-y-2 text-sm text-blue-700">
        <li className="flex items-center gap-2"><Check className="w-4 h-4" /> Your location & professional snapshot</li>
        <li className="flex items-center gap-2"><Check className="w-4 h-4" /> Skills & strengths</li>
        <li className="flex items-center gap-2"><Check className="w-4 h-4" /> CV upload & work experience</li>
        <li className="flex items-center gap-2"><Check className="w-4 h-4" /> Profile boost for maximum visibility</li>
      </ul>
    </div>
    <Button onClick={onNext} className="w-full bg-blue-600 hover:bg-blue-700 h-12 text-lg font-semibold" data-testid="start-profile-btn">
      Start my profile <ChevronRight className="w-5 h-5 ml-2" />
    </Button>
    <button onClick={onSkip} className="mt-4 text-sm text-slate-400 hover:text-slate-600 transition-colors" data-testid="skip-onboarding-btn">
      Skip for now
    </button>
  </div>
);

// Step 1: Location
const LocationStep = ({ data, onChange }) => (
  <div data-testid="onboarding-step-1">
    <h2 className="text-2xl font-bold text-slate-800 mb-2">Where are you based?</h2>
    <p className="text-slate-600 mb-6">This helps us match you with nearby opportunities</p>
    <div>
      <label className="block text-sm font-medium text-slate-700 mb-2">City / Province</label>
      <div className="relative">
        <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
        <Input
          value={data.location || ''}
          onChange={(e) => onChange({ location: e.target.value })}
          placeholder="e.g. Johannesburg, Gauteng"
          className="pl-10 h-12"
          data-testid="location-input"
        />
      </div>
    </div>
  </div>
);

// Step 2: Professional Snapshot
const ProfessionalStep = ({ data, onChange }) => (
  <div data-testid="onboarding-step-2">
    <h2 className="text-2xl font-bold text-slate-800 mb-2">Professional Snapshot</h2>
    <p className="text-slate-600 mb-6">Tell us about your current career level</p>
    <div className="space-y-5">
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-2">Current Role / Job Title</label>
        <div className="relative">
          <Briefcase className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <Input
            value={data.desired_job_title || ''}
            onChange={(e) => onChange({ desired_job_title: e.target.value })}
            placeholder="e.g. Software Developer, Marketing Manager"
            className="pl-10 h-12"
            data-testid="job-title-input"
          />
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-2">Years of Experience</label>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {EXPERIENCE_LEVELS.map((level) => (
            <button
              key={level}
              onClick={() => onChange({ years_of_experience: level })}
              className={`px-3 py-2 rounded-lg text-sm font-medium border transition-all ${
                data.years_of_experience === level
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white text-slate-700 border-slate-200 hover:border-blue-300'
              }`}
            >
              {level}
            </button>
          ))}
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-2">Industry</label>
        <select
          value={data.industry_preference || ''}
          onChange={(e) => onChange({ industry_preference: e.target.value })}
          className="w-full h-12 px-3 border border-slate-200 rounded-lg text-slate-700 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          data-testid="industry-select"
        >
          <option value="">Select your industry</option>
          {INDUSTRIES.map((ind) => (
            <option key={ind} value={ind}>{ind}</option>
          ))}
        </select>
      </div>
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-2">Employment Type Preference</label>
        <div className="flex flex-wrap gap-2">
          {EMPLOYMENT_TYPES.map((type) => {
            const selected = (data.employment_type_preference || []).includes(type.id);
            return (
              <button
                key={type.id}
                onClick={() => {
                  const current = data.employment_type_preference || [];
                  const updated = selected ? current.filter(t => t !== type.id) : [...current, type.id];
                  onChange({ employment_type_preference: updated });
                }}
                className={`px-4 py-2 rounded-full text-sm font-medium border transition-all ${
                  selected
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white text-slate-700 border-slate-200 hover:border-blue-300'
                }`}
              >
                {type.label}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  </div>
);

// Step 3: Skills & Strengths
const SkillsStep = ({ data, onChange }) => {
  const [skillInput, setSkillInput] = useState('');
  const currentSkills = data.skills || [];
  const filteredSuggestions = POPULAR_SKILLS.filter(
    s => !currentSkills.includes(s) && s.toLowerCase().includes(skillInput.toLowerCase())
  ).slice(0, 8);

  const addSkill = (skill) => {
    if (skill && !currentSkills.includes(skill) && currentSkills.length < 15) {
      onChange({ skills: [...currentSkills, skill] });
      setSkillInput('');
    }
  };

  const removeSkill = (skill) => {
    onChange({ skills: currentSkills.filter(s => s !== skill) });
  };

  return (
    <div data-testid="onboarding-step-3">
      <h2 className="text-2xl font-bold text-slate-800 mb-2">Skills & Strengths</h2>
      <p className="text-slate-600 mb-1">Add your key skills to match with the right jobs</p>
      <p className="text-sm text-blue-600 font-medium mb-6">Profiles with skills get 3x more views</p>
      
      <div className="space-y-5">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Skills ({currentSkills.length}/15)
          </label>
          <div className="relative">
            <Input
              value={skillInput}
              onChange={(e) => setSkillInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); addSkill(skillInput.trim()); } }}
              placeholder="Type a skill and press Enter"
              className="h-12"
              data-testid="skill-input"
            />
          </div>
          {skillInput && filteredSuggestions.length > 0 && (
            <div className="mt-1 bg-white border border-slate-200 rounded-lg shadow-lg max-h-40 overflow-y-auto">
              {filteredSuggestions.map((s) => (
                <button key={s} onClick={() => addSkill(s)} className="w-full text-left px-3 py-2 hover:bg-blue-50 text-sm text-slate-700">
                  {s}
                </button>
              ))}
            </div>
          )}
          {currentSkills.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-3">
              {currentSkills.map((skill) => (
                <span key={skill} className="inline-flex items-center gap-1 bg-blue-100 text-blue-800 px-3 py-1.5 rounded-full text-sm font-medium">
                  {skill}
                  <button onClick={() => removeSkill(skill)} className="hover:text-red-600"><X className="w-3.5 h-3.5" /></button>
                </span>
              ))}
            </div>
          )}
          {currentSkills.length === 0 && !skillInput && (
            <div className="mt-3">
              <p className="text-xs text-slate-500 mb-2">Popular skills:</p>
              <div className="flex flex-wrap gap-1.5">
                {POPULAR_SKILLS.slice(0, 12).map((s) => (
                  <button key={s} onClick={() => addSkill(s)} className="px-2.5 py-1 rounded-full text-xs bg-slate-100 text-slate-600 hover:bg-blue-100 hover:text-blue-700 transition-colors">
                    + {s}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Seniority Level</label>
          <div className="grid grid-cols-3 gap-2">
            {SENIORITY_LEVELS.map((level) => (
              <button
                key={level}
                onClick={() => onChange({ seniority_level: level })}
                className={`px-3 py-2.5 rounded-lg text-sm font-medium border transition-all ${
                  data.seniority_level === level
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white text-slate-700 border-slate-200 hover:border-blue-300'
                }`}
              >
                {level}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Key Strengths (select up to 5)</label>
          <div className="flex flex-wrap gap-2">
            {STRENGTHS.map((strength) => {
              const selected = (data.key_strengths || []).includes(strength);
              const atLimit = (data.key_strengths || []).length >= 5 && !selected;
              return (
                <button
                  key={strength}
                  disabled={atLimit}
                  onClick={() => {
                    const current = data.key_strengths || [];
                    const updated = selected ? current.filter(s => s !== strength) : [...current, strength];
                    onChange({ key_strengths: updated });
                  }}
                  className={`px-3 py-1.5 rounded-full text-sm font-medium border transition-all ${
                    selected
                      ? 'bg-purple-600 text-white border-purple-600'
                      : atLimit
                        ? 'bg-slate-50 text-slate-300 border-slate-100 cursor-not-allowed'
                        : 'bg-white text-slate-700 border-slate-200 hover:border-purple-300'
                  }`}
                >
                  {strength}
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

// Step 4: CV Upload
const CVUploadStep = ({ data, onChange }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const fileInputRef = useRef(null);

  const handleCVUpload = async (file) => {
    if (!file) return;
    setUploading(true);
    setUploadError('');
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await axios.post(`${API}/uploads/cv`, formData, getUploadHeaders());
      onChange({ resume_url: response.data.url });
    } catch (err) {
      setUploadError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div data-testid="onboarding-step-4">
      <h2 className="text-2xl font-bold text-slate-800 mb-2">Upload Your CV</h2>
      <p className="text-slate-600 mb-1">Your CV is essential for getting noticed by recruiters</p>
      <p className="text-sm text-red-500 font-medium mb-6">Recruiters can't contact you without a CV</p>

      <div className="space-y-5">
        <div>
          <div
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
              data.resume_url ? 'border-green-400 bg-green-50' : 'border-slate-300 hover:border-blue-400 hover:bg-slate-50'
            }`}
            data-testid="cv-drop-zone"
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.doc,.docx"
              onChange={(e) => handleCVUpload(e.target.files[0])}
              className="hidden"
            />
            {uploading ? (
              <div className="space-y-2">
                <Loader2 className="w-10 h-10 mx-auto text-blue-500 animate-spin" />
                <p className="text-slate-600">Uploading...</p>
              </div>
            ) : data.resume_url ? (
              <div className="space-y-2">
                <Check className="w-10 h-10 mx-auto text-green-500" />
                <p className="font-medium text-green-700">CV uploaded successfully</p>
                <button
                  onClick={(e) => { e.stopPropagation(); onChange({ resume_url: '' }); }}
                  className="text-sm text-slate-500 hover:text-red-500"
                >
                  Replace CV
                </button>
              </div>
            ) : (
              <div className="space-y-2">
                <Upload className="w-10 h-10 mx-auto text-slate-400" />
                <p className="font-medium text-slate-700">Click to upload your CV</p>
                <p className="text-sm text-slate-500">PDF, DOC, or DOCX (max 10MB)</p>
              </div>
            )}
          </div>
          {uploadError && <p className="text-sm text-red-600 mt-2">{uploadError}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">LinkedIn URL (optional)</label>
          <div className="relative">
            <Link2 className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <Input
              value={data.linkedin_url || ''}
              onChange={(e) => onChange({ linkedin_url: e.target.value })}
              placeholder="https://linkedin.com/in/your-profile"
              className="pl-10 h-12"
              data-testid="linkedin-input"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Desired Salary Range (optional)</label>
          <Input
            value={data.desired_salary_range || ''}
            onChange={(e) => onChange({ desired_salary_range: e.target.value })}
            placeholder="e.g. R30,000 - R50,000 per month"
            className="h-12"
            data-testid="salary-input"
          />
        </div>
      </div>
    </div>
  );
};

// Step 5: Experience & Availability
const ExperienceStep = ({ data, onChange }) => {
  const workExperience = data.work_experience || [];

  const addExperience = () => {
    onChange({
      work_experience: [...workExperience, { company: '', position: '', start_date: '', end_date: '', current: false, description: '', location: '' }]
    });
  };

  const updateExperience = (index, field, value) => {
    const updated = [...workExperience];
    updated[index] = { ...updated[index], [field]: value };
    if (field === 'current' && value) updated[index].end_date = '';
    onChange({ work_experience: updated });
  };

  const removeExperience = (index) => {
    onChange({ work_experience: workExperience.filter((_, i) => i !== index) });
  };

  return (
    <div data-testid="onboarding-step-5">
      <h2 className="text-2xl font-bold text-slate-800 mb-2">Experience & Availability</h2>
      <p className="text-slate-600 mb-6">Add your work history and let recruiters know your availability</p>

      <div className="space-y-5">
        {/* Work experience entries */}
        {workExperience.map((exp, i) => (
          <Card key={i} className="border border-slate-200">
            <CardContent className="p-4 space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-slate-500">Position {i + 1}</span>
                <button onClick={() => removeExperience(i)} className="text-slate-400 hover:text-red-500"><Trash2 className="w-4 h-4" /></button>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <Input value={exp.position} onChange={(e) => updateExperience(i, 'position', e.target.value)} placeholder="Job Title" className="h-10" />
                <Input value={exp.company} onChange={(e) => updateExperience(i, 'company', e.target.value)} placeholder="Company" className="h-10" />
                <Input value={exp.location} onChange={(e) => updateExperience(i, 'location', e.target.value)} placeholder="Location" className="h-10" />
                <div className="flex items-center gap-2">
                  <input type="checkbox" checked={exp.current} onChange={(e) => updateExperience(i, 'current', e.target.checked)} id={`current-${i}`} className="rounded" />
                  <label htmlFor={`current-${i}`} className="text-sm text-slate-600">Currently working here</label>
                </div>
                <Input type="date" value={exp.start_date} onChange={(e) => updateExperience(i, 'start_date', e.target.value)} placeholder="Start Date" className="h-10" />
                {!exp.current && <Input type="date" value={exp.end_date} onChange={(e) => updateExperience(i, 'end_date', e.target.value)} placeholder="End Date" className="h-10" />}
              </div>
            </CardContent>
          </Card>
        ))}

        <Button variant="outline" onClick={addExperience} className="w-full border-dashed" data-testid="add-experience-btn">
          <Plus className="w-4 h-4 mr-2" /> Add Work Experience
        </Button>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Availability</label>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {['Immediately', '2 weeks', '1 month', '2 months', '3 months', 'Not looking'].map((opt) => (
              <button
                key={opt}
                onClick={() => onChange({ availability: opt })}
                className={`px-3 py-2.5 rounded-lg text-sm font-medium border transition-all ${
                  data.availability === opt ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-slate-700 border-slate-200 hover:border-blue-300'
                }`}
              >
                {opt}
              </button>
            ))}
          </div>
        </div>

        {data.availability && data.availability !== 'Immediately' && data.availability !== 'Not looking' && (
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Notice Period</label>
            <Input
              value={data.notice_period || ''}
              onChange={(e) => onChange({ notice_period: e.target.value })}
              placeholder="e.g. 30 days"
              className="h-12"
            />
          </div>
        )}
      </div>
    </div>
  );
};

// Step 6: Profile Boost
const ProfileBoostStep = ({ data, onChange }) => {
  const [uploading, setUploading] = useState(false);
  const [docUploading, setDocUploading] = useState(false);
  const photoRef = useRef(null);
  const docRef = useRef(null);

  const handlePhotoUpload = async (file) => {
    if (!file) return;
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await axios.post(`${API}/uploads/profile-picture`, formData, getUploadHeaders());
      onChange({ profile_picture_url: response.data.url });
    } catch { /* ignore */ }
    setUploading(false);
  };

  const handleDocUpload = async (file) => {
    if (!file) return;
    const docs = data.additional_documents || [];
    if (docs.length >= 10) return;
    setDocUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await axios.post(`${API}/uploads/document`, formData, getUploadHeaders());
      onChange({ additional_documents: [...docs, { name: file.name, url: response.data.url }] });
    } catch { /* ignore */ }
    setDocUploading(false);
  };

  const removeDoc = (index) => {
    const docs = [...(data.additional_documents || [])];
    docs.splice(index, 1);
    onChange({ additional_documents: docs });
  };

  return (
    <div data-testid="onboarding-step-6">
      <h2 className="text-2xl font-bold text-slate-800 mb-2">Profile Boost</h2>
      <p className="text-slate-600 mb-6">Final touches to make your profile stand out</p>

      <div className="space-y-5">
        {/* Profile Photo */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Profile Photo (optional)</label>
          <div className="flex items-center gap-4">
            <div
              onClick={() => photoRef.current?.click()}
              className="w-20 h-20 rounded-full bg-slate-100 border-2 border-dashed border-slate-300 flex items-center justify-center cursor-pointer hover:border-blue-400 transition-colors overflow-hidden"
              data-testid="photo-upload"
            >
              <input ref={photoRef} type="file" accept=".jpg,.jpeg,.png,.webp" onChange={(e) => handlePhotoUpload(e.target.files[0])} className="hidden" />
              {uploading ? (
                <Loader2 className="w-6 h-6 text-blue-500 animate-spin" />
              ) : data.profile_picture_url ? (
                <img src={`${BACKEND_URL}${data.profile_picture_url}`} alt="Profile" className="w-full h-full object-cover" />
              ) : (
                <User className="w-8 h-8 text-slate-400" />
              )}
            </div>
            <p className="text-sm text-slate-500">JPG, PNG, or WebP (max 5MB)</p>
          </div>
        </div>

        {/* Short Intro */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Short Intro ({(data.about_me || '').length}/300)
          </label>
          <textarea
            value={data.about_me || ''}
            onChange={(e) => { if (e.target.value.length <= 300) onChange({ about_me: e.target.value }); }}
            placeholder="Tell recruiters what makes you great in a few sentences..."
            rows={3}
            className="w-full px-3 py-2.5 border border-slate-200 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            data-testid="intro-textarea"
          />
        </div>

        {/* Open to opportunities */}
        <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
          <div>
            <p className="font-medium text-slate-800">Open to opportunities</p>
            <p className="text-sm text-slate-500">Let recruiters know you're available</p>
          </div>
          <button
            onClick={() => onChange({ open_to_opportunities: !data.open_to_opportunities })}
            className={`relative w-12 h-6 rounded-full transition-colors ${data.open_to_opportunities !== false ? 'bg-blue-600' : 'bg-slate-300'}`}
            data-testid="open-opportunities-toggle"
          >
            <span className={`absolute top-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${data.open_to_opportunities !== false ? 'translate-x-6' : 'translate-x-0.5'}`} />
          </button>
        </div>

        {/* Additional Documents */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Additional Documents ({(data.additional_documents || []).length}/10)
          </label>
          <p className="text-xs text-slate-500 mb-3">Certifications, certificates, awards, etc.</p>
          {(data.additional_documents || []).map((doc, i) => (
            <div key={i} className="flex items-center justify-between p-2 bg-slate-50 rounded mb-2">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-blue-500" />
                <span className="text-sm text-slate-700 truncate max-w-[200px]">{doc.name}</span>
              </div>
              <button onClick={() => removeDoc(i)} className="text-slate-400 hover:text-red-500"><Trash2 className="w-4 h-4" /></button>
            </div>
          ))}
          {(data.additional_documents || []).length < 10 && (
            <Button variant="outline" size="sm" onClick={() => docRef.current?.click()} disabled={docUploading} className="border-dashed">
              <input ref={docRef} type="file" accept=".pdf,.doc,.docx,.jpg,.jpeg,.png" onChange={(e) => handleDocUpload(e.target.files[0])} className="hidden" />
              {docUploading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Plus className="w-4 h-4 mr-2" />}
              Add Document
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

// Confetti effect
const Confetti = () => {
  const colors = ['#3B82F6', '#8B5CF6', '#10B981', '#F59E0B', '#EF4444', '#EC4899'];
  return (
    <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden">
      {Array.from({ length: 60 }).map((_, i) => (
        <div
          key={i}
          className="absolute animate-bounce"
          style={{
            left: `${Math.random() * 100}%`,
            top: `-${Math.random() * 20}%`,
            width: `${6 + Math.random() * 8}px`,
            height: `${6 + Math.random() * 8}px`,
            backgroundColor: colors[i % colors.length],
            borderRadius: Math.random() > 0.5 ? '50%' : '2px',
            animation: `confetti-fall ${2 + Math.random() * 3}s ease-in forwards`,
            animationDelay: `${Math.random() * 1.5}s`,
          }}
        />
      ))}
      <style>{`
        @keyframes confetti-fall {
          0% { transform: translateY(0) rotate(0deg); opacity: 1; }
          100% { transform: translateY(100vh) rotate(720deg); opacity: 0; }
        }
      `}</style>
    </div>
  );
};

// Completion screen
const CompletionScreen = ({ onFinish }) => (
  <div className="text-center py-8 max-w-lg mx-auto" data-testid="onboarding-complete">
    <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-green-400 to-emerald-600 rounded-2xl flex items-center justify-center shadow-lg">
      <Check className="w-10 h-10 text-white" />
    </div>
    <h1 className="text-3xl font-bold text-slate-800 mb-3">You're all set!</h1>
    <p className="text-lg text-slate-600 mb-8">Your profile is now visible to recruiters. Start exploring jobs!</p>
    <div className="grid grid-cols-3 gap-3 mb-8">
      {[
        { icon: Eye, label: 'Visible to Recruiters', color: 'text-blue-600 bg-blue-50' },
        { icon: Zap, label: 'Profile Complete', color: 'text-green-600 bg-green-50' },
        { icon: Award, label: 'Badge Earned', color: 'text-purple-600 bg-purple-50' },
      ].map((item) => (
        <div key={item.label} className={`p-3 rounded-xl ${item.color}`}>
          <item.icon className="w-6 h-6 mx-auto mb-1" />
          <p className="text-xs font-medium">{item.label}</p>
        </div>
      ))}
    </div>
    <Button onClick={onFinish} className="w-full bg-blue-600 hover:bg-blue-700 h-12 text-lg font-semibold" data-testid="finish-onboarding-btn">
      Explore Jobs <ChevronRight className="w-5 h-5 ml-2" />
    </Button>
  </div>
);

// Badge popup
const BadgePopup = ({ badge, onClose }) => {
  const badgeInfo = {
    profile_started: { title: 'Profile Started', icon: Star, color: 'from-blue-500 to-blue-600' },
    almost_there: { title: 'Almost There', icon: Zap, color: 'from-purple-500 to-purple-600' },
    profile_complete: { title: 'Profile Complete', icon: Award, color: 'from-green-500 to-emerald-600' },
  };
  const info = badgeInfo[badge];
  if (!info) return null;
  const Icon = info.icon;

  return (
    <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-white rounded-2xl p-6 text-center shadow-2xl max-w-xs animate-in zoom-in-50" onClick={e => e.stopPropagation()}>
        <div className={`w-16 h-16 mx-auto mb-4 bg-gradient-to-br ${info.color} rounded-xl flex items-center justify-center`}>
          <Icon className="w-8 h-8 text-white" />
        </div>
        <h3 className="text-lg font-bold text-slate-800 mb-1">Badge Unlocked!</h3>
        <p className="text-slate-600 mb-4">{info.title}</p>
        <Button onClick={onClose} size="sm" className="bg-blue-600 hover:bg-blue-700">Continue</Button>
      </div>
    </div>
  );
};

// Main Onboarding Wizard
const JobSeekerOnboarding = ({ user, onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);
  const [formData, setFormData] = useState({
    location: user?.location || '',
    desired_job_title: '',
    years_of_experience: '',
    industry_preference: '',
    employment_type_preference: [],
    skills: user?.skills || [],
    seniority_level: '',
    key_strengths: [],
    resume_url: user?.resume_url || '',
    linkedin_url: '',
    desired_salary_range: user?.desired_salary_range || '',
    work_experience: user?.work_experience || [],
    availability: '',
    notice_period: '',
    profile_picture_url: user?.profile_picture_url || '',
    about_me: user?.about_me || '',
    open_to_opportunities: true,
    additional_documents: [],
  });
  const [saving, setSaving] = useState(false);
  const [showBadge, setShowBadge] = useState(null);
  const [showConfetti, setShowConfetti] = useState(false);
  const [completed, setCompleted] = useState(false);
  const navigate = useNavigate();

  // Load existing onboarding progress
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

  const updateFormData = (updates) => {
    setFormData(prev => ({ ...prev, ...updates }));
  };

  const saveStep = async (step) => {
    setSaving(true);
    try {
      const response = await axios.put(`${API}/onboarding/step/${step}`, formData, getAuthHeaders());
      setProgress(response.data.progress);
      
      // Check for new badges
      const badges = response.data.badges || [];
      const badgeForStep = { 2: 'profile_started', 5: 'almost_there', 6: 'profile_complete' };
      const expectedBadge = badgeForStep[step];
      if (expectedBadge && badges.includes(expectedBadge)) {
        setShowBadge(expectedBadge);
      }
      return true;
    } catch (err) {
      console.error('Error saving step:', err);
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
      // Update user in localStorage
      const savedUser = JSON.parse(localStorage.getItem('user') || '{}');
      savedUser.onboarding_completed = true;
      savedUser.onboarding_progress = 100;
      Object.assign(savedUser, formData);
      localStorage.setItem('user', JSON.stringify(savedUser));
      return;
    }

    setCurrentStep(currentStep + 1);
  };

  const handleBack = () => {
    if (currentStep > 0) setCurrentStep(currentStep - 1);
  };

  const handleSkip = async () => {
    try {
      await axios.post(`${API}/onboarding/skip`, {}, getAuthHeaders());
      const savedUser = JSON.parse(localStorage.getItem('user') || '{}');
      savedUser.onboarding_completed = true;
      localStorage.setItem('user', JSON.stringify(savedUser));
      if (onComplete) onComplete();
      else navigate('/jobs');
    } catch { navigate('/jobs'); }
  };

  const handleFinish = () => {
    if (onComplete) onComplete();
    else navigate('/jobs');
  };

  const renderStep = () => {
    switch (currentStep) {
      case 0: return <WelcomeStep userName={user?.first_name} onNext={handleNext} onSkip={handleSkip} />;
      case 1: return <LocationStep data={formData} onChange={updateFormData} />;
      case 2: return <ProfessionalStep data={formData} onChange={updateFormData} />;
      case 3: return <SkillsStep data={formData} onChange={updateFormData} />;
      case 4: return <CVUploadStep data={formData} onChange={updateFormData} />;
      case 5: return <ExperienceStep data={formData} onChange={updateFormData} />;
      case 6: return <ProfileBoostStep data={formData} onChange={updateFormData} />;
      default: return null;
    }
  };

  const STEP_MESSAGES = {
    1: 'Great start!',
    2: null,
    3: null,
    4: null,
    5: null,
    6: 'Your profile is now visible to recruiters!',
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
      {showConfetti && <Confetti />}
      {showBadge && <BadgePopup badge={showBadge} onClose={() => setShowBadge(null)} />}

      <div className="max-w-2xl mx-auto px-4 py-8">
        {/* Logo */}
        <div className="flex items-center justify-center mb-6">
          <div className="bg-gradient-to-br from-blue-600 to-purple-600 p-2 rounded-lg mr-2">
            <Rocket className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Job Rocket
          </span>
        </div>

        {/* Progress bar - show for steps 1-6 */}
        {currentStep > 0 && !completed && (
          <ProgressBar progress={progress} currentStep={currentStep} />
        )}

        {/* Card */}
        <Card className="bg-white/90 backdrop-blur-sm shadow-xl border-0">
          <CardContent className="p-6 sm:p-8">
            {completed ? (
              <CompletionScreen onFinish={handleFinish} />
            ) : (
              <>
                {renderStep()}

                {/* Navigation buttons (not for step 0 or completion) */}
                {currentStep > 0 && (
                  <div className="flex items-center justify-between mt-8 pt-6 border-t border-slate-100">
                    <Button variant="ghost" onClick={handleBack} disabled={saving} data-testid="onboarding-back-btn">
                      <ChevronLeft className="w-4 h-4 mr-1" /> Back
                    </Button>

                    <div className="flex items-center gap-3">
                      {currentStep < 6 && (
                        <button onClick={() => setCurrentStep(currentStep + 1)} className="text-sm text-slate-400 hover:text-slate-600" data-testid="skip-step-btn">
                          Skip
                        </button>
                      )}
                      <Button onClick={handleNext} disabled={saving} className="bg-blue-600 hover:bg-blue-700 px-6" data-testid="onboarding-next-btn">
                        {saving ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : currentStep === 6 ? (
                          <>Complete Profile <Check className="w-4 h-4 ml-2" /></>
                        ) : (
                          <>Continue <ChevronRight className="w-4 h-4 ml-2" /></>
                        )}
                      </Button>
                    </div>
                  </div>
                )}

                {/* Motivational message */}
                {currentStep > 0 && STEP_MESSAGES[currentStep] && (
                  <p className="text-center text-sm text-blue-600 font-medium mt-4">
                    {STEP_MESSAGES[currentStep]}
                  </p>
                )}
              </>
            )}
          </CardContent>
        </Card>

        {/* Skip link for steps > 0 */}
        {currentStep > 0 && !completed && (
          <div className="text-center mt-4">
            <button onClick={handleSkip} className="text-sm text-slate-400 hover:text-slate-600 transition-colors" data-testid="skip-all-btn">
              Skip onboarding entirely
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default JobSeekerOnboarding;
