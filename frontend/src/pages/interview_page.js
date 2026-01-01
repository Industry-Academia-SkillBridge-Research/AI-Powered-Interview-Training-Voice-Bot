import React, { useEffect, useMemo, useRef, useState } from "react";
import BotQuestionBox from "../components/bot_question_box";
import MicRecorder from "../components/mic_recorder";
import TranscriptBox from "../components/transcript_box";
import { useNavigate } from "react-router-dom";
import { useJobContext } from "../job_context";

function InterviewPage() {
  const navigate = useNavigate();
  const { summary, questions, extractedText } = useJobContext();

  const [qIndex, setQIndex] = useState(0);
  const [transcript, setTranscript] = useState("");
  const [answers, setAnswers] = useState([]);
  const [listening, setListening] = useState(false);
  const [ttsReady, setTtsReady] = useState(Boolean(window.speechSynthesis));
  const [sttReady, setSttReady] = useState(true);
  const recognitionRef = useRef(null);

  const activeQuestion = questions?.[qIndex] || "Tell me about yourself and your key strengths.";

  useEffect(() => {
    if (!extractedText) navigate("/");
  }, [extractedText, navigate]);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setSttReady(false);
      return undefined;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onresult = (event) => {
      const result = Array.from(event.results)
        .map((res) => res[0].transcript)
        .join(" ");
      setTranscript(result);
    };

    recognition.onstart = () => setListening(true);
    recognition.onend = () => setListening(false);
    recognition.onerror = () => setListening(false);

    recognitionRef.current = recognition;
    return () => recognition.stop();
  }, []);

  const speakQuestion = () => {
    if (!window.speechSynthesis) {
      setTtsReady(false);
      return;
    }
    const utterance = new SpeechSynthesisUtterance(activeQuestion);
    utterance.rate = 0.95;
    utterance.pitch = 1.02;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
  };

  const startListening = () => {
    recognitionRef.current?.start();
  };

  const stopListening = (capture = false) => {
    recognitionRef.current?.stop();
    setListening(false);
    if (capture && transcript) {
      setAnswers((prev) => [...prev, { question: activeQuestion, answer: transcript }]);
      setTranscript("");
    }
  };

  const goNext = () => {
    stopListening();
    const latest = transcript ? [...answers, { question: activeQuestion, answer: transcript }] : answers;
    setAnswers(latest);
    setTranscript("");
    if (qIndex < questions.length - 1) setQIndex((prev) => prev + 1);
    else navigate("/feedback", { state: { answers: latest } });
  };

  const plannedQuestions = useMemo(() => questions || [], [questions]);

  return (
    <div className="page interview-layout">
      <div className="page-header">
        <div>
          <p className="eyebrow">Step 2 · Voice interview</p>
          <h1>AI follows up using the uploaded role</h1>
          <p className="muted">We speak the question, you answer in voice. Live transcript and recordings stay on your device.</p>
        </div>
        <div className="badge">Speech beta</div>
      </div>

      <div className="interview-grid">
        <div>
          <BotQuestionBox question={activeQuestion} />

          <div className="control-card">
            <div className="control-row">
              <button className="button" onClick={speakQuestion}>🔊 Play question</button>
              <button className="ghost" onClick={startListening} disabled={!sttReady || listening}>🎙️ Start listening</button>
              <button className="secondary" onClick={() => stopListening(true)} disabled={!listening}>⏹ Stop</button>
            </div>
            {!sttReady && <div className="error-banner">Speech recognition not supported in this browser.</div>}
            {!ttsReady && <div className="error-banner">Speech synthesis unavailable. Questions will still show on screen.</div>}
          </div>

          <div className="control-card">
            <TranscriptBox transcript={transcript} />
          </div>

          <div className="control-card">
            <MicRecorder onStop={(data) => console.log("Audio blob:", data)} />
          </div>

          <div className="actions">
            <button className="button" onClick={goNext}>
              {qIndex < plannedQuestions.length - 1 ? "Next question →" : "Finish and view feedback"}
            </button>
            <button className="secondary" onClick={() => navigate("/")}>Replace job description</button>
          </div>
        </div>

        <div className="side-panel">
          <div className="panel-title">Job description snapshot</div>
          <p>{summary || "Upload a job description first."}</p>

          <div className="panel-title" style={{ marginTop: 18 }}>Planned prompts</div>
          <ul className="question-list">
            {plannedQuestions.map((q, idx) => (
              <li key={q} className={idx === qIndex ? "active" : ""}>
                <span className="pill">Q{idx + 1}</span>
                <span>{q}</span>
              </li>
            ))}
          </ul>

          <div className="panel-title" style={{ marginTop: 18 }}>Captured answers</div>
          {answers.length === 0 && <p className="muted">Your answers appear here after you stop listening.</p>}
          {answers.map((item, idx) => (
            <div className="card" key={idx}>
              <div className="muted" style={{ marginBottom: 6 }}>{item.question}</div>
              <div>{item.answer}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default InterviewPage;
