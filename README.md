# HälsaVeda Copilot 🏥

AI-powered Swedish healthcare navigation assistant using RAG (Retrieval-Augmented Generation).

🌐 **Live Demo:** https://halsaveda.app

## Quick Links

- 🌐 **Live Application:** https://halsaveda.app
- 📡 **API Endpoint:** https://api.halsaveda.app
- 📚 **API Documentation:** https://api.halsaveda.app/docs
- 💻 **Source Code:** https://github.com/entropy1208/halsaveda-copilot

## Features

- 🤖 AI-powered Q&A with source citations
- 🔍 Semantic search across Swedish healthcare information (1177.se)
- 🌐 Cross-language support (English queries → Swedish content)
- 💬 Beautiful, responsive chat interface
- ⚡ Real-time responses with GPT-4o-mini

## Tech Stack

**Backend:**
- FastAPI (Python)
- OpenAI API (text-embedding-3-small + GPT-4o-mini)
- Pinecone Vector Database
- BeautifulSoup (web scraping)
- Deployed on Railway

**Frontend:**
- Next.js 15 + TypeScript
- Tailwind CSS
- Deployed on Vercel

## Architecture
```
User Query → Next.js Frontend (halsaveda.app)
              ↓
         FastAPI Backend (api.halsaveda.app)
              ↓
         Semantic Search (Pinecone)
              ↓
         GPT-4o-mini (OpenAI)
              ↓
         Cited Answer → User
```

## Local Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for setup instructions.

## Project Status

✅ MVP deployed and functional
🔄 Scaling data coverage (currently 3 pages, expanding to 200+)
📋 Roadmap: Document upload, conversation history, multi-language UI

## Built By

Kush - AI/ML Engineer
- 🌐 Live Demo: https://halsaveda.app
- 💼 GitHub: https://github.com/entropy1208

## License

MIT