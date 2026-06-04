import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Lock, Eye, EyeOff, CheckCircle, AlertCircle, Loader2, Settings, CreditCard, Zap, Trash2, ExternalLink } from "lucide-react";
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SettingsPage = ({ user }) => {
  // Password state
  const [passwordForm, setPasswordForm] = useState({ current_password: '', new_password: '', confirm_password: '' });
  const [showCurrentPw, setShowCurrentPw] = useState(false);
  const [showNewPw, setShowNewPw] = useState(false);
  const [pwLoading, setPwLoading] = useState(false);
  const [pwMsg, setPwMsg] = useState({ type: '', text: '' });

  // Auto top-up state
  const [cardStatus, setCardStatus] = useState({ has_card: false, saved_at: null });
  const [topupSettings, setTopupSettings] = useState({ enabled: false, threshold: 50, amount: 200 });
  const [topupLoading, setTopupLoading] = useState(false);
  const [topupMsg, setTopupMsg] = useState({ type: '', text: '' });
  const [cardLoading, setCardLoading] = useState(false);
  const [removeCardLoading, setRemoveCardLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);

  const token = localStorage.getItem('token');
  const headers = { Authorization: `Bearer ${token}` };

  const loadCardSettings = useCallback(async () => {
    try {
      const [statusRes, settingsRes] = await Promise.all([
        axios.get(`${API}/ai/wallet/card-status`, { headers }),
        axios.get(`${API}/ai/wallet/auto-topup`, { headers }),
      ]);
      setCardStatus(statusRes.data);
      setTopupSettings({
        enabled: settingsRes.data.enabled,
        threshold: settingsRes.data.threshold,
        amount: settingsRes.data.amount,
      });
    } catch {
      // Silently handle — user may not have wallet features
    } finally {
      setInitialLoading(false);
    }
  }, []);

  useEffect(() => {
    if (user?.role === 'job_seeker') loadCardSettings();
    else setInitialLoading(false);
  }, [user, loadCardSettings]);

  // Check URL params for card save result
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('card_saved') === 'true') {
      setTopupMsg({ type: 'success', text: 'Card saved successfully! You can now enable auto top-up.' });
      loadCardSettings();
      window.history.replaceState({}, '', '/settings');
    } else if (params.get('card_saved') === 'false') {
      setTopupMsg({ type: 'error', text: 'Card setup was cancelled.' });
      window.history.replaceState({}, '', '/settings');
    }
  }, [loadCardSettings]);

  const handleChangePassword = async () => {
    setPwMsg({ type: '', text: '' });
    const { current_password, new_password, confirm_password } = passwordForm;
    if (!current_password || !new_password) { setPwMsg({ type: 'error', text: 'Please fill in all fields' }); return; }
    if (new_password.length < 6) { setPwMsg({ type: 'error', text: 'New password must be at least 6 characters' }); return; }
    if (new_password !== confirm_password) { setPwMsg({ type: 'error', text: 'New passwords do not match' }); return; }
    setPwLoading(true);
    try {
      await axios.post(`${API}/auth/change-password`, { current_password, new_password }, { headers });
      setPwMsg({ type: 'success', text: 'Password changed successfully!' });
      setPasswordForm({ current_password: '', new_password: '', confirm_password: '' });
    } catch (err) {
      setPwMsg({ type: 'error', text: err.response?.data?.detail || 'Failed to change password' });
    } finally { setPwLoading(false); }
  };

  const handleSetupCard = async () => {
    setCardLoading(true);
    try {
      const res = await axios.post(`${API}/ai/wallet/setup-card`, {}, { headers });
      const { form_data, action_url } = res.data;
      // Create and submit a hidden form to PayFast
      const form = document.createElement('form');
      form.method = 'POST';
      form.action = action_url;
      Object.entries(form_data).forEach(([key, value]) => {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = key;
        input.value = value;
        form.appendChild(input);
      });
      document.body.appendChild(form);
      form.submit();
    } catch (err) {
      setTopupMsg({ type: 'error', text: err.response?.data?.detail || 'Failed to setup card' });
      setCardLoading(false);
    }
  };

  const handleRemoveCard = async () => {
    if (!window.confirm('Remove saved card? This will also disable auto top-up.')) return;
    setRemoveCardLoading(true);
    try {
      await axios.delete(`${API}/ai/wallet/remove-card`, { headers });
      setCardStatus({ has_card: false, saved_at: null });
      setTopupSettings(prev => ({ ...prev, enabled: false }));
      setTopupMsg({ type: 'success', text: 'Card removed and auto top-up disabled.' });
    } catch (err) {
      setTopupMsg({ type: 'error', text: err.response?.data?.detail || 'Failed to remove card' });
    } finally { setRemoveCardLoading(false); }
  };

  const handleSaveTopup = async () => {
    setTopupMsg({ type: '', text: '' });
    setTopupLoading(true);
    try {
      const res = await axios.post(`${API}/ai/wallet/auto-topup`, topupSettings, { headers });
      setTopupMsg({ type: 'success', text: res.data.enabled ? 'Auto top-up enabled!' : 'Settings saved.' });
    } catch (err) {
      setTopupMsg({ type: 'error', text: err.response?.data?.detail || 'Failed to save settings' });
    } finally { setTopupLoading(false); }
  };

  const isJobSeeker = user?.role === 'job_seeker';

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100" data-testid="settings-page">
      <div className="max-w-2xl mx-auto px-4 py-8 space-y-6">
        <div className="flex items-center gap-3">
          <Settings className="w-6 h-6 text-blue-600" />
          <h1 className="text-2xl font-bold text-slate-900">Account Settings</h1>
        </div>

        {/* Change Password */}
        <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
          <CardHeader><CardTitle className="flex items-center space-x-2"><Lock className="w-5 h-5 text-blue-600" /><span>Change Password</span></CardTitle></CardHeader>
          <CardContent>
            <div className="max-w-md space-y-4">
              {pwMsg.text && (
                <div className={`flex items-center gap-2 p-3 rounded-lg text-sm ${pwMsg.type === 'success' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-red-50 text-red-700 border border-red-200'}`} data-testid="password-change-msg">
                  {pwMsg.type === 'success' ? <CheckCircle className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
                  {pwMsg.text}
                </div>
              )}
              <div className="space-y-2">
                <Label htmlFor="settings_current_password">Current Password</Label>
                <div className="relative">
                  <Input id="settings_current_password" type={showCurrentPw ? 'text' : 'password'} value={passwordForm.current_password}
                    onChange={(e) => setPasswordForm(prev => ({ ...prev, current_password: e.target.value }))} placeholder="Enter current password" data-testid="settings-current-password-input" />
                  <button type="button" onClick={() => setShowCurrentPw(!showCurrentPw)} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
                    {showCurrentPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="settings_new_password">New Password</Label>
                <div className="relative">
                  <Input id="settings_new_password" type={showNewPw ? 'text' : 'password'} value={passwordForm.new_password}
                    onChange={(e) => setPasswordForm(prev => ({ ...prev, new_password: e.target.value }))} placeholder="At least 6 characters" data-testid="settings-new-password-input" />
                  <button type="button" onClick={() => setShowNewPw(!showNewPw)} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
                    {showNewPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="settings_confirm_password">Confirm New Password</Label>
                <Input id="settings_confirm_password" type="password" value={passwordForm.confirm_password}
                  onChange={(e) => setPasswordForm(prev => ({ ...prev, confirm_password: e.target.value }))} placeholder="Re-enter new password" data-testid="settings-confirm-password-input" />
              </div>
              <Button onClick={handleChangePassword} disabled={pwLoading} className="bg-blue-600 hover:bg-blue-700" data-testid="settings-change-password-btn">
                {pwLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Lock className="w-4 h-4 mr-2" />}
                Change Password
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Auto Top-Up - Only for Job Seekers */}
        {isJobSeeker && !initialLoading && (
          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl" data-testid="auto-topup-card">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Zap className="w-5 h-5 text-amber-500" />
                <span>Wallet Auto Top-Up</span>
              </CardTitle>
              <p className="text-sm text-slate-500 mt-1">
                Never run out of AI credits. Save your card and automatically top up when your balance drops below a threshold.
              </p>
            </CardHeader>
            <CardContent>
              <div className="space-y-5">
                {topupMsg.text && (
                  <div className={`flex items-center gap-2 p-3 rounded-lg text-sm ${topupMsg.type === 'success' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-red-50 text-red-700 border border-red-200'}`} data-testid="topup-msg">
                    {topupMsg.type === 'success' ? <CheckCircle className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
                    {topupMsg.text}
                  </div>
                )}

                {/* Card Status */}
                <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${cardStatus.has_card ? 'bg-emerald-100' : 'bg-slate-200'}`}>
                        <CreditCard className={`w-5 h-5 ${cardStatus.has_card ? 'text-emerald-600' : 'text-slate-400'}`} />
                      </div>
                      <div>
                        <p className="font-medium text-slate-800" data-testid="card-status-text">
                          {cardStatus.has_card ? 'Card on file' : 'No card saved'}
                        </p>
                        {cardStatus.has_card && cardStatus.saved_at && (
                          <p className="text-xs text-slate-500">Saved {new Date(cardStatus.saved_at).toLocaleDateString()}</p>
                        )}
                      </div>
                    </div>
                    {cardStatus.has_card ? (
                      <Button variant="outline" size="sm" onClick={handleRemoveCard} disabled={removeCardLoading}
                        className="text-red-600 border-red-200 hover:bg-red-50" data-testid="remove-card-btn">
                        {removeCardLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4 mr-1" />}
                        Remove
                      </Button>
                    ) : (
                      <Button onClick={handleSetupCard} disabled={cardLoading}
                        className="bg-blue-600 hover:bg-blue-700" data-testid="setup-card-btn">
                        {cardLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <ExternalLink className="w-4 h-4 mr-2" />}
                        Save Card via PayFast
                      </Button>
                    )}
                  </div>
                </div>

                {/* Auto Top-Up Settings */}
                <div className={`space-y-4 ${!cardStatus.has_card ? 'opacity-50 pointer-events-none' : ''}`}>
                  <div className="flex items-center justify-between">
                    <Label className="text-base font-medium">Enable Auto Top-Up</Label>
                    <button
                      onClick={() => setTopupSettings(prev => ({ ...prev, enabled: !prev.enabled }))}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${topupSettings.enabled ? 'bg-blue-600' : 'bg-slate-300'}`}
                      data-testid="auto-topup-toggle"
                    >
                      <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${topupSettings.enabled ? 'translate-x-6' : 'translate-x-1'}`} />
                    </button>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="threshold">When balance drops below</Label>
                      <div className="relative">
                        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 font-medium">R</span>
                        <Input id="threshold" type="number" min={0} max={5000} value={topupSettings.threshold}
                          onChange={(e) => setTopupSettings(prev => ({ ...prev, threshold: Number(e.target.value) }))}
                          className="pl-8" data-testid="topup-threshold-input" />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="topup_amount">Top up with</Label>
                      <div className="relative">
                        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 font-medium">R</span>
                        <Input id="topup_amount" type="number" min={5} max={10000} value={topupSettings.amount}
                          onChange={(e) => setTopupSettings(prev => ({ ...prev, amount: Number(e.target.value) }))}
                          className="pl-8" data-testid="topup-amount-input" />
                      </div>
                    </div>
                  </div>

                  {topupSettings.enabled && (
                    <p className="text-sm text-blue-600 bg-blue-50 p-3 rounded-lg">
                      When your wallet drops below <strong>R{topupSettings.threshold}</strong>, your saved card will be charged <strong>R{topupSettings.amount}</strong> automatically.
                    </p>
                  )}

                  <Button onClick={handleSaveTopup} disabled={topupLoading} className="bg-blue-600 hover:bg-blue-700" data-testid="save-topup-btn">
                    {topupLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Zap className="w-4 h-4 mr-2" />}
                    Save Auto Top-Up Settings
                  </Button>
                </div>

                {!cardStatus.has_card && (
                  <p className="text-sm text-slate-500 text-center">Save a card first to configure auto top-up settings.</p>
                )}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default SettingsPage;
