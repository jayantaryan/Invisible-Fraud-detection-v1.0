import axios from "axios";

const API_URL = "http://127.0.0.1:8000/check";

// Send transaction details to the backend /check endpoint.
export async function checkTransaction(transactionData) {
  const response = await axios.post(API_URL, transactionData);
  return response.data;
}
