import React, { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { GlobalWorkerOptions, getDocument } from "pdfjs-dist";
import * as mammoth from "mammoth/mammoth.browser";
import { useJobContext } from "../job_context";

// Point pdf.js to its bundled worker (CRA webpack handles asset URL)
const workerSrc = new URL("pdfjs-dist/build/pdf.worker.min.mjs", import.meta.url);
GlobalWorkerOptions.workerSrc = workerSrc.toString();

const formatBytes = (bytes) => {
  if (!bytes) return "";
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), sizes.length - 1);
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
};

async function extractPdf(file) {
  const data = new Uint8Array(await file.arrayBuffer());
  const pdf = await getDocument({ data }).promise;
  let text = "";
  for (let i = 1; i <= pdf.numPages; i += 1) {
    const page = await pdf.getPage(i);
    const content = await page.getTextContent();
    text += content.items.map((item) => item.str).join(" ") + " ";
  }
  return text;
}

async function extractDocx(file) {
  const arrayBuffer = await file.arrayBuffer();
  const { value } = await mammoth.extractRawText({ arrayBuffer });
  return value || "";
}

async function extractPlain(file) {
  return file.text();
}

function UploadJDPage() {
  const [fileName, setFileName] = useState(null);
  const [fileSize, setFileSize] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [preview, setPreview] = useState("");
  const [error, setError] = useState(null);
  const [extracting, setExtracting] = useState(false);
  const navigate = useNavigate();
  const inputRef = useRef();
  const { saveExtraction, clearJob, summary, extractedText } = useJobContext();

  useEffect(() => {
    if (!fileName && extractedText) {
      setPreview(extractedText.slice(0, 400));
    }
  }, [extractedText, fileName]);

  const readFile = async (file) => {
    const mime = file.type;
    if (mime === "application/pdf") return extractPdf(file);
    if (mime === "application/vnd.openxmlformats-officedocument.wordprocessingml.document") return extractDocx(file);
    if (mime === "text/plain") return extractPlain(file);
    throw new Error("Unsupported file type. Please upload PDF, DOCX or TXT.");
  };

  const handleFileObject = async (file) => {
    if (!file) return;
    setError(null);
    setExtracting(true);
    setFileName(file.name);
    setFileSize(file.size);
    try {
      const text = await readFile(file);
      if (!text.trim()) throw new Error("Could not extract text. Try a different file.");
      saveExtraction({ name: file.name, size: file.size, text });
      setPreview(text.slice(0, 600));
    } catch (err) {
      console.error(err);
      setError(err.message || "Extraction failed");
      clearJob();
      setPreview("");
    } finally {
      setExtracting(false);
    }
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

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <p className="eyebrow">Step 1 · Upload</p>
          <h1>Upload a job description to personalize the interview</h1>
          <p className="muted">We extract key requirements (PDF, DOCX, TXT) and tailor voice questions on the fly.</p>
        </div>
        <div className="badge">Voice-ready</div>
      </div>

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
            <div className="drop-title">Drag & drop the job description</div>
            <p className="muted">or click to browse. We recommend PDF or DOCX for best extraction.</p>
            <input
              ref={inputRef}
              type="file"
              accept=".pdf,.docx,.txt"
              style={{ display: "none" }}
              onChange={handleFile}
            />
            {!fileName && (
              <div className="muted" style={{ marginTop: 12 }}>No file selected yet</div>
            )}
            {fileName && (
              <div className="card" style={{ marginTop: 12 }}>
                <div style={{ fontSize: 18 }}>📄</div>
                <div>
                  <div className="file-name">{fileName}</div>
                  <div className="muted">{formatBytes(fileSize)}</div>
                </div>
              </div>
            )}
            {extracting && <div className="inline-pill">Extracting text…</div>}
            {error && <div className="error-banner">{error}</div>}
          </div>
        </label>

        <div className="info-panel">
          <div className="panel-title">Extraction preview</div>
          {preview ? (
            <div className="preview-box">
              <div className="muted">First lines</div>
              <p>{preview}</p>
            </div>
          ) : (
            <div className="muted">Upload a file to see extracted content.</div>
          )}

          <div className="stats-row">
            <div>
              <div className="muted">Status</div>
              <div className="stat-value">{extracting ? "Extracting" : fileName ? "Ready" : "Waiting"}</div>
            </div>
            <div>
              <div className="muted">Characters read</div>
              <div className="stat-value">{summary ? summary.length : 0}</div>
            </div>
            <div>
              <div className="muted">File size</div>
              <div className="stat-value">{fileSize ? formatBytes(fileSize) : "—"}</div>
            </div>
          </div>

          <div className="actions">
            <button
              className="button"
              disabled={!summary || extracting}
              onClick={() => navigate("/interview")}
            >
              Continue to interview →
            </button>
            <button
              className="secondary"
              onClick={() => {
                setFileName(null);
                setFileSize(null);
                setPreview("");
                setError(null);
                clearJob();
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
