import React, { useState, useEffect } from 'react';

function App() {
  const [message, setMessage] = useState("Loading...");

  useEffect(() => {
    console.log(process.env)
    const apiUrl = process.env.REACT_APP_API_URL;
    fetch(apiUrl)
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => setMessage(data.message))
      .catch(error => {
        console.error("Error fetching data:", error);
        setMessage("Error fetching message.");
      });
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <p>{message}</p>
      </header>
    </div>
  );
}

export default App;