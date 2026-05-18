import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import UploadPage from "./pages/UploadPage";
import LoginPage from "./pages/LoginPage";
import JoinPage from "./pages/JoinPage";
function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* web 히스토리에서 login만 기록이남도록 replace를 사용. */}
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/join" element={<JoinPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
