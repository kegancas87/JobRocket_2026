import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Label } from "./ui/label";
import { Rocket, Mail, ArrowLeft, CheckCircle } from "lucide-react";
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ForgotPasswordPage = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await axios.post(`${API}/auth/forgot-password`, { email });
      setSent(true);
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong. Please try again.');
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
      <div className="absolute inset-0 stars"></div>
      
      <Card className="w-full max-w-md bg-white/90 backdrop-blur-lg shadow-2xl border-0 relative z-10">
        <CardHeader className="text-center pb-6">
          <div className="flex justify-center mb-4">
            <div className="bg-gradient-to-br from-blue-600 to-slate-700 text-white p-4 rounded-2xl shadow-lg">
              <Rocket className="w-10 h-10" />
            </div>
          </div>
          <CardTitle className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-slate-800 bg-clip-text text-transparent">
            {sent ? 'Check Your Email' : 'Forgot Password'}
          </CardTitle>
          <p className="text-slate-600 mt-2 text-sm">
            {sent 
              ? 'We\'ve sent a password reset link to your email.' 
              : 'Enter your email and we\'ll send you a reset link.'}
          </p>
        </CardHeader>
        
        <CardContent>
          {sent ? (
            <div className="space-y-6">
              <div className="flex justify-center">
                <div className="bg-green-50 border border-green-200 rounded-full p-4">
                  <CheckCircle className="w-12 h-12 text-green-500" />
                </div>
              </div>
              <div className="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-lg text-sm text-center">
                If an account with <strong>{email}</strong> exists, you'll receive an email with instructions to reset your password. Check your spam folder too.
              </div>
              <Button
                onClick={() => navigate('/')}
                className="w-full bg-gradient-to-r from-blue-600 to-slate-700 hover:from-blue-700 hover:to-slate-800 h-12 font-semibold"
                data-testid="back-to-login-btn"
              >
                <ArrowLeft className="w-5 h-5 mr-2" />
                Back to Login
              </Button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                  {error}
                </div>
              )}
              
              <div className="space-y-2">
                <Label htmlFor="email" className="text-slate-700 font-medium">Email Address</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="your@email.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="pl-10 h-12 border-slate-300 focus:border-blue-500 focus:ring-blue-500"
                    required
                    data-testid="forgot-email-input"
                  />
                </div>
              </div>
              
              <Button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-blue-600 to-slate-700 hover:from-blue-700 hover:to-slate-800 h-12 text-lg font-semibold shadow-lg"
                data-testid="send-reset-link-btn"
              >
                {loading ? (
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span>Sending...</span>
                  </div>
                ) : (
                  'Send Reset Link'
                )}
              </Button>
              
              <Button
                type="button"
                variant="ghost"
                onClick={() => navigate('/')}
                className="w-full h-10 text-slate-600 hover:text-slate-800"
                data-testid="back-to-login-link"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Login
              </Button>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default ForgotPasswordPage;
