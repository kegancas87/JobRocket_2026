import React, { useState, useRef } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Progress } from './ui/progress';
import {
  Upload,
  FileText,
  CheckCircle,
  AlertCircle,
  Loader2,
  X,
  Users,
} from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const MAX_FILES = 1000;
const ALLOWED_EXT = ['.pdf', '.doc', '.docx'];

const humanSize = (bytes) => {
  if (!bytes) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  let i = 0;
  let n = bytes;
  while (n >= 1024 && i < units.length - 1) {
    n /= 1024;
    i += 1;
  }
  return `${n.toFixed(1)} ${units[i]}`;
};

const BulkCVUpload = ({ user }) => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState(null); // backend response
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const getAuthHeaders = () => ({
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  });

  const isAllowed = (name) => {
    const lower = (name || '').toLowerCase();
    return ALLOWED_EXT.some((ext) => lower.endsWith(ext));
  };

  const handleFileSelect = (e) => {
    setError('');
    setResult(null);
    const picked = Array.from(e.target.files || []);
    if (picked.length === 0) return;

    // Filter unsupported files
    const supported = picked.filter((f) => isAllowed(f.name));
    const skipped = picked.length - supported.length;

    // Combine with any previously selected files (dedupe by name+size)
    const combined = [...files];
    for (const f of supported) {
      if (!combined.find((c) => c.name === f.name && c.size === f.size)) {
        combined.push(f);
      }
    }

    if (combined.length > MAX_FILES) {
      setError(`Maximum ${MAX_FILES} files allowed per upload. Trimmed to first ${MAX_FILES}.`);
      combined.length = MAX_FILES;
    }
    if (skipped > 0) {
      setError(
        (prev) =>
          (prev ? prev + ' ' : '') +
          `${skipped} file(s) skipped — only .pdf, .doc, .docx are supported.`
      );
    }

    setFiles(combined);
    // Reset input so same file can be picked again if user removes it
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const removeFile = (index) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const clearAll = () => {
    setFiles([]);
    setResult(null);
    setError('');
    setProgress(0);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleUpload = async () => {
    if (files.length === 0) return;
    setUploading(true);
    setProgress(0);
    setError('');
    setResult(null);
    try {
      const formData = new FormData();
      files.forEach((f) => formData.append('files', f, f.name));

      const res = await axios.post(`${API}/admin/bulk-cv-upload`, formData, {
        ...getAuthHeaders(),
        headers: {
          ...getAuthHeaders().headers,
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (evt) => {
          if (evt.total) {
            setProgress(Math.round((evt.loaded * 100) / evt.total));
          }
        },
        // Long timeout — big batches can take a while
        timeout: 15 * 60 * 1000,
      });

      setResult(res.data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          err.message ||
          'Upload failed. Please try again.'
      );
    } finally {
      setUploading(false);
      setProgress(0);
    }
  };

  const totalSize = files.reduce((sum, f) => sum + f.size, 0);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-6" data-testid="bulk-cv-upload-page">
      <div className="max-w-5xl mx-auto space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-3">
            <Users className="w-8 h-8 text-blue-600" />
            Bulk CV Upload
          </h1>
          <p className="text-slate-600 mt-1">
            Upload up to {MAX_FILES} CV files at once. Each file will create a new job seeker
            account and their CV will be attached to their profile.
          </p>
        </div>

        {/* File Picker */}
        <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
          <CardHeader>
            <CardTitle className="text-lg text-slate-700 flex items-center">
              <Upload className="w-5 h-5 mr-2 text-blue-600" />
              1. Select CV Files
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div
              onClick={() => !uploading && fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
                uploading
                  ? 'border-slate-200 bg-slate-50 cursor-not-allowed'
                  : 'border-blue-300 bg-blue-50/30 hover:bg-blue-50 cursor-pointer'
              }`}
              data-testid="bulk-cv-dropzone"
            >
              <Upload className="w-10 h-10 mx-auto mb-3 text-blue-500" />
              <p className="font-semibold text-slate-700">
                Click to select CV files
              </p>
              <p className="text-sm text-slate-500 mt-1">
                .pdf, .doc, .docx &middot; up to {MAX_FILES} files &middot; max 10MB each
              </p>
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                onChange={handleFileSelect}
                className="hidden"
                disabled={uploading}
                data-testid="bulk-cv-file-input"
              />
            </div>

            {error && (
              <div className="flex items-start gap-2 p-3 rounded-lg bg-amber-50 border border-amber-200 text-amber-800 text-sm" data-testid="bulk-cv-error">
                <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Selected files list */}
        {files.length > 0 && (
          <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg text-slate-700 flex items-center">
                  <FileText className="w-5 h-5 mr-2 text-blue-600" />
                  2. Review Selection
                </CardTitle>
                <div className="text-sm text-slate-600" data-testid="bulk-cv-selection-summary">
                  <strong>{files.length}</strong> file(s) &middot; {humanSize(totalSize)}
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="max-h-72 overflow-y-auto border border-slate-200 rounded-lg divide-y divide-slate-100">
                {files.map((f, idx) => (
                  <div
                    key={`${f.name}-${idx}`}
                    className="flex items-center justify-between px-3 py-2 text-sm hover:bg-slate-50"
                    data-testid={`bulk-cv-file-row-${idx}`}
                  >
                    <div className="flex items-center gap-2 flex-1 min-w-0">
                      <FileText className="w-4 h-4 text-slate-400 flex-shrink-0" />
                      <span className="truncate text-slate-700">{f.name}</span>
                    </div>
                    <div className="flex items-center gap-3 ml-3">
                      <span className="text-xs text-slate-500 whitespace-nowrap">
                        {humanSize(f.size)}
                      </span>
                      <button
                        type="button"
                        onClick={() => removeFile(idx)}
                        disabled={uploading}
                        className="text-slate-400 hover:text-red-600 disabled:opacity-40"
                        data-testid={`bulk-cv-remove-file-${idx}`}
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              <div className="flex flex-wrap gap-3 mt-4">
                <Button
                  onClick={handleUpload}
                  disabled={uploading || files.length === 0}
                  className="bg-blue-600 hover:bg-blue-700 text-white"
                  data-testid="bulk-cv-upload-btn"
                >
                  {uploading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Uploading &amp; processing...
                    </>
                  ) : (
                    <>
                      <Upload className="w-4 h-4 mr-2" />
                      Upload {files.length} CV{files.length === 1 ? '' : 's'}
                    </>
                  )}
                </Button>
                <Button
                  onClick={clearAll}
                  disabled={uploading}
                  variant="outline"
                  data-testid="bulk-cv-clear-btn"
                >
                  <X className="w-4 h-4 mr-2" />
                  Clear All
                </Button>
              </div>

              {uploading && (
                <div className="mt-4" data-testid="bulk-cv-progress">
                  <div className="flex justify-between text-sm text-slate-600 mb-1">
                    <span>Uploading files to server...</span>
                    <span>{progress}%</span>
                  </div>
                  <Progress value={progress} />
                  <p className="text-xs text-slate-500 mt-2">
                    Once files reach the server, they&apos;ll be parsed and users created. This can take a few minutes for large batches.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Results */}
        {result && (
          <Card className="bg-white/90 backdrop-blur-sm shadow-lg border-0" data-testid="bulk-cv-results">
            <CardHeader>
              <CardTitle className="text-lg text-slate-700 flex items-center">
                <CheckCircle className="w-5 h-5 mr-2 text-emerald-600" />
                3. Results
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-5">
                <div className="rounded-lg border border-slate-200 p-4">
                  <p className="text-xs text-slate-500">Total Processed</p>
                  <p className="text-2xl font-bold text-slate-900" data-testid="result-total">
                    {result.total}
                  </p>
                </div>
                <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4">
                  <p className="text-xs text-emerald-700">Users Created</p>
                  <p className="text-2xl font-bold text-emerald-700" data-testid="result-created">
                    {result.created}
                  </p>
                </div>
                <div className="rounded-lg border border-red-200 bg-red-50 p-4">
                  <p className="text-xs text-red-700">Failed</p>
                  <p className="text-2xl font-bold text-red-700" data-testid="result-failed">
                    {result.failed}
                  </p>
                </div>
              </div>

              {result.users && result.users.length > 0 && (
                <div className="mb-5">
                  <h3 className="text-sm font-semibold text-slate-700 mb-2">
                    Created Users ({result.users.length})
                  </h3>
                  <div className="max-h-72 overflow-y-auto border border-slate-200 rounded-lg">
                    <table className="w-full text-sm">
                      <thead className="bg-slate-50 sticky top-0">
                        <tr>
                          <th className="text-left p-2 font-medium text-slate-600">Filename</th>
                          <th className="text-left p-2 font-medium text-slate-600">Name</th>
                          <th className="text-left p-2 font-medium text-slate-600">Email</th>
                          <th className="text-left p-2 font-medium text-slate-600">Detected</th>
                        </tr>
                      </thead>
                      <tbody>
                        {result.users.map((u, i) => (
                          <tr key={i} className="border-t border-slate-100">
                            <td className="p-2 text-slate-700 max-w-xs truncate" title={u.filename}>
                              {u.filename}
                            </td>
                            <td className="p-2 text-slate-700">
                              {u.first_name} {u.last_name}
                            </td>
                            <td className="p-2 text-slate-500 text-xs">{u.email}</td>
                            <td className="p-2 text-xs text-slate-500">
                              {u.skills_detected > 0 && (
                                <span className="mr-2">Skills: {u.skills_detected}</span>
                              )}
                              {u.phone_detected && <span className="mr-2">Phone</span>}
                              {u.email_detected && <span>Email</span>}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {result.errors && result.errors.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold text-red-700 mb-2">
                    Errors ({result.errors.length})
                  </h3>
                  <div className="max-h-56 overflow-y-auto border border-red-200 rounded-lg">
                    <table className="w-full text-sm">
                      <thead className="bg-red-50 sticky top-0">
                        <tr>
                          <th className="text-left p-2 font-medium text-red-700">Filename</th>
                          <th className="text-left p-2 font-medium text-red-700">Error</th>
                        </tr>
                      </thead>
                      <tbody>
                        {result.errors.map((e, i) => (
                          <tr key={i} className="border-t border-red-100">
                            <td className="p-2 text-slate-700 max-w-xs truncate" title={e.filename}>
                              {e.filename}
                            </td>
                            <td className="p-2 text-red-700">{e.error}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              <Button onClick={clearAll} variant="outline" className="mt-5" data-testid="bulk-cv-done-btn">
                Upload Another Batch
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default BulkCVUpload;
