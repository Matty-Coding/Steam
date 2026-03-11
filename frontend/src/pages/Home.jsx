import { useEffect, useState } from "react";
import { clientApi } from "../api/client";

export function Home() {
  useEffect(() => {
    document.title = "Home Page | Steam";
  }, []);

  const [response, setResponse] = useState(null);

  useEffect(() => {
    clientApi
      .get("/")
      .then((response) => setResponse(response.data))
      .catch((error) => console.error(error));
  }, []);

  return response ? <p>{response.message}</p> : <p>Loading...</p>;
}
