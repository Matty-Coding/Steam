import { Link } from "react-router-dom";
import reactLogo from "../assets/react.svg";

export default function NavBar() {
  return (
    <nav className="sticky p-5 flex justify-between items-center">
      <section>
        <Link to="/">
          <img src={reactLogo} alt="Home" />
        </Link>
      </section>
      <ul className="flex items-center gap-3">
        <li className="hover:underline">
          <Link to="/login">Sign In</Link>
        </li>
        <li className="hover:underline">
          <Link to="/register">Sign Up</Link>
        </li>
      </ul>
    </nav>
  );
}
