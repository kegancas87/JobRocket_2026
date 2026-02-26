import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { 
  PieChart, 
  BarChart3, 
  TrendingUp, 
  Users, 
  Briefcase,
  Search,
  FileText,
  Clock
} from "lucide-react";

const Reports = ({ user }) => {
  return (
    <div className="space-y-6 p-6" data-testid="reports-page">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-800 mb-2">Reports</h1>
        <p className="text-slate-600">Analytics and insights for your recruitment activities</p>
      </div>

      {/* Coming Soon Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* CV Search Usage Report */}
        <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl hover:shadow-2xl transition-all duration-300">
          <CardHeader className="pb-3">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Search className="w-5 h-5 text-blue-600" />
              </div>
              <CardTitle className="text-lg font-semibold text-slate-800">CV Search Usage</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-slate-600 text-sm mb-4">
              Track your CV search activity, contact reveals, and remaining quota.
            </p>
            <div className="flex items-center justify-center py-8 bg-slate-50 rounded-lg">
              <div className="text-center">
                <Clock className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                <p className="text-sm font-medium text-slate-500">Coming Soon</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Job Performance Report */}
        <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl hover:shadow-2xl transition-all duration-300">
          <CardHeader className="pb-3">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-emerald-100 rounded-lg">
                <Briefcase className="w-5 h-5 text-emerald-600" />
              </div>
              <CardTitle className="text-lg font-semibold text-slate-800">Job Performance</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-slate-600 text-sm mb-4">
              View application rates, time-to-fill, and job listing performance metrics.
            </p>
            <div className="flex items-center justify-center py-8 bg-slate-50 rounded-lg">
              <div className="text-center">
                <Clock className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                <p className="text-sm font-medium text-slate-500">Coming Soon</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Pipeline Analytics */}
        <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl hover:shadow-2xl transition-all duration-300">
          <CardHeader className="pb-3">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <TrendingUp className="w-5 h-5 text-purple-600" />
              </div>
              <CardTitle className="text-lg font-semibold text-slate-800">Pipeline Analytics</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-slate-600 text-sm mb-4">
              Analyze your hiring pipeline, conversion rates, and bottlenecks.
            </p>
            <div className="flex items-center justify-center py-8 bg-slate-50 rounded-lg">
              <div className="text-center">
                <Clock className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                <p className="text-sm font-medium text-slate-500">Coming Soon</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Candidate Source Report */}
        <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl hover:shadow-2xl transition-all duration-300">
          <CardHeader className="pb-3">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-orange-100 rounded-lg">
                <Users className="w-5 h-5 text-orange-600" />
              </div>
              <CardTitle className="text-lg font-semibold text-slate-800">Candidate Sources</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-slate-600 text-sm mb-4">
              Understand where your best candidates come from.
            </p>
            <div className="flex items-center justify-center py-8 bg-slate-50 rounded-lg">
              <div className="text-center">
                <Clock className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                <p className="text-sm font-medium text-slate-500">Coming Soon</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Application Trends */}
        <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl hover:shadow-2xl transition-all duration-300">
          <CardHeader className="pb-3">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-pink-100 rounded-lg">
                <BarChart3 className="w-5 h-5 text-pink-600" />
              </div>
              <CardTitle className="text-lg font-semibold text-slate-800">Application Trends</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-slate-600 text-sm mb-4">
              Weekly and monthly application volume trends and patterns.
            </p>
            <div className="flex items-center justify-center py-8 bg-slate-50 rounded-lg">
              <div className="text-center">
                <Clock className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                <p className="text-sm font-medium text-slate-500">Coming Soon</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Activity Log */}
        <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl hover:shadow-2xl transition-all duration-300">
          <CardHeader className="pb-3">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-slate-100 rounded-lg">
                <FileText className="w-5 h-5 text-slate-600" />
              </div>
              <CardTitle className="text-lg font-semibold text-slate-800">Activity Log</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-slate-600 text-sm mb-4">
              Complete audit trail of all recruitment activities.
            </p>
            <div className="flex items-center justify-center py-8 bg-slate-50 rounded-lg">
              <div className="text-center">
                <Clock className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                <p className="text-sm font-medium text-slate-500">Coming Soon</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Info Banner */}
      <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-0 shadow-lg">
        <CardContent className="p-6">
          <div className="flex items-start space-x-4">
            <div className="p-3 bg-white rounded-lg shadow-sm">
              <PieChart className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h3 className="font-semibold text-slate-800 mb-1">Reports Feature Coming Soon</h3>
              <p className="text-slate-600 text-sm">
                We're building comprehensive reporting tools to help you make data-driven hiring decisions. 
                The first report - CV Search Usage - will be available shortly.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Reports;
