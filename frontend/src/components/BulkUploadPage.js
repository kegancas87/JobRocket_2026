import React, { useState, useRef } from 'react';
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "./ui/card";
import { Badge } from "./ui/badge";
import {
  Upload,
  FileText,
  Download,
  CheckCircle,
  XCircle,
  AlertTriangle,
  FileSpreadsheet,
  Loader2,
  ArrowLeft,
  Info
} from "lucide-react";
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const BulkUploadPage = ({ user }) => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    return { Authorization: `Bearer ${token}` };
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) validateAndSetFile(droppedFile);
  };

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) validateAndSetFile(selectedFile);
  };

  const validateAndSetFile = (f) => {
    setError('');
    setResult(null);
    const validExtensions = ['.csv', '.xlsx', '.xls'];
    const ext = f.name.substring(f.name.lastIndexOf('.')).toLowerCase();
    if (!validExtensions.includes(ext)) {
      setError('Invalid file type. Please upload a .csv or .xlsx file.');
      return;
    }
    if (f.size > 5 * 1024 * 1024) {
      setError('File is too large. Maximum size is 5MB.');
      return;
    }
    setFile(f);
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError('');
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(`${API}/jobs/bulk`, formData, {
        headers: {
          ...getAuthHeaders(),
          'Content-Type': 'multipart/form-data'
        }
      });
      setResult(response.data);
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (err.response?.status === 403) {
        setError('Bulk upload is only available for Pro and Enterprise plans. Please upgrade your subscription.');
      } else {
        setError(typeof detail === 'string' ? detail : 'Failed to upload file. Please check the format and try again.');
      }
    } finally {
      setUploading(false);
    }
  };

  const handleDownloadTemplate = async (format) => {
    try {
      const response = await axios.get(`${API}/jobs/bulk/template?format=${format}`, {
        headers: getAuthHeaders(),
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `job_upload_template.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError('Failed to download template.');
    }
  };

  const resetUpload = () => {
    setFile(null);
    setResult(null);
    setError('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 data-testid="bulk-upload-title" className="text-3xl font-bold text-slate-800 flex items-center">
              <FileSpreadsheet className="w-8 h-8 mr-3 text-blue-600" />
              Bulk Job Upload
            </h1>
            <p className="text-slate-600 mt-1">Upload multiple job listings at once using CSV or Excel files</p>
          </div>
          <Button
            variant="outline"
            onClick={() => navigate('/my-jobs')}
            data-testid="back-to-jobs-btn"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            My Jobs
          </Button>
        </div>

        {/* Template Download */}
        <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0 mb-6">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg font-semibold text-slate-700 flex items-center">
              <Download className="w-5 h-5 mr-2 text-blue-600" />
              Step 1: Download Template
            </CardTitle>
            <CardDescription>Start with our template to ensure your data is formatted correctly</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-3">
              <Button
                variant="outline"
                onClick={() => handleDownloadTemplate('csv')}
                data-testid="download-csv-template-btn"
                className="border-blue-200 hover:bg-blue-50"
              >
                <FileText className="w-4 h-4 mr-2 text-green-600" />
                Download CSV Template
              </Button>
              <Button
                variant="outline"
                onClick={() => handleDownloadTemplate('xlsx')}
                data-testid="download-xlsx-template-btn"
                className="border-blue-200 hover:bg-blue-50"
              >
                <FileSpreadsheet className="w-4 h-4 mr-2 text-blue-600" />
                Download Excel Template
              </Button>
            </div>
            <div className="mt-4 p-3 bg-slate-50 rounded-lg">
              <p className="text-sm text-slate-600 flex items-start">
                <Info className="w-4 h-4 mr-2 mt-0.5 text-slate-500 flex-shrink-0" />
                <span>
                  <strong>Required columns:</strong> title, description, location, salary, job_type.{' '}
                  <strong>Optional:</strong> work_type, industry, experience, qualifications, closing_date
                </span>
              </p>
            </div>
          </CardContent>
        </Card>

        {/* File Upload Area */}
        <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0 mb-6">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg font-semibold text-slate-700 flex items-center">
              <Upload className="w-5 h-5 mr-2 text-blue-600" />
              Step 2: Upload Your File
            </CardTitle>
          </CardHeader>
          <CardContent>
            {!result ? (
              <>
                {/* Drop Zone */}
                <div
                  data-testid="file-drop-zone"
                  className={`border-2 border-dashed rounded-xl p-10 text-center transition-all cursor-pointer ${
                    dragActive
                      ? 'border-blue-500 bg-blue-50'
                      : file
                        ? 'border-green-400 bg-green-50'
                        : 'border-slate-300 hover:border-blue-400 hover:bg-slate-50'
                  }`}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".csv,.xlsx,.xls"
                    onChange={handleFileSelect}
                    className="hidden"
                    data-testid="file-input"
                  />
                  {file ? (
                    <div className="space-y-2">
                      <CheckCircle className="w-12 h-12 mx-auto text-green-500" />
                      <p className="text-lg font-medium text-slate-800">{file.name}</p>
                      <p className="text-sm text-slate-500">
                        {(file.size / 1024).toFixed(1)} KB
                      </p>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => { e.stopPropagation(); resetUpload(); }}
                        className="text-slate-500 hover:text-red-600"
                      >
                        Remove file
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <Upload className="w-12 h-12 mx-auto text-slate-400" />
                      <p className="text-lg font-medium text-slate-700">
                        Drag & drop your file here
                      </p>
                      <p className="text-sm text-slate-500">or click to browse</p>
                      <p className="text-xs text-slate-400">Supports CSV and Excel (.xlsx) files up to 5MB</p>
                    </div>
                  )}
                </div>

                {/* Upload Button */}
                {file && (
                  <div className="mt-4 flex justify-end">
                    <Button
                      onClick={handleUpload}
                      disabled={uploading}
                      data-testid="upload-jobs-btn"
                      className="bg-blue-600 hover:bg-blue-700 px-8"
                    >
                      {uploading ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Uploading...
                        </>
                      ) : (
                        <>
                          <Upload className="w-4 h-4 mr-2" />
                          Upload Jobs
                        </>
                      )}
                    </Button>
                  </div>
                )}
              </>
            ) : (
              /* Upload Results */
              <div data-testid="upload-results" className="space-y-4">
                {/* Summary */}
                <div className={`p-4 rounded-lg flex items-center space-x-3 ${
                  result.success ? 'bg-green-50 border border-green-200' : 'bg-yellow-50 border border-yellow-200'
                }`}>
                  {result.success ? (
                    <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0" />
                  ) : (
                    <AlertTriangle className="w-6 h-6 text-yellow-600 flex-shrink-0" />
                  )}
                  <div>
                    <p className="font-medium text-slate-800">
                      {result.success ? 'All jobs uploaded successfully!' : 'Upload completed with some issues'}
                    </p>
                    <p className="text-sm text-slate-600">
                      {result.created} of {result.total_rows} jobs created
                      {result.failed > 0 && ` - ${result.failed} failed`}
                    </p>
                  </div>
                </div>

                {/* Stats Cards */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="p-4 bg-slate-50 rounded-lg text-center">
                    <p className="text-2xl font-bold text-slate-800">{result.total_rows}</p>
                    <p className="text-sm text-slate-600">Total Rows</p>
                  </div>
                  <div className="p-4 bg-green-50 rounded-lg text-center">
                    <p className="text-2xl font-bold text-green-700">{result.created}</p>
                    <p className="text-sm text-green-600">Created</p>
                  </div>
                  <div className="p-4 bg-red-50 rounded-lg text-center">
                    <p className="text-2xl font-bold text-red-700">{result.failed}</p>
                    <p className="text-sm text-red-600">Failed</p>
                  </div>
                </div>

                {/* Errors */}
                {result.errors && result.errors.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="font-medium text-slate-700">Errors:</h4>
                    <div className="max-h-48 overflow-y-auto space-y-1">
                      {result.errors.map((err, i) => (
                        <div key={i} className="flex items-start space-x-2 p-2 bg-red-50 rounded text-sm">
                          <XCircle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                          <span className="text-red-700">Row {err.row}: {err.error}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="flex justify-between pt-2">
                  <Button
                    variant="outline"
                    onClick={resetUpload}
                    data-testid="upload-another-btn"
                  >
                    Upload Another File
                  </Button>
                  <Button
                    onClick={() => navigate('/my-jobs')}
                    className="bg-blue-600 hover:bg-blue-700"
                    data-testid="view-jobs-btn"
                  >
                    View My Jobs
                  </Button>
                </div>
              </div>
            )}

            {/* Error Alert */}
            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-3" data-testid="upload-error">
                <XCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
                <span className="text-red-700">{error}</span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Instructions */}
        <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg font-semibold text-slate-700 flex items-center">
              <Info className="w-5 h-5 mr-2 text-blue-600" />
              Upload Guidelines
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-slate-800 mb-2">Column Requirements</h4>
                <ul className="space-y-1.5 text-sm text-slate-600">
                  <li className="flex items-center space-x-2">
                    <Badge className="bg-red-100 text-red-700 text-xs">Required</Badge>
                    <span>title - Job title</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <Badge className="bg-red-100 text-red-700 text-xs">Required</Badge>
                    <span>description - Job description</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <Badge className="bg-red-100 text-red-700 text-xs">Required</Badge>
                    <span>location - Job location</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <Badge className="bg-red-100 text-red-700 text-xs">Required</Badge>
                    <span>salary - Salary/compensation</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <Badge className="bg-red-100 text-red-700 text-xs">Required</Badge>
                    <span>job_type - Permanent or Contract</span>
                  </li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-slate-800 mb-2">Tips</h4>
                <ul className="space-y-1.5 text-sm text-slate-600 list-disc pl-5">
                  <li>Download the template first to see the expected format</li>
                  <li>Valid job types: Permanent, Contract</li>
                  <li>Valid work types: Remote, Onsite, Hybrid</li>
                  <li>Use date format YYYY-MM-DD for closing dates</li>
                  <li>Maximum 5MB file size</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default BulkUploadPage;
