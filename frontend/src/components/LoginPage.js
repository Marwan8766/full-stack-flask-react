import React, { useState } from "react";
import "./LoginPage.css";

function LoginPage({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleEmailChange = (event) => {
    setEmail(event.target.value);
  };

  const handlePasswordChange = (event) => {
    setPassword(event.target.value);
  };

  const handleLoginClick = async () => {
    // Prepare the request payload
    const payload = {
      email: email,
      password: password,
    };

    try {
      // Make the POST request
      const response = await fetch("http://127.0.0.1:5000/api/v1/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      // Check if the response is successful
      const data = await response.json();
      if (data.status === "success") {
        const token = data.token;
        onLogin(token); // Pass the token to the parent component's onLogin function
      } else {
        console.error(`Login failed. ${data.message}`);
        alert(data.message);
      }
    } catch (error) {
      console.error("An error occurred:", error);
    }
  };

  return (
    <div className="login-container">
      <div className="login-form">
        <h2 className="login-form-label">Login Page</h2>
        <div>
          <label className="login-form-label">Email:</label>
          <input
            className="login-input"
            type="email"
            value={email}
            onChange={handleEmailChange}
          />
        </div>
        <div>
          <label className="login-form-label">Password:</label>
          <input
            className="login-input"
            type="password"
            value={password}
            onChange={handlePasswordChange}
          />
        </div>
        <button className="login-button" onClick={handleLoginClick}>
          Login
        </button>
      </div>
    </div>
  );
}

export default LoginPage;
