# Stony Brook FC Service

The backend service for managing FIFA tournament matches (1v1 and 2v2 matches) and tracking player & match statistics.

## Project Structure

```
fifa-tournament/
├── frontend/    # React application
├── backend/     # FastAPI server
└── sql/         # Database schemas and migrations
```

## Setup Instructions

### Backend Setup

1. Create a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up the database:
```bash
psql -U postgres
CREATE DATABASE fifa_tournament;
\c fifa_tournament
\i sql/schema.sql
```

4. Run the server:
```bash
cd app
python main.py
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Run the development server:
```bash
npm start
```

## Development

- Backend API runs on: http://localhost:8000
- Frontend dev server runs on: http://localhost:3000
- API documentation available at: http://localhost:8000/docs

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Submit a pull request
