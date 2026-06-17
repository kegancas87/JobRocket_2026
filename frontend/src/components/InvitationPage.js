import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Label } from "./ui/label";
import { Badge } from "./ui/badge";
import { 
  Building2, 
  Users, 
  MapPin, 
  Calendar,
  Mail,
  User,
  Eye,
  EyeOff,
  CheckCircle2,
  XCircle,
  Clock
} from "lucide-react";
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const InvitationPage = ({ onLogin }) => {
  const { token } = useParams();
  const navigate = useNavigate();
  
  const [invitation, setInvitation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [registering, setRegistering] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });

  useEffect(() => {
    fetchInvitationDetails();
  }, [token]);

  const fetchInvitationDetails = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/public/invitations/${token}`);
      setInvitation(response.data);
      
      // Pre-fill form data from invitation
      setFormData(prev => ({
        ...prev,
        first_name: response.data.first_name,
        last_name: response.data.last_name,
        email: response.data.email || ''
      }));
    } catch (error) {
      console.error('Error fetching invitation:', error);
      setError(error.response?.data?.detail || 'Failed to load invitation details');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const handleRegistration = async (e) => {
    e.preventDefault();
    
    // Validate passwords match
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters long');
      return;
    }

    try {
      setRegistering(true);
      setError('');
      
      const response = await axios.post(`${API}/public/invitations/${token}/register`, {
        email: formData.email,
        password: formData.password,
        first_name: formData.first_name,
        last_name: formData.last_name
      });

      // Store token and user data
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      
      // Call onLogin callback to update app state
      onLogin(response.data.user);
      
      // Navigate to recruiter dashboard
      navigate('/recruiter-dashboard');
      
    } catch (error) {
      console.error('Registration error:', error);
      setError(error.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setRegistering(false);
    }
  };

  const formatRole = (role) => {
    return role.charAt(0).toUpperCase() + role.slice(1).toLowerCase();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading invitation...</p>
        </div>
      </div>
    );
  }

  if (error && !invitation) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 flex items-center justify-center p-4">
        <Card className="w-full max-w-md bg-white/80 backdrop-blur-sm border-0 shadow-xl">
          <CardHeader className="text-center">
            <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <CardTitle className="text-xl text-slate-800">Invitation Error</CardTitle>
          </CardHeader>
          <CardContent className="text-center">
            <p className="text-slate-600 mb-6">{error}</p>
            <Button onClick={() => navigate('/')}>
              Go to Home
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 p-4">
      <div className="max-w-2xl mx-auto pt-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-full mb-4">
            <Users className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-slate-800 mb-2">
            Team Invitation
          </h1>
          <p className="text-slate-600">
            You've been invited to join a team at Job Rocket
          </p>
        </div>

        {invitation && (
          <>
            {/* Invitation Details */}
            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl mb-8">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Building2 className="w-5 h-5 text-blue-600" />
                  <span>Invitation Details</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <Label className="text-slate-600">Company</Label>
                    <p className="font-semibold text-slate-800">{invitation.company_name}</p>
                  </div>
                  <div className="space-y-1">
                    <Label className="text-slate-600">Role</Label>
                    <Badge variant="outline" className="text-blue-700 border-blue-200">
                      {formatRole(invitation.role)}
                    </Badge>
                  </div>
                </div>

                {invitation.branches.length > 0 && (
                  <div className="space-y-2">
                    <Label className="text-slate-600">Assigned Branches</Label>
                    <div className="flex flex-wrap gap-2">
                      {invitation.branches.map((branch) => (
                        <div key={branch.id} className="flex items-center space-x-1 bg-slate-100 rounded-lg px-3 py-1">
                          <MapPin className="w-3 h-3 text-slate-500" />
                          <span className="text-sm text-slate-700">{branch.name}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="flex items-center space-x-2 text-sm text-slate-500">
                  <Clock className="w-4 h-4" />
                  <span>Expires: {new Date(invitation.expires_at).toLocaleDateString()}</span>
                </div>
              </CardContent>
            </Card>

            {/* Registration Form */}
            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <User className="w-5 h-5 text-blue-600" />
                  <span>Complete Your Registration</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleRegistration} className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="first_name">First Name</Label>
                      <Input
                        id="first_name"
                        name="first_name"
                        value={formData.first_name}
                        onChange={handleInputChange}
                        required
                        disabled={registering}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="last_name">Last Name</Label>
                      <Input
                        id="last_name"
                        name="last_name"
                        value={formData.last_name}
                        onChange={handleInputChange}
                        required
                        disabled={registering}
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="email">Email Address</Label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
                      <Input
                        id="email"
                        name="email"
                        type="email"
                        value={formData.email}
                        onChange={handleInputChange}
                        className="pl-10"
                        required
                        disabled={registering}
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="password">Create Password</Label>
                    <div className="relative">
                      <Input
                        id="password"
                        name="password"
                        type={showPassword ? "text" : "password"}
                        value={formData.password}
                        onChange={handleInputChange}
                        className="pr-10"
                        required
                        minLength={6}
                        disabled={registering}
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 hover:text-slate-600"
                      >
                        {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                      </button>
                    </div>
                    <p className="text-sm text-slate-500">Minimum 6 characters</p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="confirmPassword">Confirm Password</Label>
                    <Input
                      id="confirmPassword"
                      name="confirmPassword"
                      type="password"
                      value={formData.confirmPassword}
                      onChange={handleInputChange}
                      required
                      disabled={registering}
                    />
                  </div>

                  {error && (
                    <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                      <div className="flex items-center space-x-2">
                        <XCircle className="w-5 h-5 text-red-600" />
                        <p className="text-red-700">{error}</p>
                      </div>
                    </div>
                  )}

                  <Button 
                    type="submit" 
                    disabled={registering}
                    className="w-full bg-gradient-to-r from-blue-600 to-slate-700 hover:from-blue-700 hover:to-slate-800"
                  >
                    {registering ? (
                      <div className="flex items-center space-x-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        <span>Creating Account...</span>
                      </div>
                    ) : (
                      <div className="flex items-center space-x-2">
                        <CheckCircle2 className="w-4 h-4" />
                        <span>Join Team</span>
                      </div>
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </div>
  );
};

export default InvitationPage;