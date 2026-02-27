import React, { useState, useRef } from 'react';
import { apiService } from '../services/apiService';

function PdfUpload() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

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

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      if (files[0].type === 'application/pdf') {
        processFile(files[0]);
      } else {
        setError('Please drop a PDF file');
      }
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  const processFile = async (file) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await apiService.processPdf(file);
      if (response.data.status === 'success') {
        setResult(response.data);
      } else {
        setError(response.data.message || 'Failed to process PDF');
      }
    } catch (err) {
      setError(err.response?.data?.message || `Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>📄 Generate Rules from Contract PDF</h2>
      <p>Upload a contract PDF to automatically extract and generate enforceable rules</p>

      <div
        className={`upload-area ${dragActive ? 'drag-over' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <div className="upload-icon">📑</div>
        <p>Drag and drop your PDF here</p>
        <p className="or-text">or</p>
        <button className="btn btn-primary">Select PDF File</button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handleFileInput}
          style={{ display: 'none' }}
        />
      </div>

      {loading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Processing PDF and generating rules...</p>
        </div>
      )}

      {error && (
        <div className="result">
          <div className="result-header error">
            <span className="result-icon">✗</span>
            <span>Error Processing PDF</span>
          </div>
          <div className="result-body">
            <p>{error}</p>
          </div>
        </div>
      )}

      {result && (
        <div className="result">
          <div className="result-header success">
            <span className="result-icon">✓</span>
            <span>Rules Generated Successfully</span>
          </div>
          <div className="result-body">
            <p>
              <strong>Rules Generated:</strong> {result.rules_count}
            </p>
            <div className="rules-list">
              {result.rules.map((rule, index) => (
                <div key={index} className="rule-item">
                  <h4>
                    {rule.rule_id}: {rule.title || 'Untitled'}
                  </h4>
                  <p>
                    <strong>Description:</strong> {rule.description || 'N/A'}
                  </p>
                  <p>
                    <strong>Category:</strong> {rule.action_category || 'N/A'}
                  </p>
                  <p>
                    <strong>Effect:</strong> <code>{rule.effect || 'N/A'}</code>
                  </p>
                  <p>
                    <strong>Applies To:</strong>{' '}
                    {rule.conditions?.applies_to || 'N/A'}
                  </p>
                  <p>
                    <strong>Data Type:</strong> {rule.conditions?.data_type || 'N/A'}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default PdfUpload;
