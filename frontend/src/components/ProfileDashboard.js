import React, { useState, useEffect, useRef } from 'react';
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Textarea } from "./ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Label } from "./ui/label";
import TrophyProgress from './TrophyProgress';
import MyApplications from './MyApplications';
import { 
  User, 
  Briefcase, 
  GraduationCap, 
  Award, 
  Video, 
  Mail, 
  DollarSign,
  Plus,
  Upload,
  Save,
  Camera,
  Rocket,
  Star,
  MapPin,
  Calendar,
  Building2,
  Target,
  Zap,
  FileText,
  Bell,
  Trash2,
  Pencil,
  Loader2
} from "lucide-react";
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ProfileDashboard = ({ user, onUpdateUser }) => {
  const [profile, setProfile] = useState(user);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [progress, setProgress] = useState(user.profile_progress || {});
  
  // Form states
  const [profileForm, setProfileForm] = useState({
    first_name: user.first_name || '',
    last_name: user.last_name || '',
    about_me: user.about_me || '',
    phone: user.phone || '',
    location: user.location || '',
    current_salary_range: user.current_salary_range || '',
    desired_salary_range: user.desired_salary_range || '',
    skills: user.skills || []
  });

  const [newSkill, setNewSkill] = useState('');
  const [workExperience, setWorkExperience] = useState({
    company: '',
    position: '',
    start_date: '',
    end_date: '',
    current: false,
    description: '',
    location: ''
  });

  const [education, setEducation] = useState({
    institution: '',
    degree: '',
    field_of_study: '',
    level: 'Bachelors',
    start_date: '',
    end_date: '',
    current: false,
    grade: ''
  });

  const [achievement, setAchievement] = useState({
    title: '',
    description: '',
    date_achieved: '',
    issuer: '',
    credential_url: ''
  });

  // Job Alert state
  const [jobAlerts, setJobAlerts] = useState([]);
  const [newJobAlert, setNewJobAlert] = useState({
    job_title: '',
    location: '',
    employment_types: [],
    work_types: [],
    salary_range: ''
  });

  // Profile picture upload state
  const profilePictureRef = useRef(null);
  const [uploadingPicture, setUploadingPicture] = useState(false);

  // Video upload state
  const videoRef = useRef(null);
  const [uploadingVideo, setUploadingVideo] = useState(false);

  // Media/Portfolio links state
  const [mediaForm, setMediaForm] = useState({
    linkedin_url: user.linkedin_url || '',
    portfolio_url: user.portfolio_url || ''
  });

  const toggleEmploymentType = (type) => {
    setNewJobAlert(prev => ({
      ...prev,
      employment_types: prev.employment_types.includes(type)
        ? prev.employment_types.filter(t => t !== type)
        : [...prev.employment_types, type]
    }));
  };

  const toggleWorkType = (type) => {
    setNewJobAlert(prev => ({
      ...prev,
      work_types: prev.work_types.includes(type)
        ? prev.work_types.filter(t => t !== type)
        : [...prev.work_types, type]
    }));
  };

  const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    return {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    };
  };

  const getUploadHeaders = () => {
    const token = localStorage.getItem('token');
    return {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    };
  };

  const handleProfilePictureUpload = async (file) => {
    if (!file) return;
    setUploadingPicture(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await axios.post(`${API}/uploads/profile-picture`, formData, getUploadHeaders());
      await fetchCurrentUser();
    } catch (error) {
      console.error('Error uploading profile picture:', error);
    } finally {
      setUploadingPicture(false);
    }
  };

  const handleVideoUpload = async (file) => {
    if (!file) return;
    // Validate file size (50MB max)
    if (file.size > 50 * 1024 * 1024) {
      alert('Video file must be less than 50MB');
      return;
    }
    setUploadingVideo(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await axios.post(`${API}/uploads/video`, formData, getUploadHeaders());
      await fetchCurrentUser();
    } catch (error) {
      console.error('Error uploading video:', error);
    } finally {
      setUploadingVideo(false);
    }
  };

  const handleMediaSubmit = async (e) => {
    e.preventDefault();
    await updateProfile(mediaForm);
  };

  const fetchCurrentUser = async () => {
    try {
      const response = await axios.get(`${API}/auth/me`, getAuthHeaders());
      setProfile(response.data);
      setProgress(response.data.profile_progress || {});
      // Update mediaForm with fetched data
      setMediaForm({
        linkedin_url: response.data.linkedin_url || '',
        portfolio_url: response.data.portfolio_url || ''
      });
      onUpdateUser(response.data);
    } catch (error) {
      console.error('Error fetching user data:', error);
    }
  };

  const updateProfile = async (updates) => {
    try {
      setLoading(true);
      await axios.put(`${API}/profile`, updates, getAuthHeaders());
      await fetchCurrentUser();
    } catch (error) {
      console.error('Error updating profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    await updateProfile(profileForm);
  };

  const addSkill = () => {
    if (newSkill.trim() && !profileForm.skills.includes(newSkill.trim())) {
      const updatedSkills = [...profileForm.skills, newSkill.trim()];
      setProfileForm(prev => ({ ...prev, skills: updatedSkills }));
      updateProfile({ skills: updatedSkills });
      setNewSkill('');
    }
  };

  const removeSkill = (skillToRemove) => {
    const updatedSkills = profileForm.skills.filter(skill => skill !== skillToRemove);
    setProfileForm(prev => ({ ...prev, skills: updatedSkills }));
    updateProfile({ skills: updatedSkills });
  };

  const addWorkExperience = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/profile/work-experience`, {
        ...workExperience,
        start_date: new Date(workExperience.start_date).toISOString(),
        end_date: workExperience.end_date ? new Date(workExperience.end_date).toISOString() : null
      }, getAuthHeaders());
      
      setWorkExperience({
        company: '',
        position: '',
        start_date: '',
        end_date: '',
        current: false,
        description: '',
        location: ''
      });
      await fetchCurrentUser();
    } catch (error) {
      console.error('Error adding work experience:', error);
    }
  };

  const addEducation = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/profile/education`, {
        ...education,
        start_date: new Date(education.start_date).toISOString(),
        end_date: education.end_date ? new Date(education.end_date).toISOString() : null
      }, getAuthHeaders());
      
      setEducation({
        institution: '',
        degree: '',
        field_of_study: '',
        level: 'Bachelors',
        start_date: '',
        end_date: '',
        current: false,
        grade: ''
      });
      await fetchCurrentUser();
    } catch (error) {
      console.error('Error adding education:', error);
    }
  };

  const addAchievement = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/profile/achievement`, {
        ...achievement,
        date_achieved: new Date(achievement.date_achieved).toISOString()
      }, getAuthHeaders());
      
      setAchievement({
        title: '',
        description: '',
        date_achieved: '',
        issuer: '',
        credential_url: ''
      });
      await fetchCurrentUser();
    } catch (error) {
      console.error('Error adding achievement:', error);
    }
  };

  // Delete functions
  const deleteWorkExperience = async (experienceId) => {
    if (!window.confirm('Are you sure you want to delete this work experience?')) return;
    try {
      await axios.delete(`${API}/profile/work-experience/${experienceId}`, getAuthHeaders());
      await fetchCurrentUser();
    } catch (error) {
      console.error('Error deleting work experience:', error);
    }
  };

  const deleteEducation = async (educationId) => {
    if (!window.confirm('Are you sure you want to delete this education entry?')) return;
    try {
      await axios.delete(`${API}/profile/education/${educationId}`, getAuthHeaders());
      await fetchCurrentUser();
    } catch (error) {
      console.error('Error deleting education:', error);
    }
  };

  const deleteAchievement = async (achievementId) => {
    if (!window.confirm('Are you sure you want to delete this achievement?')) return;
    try {
      await axios.delete(`${API}/profile/achievement/${achievementId}`, getAuthHeaders());
      await fetchCurrentUser();
    } catch (error) {
      console.error('Error deleting achievement:', error);
    }
  };

  // Edit functions - populate form and scroll to it
  const editWorkExperience = (exp) => {
    setWorkExperience({
      id: exp.id,
      company: exp.company || '',
      position: exp.position || '',
      start_date: exp.start_date ? exp.start_date.split('T')[0] : '',
      end_date: exp.end_date ? exp.end_date.split('T')[0] : '',
      current: exp.current || false,
      description: exp.description || '',
      location: exp.location || ''
    });
    setActiveTab('experience');
    // Scroll to form
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const editEducation = (edu) => {
    setEducation({
      id: edu.id,
      institution: edu.institution || '',
      degree: edu.degree || '',
      field_of_study: edu.field_of_study || '',
      level: edu.level || 'Bachelors',
      start_date: edu.start_date ? edu.start_date.split('T')[0] : '',
      end_date: edu.end_date ? edu.end_date.split('T')[0] : '',
      current: edu.current || false,
      grade: edu.grade || ''
    });
    setActiveTab('education');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const editAchievement = (ach) => {
    setAchievement({
      id: ach.id,
      title: ach.title || '',
      description: ach.description || '',
      date_achieved: ach.date_achieved ? ach.date_achieved.split('T')[0] : '',
      issuer: ach.issuer || '',
      credential_url: ach.credential_url || ''
    });
    setActiveTab('achievements');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Update functions (for editing existing entries)
  const updateWorkExperience = async (e) => {
    e.preventDefault();
    if (!workExperience.id) {
      // No id means it's a new entry, use add
      return addWorkExperience(e);
    }
    try {
      await axios.put(`${API}/profile/work-experience/${workExperience.id}`, {
        ...workExperience,
        start_date: new Date(workExperience.start_date).toISOString(),
        end_date: workExperience.end_date ? new Date(workExperience.end_date).toISOString() : null
      }, getAuthHeaders());
      
      setWorkExperience({
        company: '',
        position: '',
        start_date: '',
        end_date: '',
        current: false,
        description: '',
        location: ''
      });
      await fetchCurrentUser();
    } catch (error) {
      console.error('Error updating work experience:', error);
    }
  };

  const updateEducation = async (e) => {
    e.preventDefault();
    if (!education.id) {
      return addEducation(e);
    }
    try {
      await axios.put(`${API}/profile/education/${education.id}`, {
        ...education,
        start_date: new Date(education.start_date).toISOString(),
        end_date: education.end_date ? new Date(education.end_date).toISOString() : null
      }, getAuthHeaders());
      
      setEducation({
        institution: '',
        degree: '',
        field_of_study: '',
        level: 'Bachelors',
        start_date: '',
        end_date: '',
        current: false,
        grade: ''
      });
      await fetchCurrentUser();
    } catch (error) {
      console.error('Error updating education:', error);
    }
  };

  const updateAchievement = async (e) => {
    e.preventDefault();
    if (!achievement.id) {
      return addAchievement(e);
    }
    try {
      await axios.put(`${API}/profile/achievement/${achievement.id}`, {
        ...achievement,
        date_achieved: new Date(achievement.date_achieved).toISOString()
      }, getAuthHeaders());
      
      setAchievement({
        title: '',
        description: '',
        date_achieved: '',
        issuer: '',
        credential_url: ''
      });
      await fetchCurrentUser();
    } catch (error) {
      console.error('Error updating achievement:', error);
    }
  };

  const cancelEdit = (type) => {
    if (type === 'experience') {
      setWorkExperience({
        company: '',
        position: '',
        start_date: '',
        end_date: '',
        current: false,
        description: '',
        location: ''
      });
    } else if (type === 'education') {
      setEducation({
        institution: '',
        degree: '',
        field_of_study: '',
        level: 'Bachelors',
        start_date: '',
        end_date: '',
        current: false,
        grade: ''
      });
    } else if (type === 'achievement') {
      setAchievement({
        title: '',
        description: '',
        date_achieved: '',
        issuer: '',
        credential_url: ''
      });
    }
  };

  const setupEmailAlerts = async () => {
    try {
      await axios.post(`${API}/profile/email-alerts`, {}, getAuthHeaders());
      await fetchCurrentUser();
    } catch (error) {
      console.error('Error setting up email alerts:', error);
    }
  };

  // Job Alerts functions
  const fetchJobAlerts = async () => {
    try {
      const response = await axios.get(`${API}/profile/job-alerts`, getAuthHeaders());
      setJobAlerts(response.data);
    } catch (error) {
      console.error('Error fetching job alerts:', error);
    }
  };

  const addJobAlert = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/profile/job-alerts`, newJobAlert, getAuthHeaders());
      setNewJobAlert({
        job_title: '',
        location: '',
        employment_types: [],
        work_types: [],
        salary_range: ''
      });
      await fetchJobAlerts();
      await fetchCurrentUser();
    } catch (error) {
      console.error('Error adding job alert:', error);
    }
  };

  const deleteJobAlert = async (alertId) => {
    try {
      await axios.delete(`${API}/profile/job-alerts/${alertId}`, getAuthHeaders());
      await fetchJobAlerts();
    } catch (error) {
      console.error('Error deleting job alert:', error);
    }
  };

  const onProfileComplete = () => {
    // Trigger completion celebration
    console.log('Profile completed! 🚀');
  };

  useEffect(() => {
    fetchCurrentUser();
    fetchJobAlerts();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 relative">
      {/* Background tech grid pattern */}
      <div className="absolute inset-0 opacity-5 tech-grid"></div>
      
      <div className="max-w-7xl mx-auto px-6 lg:px-8 py-8 relative z-10">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-slate-800 mb-2">
                Welcome back, {profile.first_name}! 👋
              </h1>
              <p className="text-slate-600 text-lg">
                Complete your profile to unlock all Job Rocket features
              </p>
            </div>
            <div className="hidden lg:block">
              <TrophyProgress 
                progress={progress} 
                onComplete={onProfileComplete}
                userRole="job_seeker"
              />
            </div>
          </div>
        </div>

        {/* Mobile Trophy Progress */}
        <div className="lg:hidden mb-8">
          <TrophyProgress 
            progress={progress} 
            onComplete={onProfileComplete}
            userRole="job_seeker"
          />
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar - Profile Overview */}
          <div className="lg:col-span-1">
            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
              <CardContent className="p-6">
                <div className="text-center mb-6">
                  <div className="relative inline-block mb-4">
                    <div className="w-24 h-24 bg-gradient-to-br from-blue-100 to-slate-200 rounded-full flex items-center justify-center overflow-hidden">
                      {uploadingPicture ? (
                        <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
                      ) : profile.profile_picture_url ? (
                        <img 
                          src={profile.profile_picture_url.startsWith('http') ? profile.profile_picture_url : `${BACKEND_URL}${profile.profile_picture_url}`}
                          alt="Profile" 
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <User className="w-12 h-12 text-slate-400" />
                      )}
                    </div>
                    <input
                      ref={profilePictureRef}
                      type="file"
                      accept=".jpg,.jpeg,.png,.webp"
                      onChange={(e) => handleProfilePictureUpload(e.target.files[0])}
                      className="hidden"
                      data-testid="profile-picture-input"
                    />
                    <Button
                      size="sm"
                      className="absolute -bottom-2 -right-2 w-8 h-8 rounded-full p-0"
                      onClick={() => profilePictureRef.current?.click()}
                      disabled={uploadingPicture}
                      data-testid="profile-picture-btn"
                    >
                      <Camera className="w-4 h-4" />
                    </Button>
                  </div>
                  <h3 className="font-bold text-slate-800 text-lg">
                    {profile.first_name} {profile.last_name}
                  </h3>
                  <p className="text-slate-600 text-sm">{profile.email}</p>
                  {profile.location && (
                    <div className="flex items-center justify-center space-x-1 text-slate-500 text-sm mt-2">
                      <MapPin className="w-4 h-4" />
                      <span>{profile.location}</span>
                    </div>
                  )}
                </div>

                {/* Quick Stats */}
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-600 text-sm">Profile Score</span>
                    <Badge className="bg-blue-100 text-blue-800">
                      {progress.total_points || 0}/100
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-600 text-sm">Skills</span>
                    <Badge variant="outline">
                      {profile.skills?.length || 0} added
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-600 text-sm">Experience</span>
                    <Badge variant="outline">
                      {profile.work_experience?.length || 0} roles
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Main Profile Tabs */}
          <div className="lg:col-span-3">
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="grid w-full grid-cols-7 bg-white/80 backdrop-blur-sm">
                <TabsTrigger value="overview" className="flex items-center space-x-1">
                  <User className="w-4 h-4" />
                  <span className="hidden sm:inline">Overview</span>
                </TabsTrigger>
                <TabsTrigger value="experience" className="flex items-center space-x-1">
                  <Briefcase className="w-4 h-4" />
                  <span className="hidden sm:inline">Experience</span>
                </TabsTrigger>
                <TabsTrigger value="education" className="flex items-center space-x-1">
                  <GraduationCap className="w-4 h-4" />
                  <span className="hidden sm:inline">Education</span>
                </TabsTrigger>
                <TabsTrigger value="achievements" className="flex items-center space-x-1">
                  <Award className="w-4 h-4" />
                  <span className="hidden sm:inline">Awards</span>
                </TabsTrigger>
                <TabsTrigger value="applications" className="flex items-center space-x-1">
                  <FileText className="w-4 h-4" />
                  <span className="hidden sm:inline">Applications</span>
                </TabsTrigger>
                <TabsTrigger value="media" className="flex items-center space-x-1">
                  <Video className="w-4 h-4" />
                  <span className="hidden sm:inline">Media</span>
                </TabsTrigger>
                <TabsTrigger value="alerts" className="flex items-center space-x-1">
                  <Bell className="w-4 h-4" />
                  <span className="hidden sm:inline">Alerts</span>
                </TabsTrigger>
              </TabsList>

              {/* Overview Tab */}
              <TabsContent value="overview" className="space-y-6 mt-6">
                <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <User className="w-5 h-5 text-blue-600" />
                      <span>Basic Information</span>
                      {!progress.about_me && (
                        <Badge className="bg-yellow-100 text-yellow-800 text-xs">
                          +10 points
                        </Badge>
                      )}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <form onSubmit={handleProfileSubmit} className="space-y-6">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-2">
                          <Label htmlFor="first_name">First Name</Label>
                          <Input
                            id="first_name"
                            value={profileForm.first_name}
                            onChange={(e) => setProfileForm(prev => ({ ...prev, first_name: e.target.value }))}
                            placeholder="Your first name"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="last_name">Last Name</Label>
                          <Input
                            id="last_name"
                            value={profileForm.last_name}
                            onChange={(e) => setProfileForm(prev => ({ ...prev, last_name: e.target.value }))}
                            placeholder="Your last name"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="phone">Phone Number</Label>
                          <Input
                            id="phone"
                            value={profileForm.phone}
                            onChange={(e) => setProfileForm(prev => ({ ...prev, phone: e.target.value }))}
                            placeholder="+27 123 456 7890"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="location">Location</Label>
                          <Input
                            id="location"
                            value={profileForm.location}
                            onChange={(e) => setProfileForm(prev => ({ ...prev, location: e.target.value }))}
                            placeholder="City, Province"
                          />
                        </div>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="about_me">About Me (50+ characters for points)</Label>
                        <Textarea
                          id="about_me"
                          value={profileForm.about_me}
                          onChange={(e) => setProfileForm(prev => ({ ...prev, about_me: e.target.value }))}
                          placeholder="Tell us about yourself, your career goals, and what makes you unique..."
                          rows={4}
                          className="resize-none"
                        />
                        <div className="text-sm text-slate-500">
                          {profileForm.about_me.length}/50 characters minimum
                        </div>
                      </div>

                      <Button 
                        type="submit" 
                        disabled={loading}
                        className="bg-gradient-to-r from-blue-600 to-slate-700 hover:from-blue-700 hover:to-slate-800"
                      >
                        {loading ? (
                          <div className="flex items-center space-x-2">
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                            <span>Saving...</span>
                          </div>
                        ) : (
                          <div className="flex items-center space-x-2">
                            <Save className="w-4 h-4" />
                            <span>Save Changes</span>
                          </div>
                        )}
                      </Button>
                    </form>
                  </CardContent>
                </Card>

                {/* Skills Section */}
                <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Zap className="w-5 h-5 text-blue-600" />
                      <span>Skills</span>
                      {!progress.skills && (
                        <Badge className="bg-yellow-100 text-yellow-800 text-xs">
                          +20 points (5+ skills)
                        </Badge>
                      )}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex space-x-2">
                        <Input
                          value={newSkill}
                          onChange={(e) => setNewSkill(e.target.value)}
                          placeholder="Add a skill (e.g., React, Python, Leadership)"
                          onKeyPress={(e) => e.key === 'Enter' && addSkill()}
                        />
                        <Button onClick={addSkill} disabled={!newSkill.trim()}>
                          <Plus className="w-4 h-4" />
                        </Button>
                      </div>
                      
                      <div className="flex flex-wrap gap-2">
                        {profileForm.skills.map((skill, index) => (
                          <Badge
                            key={index}
                            variant="secondary"
                            className="text-sm px-3 py-1 cursor-pointer hover:bg-red-100 hover:text-red-800"
                            onClick={() => removeSkill(skill)}
                          >
                            {skill} ×
                          </Badge>
                        ))}
                      </div>
                      
                      <div className="text-sm text-slate-600">
                        {profileForm.skills.length}/5 skills minimum for points
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Additional tabs would go here - Experience, Education, etc. */}
              <TabsContent value="experience" className="space-y-6 mt-6">
                <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Briefcase className="w-5 h-5 text-blue-600" />
                      <span>{workExperience.id ? 'Edit Work Experience' : 'Work Experience'}</span>
                      {!progress.work_history && (
                        <Badge className="bg-yellow-100 text-yellow-800 text-xs">
                          +10 points
                        </Badge>
                      )}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <form onSubmit={workExperience.id ? updateWorkExperience : addWorkExperience} className="space-y-6">
                      {/* Work experience form fields */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-2">
                          <Label htmlFor="company">Company</Label>
                          <Input
                            id="company"
                            value={workExperience.company}
                            onChange={(e) => setWorkExperience(prev => ({ ...prev, company: e.target.value }))}
                            placeholder="Company name"
                            required
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="position">Position</Label>
                          <Input
                            id="position"
                            value={workExperience.position}
                            onChange={(e) => setWorkExperience(prev => ({ ...prev, position: e.target.value }))}
                            placeholder="Job title"
                            required
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="work_location">Location</Label>
                          <Input
                            id="work_location"
                            value={workExperience.location}
                            onChange={(e) => setWorkExperience(prev => ({ ...prev, location: e.target.value }))}
                            placeholder="City, Province"
                            required
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="start_date">Start Date</Label>
                          <Input
                            id="start_date"
                            type="date"
                            value={workExperience.start_date}
                            onChange={(e) => setWorkExperience(prev => ({ ...prev, start_date: e.target.value }))}
                            required
                          />
                        </div>
                        {!workExperience.current && (
                          <div className="space-y-2">
                            <Label htmlFor="end_date">End Date</Label>
                            <Input
                              id="end_date"
                              type="date"
                              value={workExperience.end_date}
                              onChange={(e) => setWorkExperience(prev => ({ ...prev, end_date: e.target.value }))}
                            />
                          </div>
                        )}
                      </div>

                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          id="current"
                          checked={workExperience.current}
                          onChange={(e) => setWorkExperience(prev => ({ ...prev, current: e.target.checked, end_date: e.target.checked ? '' : prev.end_date }))}
                          className="w-4 h-4 text-blue-600"
                        />
                        <Label htmlFor="current">I currently work here</Label>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="description">Description</Label>
                        <Textarea
                          id="description"
                          value={workExperience.description}
                          onChange={(e) => setWorkExperience(prev => ({ ...prev, description: e.target.value }))}
                          placeholder="Describe your role, responsibilities, and achievements..."
                          rows={4}
                          required
                        />
                      </div>

                      <div className="flex space-x-3">
                        <Button 
                          type="submit"
                          className="bg-gradient-to-r from-blue-600 to-slate-700 hover:from-blue-700 hover:to-slate-800"
                          data-testid="save-experience-btn"
                        >
                          {workExperience.id ? (
                            <>
                              <Save className="w-4 h-4 mr-2" />
                              Update Experience
                            </>
                          ) : (
                            <>
                              <Plus className="w-4 h-4 mr-2" />
                              Add Experience
                            </>
                          )}
                        </Button>
                        {workExperience.id && (
                          <Button 
                            type="button"
                            variant="outline"
                            onClick={() => cancelEdit('experience')}
                            data-testid="cancel-edit-experience-btn"
                          >
                            Cancel
                          </Button>
                        )}
                      </div>
                    </form>

                    {/* Display existing work experience */}
                    <div className="mt-8 space-y-4">
                      <h4 className="font-semibold text-slate-700">Your Experience ({profile.work_experience?.length || 0})</h4>
                      {profile.work_experience?.length > 0 ? (
                        profile.work_experience.map((exp, index) => (
                          <div key={exp.id || index} className="border border-slate-200 rounded-lg p-4 hover:border-blue-200 transition-colors">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <h4 className="font-semibold text-slate-800">{exp.position}</h4>
                                <p className="text-blue-600 font-medium">{exp.company}</p>
                                <p className="text-sm text-slate-600">{exp.location}</p>
                                <p className="text-sm text-slate-500">
                                  {new Date(exp.start_date).toLocaleDateString('en-ZA', { year: 'numeric', month: 'short' })} - {
                                    exp.current ? 'Present' : new Date(exp.end_date).toLocaleDateString('en-ZA', { year: 'numeric', month: 'short' })
                                  }
                                </p>
                              </div>
                              <div className="flex space-x-2">
                                <Button 
                                  variant="ghost" 
                                  size="sm"
                                  onClick={() => editWorkExperience(exp)}
                                  className="text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                                  data-testid={`edit-experience-${index}`}
                                >
                                  <Pencil className="w-4 h-4" />
                                </Button>
                                <Button 
                                  variant="ghost" 
                                  size="sm"
                                  onClick={() => deleteWorkExperience(exp.id)}
                                  className="text-red-600 hover:text-red-700 hover:bg-red-50"
                                  data-testid={`delete-experience-${index}`}
                                >
                                  <Trash2 className="w-4 h-4" />
                                </Button>
                              </div>
                            </div>
                            <p className="mt-2 text-slate-700 text-sm">{exp.description}</p>
                          </div>
                        ))
                      ) : (
                        <div className="text-center py-8 text-slate-500">
                          <Briefcase className="w-12 h-12 mx-auto mb-3 text-slate-300" />
                          <p>No work experience added yet</p>
                          <p className="text-sm">Add your work history to improve your profile</p>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Education Tab */}
              <TabsContent value="education" className="space-y-6 mt-6">
                <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <GraduationCap className="w-5 h-5 text-blue-600" />
                      <span>{education.id ? 'Edit Education' : 'Education'}</span>
                      {!progress.education && (
                        <Badge className="bg-yellow-100 text-yellow-800 text-xs">
                          +10 points
                        </Badge>
                      )}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <form onSubmit={education.id ? updateEducation : addEducation} className="space-y-6">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-2">
                          <Label htmlFor="institution">Institution</Label>
                          <Input
                            id="institution"
                            value={education.institution}
                            onChange={(e) => setEducation(prev => ({ ...prev, institution: e.target.value }))}
                            placeholder="University or school name"
                            required
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="degree">Degree / Qualification</Label>
                          <Input
                            id="degree"
                            value={education.degree}
                            onChange={(e) => setEducation(prev => ({ ...prev, degree: e.target.value }))}
                            placeholder="e.g., BSc Computer Science"
                            required
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="field_of_study">Field of Study</Label>
                          <Input
                            id="field_of_study"
                            value={education.field_of_study}
                            onChange={(e) => setEducation(prev => ({ ...prev, field_of_study: e.target.value }))}
                            placeholder="e.g., Information Technology"
                            required
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="level">Level</Label>
                          <select
                            id="level"
                            value={education.level}
                            onChange={(e) => setEducation(prev => ({ ...prev, level: e.target.value }))}
                            className="w-full px-3 py-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            required
                          >
                            <option value="Matric">Matric / Grade 12</option>
                            <option value="Certificate">Certificate</option>
                            <option value="Diploma">Diploma</option>
                            <option value="Bachelors">Bachelor's Degree</option>
                            <option value="Honours">Honours Degree</option>
                            <option value="Masters">Master's Degree</option>
                            <option value="Doctorate">Doctorate / PhD</option>
                          </select>
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="edu_start_date">Start Date</Label>
                          <Input
                            id="edu_start_date"
                            type="date"
                            value={education.start_date}
                            onChange={(e) => setEducation(prev => ({ ...prev, start_date: e.target.value }))}
                            required
                          />
                        </div>
                        {!education.current && (
                          <div className="space-y-2">
                            <Label htmlFor="edu_end_date">End Date</Label>
                            <Input
                              id="edu_end_date"
                              type="date"
                              value={education.end_date}
                              onChange={(e) => setEducation(prev => ({ ...prev, end_date: e.target.value }))}
                            />
                          </div>
                        )}
                        <div className="space-y-2">
                          <Label htmlFor="grade">Grade / GPA (Optional)</Label>
                          <Input
                            id="grade"
                            value={education.grade}
                            onChange={(e) => setEducation(prev => ({ ...prev, grade: e.target.value }))}
                            placeholder="e.g., Cum Laude, 3.8 GPA"
                          />
                        </div>
                      </div>

                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          id="edu_current"
                          checked={education.current}
                          onChange={(e) => setEducation(prev => ({ ...prev, current: e.target.checked, end_date: e.target.checked ? '' : prev.end_date }))}
                          className="w-4 h-4 text-blue-600"
                        />
                        <Label htmlFor="edu_current">I'm currently studying here</Label>
                      </div>

                      <div className="flex space-x-3">
                        <Button 
                          type="submit"
                          className="bg-gradient-to-r from-blue-600 to-slate-700 hover:from-blue-700 hover:to-slate-800"
                          data-testid="save-education-btn"
                        >
                          {education.id ? (
                            <>
                              <Save className="w-4 h-4 mr-2" />
                              Update Education
                            </>
                          ) : (
                            <>
                              <Plus className="w-4 h-4 mr-2" />
                              Add Education
                            </>
                          )}
                        </Button>
                        {education.id && (
                          <Button 
                            type="button"
                            variant="outline"
                            onClick={() => cancelEdit('education')}
                            data-testid="cancel-edit-education-btn"
                          >
                            Cancel
                          </Button>
                        )}
                      </div>
                    </form>

                    {/* Display existing education */}
                    <div className="mt-8 space-y-4">
                      <h4 className="font-semibold text-slate-700">Your Education ({profile.education?.length || 0})</h4>
                      {profile.education?.length > 0 ? (
                        profile.education.map((edu, index) => (
                          <div key={edu.id || index} className="border border-slate-200 rounded-lg p-4 hover:border-blue-200 transition-colors">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <h4 className="font-semibold text-slate-800">{edu.degree}</h4>
                                <p className="text-blue-600 font-medium">{edu.institution}</p>
                                <p className="text-sm text-slate-600">{edu.field_of_study}</p>
                                <p className="text-sm text-slate-500">
                                  {new Date(edu.start_date).toLocaleDateString('en-ZA', { year: 'numeric', month: 'short' })} - {
                                    edu.current ? 'Present' : new Date(edu.end_date).toLocaleDateString('en-ZA', { year: 'numeric', month: 'short' })
                                  }
                                </p>
                                {edu.grade && (
                                  <Badge className="mt-2 bg-green-100 text-green-800">{edu.grade}</Badge>
                                )}
                              </div>
                              <div className="flex items-center space-x-2">
                                <Badge variant="outline" className="capitalize">{edu.level}</Badge>
                                <Button 
                                  variant="ghost" 
                                  size="sm"
                                  onClick={() => editEducation(edu)}
                                  className="text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                                  data-testid={`edit-education-${index}`}
                                >
                                  <Pencil className="w-4 h-4" />
                                </Button>
                                <Button 
                                  variant="ghost" 
                                  size="sm"
                                  onClick={() => deleteEducation(edu.id)}
                                  className="text-red-600 hover:text-red-700 hover:bg-red-50"
                                  data-testid={`delete-education-${index}`}
                                >
                                  <Trash2 className="w-4 h-4" />
                                </Button>
                              </div>
                            </div>
                          </div>
                        ))
                      ) : (
                        <div className="text-center py-8 text-slate-500">
                          <GraduationCap className="w-12 h-12 mx-auto mb-3 text-slate-300" />
                          <p>No education added yet</p>
                          <p className="text-sm">Add your qualifications to improve your profile</p>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Awards/Achievements Tab */}
              <TabsContent value="achievements" className="space-y-6 mt-6">
                <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Award className="w-5 h-5 text-blue-600" />
                      <span>{achievement.id ? 'Edit Award/Achievement' : 'Awards & Achievements'}</span>
                      {!progress.achievements && (
                        <Badge className="bg-yellow-100 text-yellow-800 text-xs">
                          +10 points
                        </Badge>
                      )}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <form onSubmit={achievement.id ? updateAchievement : addAchievement} className="space-y-6">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-2">
                          <Label htmlFor="achievement_title">Award / Achievement Title</Label>
                          <Input
                            id="achievement_title"
                            value={achievement.title}
                            onChange={(e) => setAchievement(prev => ({ ...prev, title: e.target.value }))}
                            placeholder="e.g., Employee of the Year"
                            required
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="issuer">Issuing Organization</Label>
                          <Input
                            id="issuer"
                            value={achievement.issuer}
                            onChange={(e) => setAchievement(prev => ({ ...prev, issuer: e.target.value }))}
                            placeholder="e.g., Microsoft, SAQA"
                            required
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="date_achieved">Date Achieved</Label>
                          <Input
                            id="date_achieved"
                            type="date"
                            value={achievement.date_achieved}
                            onChange={(e) => setAchievement(prev => ({ ...prev, date_achieved: e.target.value }))}
                            required
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="credential_url">Credential URL (Optional)</Label>
                          <Input
                            id="credential_url"
                            type="url"
                            value={achievement.credential_url}
                            onChange={(e) => setAchievement(prev => ({ ...prev, credential_url: e.target.value }))}
                            placeholder="https://..."
                          />
                        </div>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="achievement_description">Description</Label>
                        <Textarea
                          id="achievement_description"
                          value={achievement.description}
                          onChange={(e) => setAchievement(prev => ({ ...prev, description: e.target.value }))}
                          placeholder="Describe your achievement and its significance..."
                          rows={3}
                          required
                        />
                      </div>

                      <div className="flex space-x-3">
                        <Button 
                          type="submit"
                          className="bg-gradient-to-r from-blue-600 to-slate-700 hover:from-blue-700 hover:to-slate-800"
                          data-testid="save-achievement-btn"
                        >
                          {achievement.id ? (
                            <>
                              <Save className="w-4 h-4 mr-2" />
                              Update Achievement
                            </>
                          ) : (
                            <>
                              <Plus className="w-4 h-4 mr-2" />
                              Add Achievement
                            </>
                          )}
                        </Button>
                        {achievement.id && (
                          <Button 
                            type="button"
                            variant="outline"
                            onClick={() => cancelEdit('achievement')}
                            data-testid="cancel-edit-achievement-btn"
                          >
                            Cancel
                          </Button>
                        )}
                      </div>
                    </form>

                    {/* Display existing achievements */}
                    <div className="mt-8 space-y-4">
                      <h4 className="font-semibold text-slate-700">Your Achievements ({profile.achievements?.length || 0})</h4>
                      {profile.achievements?.length > 0 ? (
                        profile.achievements.map((ach, index) => (
                          <div key={ach.id || index} className="border border-slate-200 rounded-lg p-4 hover:border-blue-200 transition-colors">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center space-x-2">
                                  <Star className="w-5 h-5 text-yellow-500" />
                                  <h4 className="font-semibold text-slate-800">{ach.title}</h4>
                                </div>
                                <p className="text-blue-600 font-medium mt-1">{ach.issuer}</p>
                                <p className="text-sm text-slate-500">
                                  {new Date(ach.date_achieved).toLocaleDateString('en-ZA', { year: 'numeric', month: 'long' })}
                                </p>
                                <p className="mt-2 text-slate-700 text-sm">{ach.description}</p>
                                {ach.credential_url && (
                                  <a 
                                    href={ach.credential_url} 
                                    target="_blank" 
                                    rel="noopener noreferrer"
                                    className="mt-2 inline-flex items-center text-sm text-blue-600 hover:underline"
                                  >
                                    View Credential →
                                  </a>
                                )}
                              </div>
                              <div className="flex space-x-2">
                                <Button 
                                  variant="ghost" 
                                  size="sm"
                                  onClick={() => editAchievement(ach)}
                                  className="text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                                  data-testid={`edit-achievement-${index}`}
                                >
                                  <Pencil className="w-4 h-4" />
                                </Button>
                                <Button 
                                  variant="ghost" 
                                  size="sm"
                                  onClick={() => deleteAchievement(ach.id)}
                                  className="text-red-600 hover:text-red-700 hover:bg-red-50"
                                  data-testid={`delete-achievement-${index}`}
                                >
                                  <Trash2 className="w-4 h-4" />
                                </Button>
                              </div>
                            </div>
                          </div>
                        ))
                      ) : (
                        <div className="text-center py-8 text-slate-500">
                          <Award className="w-12 h-12 mx-auto mb-3 text-slate-300" />
                          <p>No achievements added yet</p>
                          <p className="text-sm">Add your awards and certifications to stand out</p>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Media Tab */}
              <TabsContent value="media" className="space-y-6 mt-6">
                <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Video className="w-5 h-5 text-blue-600" />
                      <span>Media & Portfolio</span>
                      {!progress.media && (
                        <Badge className="bg-yellow-100 text-yellow-800 text-xs">
                          +15 points
                        </Badge>
                      )}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-6">
                      {/* Video Introduction */}
                      <div>
                        <input
                          ref={videoRef}
                          type="file"
                          accept=".mp4,.mov,.avi,.webm"
                          onChange={(e) => handleVideoUpload(e.target.files[0])}
                          className="hidden"
                          data-testid="video-upload-input"
                        />
                        {profile.video_intro_url ? (
                          <div>
                            <h3 className="text-lg font-semibold text-slate-800 mb-3">Your Video Introduction</h3>
                            <video 
                              controls 
                              className="w-full max-w-md rounded-lg shadow-lg mb-4"
                              src={profile.video_intro_url.startsWith('http') ? profile.video_intro_url : `${BACKEND_URL}${profile.video_intro_url}`}
                            >
                              Your browser does not support the video tag.
                            </video>
                            <Button 
                              variant="outline" 
                              onClick={() => videoRef.current?.click()}
                              disabled={uploadingVideo}
                              data-testid="replace-video-btn"
                            >
                              {uploadingVideo ? (
                                <>
                                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                  Uploading...
                                </>
                              ) : (
                                <>
                                  <Upload className="w-4 h-4 mr-2" />
                                  Replace Video
                                </>
                              )}
                            </Button>
                          </div>
                        ) : (
                          <div 
                            className="border-2 border-dashed border-slate-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-400 hover:bg-slate-50 transition-colors"
                            onClick={() => videoRef.current?.click()}
                            data-testid="video-upload-zone"
                          >
                            {uploadingVideo ? (
                              <>
                                <Loader2 className="w-16 h-16 mx-auto mb-4 text-blue-500 animate-spin" />
                                <h3 className="text-lg font-semibold text-slate-800 mb-2">Uploading Video...</h3>
                                <p className="text-slate-600">Please wait while your video is being uploaded</p>
                              </>
                            ) : (
                              <>
                                <Video className="w-16 h-16 mx-auto mb-4 text-slate-400" />
                                <h3 className="text-lg font-semibold text-slate-800 mb-2">Video Introduction</h3>
                                <p className="text-slate-600 mb-4">
                                  Record a 60-second video introducing yourself to potential employers
                                </p>
                                <Button variant="outline" className="border-blue-600 text-blue-600 hover:bg-blue-50">
                                  <Upload className="w-4 h-4 mr-2" />
                                  Upload Video
                                </Button>
                                <p className="text-xs text-slate-500 mt-2">MP4, MOV, AVI, or WebM format, max 50MB</p>
                              </>
                            )}
                          </div>
                        )}
                      </div>

                      {/* Portfolio Links */}
                      <form onSubmit={handleMediaSubmit} className="space-y-4">
                        <h3 className="text-lg font-semibold text-slate-800">Portfolio Links</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <Label htmlFor="linkedin_url">LinkedIn Profile</Label>
                            <Input
                              id="linkedin_url"
                              type="url"
                              placeholder="https://linkedin.com/in/yourprofile"
                              value={mediaForm.linkedin_url}
                              onChange={(e) => setMediaForm(prev => ({ ...prev, linkedin_url: e.target.value }))}
                              data-testid="linkedin-input"
                            />
                          </div>
                          <div className="space-y-2">
                            <Label htmlFor="portfolio_url">Personal Website / Portfolio</Label>
                            <Input
                              id="portfolio_url"
                              type="url"
                              placeholder="https://yourportfolio.com"
                              value={mediaForm.portfolio_url}
                              onChange={(e) => setMediaForm(prev => ({ ...prev, portfolio_url: e.target.value }))}
                              data-testid="portfolio-input"
                            />
                          </div>
                        </div>
                        <Button 
                          type="submit"
                          disabled={loading}
                          className="bg-gradient-to-r from-blue-600 to-slate-700 hover:from-blue-700 hover:to-slate-800"
                          data-testid="save-media-btn"
                        >
                          {loading ? (
                            <div className="flex items-center space-x-2">
                              <Loader2 className="w-4 h-4 animate-spin" />
                              <span>Saving...</span>
                            </div>
                          ) : (
                            <div className="flex items-center space-x-2">
                              <Save className="w-4 h-4" />
                              <span>Save Links</span>
                            </div>
                          )}
                        </Button>
                      </form>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Applications Tab */}
              <TabsContent value="applications" className="space-y-6 mt-6">
                <MyApplications user={profile} />
              </TabsContent>

              {/* Alerts Tab - Job Alerts */}
              <TabsContent value="alerts" className="space-y-6 mt-6">
                <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Bell className="w-5 h-5 text-blue-600" />
                      <span>Job Alerts</span>
                      {!progress.email_alerts && (
                        <Badge className="bg-yellow-100 text-yellow-800 text-xs">
                          +5 points
                        </Badge>
                      )}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-6">
                      {/* Description */}
                      <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                        <p className="text-sm text-blue-800">
                          Create job alerts to get notified via email when new jobs matching your criteria are posted. 
                          You can create multiple alerts for different job types or locations.
                        </p>
                      </div>

                      {/* New Job Alert Form */}
                      <form onSubmit={addJobAlert} className="space-y-4">
                        <h4 className="font-medium text-slate-800">Create New Job Alert</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <Label htmlFor="alert_job_title">Job Title</Label>
                            <Input
                              id="alert_job_title"
                              value={newJobAlert.job_title}
                              onChange={(e) => setNewJobAlert(prev => ({ ...prev, job_title: e.target.value }))}
                              placeholder="e.g., Software Developer"
                              required
                            />
                          </div>
                          <div className="space-y-2">
                            <Label htmlFor="alert_location">Location</Label>
                            <Input
                              id="alert_location"
                              value={newJobAlert.location}
                              onChange={(e) => setNewJobAlert(prev => ({ ...prev, location: e.target.value }))}
                              placeholder="e.g., Cape Town, Johannesburg"
                              required
                            />
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          <div className="space-y-3">
                            <Label>Employment Type (select all that apply)</Label>
                            <div className="flex flex-wrap gap-3">
                              {['Permanent', 'Contract'].map((type) => (
                                <label key={type} className="flex items-center space-x-2 cursor-pointer">
                                  <input
                                    type="checkbox"
                                    checked={newJobAlert.employment_types.includes(type)}
                                    onChange={() => toggleEmploymentType(type)}
                                    className="w-4 h-4 text-blue-600 rounded border-slate-300 focus:ring-blue-500"
                                  />
                                  <span className="text-sm text-slate-700">{type}</span>
                                </label>
                              ))}
                            </div>
                          </div>
                          <div className="space-y-3">
                            <Label>Work Type (select all that apply)</Label>
                            <div className="flex flex-wrap gap-3">
                              {['In Office', 'Hybrid', 'Remote'].map((type) => (
                                <label key={type} className="flex items-center space-x-2 cursor-pointer">
                                  <input
                                    type="checkbox"
                                    checked={newJobAlert.work_types.includes(type)}
                                    onChange={() => toggleWorkType(type)}
                                    className="w-4 h-4 text-blue-600 rounded border-slate-300 focus:ring-blue-500"
                                  />
                                  <span className="text-sm text-slate-700">{type}</span>
                                </label>
                              ))}
                            </div>
                          </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <Label htmlFor="alert_salary">Desired Salary Range</Label>
                            <Input
                              id="alert_salary"
                              value={newJobAlert.salary_range}
                              onChange={(e) => setNewJobAlert(prev => ({ ...prev, salary_range: e.target.value }))}
                              placeholder="e.g., R50,000 - R80,000"
                            />
                          </div>
                        </div>
                        <Button 
                          type="submit"
                          className="bg-gradient-to-r from-blue-600 to-slate-700 hover:from-blue-700 hover:to-slate-800"
                          disabled={newJobAlert.employment_types.length === 0 || newJobAlert.work_types.length === 0}
                        >
                          <Plus className="w-4 h-4 mr-2" />
                          Create Alert
                        </Button>
                      </form>

                      {/* Existing Job Alerts */}
                      <div className="space-y-4">
                        <h4 className="font-medium text-slate-800">Your Job Alerts ({jobAlerts.length})</h4>
                        {jobAlerts.length > 0 ? (
                          <div className="space-y-3">
                            {jobAlerts.map((alert) => (
                              <div key={alert.id} className="flex items-center justify-between p-4 bg-slate-50 rounded-lg border border-slate-200">
                                <div className="flex-1">
                                  <div className="flex items-center flex-wrap gap-1 mb-1">
                                    <h5 className="font-semibold text-slate-800 mr-2">{alert.job_title}</h5>
                                    {(alert.employment_types || []).map((et) => (
                                      <Badge key={et} variant="outline" className="text-xs">{et}</Badge>
                                    ))}
                                    {(alert.work_types || []).map((wt) => (
                                      <Badge key={wt} variant="outline" className="text-xs bg-blue-50">{wt}</Badge>
                                    ))}
                                  </div>
                                  <div className="flex items-center space-x-4 text-sm text-slate-600">
                                    <span className="flex items-center">
                                      <MapPin className="w-3 h-3 mr-1" />
                                      {alert.location}
                                    </span>
                                    {alert.salary_range && (
                                      <span className="flex items-center">
                                        <span className="font-semibold mr-1">R</span>
                                        {alert.salary_range}
                                      </span>
                                    )}
                                  </div>
                                </div>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => deleteJobAlert(alert.id)}
                                  className="text-red-600 hover:text-red-700 hover:bg-red-50"
                                >
                                  <Trash2 className="w-4 h-4" />
                                </Button>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="text-center py-8 text-slate-500">
                            <Bell className="w-12 h-12 mx-auto mb-3 text-slate-300" />
                            <p>No job alerts created yet</p>
                            <p className="text-sm">Create alerts above to get notified about matching jobs</p>
                          </div>
                        )}
                      </div>

                      {/* Salary Preferences */}
                      <div className="space-y-4 pt-6 border-t border-slate-200">
                        <h4 className="font-medium text-slate-800">Salary Preferences (Optional)</h4>
                        <p className="text-sm text-slate-600">These are your general salary preferences shown on your profile.</p>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <Label htmlFor="current_salary">Current Salary Range</Label>
                            <Input
                              id="current_salary"
                              value={profileForm.current_salary_range}
                              onChange={(e) => setProfileForm(prev => ({ ...prev, current_salary_range: e.target.value }))}
                              placeholder="e.g., R50,000 - R80,000"
                            />
                          </div>
                          <div className="space-y-2">
                            <Label htmlFor="desired_salary">Desired Salary Range</Label>
                            <Input
                              id="desired_salary"
                              value={profileForm.desired_salary_range}
                              onChange={(e) => setProfileForm(prev => ({ ...prev, desired_salary_range: e.target.value }))}
                              placeholder="e.g., R80,000 - R120,000"
                            />
                          </div>
                        </div>
                        <Button 
                          onClick={() => updateProfile({ 
                            current_salary_range: profileForm.current_salary_range,
                            desired_salary_range: profileForm.desired_salary_range
                          })}
                          variant="outline"
                        >
                          <Save className="w-4 h-4 mr-2" />
                          Save Salary Preferences
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileDashboard;