import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function FeedbackPage() {
  const navigate = useNavigate();

  useEffect(() => {
    // Session data available in localStorage if needed
  }, []);

  const handleStartNew = () => {
    localStorage.clear();
    navigate("/");
  };

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <div className="eyebrow">Completed</div>
          <h1>Interview Summary</h1>
        </div>
      </div>

      <div className="feedback-container">
        <div className="feedback-card success-card">
          <div className="card-icon">✅</div>
          <h2>Interview Completed Successfully!</h2>
          <p className="card-description">
            You've finished your AI-powered interview training session. Great work!
          </p>
        </div>

        {/* <div className="feedback-card">
          <h3>What You Accomplished</h3>
          <ul className="achievement-list">
            <li>✓ Uploaded and processed job description using RAG</li>
            <li>✓ Completed AI-generated interview questions</li>
            <li>✓ Practiced real-world interview scenarios</li>
            <li>✓ Improved your interview skills with AI feedback</li>
          </ul>
        </div> */}

        <div className="feedback-card">
          <h3>Next Steps</h3>
          <div className="next-steps">
            <div className="step-item">
              <div className="step-number">1</div>
              <div className="step-content">
                <h4>Review Your Responses</h4>
                <p>Reflect on your answers and identify areas for improvement</p>
              </div>
            </div>
            <div className="step-item">
              <div className="step-number">2</div>
              <div className="step-content">
                <h4>Practice More</h4>
                <p>Try different job descriptions to expand your preparation</p>
              </div>
            </div>
            <div className="step-item">
              <div className="step-number">3</div>
              <div className="step-content">
                <h4>Refine Your Approach</h4>
                <p>Use insights gained to improve your interview technique</p>
              </div>
            </div>
          </div>
        </div>

        {/* <div className="feedback-card tech-card">
          <h3>Powered By</h3>
          <div className="tech-grid">
            <div className="tech-item">
              <div className="tech-icon">🦙</div>
              <div className="tech-name">Ollama LLaMA 3.2</div>
              <div className="tech-desc">Advanced language model</div>
            </div>
            <div className="tech-item">
              <div className="tech-icon">🔍</div>
              <div className="tech-name">RAG with FAISS</div>
              <div className="tech-desc">Semantic search</div>
            </div>
            <div className="tech-item">
              <div className="tech-icon">📊</div>
              <div className="tech-name">Vector Embeddings</div>
              <div className="tech-desc">Context-aware AI</div>
            </div>
            <div className="tech-item">
              <div className="tech-icon">⚡</div>
              <div className="tech-name">FastAPI Backend</div>
              <div className="tech-desc">High-performance API</div>
            </div>
          </div>
        </div> */}

        <div className="action-buttons">
          <button className="button primary large" onClick={handleStartNew}>
            Start New Interview
          </button>
        </div>
      </div>
    </div>
  );
}

export default FeedbackPage;
