import React, { useState, useEffect } from 'react';
import { apiService } from '../services/apiService';

function RulesView() {
  const [loading, setLoading] = useState(false);
  const [rules, setRules] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadRules();
  }, []);

  const loadRules = async () => {
    setLoading(true);
    setError(null);
    setRules([]);

    try {
      const response = await apiService.getRules();
      if (response.data.status === 'success') {
        setRules(response.data.rules);
      } else {
        setError(response.data.message || 'Failed to load rules');
      }
    } catch (err) {
      setError(err.response?.data?.message || `Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>📜 Stored Governance Rules</h2>
      <p>View all rules that have been generated from contracts</p>

      <button onClick={loadRules} className="btn btn-secondary">
        Refresh Rules
      </button>

      {loading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading rules...</p>
        </div>
      )}

      {error && (
        <div className="result">
          <div className="result-header error">
            <span className="result-icon">✗</span>
            <span>Error Loading Rules</span>
          </div>
          <div className="result-body">
            <p>{error}</p>
          </div>
        </div>
      )}

      {!loading && !error && rules.length === 0 && (
        <div className="empty-state">
          <p>No rules found. Generate rules by uploading a PDF first.</p>
        </div>
      )}

      {!loading && !error && rules.length > 0 && (
        <div className="result">
          <div className="result-body">
            <p>
              <strong>Total Rules:</strong> {rules.length}
            </p>
            <div className="rules-list">
              {rules.map((rule, index) => (
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
                  <p>
                    <strong>Context:</strong> {rule.conditions?.context || 'N/A'}
                  </p>
                  <p>
                    <strong>Exceptions:</strong> {rule.conditions?.exceptions || 'None'}
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

export default RulesView;
