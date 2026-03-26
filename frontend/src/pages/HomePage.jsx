import NavBar from "../components/NavBar";
import { useEffect } from "react";

export default function HomePage() {
  useEffect(() => {
    document.title = "Steam | HomePage";
  }, []);

  return <NavBar />;
}
