import { useNavigate, useParams } from "react-router-dom";
import { activateAccountUser } from "../api/auth";
import { useEffect } from "react";

function ActivateAccount() {
  const navigate = useNavigate();
  const { uidb64, token } = useParams();

  useEffect(() => {
    const activatingAccount = async () => {
      try {
        const response = await activateAccountUser(uidb64, token);
        if (response.status === 200) navigate("/login");
      } catch {
        navigate("/activate-error");
      }
    };
    activatingAccount();
  }, [uidb64, token]); // eslint-disable-line

  return <></>;
}

export default ActivateAccount;
