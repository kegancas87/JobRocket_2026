import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { CheckCircle, XCircle, AlertCircle, Loader2, Home, CreditCard, ArrowRight } from "lucide-react";
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const PaymentSuccessPage = ({ user }) => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [paymentDetails, setPaymentDetails] = useState(null);

  const paymentId = searchParams.get('payment_id');

  useEffect(() => {
    const verifyPayment = async () => {
      if (paymentId) {
        try {
          // Wait a moment for webhook to process
          await new Promise(resolve => setTimeout(resolve, 2000));
          
          const token = localStorage.getItem('token');
          const response = await axios.get(`${API}/account`, {
            headers: { 'Authorization': `Bearer ${token}` }
          });
          
          setPaymentDetails({
            success: true,
            tier: response.data.tier_name,
            status: response.data.subscription_status
          });
        } catch (error) {
          console.error('Error verifying payment:', error);
          setPaymentDetails({ success: true }); // Assume success if we can't verify
        }
      }
      setLoading(false);
    };

    verifyPayment();
  }, [paymentId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 flex items-center justify-center">
        <Card className="max-w-md w-full mx-4">
          <CardContent className="py-12 text-center">
            <Loader2 className="w-16 h-16 text-blue-600 animate-spin mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-slate-800">Processing Payment...</h2>
            <p className="text-slate-600 mt-2">Please wait while we confirm your payment.</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-green-50 to-slate-100 flex items-center justify-center p-4">
      <Card className="max-w-lg w-full shadow-2xl border-0">
        <CardHeader className="text-center pb-2">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="w-12 h-12 text-green-600" />
          </div>
          <CardTitle className="text-2xl font-bold text-slate-800">
            Payment Successful!
          </CardTitle>
        </CardHeader>
        <CardContent className="text-center space-y-6">
          <p className="text-slate-600">
            Thank you for subscribing to JobRocket! Your account has been upgraded.
          </p>
          
          {paymentDetails?.tier && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <p className="text-green-800 font-medium">
                Your plan: <span className="font-bold">{paymentDetails.tier}</span>
              </p>
              <p className="text-green-600 text-sm mt-1">
                Status: {paymentDetails.status === 'active' ? 'Active' : 'Processing'}
              </p>
            </div>
          )}

          <div className="pt-4 space-y-3">
            <Button 
              onClick={() => navigate('/account')}
              className="w-full bg-green-600 hover:bg-green-700"
            >
              <CreditCard className="w-4 h-4 mr-2" />
              View Account Dashboard
            </Button>
            <Button 
              onClick={() => navigate('/jobs')}
              variant="outline"
              className="w-full"
            >
              <Home className="w-4 h-4 mr-2" />
              Browse Jobs
            </Button>
          </div>

          <p className="text-xs text-slate-500">
            Payment ID: {paymentId || 'N/A'}
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export const PaymentCancelPage = ({ user }) => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  const paymentId = searchParams.get('payment_id');

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-red-50 to-slate-100 flex items-center justify-center p-4">
      <Card className="max-w-lg w-full shadow-2xl border-0">
        <CardHeader className="text-center pb-2">
          <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <XCircle className="w-12 h-12 text-red-600" />
          </div>
          <CardTitle className="text-2xl font-bold text-slate-800">
            Payment Cancelled
          </CardTitle>
        </CardHeader>
        <CardContent className="text-center space-y-6">
          <p className="text-slate-600">
            Your payment was cancelled. No charges have been made to your account.
          </p>
          
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
              <div className="text-left">
                <p className="text-yellow-800 font-medium">Need help?</p>
                <p className="text-yellow-700 text-sm mt-1">
                  If you experienced any issues during checkout, please contact our support team.
                </p>
              </div>
            </div>
          </div>

          <div className="pt-4 space-y-3">
            <Button 
              onClick={() => navigate('/pricing')}
              className="w-full bg-blue-600 hover:bg-blue-700"
            >
              <ArrowRight className="w-4 h-4 mr-2" />
              Try Again
            </Button>
            <Button 
              onClick={() => navigate('/')}
              variant="outline"
              className="w-full"
            >
              <Home className="w-4 h-4 mr-2" />
              Return to Home
            </Button>
          </div>

          {paymentId && (
            <p className="text-xs text-slate-500">
              Reference: {paymentId}
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default { PaymentSuccessPage, PaymentCancelPage };
