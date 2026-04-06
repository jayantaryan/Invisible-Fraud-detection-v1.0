# Invisible Fraud Detector MVP

A full-stack fraud detection system built with FastAPI backend and React frontend.

## Features

- **Machine Learning Model**: RandomForest classifier trained on synthetic transaction data
- **Rule-Based Scoring**: Behavior-based risk assessment (high amounts, odd hours, device/location changes)
- **Combined Scoring**: ML predictions + rule-based scores for comprehensive risk assessment
- **Real-time API**: FastAPI backend with automatic documentation
- **Modern Frontend**: React app with clean UI for transaction risk checking

## Project Structure

```
invis-fraud/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── utils.py             # ML model, data generation, and scoring logic
│   ├── requirements.txt     # Python dependencies
│   └── model/
│       ├── dataset.csv      # Generated synthetic training data
│       └── model.pkl        # Trained RandomForest model
└── frontend/
    ├── src/
    │   ├── App.jsx          # Main React component
    │   ├── api.js           # API client for backend communication
    │   └── main.jsx         # React app entry point
    ├── package.json         # Node.js dependencies
    ├── vite.config.js       # Vite configuration
    └── index.html           # HTML template
```

## Quick Start

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the FastAPI server:
   ```bash
   python -m uvicorn main:app --host 127.0.0.1 --port 8001 --reload
   ```

   The API will be available at: `http://127.0.0.1:8001`

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

   The app will be available at: `http://127.0.0.1:5173`

## API Usage

### POST /check

Check transaction risk with the following JSON payload:

```json
{
  "amount": 100.0,
  "hour": 12,
  "location_change": 0,
  "device_change": 0,
  "transaction_type": "online"
}
```

**Response:**
```json
{
  "risk_score": 0.0,
  "status": "SAFE",
  "reasons": [
    "No behavior-based risk flags detected",
    "Model confidence for fraud: 0.00"
  ]
}
```

**Fields:**
- `amount`: Transaction amount (float, > 0)
- `hour`: Hour of day (0-23)
- `location_change`: 1 if location changed, 0 otherwise
- `device_change`: 1 if device changed, 0 otherwise
- `transaction_type`: "online", "pos", or "atm"

## Model Details

- **Algorithm**: RandomForestClassifier with 100 trees
- **Features**: Amount, hour, location change, device change, transaction type (one-hot encoded)
- **Training Data**: 1000 synthetic transactions generated programmatically
- **Accuracy**: 100% on training data (synthetic dataset)
- **Rule-based Scoring**: Combines ML prediction with behavior rules

## Risk Factors

The system flags transactions as high-risk for:
- Amount > $3000
- Transactions between 12 AM - 6 AM or 10 PM - 12 AM
- Device changes
- Location changes

## Development

- Backend uses Pydantic V2 for data validation
- Frontend built with Vite + React
- CORS enabled for local development
- Automatic API documentation at `/docs`

## Deployment

For production deployment:
1. Update CORS origins in `backend/main.py`
2. Configure proper environment variables
3. Use a production WSGI server (gunicorn)
4. Set up proper logging and monitoring