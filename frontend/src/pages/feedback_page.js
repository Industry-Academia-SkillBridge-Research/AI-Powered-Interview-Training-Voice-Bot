function FeedbackPage() {
  return (
    <div className="page">
      <h1>Interview Feedback</h1>

      <div className="card">
        <h3>Summary Scores</h3>
        <p>• Confidence Score: 72/100</p>
        <p>• Clarity Score: 80/100</p>
        <p>• Relevance Score: 68/100</p>
        <p>• Emotion Stability: Moderate</p>
      </div>

      <div className="card">
        <h3>Transcript + Analysis</h3>
        <p><strong>Q:</strong> Tell me about yourself</p>
        <p><strong>A:</strong> "I am a final year IT student..."</p>
        <ul>
          <li>Filler words: 3</li>
          <li>Pace: Slightly fast</li>
          <li>Sentiment: Neutral</li>
        </ul>
      </div>

      <div className="card">
        <h3>Improvement Tips</h3>
        <ul>
          <li>Reduce filler words (um, like, uh).</li>
          <li>Speak 10% slower for clarity.</li>
          <li>Add more examples relevant to the job.</li>
        </ul>
      </div>

      <button className="button" onClick={() => window.location.href = "/interview"}>
        Retry Interview
      </button>
    </div>
  );
}

export default FeedbackPage;
