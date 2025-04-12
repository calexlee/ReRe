# TimeLoop Tales

A browser-based, AI-driven narrative RPG where players are trapped in a time loop that resets on death. Each loop provides more knowledge, dialogue options, and clues about how to survive until the next day.

## Project Structure

```
timeloop-tales/
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

## MVP Features
- Dark fantasy village setting
- 3-5 NPCs with persistent dialogue memory
- Time loop mechanics
- Basic vector memory system
- One core mystery/death event

## Future Improvements
- Additional settings (sci-fi, noir, historical)
- Custom setting/character creation
- Enhanced AI memory systems
- Procedural event generation
- Multiplayer support

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

## Contributing
Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests. 