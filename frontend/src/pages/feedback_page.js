import { useLocation, useNavigate } from "react-router-dom";
import { useJobContext } from "../job_context";

const fillerTokens = ["um", "uh", "like", "you know", "sort of", "kinda"];

const analyzeAnswers = (answers) => {
  const text = answers.map((a) => a.answer).join(" ") || "";
  const wordCount = text.split(/\s+/).filter(Boolean).length;
  const fillerCount = fillerTokens.reduce(
    (acc, token) => acc + (text.toLowerCase().match(new RegExp(`\\b${token}\\b`, "g")) || []).length,
    0
  );
  const clarityScore = Math.max(55, Math.min(95, 100 - fillerCount * 2));
  const relevanceScore = Math.min(95, 60 + Math.min(answers.length * 8, 30));
  const confidenceScore = Math.min(95, 65 + Math.min(wordCount / 6, 30));
  const pace = wordCount > 220 ? "Slightly fast" : wordCount < 120 ? "Calm" : "Balanced";

  return {
    clarityScore,
    relevanceScore,
    confidenceScore,
    fillerCount,
    pace,
    wordCount
  };
};

function FeedbackPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const answers = location.state?.answers || [];
  const { summary } = useJobContext();
  const insights = analyzeAnswers(answers);

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <p className="eyebrow">Step 3 · Feedback</p>
          <h1>Rapid feedback generated from your voice responses</h1>
          <p className="muted">A quick pulse on clarity, confidence, and relevancy to the uploaded job description.</p>
        </div>
        <div className="badge">Beta</div>
      </div>

      <div className="card-grid">
        <div className="card">
          <h3>Summary Scores</h3>
          <p>Confidence: {insights.confidenceScore}/100</p>
          <p>Clarity: {insights.clarityScore}/100</p>
          <p>Relevance: {insights.relevanceScore}/100</p>
          <p>Filler words: {insights.fillerCount}</p>
        </div>

        <div className="card">
          <h3>Job context</h3>
          <p>{summary || "Upload a job description to tailor feedback."}</p>
        </div>

        <div className="card">
          <h3>Transcript + Quick Analysis</h3>
          {answers.length === 0 && <p className="muted">No answers captured yet.</p>}
          {answers.map((item, idx) => (
            <div key={idx} className="answer-block">
              <p><strong>Q:</strong> {item.question}</p>
              <p><strong>A:</strong> {item.answer}</p>
            </div>
          ))}
          {answers.length > 0 && (
            <ul>
              <li>Pace: {insights.pace}</li>
              <li>Words spoken: {insights.wordCount}</li>
              <li>Filler words spotted: {insights.fillerCount}</li>
            </ul>
          )}
        </div>

        <div className="card">
          <h3>Improvement Tips</h3>
          <ul>
            <li>Lead with a 15-second summary tied to the role requirements.</li>
            <li>Trim filler words and add 1-2 concrete metrics per story.</li>
            <li>Close each answer with how it maps to the job description.</li>
          </ul>
        </div>
      </div>

      <div className="actions">
        <button className="button" onClick={() => navigate("/interview")}>Retry interview</button>
        <button className="secondary" onClick={() => navigate("/")}>Upload a new job description</button>
      </div>
    </div>
  );
}

export default FeedbackPage;
