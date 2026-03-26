import { Link } from "react-router-dom";

export default function ActivationErrorPage() {
  return (
    <div className="flex flex-col justify-center items-center gap-3 p-3">
      <h1 className="text-3xl text-center">Activation Failed</h1>

      <p className="text-xl text-center">
        If you see this page, link is invalid, has expired or your account is
        already activated
      </p>

      <Link to="/" className="text-xl">
        Back to{" "}
        <span className="text-emerald-500 hover:text-emerald-300">
          HomePage
        </span>
      </Link>
    </div>
  );
}
