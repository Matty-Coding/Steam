import "./App.css";
import { Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import NotFoundPage from "./pages/NotFoundPage";
import ActivateAccountPage from "./pages/ActivateAccountPage";
import ActivateAccount from "./components/ActivateAccount";
import ActivationErrorPage from "./pages/ActivationErrorPage";

function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="*" element={<NotFoundPage />} />
        <Route path="/activate" element={<ActivateAccountPage />} />
        <Route
          path="/auth/activate/:uidb64/:token"
          element={<ActivateAccount />}
        />
        <Route path="/activate-error" element={<ActivationErrorPage />}></Route>
      </Routes>
    </>
  );
}

export default App;
