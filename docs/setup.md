# External Setup Requirements

## Firebase Setup

1. Create a new Firebase project at https://console.firebase.google.com/
2. Enable Authentication:
   - Go to Authentication > Sign-in method
   - Enable Email/Password authentication
3. Set up Firestore:
   - Go to Firestore Database
   - Create database in production mode
   - Set up security rules:
   ```javascript
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       match /{document=**} {
         allow read, write: if request.auth != null;
       }
     }
   }
   ```
4. Get Firebase configuration:
   - Go to Project Settings
   - Copy the configuration object
   - Add to frontend/.env:
   ```
   VITE_FIREBASE_API_KEY=your_api_key
   VITE_FIREBASE_AUTH_DOMAIN=your_auth_domain
   VITE_FIREBASE_PROJECT_ID=your_project_id
   VITE_FIREBASE_STORAGE_BUCKET=your_storage_bucket
   VITE_FIREBASE_MESSAGING_SENDER_ID=your_messaging_sender_id
   VITE_FIREBASE_APP_ID=your_app_id
   ```

## OpenAI API Setup

1. Create an OpenAI account at https://platform.openai.com/
2. Generate an API key:
   - Go to API keys
   - Create new secret key
3. Add to backend/.env:
   ```
   OPENAI_API_KEY=your_api_key
   ```

## Pinecone Setup

1. Create a Pinecone account at https://www.pinecone.io/
2. Create a new project and index:
   - Project name: timeloop-tales
   - Index name: npc-memories
   - Dimension: 1536 (for OpenAI embeddings)
   - Metric: cosine
3. Get API credentials:
   - Copy API key and environment
   - Add to backend/.env:
   ```
   PINECONE_API_KEY=your_api_key
   PINECONE_ENVIRONMENT=your_environment
   ```

## Environment Variables

### Frontend (.env)
```
VITE_FIREBASE_API_KEY=your_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_auth_domain
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_storage_bucket
VITE_FIREBASE_MESSAGING_SENDER_ID=your_messaging_sender_id
VITE_FIREBASE_APP_ID=your_app_id
```

### Backend (.env)
```
OPENAI_API_KEY=your_api_key
PINECONE_API_KEY=your_api_key
PINECONE_ENVIRONMENT=your_environment
```

## Development Setup

1. Install dependencies:
   ```bash
   # Frontend
   cd frontend
   npm install

   # Backend
   cd backend
   python -m venv venv
   source venv/bin/activate  # or .\venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. Start development servers:
   ```bash
   # Frontend (in one terminal)
   cd frontend
   npm run dev

   # Backend (in another terminal)
   cd backend
   uvicorn main:app --reload
   ```

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs 