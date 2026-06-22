'use client';

import { useState, useRef, useEffect } from 'react';

interface Source {
  title: string;
  url: string;
  score: number;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
  timestamp?: string;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [totalQueries, setTotalQueries] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const exampleQuestions = [
    "What should I do for a cold?",
    "When should I see a doctor for fever?",
    "How do I treat a sore throat?",
    "Hur behandlar man förkylning?"
  ];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/stats/usage`);
        const data = await response.json();
        setTotalQueries(data.total_queries);
      } catch (e) {
        // Stats unavailable
      }
    };
    fetchStats();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    await sendMessage(input.trim());
  };

  const handleExampleClick = async (question: string) => {
    if (loading) return;
    await sendMessage(question);
  };

  const sendMessage = async (userMessage: string) => {
    setInput('');
    
    const timestamp = new Date().toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
    
    setMessages(prev => [...prev, {
      role: 'user',
      content: userMessage,
      timestamp
    }]);
    
    setLoading(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000);

      const response = await fetch(`${apiUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: userMessage, top_k: 3 }),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error('API error');
      }

      const data = await response.json();
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
        timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
      }]);

      if (totalQueries !== null) {
        setTotalQueries(totalQueries + 1);
      }

    } catch (error) {
      const errorMsg = error instanceof Error && error.name === 'AbortError' 
        ? '❌ Request timeout. Please try a simpler question.'
        : '❌ Could not get response. Please try again.';
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: errorMsg,
        timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
      }]);
    }
    
    setLoading(false);
  };

  return (
    <div className="flex flex-col h-screen bg-white">
      {/* HEADER */}
      <header className="border-b border-gray-200 bg-white sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-600 to-blue-700 flex items-center justify-center">
              <span className="text-white font-bold">H</span>
            </div>
            <div>
              <h1 className="text-xl font-semibold text-gray-900">HälsaVeda</h1>
              <p className="text-xs text-gray-600">Healthcare Assistant</p>
            </div>
          </div>
          
          {totalQueries !== null && (
            <div className="text-right">
              <div className="text-2xl font-bold text-gray-900">{totalQueries}</div>
              <div className="text-xs text-gray-600">answered</div>
            </div>
          )}
        </div>
      </header>

      {/* CHAT AREA */}
      <div className="flex-1 overflow-y-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          
          {/* WELCOME */}
          {messages.length === 0 && (
            <div className="space-y-8 py-12 text-center">
              <div className="space-y-4">
                <div className="inline-block text-4xl">🏥</div>
                <h2 className="text-4xl font-bold text-gray-900">
                  Healthcare at your fingertips
                </h2>
                <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                  Ask anything about Swedish healthcare
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl mx-auto">
                {exampleQuestions.map((q, i) => (
                  <button
                    key={i}
                    onClick={() => handleExampleClick(q)}
                    className="p-4 rounded-xl border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition text-left"
                  >
                    <div className="text-sm font-medium text-gray-900">{q}</div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* MESSAGES */}
          {messages.map((msg, i) => (
            <MessageBubble key={i} message={msg} />
          ))}

          {/* LOADING */}
          {loading && (
            <div className="flex justify-start mb-6">
              <div className="bg-gray-100 rounded-2xl px-6 py-4 flex gap-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* INPUT */}
      <div className="border-t border-gray-200 bg-white px-4 py-6">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
          <div className="flex gap-3 mb-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about Swedish healthcare..."
              className="flex-1 rounded-2xl border border-gray-300 px-6 py-4 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
              disabled={loading}
              autoFocus
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white px-6 py-4 rounded-2xl font-semibold transition"
            >
              Send
            </button>
          </div>
          <p className="text-xs text-gray-500 text-center">
            Powered by OpenAI · 1177.se
          </p>
        </form>
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex mb-6 ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className="max-w-2xl">
        {/* Message */}
        <div className={`rounded-2xl px-6 py-4 ${
          isUser ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-900'
        }`}>
          <div className="text-sm leading-relaxed whitespace-pre-wrap">
            {message.content}
          </div>
        </div>

        {/* Timestamp */}
        <div className="text-xs text-gray-500 mt-2 px-3">
          {message.timestamp}
        </div>

        {/* Sources */}
        {message.sources && message.sources.length > 0 && (
          <div className="mt-4">
            <div className="text-xs font-semibold text-gray-700 px-3 mb-2">
              📚 Sources
            </div>
            <SourceList sources={message.sources} />
          </div>
        )}
      </div>
    </div>
  );
}

function SourceList({ sources }: { sources: Source[] }) {
  return (
    <div className="space-y-2">
      {sources.map((src, idx) => (
        <SourceItem key={idx} source={src} index={idx} />
      ))}
    </div>
  );
}

function SourceItem({ source, index }: { source: Source; index: number }) {
  return (
    <div className="px-3 py-2 rounded-lg bg-gray-50 hover:bg-gray-100 transition">
      <a 
        href={source.url}
        target="_blank"
        rel="noopener noreferrer"
        className="text-xs font-medium text-blue-600 hover:text-blue-700 block"
      >
        [{index + 1}] {source.title}
      </a>
      <div className="text-xs text-gray-500 mt-1">
        Relevance: {Math.round(source.score * 100)}%
      </div>
    </div>
  );
}