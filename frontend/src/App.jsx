import { useState } from "react";
import { checkTransaction } from "./api.js";

export default function App() {
  const [form, setForm] = useState({
    amount: 100.0,
    hour: 12,
    location_change: 0,
    device_change: 0,
    transaction_type: "online",
  });
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({
      ...current,
      [name]: name === "transaction_type" ? value : Number(value),
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await checkTransaction(form);
      setResult(response);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Request failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <h1 style={styles.heading}>Invisible Fraud Detector</h1>
        <p style={styles.copy}>
          Enter transaction details and check whether the payment looks safe or fraudulent.
        </p>

        <form onSubmit={handleSubmit} style={styles.form}>
          <label style={styles.label}>
            Amount ($)
            <input
              style={styles.input}
              type="number"
              name="amount"
              value={form.amount}
              min="0"
              step="0.01"
              onChange={handleChange}
            />
          </label>

          <label style={styles.label}>
            Hour of day
            <input
              style={styles.input}
              type="number"
              name="hour"
              value={form.hour}
              min="0"
              max="23"
              onChange={handleChange}
            />
          </label>

          <label style={styles.label}>
            Location changed?
            <select style={styles.input} name="location_change" value={form.location_change} onChange={handleChange}>
              <option value={0}>No</option>
              <option value={1}>Yes</option>
            </select>
          </label>

          <label style={styles.label}>
            Device changed?
            <select style={styles.input} name="device_change" value={form.device_change} onChange={handleChange}>
              <option value={0}>No</option>
              <option value={1}>Yes</option>
            </select>
          </label>

          <label style={styles.label}>
            Transaction type
            <select style={styles.input} name="transaction_type" value={form.transaction_type} onChange={handleChange}>
              <option value="online">Online</option>
              <option value="pos">POS</option>
              <option value="atm">ATM</option>
            </select>
          </label>

          <button type="submit" style={styles.button} disabled={loading}>
            {loading ? "Checking..." : "Check Fraud Risk"}
          </button>
        </form>

        {error && <div style={styles.error}>Error: {error}</div>}

        {result && (
          <div style={styles.resultBox}>
            <h2>{result.status}</h2>
            <p>Risk score: {result.risk_score}</p>
            <strong>Reasons:</strong>
            <ul>
              {result.reasons.map((reason, index) => (
                <li key={index}>{reason}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    background: "#f3f5f9",
    padding: "2rem",
  },
  card: {
    width: "100%",
    maxWidth: "520px",
    background: "white",
    padding: "2rem",
    borderRadius: "16px",
    boxShadow: "0 20px 80px rgba(0,0,0,0.08)",
  },
  heading: {
    margin: "0 0 0.5rem",
  },
  copy: {
    margin: "0 0 1.75rem",
    color: "#555",
  },
  form: {
    display: "grid",
    gap: "1rem",
  },
  label: {
    display: "grid",
    gap: "0.5rem",
    fontSize: "0.95rem",
    color: "#333",
  },
  input: {
    width: "100%",
    padding: "0.8rem",
    borderRadius: "10px",
    border: "1px solid #d8dce7",
    fontSize: "1rem",
  },
  button: {
    marginTop: "0.5rem",
    padding: "0.95rem 1rem",
    borderRadius: "10px",
    border: "none",
    background: "#2d60ff",
    color: "white",
    fontSize: "1rem",
    cursor: "pointer",
  },
  resultBox: {
    marginTop: "1.5rem",
    padding: "1rem",
    background: "#f6f8ff",
    borderRadius: "12px",
    border: "1px solid #dde2ff",
  },
  error: {
    marginTop: "1rem",
    padding: "1rem",
    borderRadius: "10px",
    background: "#ffe8e8",
    color: "#9a1c1c",
  },
};
