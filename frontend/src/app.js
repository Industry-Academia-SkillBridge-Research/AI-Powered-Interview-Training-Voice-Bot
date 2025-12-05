import { BrowserRouter, Routes, Route } from "react-router-dom";
import UploadJDPage from "./pages/upload_jd_page.js";
import InterviewPage from "./pages/interview_page.js";
import FeedbackPage from "./pages/feedback_page.js";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<UploadJDPage />} />
        <Route path="/interview" element={<InterviewPage />} />
        <Route path="/feedback" element={<FeedbackPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
