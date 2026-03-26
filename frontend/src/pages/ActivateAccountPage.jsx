import { resendActivationEmail } from "../api/auth";
import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

function ActivateAccountPage() {
  useEffect(() => {
    document.title = "Steam | ActivationAccountPage";
  }, []);

  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const email = searchParams.get("email");

  useEffect(() => {
    if (!email) navigate("/register", { replace: true });
  }, [email, navigate]);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState("");
  const [isSent, setIsSent] = useState(true);

  const handleClick = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const response = await resendActivationEmail(email);
      setMessage(response.data.message);
    } catch (error) {
      setMessage(error.data.message);
      setIsSent(false);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col justify-center items-center gap-3">
      <h1 className="text-3xl text-center p-3">
        Your account has been registered!
      </h1>
      <h2 className="text-xl text-center p-3">{message}</h2>
      <p
        className={`text-xl text-center p-3 ${isSent ? "text-green-400" : "text-red-400"}`}
      >
        We've sent an email to your mailbox, click the link to activate your
        account!
      </p>

      <button
        onClick={handleClick}
        disabled={isSubmitting}
        type="submit"
        className={`py-2 border w-1/2 rounded-xl mx-auto block my-5 bg-linear-to-tr from-emerald-200 via-emerald-400 to-emerald-600 hover:bg-linear-to-bl text-black hover:cursor-pointer transition-all duration-300 ease-in-out ${isSubmitting ? "opacity-50 cursor-not-allowed" : ""}`}
      >
        {isSubmitting ? "Resending email..." : "Resend"}
      </button>
    </div>
  );
}

export default ActivateAccountPage;
