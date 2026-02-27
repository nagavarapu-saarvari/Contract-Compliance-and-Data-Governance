import React, { useState } from 'react';
import './App.css';
import PdfUpload from './components/PdfUpload';
import PythonCheck from './components/PythonCheck';
import RulesView from './components/RulesView';

function App() {
  const [activeTab, setActiveTab] = useState('pdf');

  return (
    <div className="App">
      <header className="header">
        <div className="header-content">
          <h1>📋 Contract Compliance & Data Governance</h1>
          <p className="subtitle">Upload PDFs to generate rules or Python files to check compliance</p>
        </div>
      </header>

      <main className="main-content">
        <div className="container">
          <div className="tabs">
            <button
              className={`tab-button ${activeTab === 'pdf' ? 'active' : ''}`}
              onClick={() => setActiveTab('pdf')}
            >
              📄 Generate Rules (PDF)
            </button>
            <button
              className={`tab-button ${activeTab === 'python' ? 'active' : ''}`}
              onClick={() => setActiveTab('python')}
            >
              🐍 Check Compliance (Python)
            </button>
           
          </div>

          <div className="tab-content">
            {activeTab === 'pdf' && <PdfUpload />}
            {activeTab === 'python' && <PythonCheck />}
            {activeTab === 'rules' && <RulesView />}
          </div>
        </div>
      </main>

      <footer className="footer">
        <p>&copy; 2026 Contract Compliance & Data Governance System</p>
      </footer>
    </div>
  );
}

export default App;
