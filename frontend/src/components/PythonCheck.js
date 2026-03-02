import React, { useState, useRef } from 'react';
import { apiService } from '../services/apiService';

function PythonCheck() {
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
      if (files[0].name.endsWith('.py')) {
        processFile(files[0]);
      } else {
        setError('Please drop a Python file (.py)');
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
      const response = await apiService.checkCompliance(file);
      if (response.data.status === 'success') {
        setResult(response.data);
      } else {
        setError(response.data.message || 'Failed to check compliance');
      }
    } catch (err) {
      setError(err.response?.data?.message || `Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'safe':
        return 'safe';
      case 'violation_found':
        return 'violation';
      case 'suspicious_blocks_found':
        return 'warning';
      default:
        return 'warning';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'safe':
        return 'SAFE';
      case 'violation_found':
        return 'VIOLATION';
      case 'suspicious_blocks_found':
        return 'SUSPICIOUS';
      default:
        return 'UNKNOWN';
    }
  };

  return (
    <div className="card">
      <h2> Check Python File for Compliance</h2>
      <p>Upload a Python file to check it against stored governance rules</p>

      <div
        className={`upload-area ${dragActive ? 'drag-over' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <p>Drag and drop your Python file here</p>
        <p className="or-text">or</p>
        <button className="btn btn-primary">Select Python File</button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".py"
          onChange={handleFileInput}
          style={{ display: 'none' }}
        />
      </div>

      {loading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Analyzing Python file for compliance...</p>
        </div>
      )}

      {error && (
        <div className="result">
          <div className="result-header error">
            <span className="result-icon">✗</span>
            <span>Error Checking Compliance</span>
          </div>
          <div className="result-body">
            <p>{error}</p>
          </div>
        </div>
      )}

      {result && (
        <div className="result">
          <div
            className={`result-header ${
              result.compliance_status === 'safe'
                ? 'success'
                : result.compliance_status === 'violation_found'
                ? 'error'
                : 'warning'
            }`}
          >
            <span className="result-icon">
              {result.compliance_status === 'safe'
                ? '✓'
                : result.compliance_status === 'violation_found'
                ? '✗'
                : '⚠'}
            </span>
            <span>
              {result.compliance_status === 'safe'
                ? 'Code is Compliant'
                : result.compliance_status === 'violation_found'
                ? 'Violations Detected'
                : 'Suspicious Blocks Detected'}
            </span>
          </div>
          <div className="result-body">
            <p>
              <strong>Status:</strong>{' '}
              <span className={`status-badge ${getStatusBadgeClass(result.compliance_status)}`}>
                {getStatusText(result.compliance_status)}
              </span>
            </p>
            <p>
              <strong>Suspicious Blocks:</strong> {result.suspicious_blocks_count}
            </p>
            <p>
              <strong>Violations:</strong> {result.violations_count}
            </p>

            {result.suspicious_blocks_count > 0 && (
              <div style={{ marginTop: '1.5rem' }}>
                <h3>Suspicious Blocks Detected</h3>
                <div className="blocks-list">
                  {result.suspicious_blocks.map((block, index) => (
                    <div key={index} className="block-item">
                      <h4>
                        Scope: {block.scope} - {block.name}
                      </h4>
                      <p>
                        <strong>Reason:</strong> {block.reason}
                      </p>
                      <p>
                        <strong>Code Preview:</strong>
                      </p>
                      <div className="code-preview">{block.code_preview}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {result.violations_count > 0 && (
              <div style={{ marginTop: '1.5rem' }}>
                <h3>Rule Violations</h3>
                <div className="violations-list">
                  {result.violations.map((violation, index) => (
                    <div key={index} className="violation-item">
                      <h4>
                        Block: {violation.block_scope} - {violation.block_name}
                      </h4>
                      {violation.violations.map((v, vIndex) => (
                        <div key={vIndex} className="violation-rule">
                          <strong>Rule {v.rule_id}:</strong> {v.title || 'N/A'}
                          <br />
                          <strong>Reason:</strong> {v.reason}
                        </div>
                      ))}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default PythonCheck;
