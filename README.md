# HälsaVeda Copilot 🏥

AI-powered Swedish healthcare navigation assistant using RAG (Retrieval-Augmented Generation).

## Features

- 🤖 Semantic search across Swedish healthcare information (1177.se)
- 🔍 RAG-based question answering with source citations
- 🌐 Cross-language support (English queries → Swedish content)
- 💬 Beautiful chat interface
- ⚡ Fast API responses

## Tech Stack

**Backend:**
- Python 3.11
- FastAPI
- OpenAI (embeddings + GPT-4o-mini)
- Pinecone (vector database)
- BeautifulSoup (web scraping)

**Frontend:**
- Next.js 15
- TypeScript
- Tailwind CSS
- React

## Architecture
```
User Query → Frontend (Next.js)
    ↓
Backend API (FastAPI)
    ↓
Query Engine → Pinecone Vector Search
    ↓
Retrieved Chunks → GPT-4o-mini
    ↓
Answer with Citations → User
```

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 20+
- OpenAI API key
- Pinecone API key

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
echo "OPENAI_API_KEY=your_key" > .env
echo "PINECONE_API_KEY=your_key" >> .env

# Run server
python api/server.py
```

Backend runs on http://localhost:8000

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Frontend runs on http://localhost:3000

## Project Structure
```
halsaveda-copilot/
├── backend/
│   ├── scraper/          # Web scraping
│   ├── vectordb/         # Embeddings & search
│   ├── api/              # FastAPI server
│   └── data/             # Scraped content (not in git)
├── frontend/
│   ├── app/              # Next.js app
│   └── public/           # Static assets
└── README.md
```

## Deployment

- Backend: Railway
- Frontend: Vercel
- Domain: halsaveda.app

## License

MIT

## Author

Built by Kush as a learning project in AI/ML engineering.
