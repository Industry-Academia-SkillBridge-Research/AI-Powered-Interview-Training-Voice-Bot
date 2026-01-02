function TranscriptBox({ transcript }) {
  return (
    <div className="card">
      <h3>🎤 Live Transcript</h3>
      <p>{transcript || "Recording..."}</p>
    </div>
  );
}

export default TranscriptBox;
