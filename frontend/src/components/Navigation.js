import React, { useState, useRef, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Button } from "./ui/button";
import { 
  Rocket, 
  Home, 
  Briefcase, 
  User, 
  Building2,
  Settings,
  LogOut,
  Menu,
  X,
  FileText,
  Banknote,
  Users,
  Shield,
  Bell,
  Search,
  CreditCard,
  FileSpreadsheet,
  BarChart3,
  ChevronDown,
  PieChart
} from "lucide-react";

const Navigation = ({ user, onLogout }) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isUserDropdownOpen, setIsUserDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);
  const location = useLocation();
  const navigate = useNavigate();

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsUserDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const handleLogout = () => {
    onLogout();
    navigate('/');
  };

  // Dropdown menu items for recruiters
  const getDropdownItems = () => {
    if (user?.role === 'recruiter') {
      return [
        { name: 'Billing', path: '/billing', icon: CreditCard },
        { name: 'Reports', path: '/reports', icon: PieChart }
      ];
    }
    return [];
  };

  const getNavItems = () => {
    const commonItems = [
      { name: 'Jobs', path: '/jobs', icon: Briefcase },
      { name: 'Profile', path: '/profile', icon: User }
    ];

    if (user?.role === 'recruiter') {
      const features = user?.account?.features || [];
      const hasBulkUpload = features.includes('JOB_BULK_UPLOAD');
      const items = [
        { name: 'Dashboard', path: '/', icon: Home },
        { name: 'Jobs', path: '/jobs', icon: Briefcase },
        { name: 'Jobs Dashboard', path: '/jobs-dashboard', icon: BarChart3 },
        { name: 'My Jobs', path: '/my-jobs', icon: Building2 },
      ];
      if (hasBulkUpload) {
        items.push({ name: 'Bulk Upload', path: '/bulk-upload', icon: FileSpreadsheet });
      }
      items.push(
        { name: 'CV Search', path: '/cv-search', icon: Search },
        { name: 'Applications', path: '/applications', icon: FileText }
        // Billing moved to dropdown
      );
      return items;
    } else if (user?.role === 'admin') {
      return [
        { name: 'Dashboard', path: '/', icon: Home },
        { name: 'Analytics', path: '/analytics', icon: BarChart3 },
        { name: 'Manage', path: '/manage-accounts', icon: Shield },
        { name: 'Jobs', path: '/jobs', icon: Briefcase },
        { name: 'Account', path: '/account', icon: Building2 },
        { name: 'Admin Panel', path: '/admin', icon: Settings },
        { name: 'Profile', path: '/profile', icon: User }
      ];
    } else {
      // Job seeker
      return [
        { name: 'Jobs', path: '/jobs', icon: Briefcase },
        { name: 'My Applications', path: '/my-applications', icon: FileText },
        { name: 'Profile', path: '/profile', icon: User },
        { name: 'Notifications', path: '/notifications', icon: Bell }
      ];
    }
  };

  const navItems = getNavItems();
  const dropdownItems = getDropdownItems();

  return (
    <nav className="bg-white shadow-lg border-b border-slate-200 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-2">
              <div className="bg-gradient-to-br from-blue-600 to-purple-600 p-2 rounded-lg">
                <Rocket className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Job Rocket
              </span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.name}
                  to={item.path}
                  className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-blue-100 text-blue-700 border border-blue-200'
                      : 'text-slate-600 hover:text-blue-600 hover:bg-slate-50'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </div>

          {/* User Menu with Dropdown */}
          <div className="hidden md:flex items-center space-x-4">
            {user && (
              <div className="relative" ref={dropdownRef}>
                <button
                  onClick={() => setIsUserDropdownOpen(!isUserDropdownOpen)}
                  className="flex items-center space-x-3 hover:bg-slate-50 rounded-lg px-3 py-2 transition-colors"
                  data-testid="user-dropdown-trigger"
                >
                  <div className="text-right">
                    <p className="text-sm font-medium text-slate-900">
                      {user.first_name} {user.last_name}
                    </p>
                    <p className="text-xs text-slate-500 capitalize">
                      {user.role?.replace('_', ' ')}
                    </p>
                  </div>
                  <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm font-medium">
                      {user.first_name?.charAt(0)}{user.last_name?.charAt(0)}
                    </span>
                  </div>
                  {dropdownItems.length > 0 && (
                    <ChevronDown className={`w-4 h-4 text-slate-500 transition-transform ${isUserDropdownOpen ? 'rotate-180' : ''}`} />
                  )}
                </button>

                {/* Dropdown Menu */}
                {isUserDropdownOpen && dropdownItems.length > 0 && (
                  <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-slate-200 py-2 z-50" data-testid="user-dropdown-menu">
                    {/* Dropdown Items */}
                    {dropdownItems.map((item) => {
                      const Icon = item.icon;
                      const isActive = location.pathname === item.path;
                      return (
                        <Link
                          key={item.name}
                          to={item.path}
                          onClick={() => setIsUserDropdownOpen(false)}
                          className={`flex items-center space-x-3 px-4 py-2.5 text-sm transition-colors ${
                            isActive
                              ? 'bg-blue-50 text-blue-700'
                              : 'text-slate-700 hover:bg-slate-50'
                          }`}
                          data-testid={`dropdown-${item.name.toLowerCase()}`}
                        >
                          <Icon className="w-4 h-4" />
                          <span>{item.name}</span>
                        </Link>
                      );
                    })}
                    
                    {/* Divider */}
                    <div className="border-t border-slate-200 my-2"></div>
                    
                    {/* Sign Out */}
                    <button
                      onClick={() => {
                        setIsUserDropdownOpen(false);
                        handleLogout();
                      }}
                      className="flex items-center space-x-3 px-4 py-2.5 text-sm text-slate-700 hover:bg-red-50 hover:text-red-600 w-full transition-colors"
                      data-testid="dropdown-signout"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Sign Out</span>
                    </button>
                  </div>
                )}

                {/* Non-recruiter: Just show logout button */}
                {dropdownItems.length === 0 && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleLogout}
                    className="text-slate-600 hover:text-red-600 ml-2"
                  >
                    <LogOut className="w-4 h-4" />
                  </Button>
                )}
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleMobileMenu}
              className="text-slate-600"
            >
              {isMobileMenuOpen ? (
                <X className="w-6 h-6" />
              ) : (
                <Menu className="w-6 h-6" />
              )}
            </Button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      {isMobileMenuOpen && (
        <div className="md:hidden bg-white border-t border-slate-200">
          <div className="px-2 pt-2 pb-3 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.name}
                  to={item.path}
                  onClick={() => setIsMobileMenuOpen(false)}
                  className={`flex items-center space-x-3 px-3 py-2 rounded-md text-base font-medium transition-colors ${
                    isActive
                      ? 'bg-blue-100 text-blue-700 border border-blue-200'
                      : 'text-slate-600 hover:text-blue-600 hover:bg-slate-50'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span>{item.name}</span>
                </Link>
              );
            })}

            {/* Mobile: Dropdown items as separate section for recruiters */}
            {dropdownItems.length > 0 && (
              <div className="border-t border-slate-200 mt-4 pt-4">
                <p className="px-3 py-1 text-xs font-semibold text-slate-400 uppercase tracking-wider">Account</p>
                {dropdownItems.map((item) => {
                  const Icon = item.icon;
                  const isActive = location.pathname === item.path;
                  return (
                    <Link
                      key={item.name}
                      to={item.path}
                      onClick={() => setIsMobileMenuOpen(false)}
                      className={`flex items-center space-x-3 px-3 py-2 rounded-md text-base font-medium transition-colors ${
                        isActive
                          ? 'bg-blue-100 text-blue-700 border border-blue-200'
                          : 'text-slate-600 hover:text-blue-600 hover:bg-slate-50'
                      }`}
                    >
                      <Icon className="w-5 h-5" />
                      <span>{item.name}</span>
                    </Link>
                  );
                })}
              </div>
            )}
            
            {user && (
              <div className="border-t border-slate-200 mt-4 pt-4">
                <div className="flex items-center px-3 py-2">
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mr-3">
                    <span className="text-white font-medium">
                      {user.first_name?.charAt(0)}{user.last_name?.charAt(0)}
                    </span>
                  </div>
                  <div>
                    <p className="text-base font-medium text-slate-900">
                      {user.first_name} {user.last_name}
                    </p>
                    <p className="text-sm text-slate-500 capitalize">
                      {user.role?.replace('_', ' ')}
                    </p>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  onClick={() => {
                    handleLogout();
                    setIsMobileMenuOpen(false);
                  }}
                  className="w-full justify-start text-slate-600 hover:text-red-600 mt-2"
                >
                  <LogOut className="w-4 h-4 mr-2" />
                  Sign Out
                </Button>
              </div>
            )}
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navigation;