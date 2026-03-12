import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Home } from "./pages/Home";
import { NavBar } from "./components/NavBar";

function App() {
  return (
    <BrowserRouter>
      <Home />
      <NavBar />

      <Routes>
        <Route path="/" />
        <Route path="/register" />
        <Route path="/login" />
        <Route path="/logout" />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
