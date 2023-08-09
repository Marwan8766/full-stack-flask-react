import React, { useState, useEffect } from "react";
import "./TablePage.css";
import io from "socket.io-client";

const socket = io("http://127.0.0.1:5000");

function TablePage(props) {
  const [existingValue, setExistingValue] = useState("");
  const [inputValue, setInputValue] = useState("");
  const [percentage, setPercentage] = useState("");

  useEffect(() => {
    fetchExistingValue();
  }, []); // Run this effect once when the component mounts

  const fetchExistingValue = async () => {
    try {
      const response = await fetch(
        "http://127.0.0.1:5000/api/v1/users/get_existing_value",
        {
          headers: {
            Authorization: `Bearer ${props.token}`, // Include the JWT token in the Authorization header
          },
        }
      );

      const data = await response.json();
      if (data.status === "success") {
        setExistingValue(data.existing_value);
      } else {
        console.error("Failed to fetch existing value:", data.message);
      }
    } catch (error) {
      console.error("An error occurred:", error);
    }
  };

  const handleInputChange = (event) => {
    setInputValue(event.target.value);
    console.log(`i/p changed to ${event.target.value}`);
    socket.emit("calculate_percentage", {
      num1: existingValue,
      num2: event.target.value,
    });
  };

  socket.on("percentage_result", (data) => {
    setPercentage(data.percentage);
    console.log(`percentage: ${data.percentage}`);
  });

  return (
    <div className="table-container">
      {/* Add the "table-wrapper" class */}
      <div className="table-wrapper">
        <h2 className="table-header">Table Page</h2>
        <table className="table">
          <thead>
            <tr>
              <th>Input Value</th>
              <th>Existing Value</th>
              <th>Percentage</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td className="input-cell">
                <input
                  type="number"
                  value={inputValue}
                  onChange={handleInputChange}
                />
              </td>
              <td className="existing-value-cell">
                {existingValue !== null ? existingValue : "Loading..."}
              </td>
              <td className="result-cell percentage">
                {percentage !== ""
                  ? `${percentage.toFixed(2)}%`
                  : "Enter value to calculate the percentage"}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default TablePage;
