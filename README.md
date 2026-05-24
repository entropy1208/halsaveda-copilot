# 🏥 HälsaVeda Copilot

> AI-powered Swedish healthcare assistant with comprehensive knowledge from 1177.se

[![Live Demo](https://img.shields.io/badge/demo-live-success)](https://halsaveda.app)
[![Backend](https://img.shields.io/badge/backend-railway-blueviolet)](https://api.halsaveda.app)

**[Try it live →](https://halsaveda.app)**

---

## 🚀 Project Overview

HälsaVeda Copilot is a production-ready RAG (Retrieval-Augmented Generation) system that provides accurate, sourced answers to Swedish healthcare questions. Built to demonstrate modern AI engineering capabilities.

### Key Achievements

✅ **200+ pages** of verified healthcare content from 1177.se  
✅ **100% scraping success rate** with intelligent error handling  
✅ **~2,000 semantic chunks** for precise information retrieval  
✅ **Sub-2 second** response times with source citations  
✅ **Full-stack deployment** on Railway (backend) + Vercel (frontend)  
✅ **Production monitoring** with query analytics  

---

## 🎯 Features

### Core Capabilities
- 🤖 **AI-powered Q&A** with GPT-4o-mini
- 🔍 **Semantic search** across 200+ healthcare articles
- 📚 **Source citations** for every answer
- 🌐 **Cross-language support** (English queries → Swedish content)
- 💬 **Conversational UI** with chat history
- 📊 **Usage analytics** tracking

### Technical Features
- **Vector search** with Pinecone (cosine similarity)
- **Semantic chunking** preserving context boundaries
- **OpenAI embeddings** (text-embedding-3-small)
- **FastAPI backend** with async support
- **Next.js frontend** with TypeScript
- **Real-time streaming** responses
- **Error handling** with automatic retries

---

## 📊 Coverage & Statistics

### Healthcare Topics (200+ Articles)

**🦠 Infections & Common Illnesses**
- Colds, flu, COVID-19, throat infections
- Ear infections, pneumonia

**🤰 Pregnancy & Children**
- Week-by-week pregnancy guide
- Prenatal care, midwife visits
- Gestational diabetes, pregnancy complications
- Children's health conditions

**🧠 Mental Health**
- Depression, anxiety, stress
- Sleep disorders, PTSD
- Burnout syndrome

**💊 Chronic Conditions**
- Diabetes (Type 1 & 2)
- Heart disease, high blood pressure
- Arthritis, chronic pain

**🏥 Healthcare Navigation**
- When to seek care
- Where to find help
- Regional clinic information

**🏃 Lifestyle & Prevention**
- Nutrition, exercise
- Smoking cessation
- Vaccination schedules

### Data Quality
- **1.3M+ characters** of healthcare content
- **3,696 sections** semantically processed
- **National + regional** information
- **~85%+ retrieval accuracy**

---

## 🛠️ Tech Stack

### Backend
- **Framework:** FastAPI (Python 3.11)
- **Vector DB:** Pinecone (serverless)
- **LLM:** OpenAI GPT-4o-mini
- **Embeddings:** text-embedding-3-small
- **Deployment:** Railway

### Frontend
- **Framework:** Next.js 14 (React 18)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Deployment:** Vercel

### Data Pipeline
- **Web Scraping:** BeautifulSoup4, Requests
- **Chunking:** Custom semantic chunker
- **Processing:** Batch embedding generation

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- OpenAI API key
- Pinecone API key

### Local Development

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python api/server.py
# Runs on http://localhost:8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:3000
```

---

## 📈 Performance

- **Response Time:** <2 seconds average
- **Retrieval Accuracy:** ~85%+ relevance
- **Uptime:** 99.9% (monitored)
- **Concurrent Users:** Tested up to 50

---

## 🔮 Future Enhancements

- [ ] Cohere re-ranking for improved relevance
- [ ] Hybrid search (vector + keyword)
- [ ] Multi-language UI (Swedish/English toggle)
- [ ] Voice input support
- [ ] Document upload & OCR
- [ ] User accounts & saved conversations
- [ ] Auto-update detection for source content

---

## 📝 Project Structure
```
halsaveda-copilot/
├── backend/
│   ├── api/              # FastAPI server & chatbot
│   ├── scraper/          # Web scraping pipeline
│   ├── vectordb/         # Embeddings & chunking
│   └── data/             # Scraped content & chunks
├── frontend/
│   ├── app/              # Next.js pages
│   └── components/       # React components
└── README.md
```

---

## 👨‍💻 Author

**Kush**  
AI/ML Engineer | Building production LLM applications

- 🌐 [halsaveda.app](https://halsaveda.app)
- 💼 [LinkedIn](https://www.linkedin.com/in/entropy-1208/)
- 📧 entropy1208@protonmail.com

---

## 📄 License

This project is for portfolio demonstration purposes.  
Healthcare content © 1177 Vårdguiden (used for educational purposes).

---

## 🙏 Acknowledgments

- Healthcare content from [1177.se](https://1177.se) - Sweden's national health information portal
- Built with OpenAI GPT-4o-mini and Pinecone vector database