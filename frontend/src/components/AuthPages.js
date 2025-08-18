import React, { useState } from 'react';
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Label } from "./ui/label";
import { Separator } from "./ui/separator";
import { 
  Rocket, 
  Mail, 
  Lock, 
  User, 
  Eye, 
  EyeOff,
  Star,
  Sparkles,
  Zap,
  Briefcase
} from "lucide-react";
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const LoginPage = ({ onLogin, onSwitchToRegister }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API}/auth/login`, formData);
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      onLogin(response.data.user);
    } catch (error) {
      setError(error.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div 
      className="min-h-screen flex items-center justify-center p-6 relative overflow-hidden"
      style={{
        backgroundImage: `linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(30, 64, 175, 0.8)), url('https://images.unsplash.com/photo-1457365050282-c53d772ef8b2?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHw0fHxyb2NrZXQlMjBsYXVuY2h8ZW58MHx8fHx8MTc1NTM1MzYyNnww&ixlib=rb-4.1.0&q=85')`,
        backgroundSize: 'cover',
        backgroundPosition: 'center'
      }}
    >
      {/* Animated stars background */}
      <div className="absolute inset-0 stars"></div>
      
      <Card className="w-full max-w-md bg-white/90 backdrop-blur-lg shadow-2xl border-0 relative z-10">
        <CardHeader className="text-center pb-8">
          <div className="flex justify-center mb-4">
            <div className="bg-gradient-to-br from-blue-600 to-slate-700 text-white p-4 rounded-2xl shadow-lg">
              <Rocket className="w-10 h-10" />
            </div>
          </div>
          <CardTitle className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-slate-800 bg-clip-text text-transparent">
            Welcome Back
          </CardTitle>
          <p className="text-slate-600 mt-2">Ready to launch your career journey?</p>
        </CardHeader>
        
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}
            
            <div className="space-y-2">
              <Label htmlFor="email" className="text-slate-700 font-medium">Email</Label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
                <Input
                  id="email"
                  type="email"
                  placeholder="your@email.com"
                  value={formData.email}
                  onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                  className="pl-10 h-12 border-slate-300 focus:border-blue-500 focus:ring-blue-500"
                  required
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="password" className="text-slate-700 font-medium">Password</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Enter your password"
                  value={formData.password}
                  onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
                  className="pl-10 pr-10 h-12 border-slate-300 focus:border-blue-500 focus:ring-blue-500"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 hover:text-slate-600"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>
            
            <Button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-600 to-slate-700 hover:from-blue-700 hover:to-slate-800 h-12 text-lg font-semibold shadow-lg"
            >
              {loading ? (
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Launching...</span>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <Zap className="w-5 h-5" />
                  <span>Launch In</span>
                </div>
              )}
            </Button>
          </form>
          
          <div className="mt-8">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <Separator />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="bg-white px-4 text-slate-500">New to Job Rocket?</span>
              </div>
            </div>
            
            <Button
              variant="outline"
              onClick={onSwitchToRegister}
              className="w-full mt-4 h-12 border-slate-300 hover:bg-slate-50 font-medium"
            >
              <Star className="w-5 h-5 mr-2" />
              Create Account
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

const RegisterPage = ({ onRegister, onSwitchToLogin }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    role: 'job_seeker' // Default role
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API}/auth/register`, formData);
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      onRegister(response.data.user);
    } catch (error) {
      setError(error.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div 
      className="min-h-screen flex items-center justify-center p-6 relative overflow-hidden"
      style={{
        backgroundImage: `linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(30, 64, 175, 0.8)), url('https://images.unsplash.com/photo-1517976487492-5750f3195933?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwzfHxyb2NrZXQlMjBsYXVuY2h8ZW58MHx8fHwxNzU1MzUzNjI2fDA&ixlib=rb-4.1.0&q=85')`,
        backgroundSize: 'cover',
        backgroundPosition: 'center'
      }}
    >
      {/* Animated stars background */}
      <div className="absolute inset-0 stars"></div>
      
      <Card className="w-full max-w-lg bg-white/90 backdrop-blur-lg shadow-2xl border-0 relative z-10">
        <CardHeader className="text-center pb-8">
          <div className="flex justify-center mb-4">
            <div className="bg-gradient-to-br from-blue-600 to-slate-700 text-white p-4 rounded-2xl shadow-lg">
              <Sparkles className="w-10 h-10" />
            </div>
          </div>
          <CardTitle className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-slate-800 bg-clip-text text-transparent">
            Join Job Rocket
          </CardTitle>
          <p className="text-slate-600 mt-2">Start your journey to career excellence</p>
        </CardHeader>
        
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            {/* Role Selection */}
            <div className="space-y-3">
              <Label className="text-slate-700 font-medium text-base">I want to:</Label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => setFormData(prev => ({ ...prev, role: 'job_seeker' }))}
                  className={`p-4 rounded-xl border-2 transition-all text-left ${
                    formData.role === 'job_seeker'
                      ? 'border-blue-500 bg-blue-50 text-blue-800'
                      : 'border-slate-300 hover:border-slate-400 text-slate-600'
                  }`}
                >
                  <User className="w-6 h-6 mb-2" />
                  <div className="font-semibold">Find Jobs</div>
                  <div className="text-sm opacity-75">Job Seeker</div>
                </button>
                <button
                  type="button"
                  onClick={() => setFormData(prev => ({ ...prev, role: 'recruiter' }))}
                  className={`p-4 rounded-xl border-2 transition-all text-left ${
                    formData.role === 'recruiter'
                      ? 'border-blue-500 bg-blue-50 text-blue-800'
                      : 'border-slate-300 hover:border-slate-400 text-slate-600'
                  }`}
                >
                  <Briefcase className="w-6 h-6 mb-2" />
                  <div className="font-semibold">Hire Talent</div>
                  <div className="text-sm opacity-75">Recruiter</div>
                </button>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="first_name" className="text-slate-700 font-medium">First Name</Label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
                  <Input
                    id="first_name"
                    type="text"
                    placeholder="John"
                    value={formData.first_name}
                    onChange={(e) => setFormData(prev => ({ ...prev, first_name: e.target.value }))}
                    className="pl-10 h-12 border-slate-300 focus:border-blue-500 focus:ring-blue-500"
                    required
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="last_name" className="text-slate-700 font-medium">Last Name</Label>
                <Input
                  id="last_name"
                  type="text"
                  placeholder="Doe"
                  value={formData.last_name}
                  onChange={(e) => setFormData(prev => ({ ...prev, last_name: e.target.value }))}
                  className="h-12 border-slate-300 focus:border-blue-500 focus:ring-blue-500"
                  required
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="email" className="text-slate-700 font-medium">Email</Label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
                <Input
                  id="email"
                  type="email"
                  placeholder="your@email.com"
                  value={formData.email}
                  onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                  className="pl-10 h-12 border-slate-300 focus:border-blue-500 focus:ring-blue-500"
                  required
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="password" className="text-slate-700 font-medium">Password</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Create a strong password"
                  value={formData.password}
                  onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
                  className="pl-10 pr-10 h-12 border-slate-300 focus:border-blue-500 focus:ring-blue-500"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 hover:text-slate-600"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>
            
            <Button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-600 to-slate-700 hover:from-blue-700 hover:to-slate-800 h-12 text-lg font-semibold shadow-lg"
            >
              {loading ? (
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Creating Account...</span>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <Rocket className="w-5 h-5" />
                  <span>
                    {formData.role === 'job_seeker' ? 'Launch My Career' : 'Start Hiring'}
                  </span>
                </div>
              )}
            </Button>
          </form>
          
          <div className="mt-8">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <Separator />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="bg-white px-4 text-slate-500">Already have an account?</span>
              </div>
            </div>
            
            <Button
              variant="outline"
              onClick={onSwitchToLogin}
              className="w-full mt-4 h-12 border-slate-300 hover:bg-slate-50 font-medium"
            >
              <Zap className="w-5 h-5 mr-2" />
              Sign In
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export { LoginPage, RegisterPage };