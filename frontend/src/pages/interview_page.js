import React, { useState, useEffect } from "react";
import BotQuestionBox from "../components/bot_question_box";
import MicRecorder from "../components/mic_recorder";
import TranscriptBox from "../components/transcript_box";
import { useNavigate } from "react-router-dom";

function InterviewPage() {
  const navigate = useNavigate();

  const questions = [
    "Tell me about yourself and your key strengths.",
    "Describe a challenge you faced and how you solved it.",
    "Why should we hire you for this role?"
  ];

  const [qIndex, setQIndex] = useState(0);
  const [transcript, setTranscript] = useState("");

  // Mock Live Transcript
  useEffect(() => {
    const recognition = new window.webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = (e) => {
      const text = e.results[e.resultIndex][0].transcript;
      setTranscript(text);
    };

    recognition.start();
  }, []);

  return (
    <div className="page">
      <h1>AI Interview Assistant</h1>

      <BotQuestionBox question={questions[qIndex]} />

      <TranscriptBox transcript={transcript} />

      <MicRecorder onStop={(data) => console.log("Audio blob:", data)} />

      <button className="button" onClick={() => {
        if (qIndex < questions.length - 1) setQIndex(qIndex + 1);
        else navigate("/feedback");
      }}>
        Next Question →
      </button>
    </div>
  );
}

export default InterviewPage;
