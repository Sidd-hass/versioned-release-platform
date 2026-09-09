import { useEffect, useState } from "react";

function App() {
  const [health, setHealth] = useState(null);

  useEffect(() => {
    fetch("http://localhost:3000/api/health")
      .then((response) => response.json())
      .then((data) => setHealth(data))
      .catch((error) => console.error("API Error:", error));
  }, []);

  return (
    <div>
      <h1>Versioned Release Platform</h1>

      {health ? (
        <>
          <p>Status: {health.status}</p>
          <p>Application Version: {health.version}</p>
        </>
      ) : (
        <p>Loading...</p>
      )}
    </div>
  );
}

export default App;