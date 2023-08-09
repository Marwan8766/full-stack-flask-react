import React, { useState } from "react";
import "./App.css";
import LoginPage from "./components/LoginPage.js";
import TablePage from "./components/TablePage.js";

function App() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [token, setToken] = useState(""); // State to store the token

  const handleLogin = (receivedToken) => {
    // Simulate login logic here
    setLoggedIn(true);
    setToken(receivedToken); // Set the token in the state
    console.log(`token in app.js ${receivedToken}`);
  };

  return (
    <div className="App">
      <header className="App-header">
        {loggedIn ? (
          <TablePage token={token} />
        ) : (
          <LoginPage onLogin={handleLogin} />
        )}
      </header>
    </div>
  );
}

export default App;
