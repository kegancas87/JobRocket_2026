import React, { useState, useEffect } from 'react';
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Label } from "./ui/label";
import { 
  Building2, 
  MapPin, 
  Mail, 
  Phone,
  Plus,
  Edit2,
  Trash2,
  Users,
  UserPlus,
  Send,
  X,
  CheckCircle,
  Clock,
  XCircle,
  Settings,
  Crown,
  Shield,
  Eye
} from "lucide-react";
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CompanyStructure = ({ user, onUpdateUser }) => {
  const [branches, setBranches] = useState([]);
  const [teamMembers, setTeamMembers] = useState([]);
  const [invitations, setInvitations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeSection, setActiveSection] = useState('branches');
  
  // Form states
  const [showAddBranch, setShowAddBranch] = useState(false);
  const [showInviteUser, setShowInviteUser] = useState(false);
  const [editingBranch, setEditingBranch] = useState(null);
  
  const [branchForm, setBranchForm] = useState({
    name: '',
    location: '',
    email: '',
    phone: '',
    is_headquarters: false
  });
  
  const [inviteForm, setInviteForm] = useState({
    email: '',
    first_name: '',
    last_name: '',
    role: 'recruiter',
    branch_ids: []
  });

  const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    return {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    };
  };

  const fetchBranches = async () => {
    try {
      const response = await axios.get(`${API}/company/branches`, getAuthHeaders());
      setBranches(response.data);
    } catch (error) {
      console.error('Error fetching branches:', error);
    }
  };

  const fetchTeamMembers = async () => {
    try {
      const response = await axios.get(`${API}/company/members`, getAuthHeaders());
      setTeamMembers(response.data);
    } catch (error) {
      console.error('Error fetching team members:', error);
    }
  };

  const fetchInvitations = async () => {
    try {
      const response = await axios.get(`${API}/company/invitations`, getAuthHeaders());
      setInvitations(response.data);
    } catch (error) {
      console.error('Error fetching invitations:', error);
    }
  };

  const fetchAllData = async () => {
    await Promise.all([fetchBranches(), fetchTeamMembers(), fetchInvitations()]);
  };

  useEffect(() => {
    fetchAllData();
  }, []);

  const handleAddBranch = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await axios.post(`${API}/company/branches`, branchForm, getAuthHeaders());
      setBranchForm({ name: '', location: '', email: '', phone: '', is_headquarters: false });
      setShowAddBranch(false);
      fetchBranches();
      onUpdateUser(); // Refresh user data to update progress
    } catch (error) {
      console.error('Error adding branch:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateBranch = async (branchId, updatedData) => {
    setLoading(true);
    
    try {
      await axios.put(`${API}/company/branches/${branchId}`, updatedData, getAuthHeaders());
      setEditingBranch(null);
      fetchBranches();
    } catch (error) {
      console.error('Error updating branch:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteBranch = async (branchId) => {
    if (!confirm('Are you sure you want to delete this branch?')) return;
    
    setLoading(true);
    
    try {
      await axios.delete(`${API}/company/branches/${branchId}`, getAuthHeaders());
      fetchBranches();
      fetchTeamMembers(); // Refresh to update branch associations
    } catch (error) {
      console.error('Error deleting branch:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInviteUser = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      const response = await axios.post(`${API}/company/invite`, inviteForm, getAuthHeaders());
      
      // Show success message with invitation link
      const invitationLink = `${window.location.origin}/invitation/${response.data.invitation_token}`;
      
      alert(`Invitation sent successfully! 

Share this link with ${inviteForm.first_name} ${inviteForm.last_name}:
${invitationLink}

Note: This link will expire in 7 days.`);
      
      // Reset form
      setInviteForm({
        email: '',
        first_name: '',
        last_name: '',
        role: 'recruiter',
        branch_ids: []
      });
      setShowInviteUser(false);
      
      // Refresh invitations list
      await fetchInvitations();
      onUpdateUser(); // Refresh user data to update progress
      
    } catch (error) {
      console.error('Error inviting user:', error);
      alert(error.response?.data?.detail || 'Failed to send invitation');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelInvitation = async (invitationId) => {
    try {
      await axios.post(`${API}/company/invitations/${invitationId}/cancel`, {}, getAuthHeaders());
      fetchInvitations();
    } catch (error) {
      console.error('Error cancelling invitation:', error);
    }
  };

  const handleBranchSelection = (branchId, checked) => {
    if (checked) {
      setInviteForm(prev => ({
        ...prev,
        branch_ids: [...prev.branch_ids, branchId]
      }));
    } else {
      setInviteForm(prev => ({
        ...prev,
        branch_ids: prev.branch_ids.filter(id => id !== branchId)
      }));
    }
  };

  const getRoleIcon = (role) => {
    switch (role) {
      case 'admin': return <Crown className="w-4 h-4" />;
      case 'manager': return <Shield className="w-4 h-4" />;
      case 'recruiter': return <Users className="w-4 h-4" />;
      case 'viewer': return <Eye className="w-4 h-4" />;
      default: return <Users className="w-4 h-4" />;
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending': return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'accepted': return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'cancelled': return <XCircle className="w-4 h-4 text-red-500" />;
      case 'expired': return <X className="w-4 h-4 text-gray-500" />;
      default: return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Section Navigation */}
      <div className="flex space-x-1 bg-white/60 backdrop-blur-sm rounded-2xl p-2">
        <Button
          variant={activeSection === 'branches' ? 'default' : 'ghost'}
          onClick={() => setActiveSection('branches')}
          className="flex items-center space-x-2 rounded-xl"
        >
          <Building2 className="w-4 h-4" />
          <span>Branches ({branches.length})</span>
        </Button>
        <Button
          variant={activeSection === 'team' ? 'default' : 'ghost'}
          onClick={() => setActiveSection('team')}
          className="flex items-center space-x-2 rounded-xl"
        >
          <Users className="w-4 h-4" />
          <span>Team ({teamMembers.length})</span>
        </Button>
        <Button
          variant={activeSection === 'invitations' ? 'default' : 'ghost'}
          onClick={() => setActiveSection('invitations')}
          className="flex items-center space-x-2 rounded-xl"
        >
          <Send className="w-4 h-4" />
          <span>Invitations ({invitations.filter(inv => inv.status === 'pending').length})</span>
        </Button>
      </div>

      {/* Branches Section */}
      {activeSection === 'branches' && (
        <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center space-x-2">
                <Building2 className="w-5 h-5 text-blue-600" />
                <span>Company Branches</span>
              </CardTitle>
              <Button
                onClick={() => setShowAddBranch(!showAddBranch)}
                className="bg-gradient-to-r from-blue-600 to-slate-700 hover:from-blue-700 hover:to-slate-800"
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Branch
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {/* Add Branch Form */}
            {showAddBranch && (
              <div className="mb-6 p-6 bg-blue-50 rounded-xl border border-blue-200">
                <h4 className="font-semibold text-slate-800 mb-4">Add New Branch</h4>
                <form onSubmit={handleAddBranch} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="branch_name">Branch Name</Label>
                      <Input
                        id="branch_name"
                        value={branchForm.name}
                        onChange={(e) => setBranchForm(prev => ({ ...prev, name: e.target.value }))}
                        placeholder="e.g., Johannesburg Office"
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="branch_location">Location</Label>
                      <Input
                        id="branch_location"
                        value={branchForm.location}
                        onChange={(e) => setBranchForm(prev => ({ ...prev, location: e.target.value }))}
                        placeholder="e.g., Sandton, Johannesburg"
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="branch_email">Email (Optional)</Label>
                      <Input
                        id="branch_email"
                        type="email"
                        value={branchForm.email}
                        onChange={(e) => setBranchForm(prev => ({ ...prev, email: e.target.value }))}
                        placeholder="branch@company.com"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="branch_phone">Phone (Optional)</Label>
                      <Input
                        id="branch_phone"
                        value={branchForm.phone}
                        onChange={(e) => setBranchForm(prev => ({ ...prev, phone: e.target.value }))}
                        placeholder="+27 11 123 4567"
                      />
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="is_headquarters"
                      checked={branchForm.is_headquarters}
                      onChange={(e) => setBranchForm(prev => ({ ...prev, is_headquarters: e.target.checked }))}
                      className="w-4 h-4 text-blue-600"
                    />
                    <Label htmlFor="is_headquarters">Mark as Headquarters</Label>
                  </div>
                  
                  <div className="flex space-x-3">
                    <Button type="submit" disabled={loading}>
                      {loading ? 'Adding...' : 'Add Branch'}
                    </Button>
                    <Button 
                      type="button" 
                      variant="outline"
                      onClick={() => setShowAddBranch(false)}
                    >
                      Cancel
                    </Button>
                  </div>
                </form>
              </div>
            )}

            {/* Branches List */}
            <div className="space-y-4">
              {branches.length === 0 ? (
                <div className="text-center py-12">
                  <Building2 className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-slate-800 mb-2">No branches yet</h3>
                  <p className="text-slate-600 mb-4">Add your first branch to organize your company structure</p>
                </div>
              ) : (
                branches.map((branch) => (
                  <div key={branch.id} className="p-6 border border-slate-200 rounded-xl hover:shadow-md transition-all">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-3">
                          <Building2 className="w-5 h-5 text-blue-600" />
                          <h4 className="text-lg font-semibold text-slate-800">{branch.name}</h4>
                          {branch.is_headquarters && (
                            <Badge className="bg-yellow-100 text-yellow-800 border-yellow-200">
                              Headquarters
                            </Badge>
                          )}
                        </div>
                        
                        <div className="space-y-2 text-sm text-slate-600">
                          <div className="flex items-center space-x-2">
                            <MapPin className="w-4 h-4" />
                            <span>{branch.location}</span>
                          </div>
                          {branch.email && (
                            <div className="flex items-center space-x-2">
                              <Mail className="w-4 h-4" />
                              <span>{branch.email}</span>
                            </div>
                          )}
                          {branch.phone && (
                            <div className="flex items-center space-x-2">
                              <Phone className="w-4 h-4" />
                              <span>{branch.phone}</span>
                            </div>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex space-x-2 ml-4">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setEditingBranch(branch)}
                        >
                          <Edit2 className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDeleteBranch(branch.id)}
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Team Members Section */}
      {activeSection === 'team' && (
        <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center space-x-2">
                <Users className="w-5 h-5 text-blue-600" />
                <span>Team Members</span>
              </CardTitle>
              <Button
                onClick={() => setShowInviteUser(!showInviteUser)}
                className="bg-gradient-to-r from-blue-600 to-slate-700 hover:from-blue-700 hover:to-slate-800"
              >
                <UserPlus className="w-4 h-4 mr-2" />
                Invite Member
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {/* Invite User Form */}
            {showInviteUser && (
              <div className="mb-6 p-6 bg-green-50 rounded-xl border border-green-200">
                <h4 className="font-semibold text-slate-800 mb-4">Invite Team Member</h4>
                <form onSubmit={handleInviteUser} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="invite_first_name">First Name</Label>
                      <Input
                        id="invite_first_name"
                        value={inviteForm.first_name}
                        onChange={(e) => setInviteForm(prev => ({ ...prev, first_name: e.target.value }))}
                        placeholder="John"
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="invite_last_name">Last Name</Label>
                      <Input
                        id="invite_last_name"
                        value={inviteForm.last_name}
                        onChange={(e) => setInviteForm(prev => ({ ...prev, last_name: e.target.value }))}
                        placeholder="Doe"
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="invite_email">Email</Label>
                      <Input
                        id="invite_email"
                        type="email"
                        value={inviteForm.email}
                        onChange={(e) => setInviteForm(prev => ({ ...prev, email: e.target.value }))}
                        placeholder="john.doe@company.com"
                        required
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="invite_role">Role</Label>
                    <select
                      id="invite_role"
                      value={inviteForm.role}
                      onChange={(e) => setInviteForm(prev => ({ ...prev, role: e.target.value }))}
                      className="w-full h-10 px-3 border border-slate-300 rounded-md focus:border-blue-500 focus:ring-blue-500 bg-white"
                    >
                      <option value="recruiter">Recruiter</option>
                      <option value="manager">Manager</option>
                      <option value="admin">Admin</option>
                      <option value="viewer">Viewer</option>
                    </select>
                  </div>

                  {branches.length > 0 && (
                    <div className="space-y-2">
                      <Label>Assign to Branches (Optional)</Label>
                      <div className="grid grid-cols-2 gap-3">
                        {branches.map((branch) => (
                          <label key={branch.id} className="flex items-center space-x-2 cursor-pointer">
                            <input
                              type="checkbox"
                              checked={inviteForm.branch_ids.includes(branch.id)}
                              onChange={(e) => handleBranchSelection(branch.id, e.target.checked)}
                              className="w-4 h-4 text-blue-600"
                            />
                            <span className="text-sm text-slate-700">{branch.name}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  <div className="flex space-x-3">
                    <Button type="submit" disabled={loading}>
                      {loading ? 'Sending...' : 'Send Invitation'}
                    </Button>
                    <Button 
                      type="button" 
                      variant="outline"
                      onClick={() => setShowInviteUser(false)}
                    >
                      Cancel
                    </Button>
                  </div>
                </form>
              </div>
            )}

            {/* Team Members List */}
            <div className="space-y-4">
              {teamMembers.length === 0 ? (
                <div className="text-center py-12">
                  <Users className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-slate-800 mb-2">No team members yet</h3>
                  <p className="text-slate-600 mb-4">Invite your first team member to start collaborating</p>
                </div>
              ) : (
                teamMembers.map((member) => {
                  const user = member.user || {};
                  const firstName = user.first_name || 'Unknown';
                  const lastName = user.last_name || 'User';
                  const email = user.email || 'No email';
                  
                  return (
                  <div key={member.member_id} className="p-6 border border-slate-200 rounded-xl hover:shadow-md transition-all">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-gradient-to-br from-blue-100 to-slate-200 rounded-full flex items-center justify-center">
                          <span className="font-bold text-slate-700">
                            {firstName[0]}{lastName[0]}
                          </span>
                        </div>
                        <div>
                          <h4 className="font-semibold text-slate-800">
                            {firstName} {lastName}
                          </h4>
                          <p className="text-sm text-slate-600">{email}</p>
                          <div className="flex items-center space-x-3 mt-1">
                            <div className="flex items-center space-x-1">
                              {getRoleIcon(member.role)}
                              <span className="text-sm text-slate-600 capitalize">{member.role}</span>
                            </div>
                            {member.branches && member.branches.length > 0 && (
                              <div className="flex items-center space-x-1">
                                <Building2 className="w-3 h-3 text-slate-500" />
                                <span className="text-xs text-slate-500">
                                  {member.branches.length} branch{member.branches.length !== 1 ? 'es' : ''}
                                </span>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        className="text-slate-600 hover:text-slate-700"
                      >
                        <Settings className="w-4 h-4" />
                      </Button>
                    </div>
                    
                    {member.branches.length > 0 && (
                      <div className="mt-4 pt-4 border-t border-slate-200">
                        <p className="text-sm font-medium text-slate-700 mb-2">Assigned Branches:</p>
                        <div className="flex flex-wrap gap-2">
                          {member.branches.map((branch) => (
                            <Badge key={branch.id} variant="outline" className="text-xs">
                              {branch.name}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Invitations Section */}
      {activeSection === 'invitations' && (
        <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Send className="w-5 h-5 text-blue-600" />
              <span>Pending Invitations</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {invitations.length === 0 ? (
                <div className="text-center py-12">
                  <Send className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-slate-800 mb-2">No invitations sent</h3>
                  <p className="text-slate-600">Invite team members to see them here</p>
                </div>
              ) : (
                invitations.map((invitation) => (
                  <div key={invitation.id} className="p-6 border border-slate-200 rounded-xl">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-gradient-to-br from-slate-100 to-slate-200 rounded-full flex items-center justify-center">
                          <span className="font-bold text-slate-700">
                            {invitation.first_name[0]}{invitation.last_name[0]}
                          </span>
                        </div>
                        <div>
                          <h4 className="font-semibold text-slate-800">
                            {invitation.first_name} {invitation.last_name}
                          </h4>
                          <p className="text-sm text-slate-600">{invitation.email}</p>
                          <div className="flex items-center space-x-3 mt-1">
                            <div className="flex items-center space-x-1">
                              {getStatusIcon(invitation.status)}
                              <span className="text-sm text-slate-600 capitalize">{invitation.status}</span>
                            </div>
                            <div className="flex items-center space-x-1">
                              {getRoleIcon(invitation.role)}
                              <span className="text-sm text-slate-600 capitalize">{invitation.role}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      {invitation.status === 'pending' && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleCancelInvitation(invitation.id)}
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        >
                          <X className="w-4 h-4 mr-1" />
                          Cancel
                        </Button>
                      )}
                    </div>
                    
                    <div className="mt-4 pt-4 border-t border-slate-200 text-sm text-slate-500">
                      <p>Invited on: {new Date(invitation.created_at).toLocaleDateString()}</p>
                      <p>Expires: {new Date(invitation.expires_at).toLocaleDateString()}</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default CompanyStructure;