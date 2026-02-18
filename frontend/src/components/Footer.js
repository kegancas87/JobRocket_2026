import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Rocket,
  Mail,
  Phone,
  MapPin,
  Facebook,
  Twitter,
  Linkedin,
  Instagram,
  Heart
} from "lucide-react";

const Footer = ({ user }) => {
  const currentYear = new Date().getFullYear();

  const getFooterLinks = () => {
    const commonLinks = [
      { name: 'About Us', href: '/about' },
      { name: 'Contact', href: '/contact' },
      { name: 'Privacy Policy', href: '/privacy-policy' },
      { name: 'Terms of Service', href: '/terms-of-service' }
    ];

    if (user?.role === 'recruiter') {
      return {
        'For Recruiters': [
          { name: 'Post Jobs', href: '/post-job' },
          { name: 'Pricing Plans', href: '/pricing' },
          { name: 'Manage Applications', href: '/applications' },
          { name: 'Company Profile', href: '/profile' }
        ],
        'Job Seekers': [
          { name: 'Browse Jobs', href: '/jobs' },
          { name: 'Career Resources', href: '/resources' },
          { name: 'Resume Tips', href: '/resume-tips' },
          { name: 'Interview Prep', href: '/interview-prep' }
        ],
        'Support': commonLinks
      };
    } else if (user?.role === 'admin') {
      return {
        'Administration': [
          { name: 'Admin Dashboard', href: '/admin' },
          { name: 'User Management', href: '/users' },
          { name: 'System Analytics', href: '/analytics' },
          { name: 'Content Management', href: '/content' }
        ],
        'Platform': [
          { name: 'Browse Jobs', href: '/jobs' },
          { name: 'For Recruiters', href: '/pricing' },
          { name: 'API Documentation', href: '/api-docs' },
          { name: 'Developer Resources', href: '/developers' }
        ],
        'Legal': commonLinks
      };
    } else {
      // Job seeker or guest
      return {
        'Job Seekers': [
          { name: 'Browse Jobs', href: '/jobs' },
          { name: 'My Applications', href: '/my-applications' },
          { name: 'Career Resources', href: '/resources' },
          { name: 'Resume Builder', href: '/resume-builder' }
        ],
        'For Employers': [
          { name: 'Post Jobs', href: '/post-job' },
          { name: 'Pricing Plans', href: '/pricing' },
          { name: 'Recruiter Tools', href: '/recruiter-tools' },
          { name: 'Success Stories', href: '/success-stories' }
        ],
        'Company': commonLinks
      };
    }
  };

  const footerSections = getFooterLinks();

  return (
    <footer className="bg-slate-900 text-white mt-auto">
      {/* Main Footer Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Brand Section */}
          <div className="lg:col-span-1">
            <div className="flex items-center space-x-2 mb-4">
              <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-2 rounded-lg">
                <Rocket className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold text-white">
                Job Rocket
              </span>
            </div>
            <p className="text-slate-400 text-sm mb-6 max-w-xs">
              Launch your career to new heights with South Africa's most innovative job platform. 
              Connecting talent with opportunity.
            </p>
            
            {/* Contact Info */}
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <Mail className="w-4 h-4 text-slate-400" />
                <span className="text-sm text-slate-400">info@jobrocket.co.za</span>
              </div>
              <div className="flex items-center space-x-2">
                <Phone className="w-4 h-4 text-slate-400" />
                <span className="text-sm text-slate-400">+27 11 123 4567</span>
              </div>
              <div className="flex items-center space-x-2">
                <MapPin className="w-4 h-4 text-slate-400" />
                <span className="text-sm text-slate-400">Johannesburg, South Africa</span>
              </div>
            </div>
          </div>

          {/* Dynamic Footer Links */}
          {Object.entries(footerSections).map(([sectionTitle, links]) => (
            <div key={sectionTitle}>
              <h3 className="text-white font-semibold mb-4">{sectionTitle}</h3>
              <ul className="space-y-2">
                {links.map((link) => (
                  <li key={link.name}>
                    <Link
                      to={link.href}
                      className="text-slate-400 hover:text-white text-sm transition-colors duration-200"
                    >
                      {link.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Newsletter Signup */}
        <div className="border-t border-slate-800 mt-12 pt-8">
          <div className="max-w-md">
            <h3 className="text-white font-semibold mb-4">Stay Updated</h3>
            <p className="text-slate-400 text-sm mb-4">
              Get the latest job opportunities and career insights delivered to your inbox.
            </p>
            <div className="flex">
              <input
                type="email"
                placeholder="Enter your email"
                className="flex-1 bg-slate-800 border border-slate-700 rounded-l-md px-4 py-2 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button className="bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-2 rounded-r-md font-medium hover:from-blue-700 hover:to-purple-700 transition-all duration-200">
                Subscribe
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            {/* Copyright */}
            <div className="flex items-center space-x-1 text-slate-400 text-sm">
              <span>© {currentYear} Job Rocket. Made with</span>
              <Heart className="w-4 h-4 text-red-500 fill-current" />
              <span>in South Africa. All rights reserved.</span>
            </div>

            {/* Social Links */}
            <div className="flex items-center space-x-4">
              <a
                href="https://facebook.com/jobrocket"
                target="_blank"
                rel="noopener noreferrer"
                className="text-slate-400 hover:text-white transition-colors duration-200"
              >
                <Facebook className="w-5 h-5" />
              </a>
              <a
                href="https://twitter.com/jobrocket"
                target="_blank"
                rel="noopener noreferrer"
                className="text-slate-400 hover:text-white transition-colors duration-200"
              >
                <Twitter className="w-5 h-5" />
              </a>
              <a
                href="https://linkedin.com/company/jobrocket"
                target="_blank"
                rel="noopener noreferrer"
                className="text-slate-400 hover:text-white transition-colors duration-200"
              >
                <Linkedin className="w-5 h-5" />
              </a>
              <a
                href="https://instagram.com/jobrocket"
                target="_blank"
                rel="noopener noreferrer"
                className="text-slate-400 hover:text-white transition-colors duration-200"
              >
                <Instagram className="w-5 h-5" />
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;