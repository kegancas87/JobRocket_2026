import React, { useState } from 'react';
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
  Search
} from "lucide-react";

const Navigation = ({ user, onLogout }) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const handleLogout = () => {
    onLogout();
    navigate('/');
  };

  const getNavItems = () => {
    const commonItems = [
      { name: 'Jobs', path: '/jobs', icon: Briefcase },
      { name: 'Profile', path: '/profile', icon: User }
    ];

    if (user?.role === 'recruiter') {
      return [
        { name: 'Dashboard', path: '/', icon: Home },
        { name: 'Jobs', path: '/jobs', icon: Briefcase },
        { name: 'My Jobs', path: '/my-jobs', icon: Building2 },
        { name: 'CV Search', path: '/cv-search', icon: Search },
        { name: 'Applications', path: '/applications', icon: FileText },
        { name: 'Pricing', path: '/pricing', icon: Banknote },
        { name: 'Profile', path: '/profile', icon: User }
      ];
    } else if (user?.role === 'admin') {
      return [
        { name: 'Dashboard', path: '/', icon: Home },
        { name: 'Jobs', path: '/jobs', icon: Briefcase },
        { name: 'Admin Panel', path: '/admin', icon: Shield },
        { name: 'Users', path: '/users', icon: Users },
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

          {/* User Menu */}
          <div className="hidden md:flex items-center space-x-4">
            {user && (
              <div className="flex items-center space-x-3">
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
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleLogout}
                  className="text-slate-600 hover:text-red-600"
                >
                  <LogOut className="w-4 h-4" />
                </Button>
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