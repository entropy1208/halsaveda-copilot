'use client';

import { useState, useRef, useEffect } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
}

interface Source {
  title: string;
  url: string;
  score: number;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Hej! I\'m HälsaVeda Copilot, your Swedish healthcare assistant. Ask me anything!'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // EXAMPLE QUESTIONS
  const exampleQuestions = [
    "What should I do for a cold?",
    "When should I see a doctor for fever?",
    "How do I treat a sore throat?",
    "Hur behandlar man förkylning?"
  ];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    await sendMessage(userMessage);
  };

  const handleExampleClick = async (question: string) => {
    setInput(question);
    await sendMessage(question);
  };

  const sendMessage = async (userMessage: string) => {
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: userMessage, top_k: 3 })
      });

      if (!response.ok) throw new Error('API failed');
      const data = await response.json();
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.answer,
        sources: data.sources
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '❌ Error: Make sure backend is running'
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <header className="bg-white border-b px-6 py-4 shadow-sm">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-2xl font-bold text-gray-900">🏥 HälsaVeda Copilot</h1>
          <p className="text-sm text-gray-600">AI-powered Swedish healthcare assistant</p>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-4xl mx-auto space-y-6">
          {messages.map((message, index) => (
            <div key={index} className={message.role === 'user' ? 'flex justify-end' : 'flex justify-start'}>
              <div className={message.role === 'user' ? 'max-w-3xl rounded-lg px-6 py-4 bg-blue-600 text-white' : 'max-w-3xl rounded-lg px-6 py-4 bg-white text-gray-900 shadow-md'}>
                <div className="whitespace-pre-wrap">{message.content}</div>
                
                {message.sources && message.sources.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <p className="text-sm font-semibold text-gray-700 mb-2">📚 Sources:</p>
                    {message.sources.map((source, idx) => (
                      <div key={idx} className="text-sm mb-1">
                        <a href={source.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                          [{idx + 1}] {source.title} ({Math.round(source.score * 100)}%)
                        </a>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {/* SHOW EXAMPLE QUESTIONS WHEN CHAT IS EMPTY */}
          {messages.length === 1 && !loading && (
            <div className="flex justify-center">
              <div className="max-w-2xl w-full">
                <p className="text-sm text-gray-600 mb-3 text-center">Try asking:</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {exampleQuestions.map((question, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleExampleClick(question)}
                      className="text-left px-4 py-3 bg-white rounded-lg shadow-sm hover:shadow-md transition border border-gray-200 hover:border-blue-400 text-gray-700 text-sm"
                    >
                      💬 {question}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
          
          {loading && (
            <div className="flex justify-start">
              <div className="bg-white rounded-lg px-6 py-4 shadow-md">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="bg-white border-t px-4 py-4">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto flex space-x-4">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about Swedish healthcare..."
            className="flex-1 rounded-lg border px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400"
          >
            {loading ? 'Sending...' : 'Send'}
          </button>
        </form>
      </div>
    </div>
  );
}
