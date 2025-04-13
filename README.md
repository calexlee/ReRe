# ReRe

A browser-based, AI-driven narrative RPG where the player is trapped in a time loop that resets on death. Each loop gives them more knowledge, dialogue options, and clues about how to survive until the next day.

## Setup

1. Install dependencies:
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

2. Set up environment variables:
```bash
# Backend
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# Frontend
cp frontend/.env.example frontend/.env
```

3. Start the development servers:
```bash
# Backend
cd backend
uvicorn main:app --reload

# Frontend
cd frontend
npm run dev
```

## Project Structure

- `backend/`: FastAPI server with game logic and AI integration
- `frontend/`: React frontend with TypeScript
- `docs/`: Project documentation

## Project Structure

```
ReRe/
├── frontend/          # React + Tailwind frontend
├── backend/           # FastAPI backend
├── ai/               # AI integration and utilities
└── docs/             # Documentation and setup guides
```

## Setup Instructions

### Prerequisites
- Node.js (v18 or higher)
- Python (v3.9 or higher)
- Firebase account
- OpenAI API key

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

### Environment Variables
Create a `.env` file in both frontend and backend directories with:
- Firebase configuration
- OpenAI API key
- Other necessary API keys

## External Setup Required
1. Firebase Project Setup
   - Create a new Firebase project
   - Enable Authentication
   - Set up Firestore database
   - Configure security rules

2. OpenAI API
   - Create an OpenAI account
   - Generate API key
   - Set up billing

3. Vector Database
   - Set up Pinecone or FAISS
   - Configure memory storage