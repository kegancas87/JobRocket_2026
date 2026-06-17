import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Rocket, 
  Target, 
  Users, 
  Shield, 
  Award,
  TrendingUp,
  Heart,
  Globe,
  ArrowLeft
} from 'lucide-react';
import { Button } from './ui/button';

const AboutUsPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
      {/* Header */}
      <div className="bg-gradient-to-r from-slate-900 to-blue-900 text-white py-16">
        <div className="max-w-6xl mx-auto px-6">
          <Link to="/" className="inline-flex items-center text-blue-300 hover:text-white mb-6 transition-colors">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Home
          </Link>
          <div className="flex items-center space-x-4 mb-4">
            <Rocket className="w-12 h-12 text-blue-400" />
            <h1 className="text-4xl md:text-5xl font-bold">About Job Rocket</h1>
          </div>
          <p className="text-xl text-slate-300 max-w-3xl">
            Empowering South African careers since 2024. We're on a mission to connect talented individuals 
            with opportunities that propel their professional journey.
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-6 py-16">
        {/* Our Story */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-slate-800 mb-6">Our Story</h2>
          <div className="bg-white rounded-xl p-8 shadow-lg">
            <p className="text-lg text-slate-700 leading-relaxed mb-4">
              Job Rocket was founded with a simple yet powerful vision: to revolutionise the way South Africans 
              find employment and how businesses discover exceptional talent. In a country with vast untapped 
              potential, we saw an opportunity to create a platform that truly understands the unique dynamics 
              of the South African job market.
            </p>
            <p className="text-lg text-slate-700 leading-relaxed mb-4">
              Based in Johannesburg, South Africa, our team combines deep local expertise with cutting-edge 
              technology to deliver a recruitment experience that's efficient, transparent, and results-driven. 
              We're proud to serve businesses across all nine provinces, from emerging startups to established 
              enterprises.
            </p>
            <p className="text-lg text-slate-700 leading-relaxed">
              Every day, we work to break down barriers in the South African employment landscape, promoting 
              equal opportunities and helping to build a more inclusive economy for all.
            </p>
          </div>
        </section>

        {/* Mission & Vision */}
        <section className="mb-16 grid md:grid-cols-2 gap-8">
          <div className="bg-gradient-to-br from-blue-600 to-blue-800 rounded-xl p-8 text-white shadow-lg">
            <Target className="w-12 h-12 mb-4" />
            <h3 className="text-2xl font-bold mb-4">Our Mission</h3>
            <p className="text-blue-100 leading-relaxed">
              To connect every South African with meaningful employment opportunities while helping 
              businesses build exceptional teams. We believe that the right job can transform lives, 
              and the right hire can transform businesses.
            </p>
          </div>
          <div className="bg-gradient-to-br from-slate-700 to-slate-900 rounded-xl p-8 text-white shadow-lg">
            <Globe className="w-12 h-12 mb-4" />
            <h3 className="text-2xl font-bold mb-4">Our Vision</h3>
            <p className="text-slate-300 leading-relaxed">
              To be South Africa's most trusted and innovative recruitment platform, setting the 
              standard for how talent and opportunity connect across the African continent.
            </p>
          </div>
        </section>

        {/* Our Values */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-slate-800 mb-8 text-center">Our Values</h2>
          <div className="grid md:grid-cols-4 gap-6">
            <div className="bg-white rounded-xl p-6 shadow-lg text-center">
              <Shield className="w-10 h-10 text-blue-600 mx-auto mb-4" />
              <h4 className="text-lg font-bold text-slate-800 mb-2">Integrity</h4>
              <p className="text-slate-600 text-sm">
                We operate with complete transparency and honesty in all our dealings.
              </p>
            </div>
            <div className="bg-white rounded-xl p-6 shadow-lg text-center">
              <TrendingUp className="w-10 h-10 text-green-600 mx-auto mb-4" />
              <h4 className="text-lg font-bold text-slate-800 mb-2">Innovation</h4>
              <p className="text-slate-600 text-sm">
                We continuously improve our platform to serve you better.
              </p>
            </div>
            <div className="bg-white rounded-xl p-6 shadow-lg text-center">
              <Users className="w-10 h-10 text-purple-600 mx-auto mb-4" />
              <h4 className="text-lg font-bold text-slate-800 mb-2">Inclusivity</h4>
              <p className="text-slate-600 text-sm">
                We promote equal opportunities for all South Africans.
              </p>
            </div>
            <div className="bg-white rounded-xl p-6 shadow-lg text-center">
              <Heart className="w-10 h-10 text-red-500 mx-auto mb-4" />
              <h4 className="text-lg font-bold text-slate-800 mb-2">Empathy</h4>
              <p className="text-slate-600 text-sm">
                We understand the challenges of job seeking and hiring.
              </p>
            </div>
          </div>
        </section>

        {/* Stats */}
        <section className="mb-16">
          <div className="bg-gradient-to-r from-blue-600 to-slate-800 rounded-xl p-8 text-white">
            <h2 className="text-2xl font-bold mb-8 text-center">Our Impact</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
              <div>
                <p className="text-4xl font-bold text-blue-300">10,000+</p>
                <p className="text-slate-300">Jobs Posted</p>
              </div>
              <div>
                <p className="text-4xl font-bold text-blue-300">50,000+</p>
                <p className="text-slate-300">Job Seekers</p>
              </div>
              <div>
                <p className="text-4xl font-bold text-blue-300">2,500+</p>
                <p className="text-slate-300">Companies</p>
              </div>
              <div>
                <p className="text-4xl font-bold text-blue-300">9</p>
                <p className="text-slate-300">Provinces Served</p>
              </div>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="text-center">
          <h2 className="text-3xl font-bold text-slate-800 mb-4">Ready to Launch Your Career?</h2>
          <p className="text-lg text-slate-600 mb-8">
            Join thousands of South Africans who've found their dream jobs through Job Rocket.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/register">
              <Button className="bg-gradient-to-r from-blue-600 to-slate-700 hover:from-blue-700 hover:to-slate-800 text-white px-8 py-3 text-lg">
                Get Started
              </Button>
            </Link>
            <Link to="/contact">
              <Button variant="outline" className="border-2 border-blue-600 text-blue-600 hover:bg-blue-50 px-8 py-3 text-lg">
                Contact Us
              </Button>
            </Link>
          </div>
        </section>
      </div>
    </div>
  );
};

export default AboutUsPage;
