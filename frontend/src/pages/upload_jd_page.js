import React, { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";

function UploadJDPage() {
  const [fileName, setFileName] = useState(null);
  const [fileSize, setFileSize] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const navigate = useNavigate();
  const inputRef = useRef();

  const handleFileObject = (file) => {
    if (!file) return;
    setFileName(file.name);
    setFileSize(file.size);
  };

  const handleFile = (e) => {
    const file = e.target.files?.[0];
    handleFileObject(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer?.files?.[0];
    handleFileObject(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const openFileDialog = () => inputRef.current?.click();

  const formatBytes = (bytes) => {
    if (!bytes) return "";
    const sizes = ["B","KB","MB","GB"];
    const i = Math.floor(Math.log(bytes)/Math.log(1024));
    return (bytes / Math.pow(1024, i)).toFixed(1) + " " + sizes[i];
  };

  return (
    <div className="page">
      <h1>Upload Job Description</h1>
      <div className="upload-container">
        <label
          className={`drop-area ${dragOver ? "drag-over" : ""}`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={() => setDragOver(false)}
          onClick={openFileDialog}
        >
          <div className="drop-left">
            <div className="icon">📁</div>
          </div>
          <div className="drop-right">
            <div className="drop-title">Drag & drop the job description here</div>
            <p className="muted">or click to browse (PDF, DOC, DOCX, TXT). We'll extract key requirements for the interview.</p>
            <input
              ref={inputRef}
              type="file"
              accept=".pdf,.doc,.docx,.txt"
              style={{ display: "none" }}
              onChange={handleFile}
            />
            {!fileName && (
              <div className="muted" style={{ marginTop: 12 }}>No file selected yet</div>
            )}
            {fileName && (
              <div className="card" style={{ marginTop: 12 }}>
                <div style={{fontSize:18}}>📄</div>
                <div>
                  <div className="file-name">{fileName}</div>
                  <div className="muted">{formatBytes(fileSize)}</div>
                </div>
              </div>
            )}
          </div>
        </label>

        <div className="info-panel">
          <div style={{fontWeight:700, marginBottom:8}}>Ready to proceed?</div>
          <div className="muted">Upload your job description to customize the interview and feedback.</div>

          <div className="actions">
            <button
              className="button"
              disabled={!fileName}
              onClick={() => navigate("/interview")}
            >
              Continue →
            </button>
            <button
              className="secondary"
              onClick={() => {
                setFileName(null);
                setFileSize(null);
              }}
            >
              Remove
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default UploadJDPage;
