import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import reactLogo from "../assets/react.svg";
import { useAuthContext } from "../hooks/useAuthContext";
import { useNavigate } from "react-router-dom";

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuthContext();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    document.title = "Steam | LoginPage";
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    const data = new FormData(e.currentTarget);
    const email = data.get("email");
    const password = data.get("password");

    try {
      const result = await login(email, password);

      if (result.status === 200) {
        navigate("/");
      } else if (result.response.userEmail?.length > 0) {
        navigate("/activate");
      }
    } catch (error) {
      setMessage(error.response.data);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <Link to="/" className="p-5 absolute">
        <img src={reactLogo} alt="Home" />
      </Link>
      <div className="max-w-lg mx-auto p-5 h-full flex flex-col justify-between translate-y-32">
        <h1 className="font-semibold text-3xl text-center">Welcome back</h1>

        <p className={message ? "text-green-500" : "text-red-500"}>{message}</p>

        <section className="p-3 mt-14">
          <form
            action=""
            method="post"
            className="flex flex-col gap-3"
            onSubmit={handleSubmit}
          >
            <div className="flex flex-col gap-1 px-2">
              <label htmlFor="email">Email</label>
              <input
                type="email"
                name="email"
                id="email"
                placeholder="email@example.com"
                className="focus:outline-none py-2 border-t placeholder:italic text-center"
                required
              />
            </div>

            <div className="flex flex-col gap-1 px-2">
              <label htmlFor="password">Password</label>
              <input
                type="password"
                name="password"
                id="password"
                placeholder="********"
                className="focus:outline-none py-2 border-t text-center"
              />
            </div>

            <button
              disabled={isSubmitting}
              type="submit"
              className={`py-2 border w-1/2 rounded-xl mx-auto block my-5 bg-linear-to-tr from-emerald-200 via-emerald-400 to-emerald-600 hover:bg-linear-to-bl text-black hover:cursor-pointer transition-all duration-300 ease-in-out ${isSubmitting ? "opacity-50 cursor-not-allowed" : ""}`}
            >
              {isSubmitting ? "Signing In..." : "Sign In"}
            </button>
          </form>

          <p className="border-t text-center pt-2">
            Do not have any account?
            <Link
              to="/register"
              className="ml-2 text-emerald-400 hover:text-emerald-300 transition-colors duration-300 ease-in-out font-semibold"
            >
              Sign Up
            </Link>
          </p>
        </section>
      </div>
    </>
  );
}
