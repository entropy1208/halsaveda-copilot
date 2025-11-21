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
      content: 'Hej! I\'m HälsaVeda Copilot, your Swedish healthcare assistant. Ask me anything about healthcare in Sweden!'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [totalQueries, setTotalQueries] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Example questions for better UX
  const exampleQuestions = [
    "What should I do for a cold?",
    "When should I see a doctor for fever?",
    "How do I treat a sore throat?",
    "Hur behandlar man förkylning?"
  ];

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Fetch usage stats on mount
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/stats/usage`);
        const data = await response.json();
        setTotalQueries(data.total_queries);
      } catch (error) {
        // Silently fail - stats are not critical
        console.log('Could not fetch stats');
      }
    };
    
    fetchStats();
  }, []);

  // Clear conversation history
  const handleClearChat = () => {
    if (confirm('Clear conversation history?')) {
      setMessages([{
        role: 'assistant',
        content: 'Hej! I\'m HälsaVeda Copilot, your Swedish healthcare assistant. Ask me anything about healthcare in Sweden!'
      }]);
    }
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    await sendMessage(userMessage);
  };

  // Handle example question clicks
  const handleExampleClick = async (question: string) => {
    if (loading) return;
    setInput(question);
    await sendMessage(question);
  };

  // Send message with retry logic and better error handling
  const sendMessage = async (userMessage: string) => {
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    const maxRetries = 2;
    let attempt = 0;

    while (attempt <= maxRetries) {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000); // 30s timeout

        const response = await fetch(`${apiUrl}/api/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question: userMessage, top_k: 3 }),
          signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          throw new Error(`API returned ${response.status}`);
        }

        const data = await response.json();
        
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: data.answer,
          sources: data.sources
        }]);
        
        // Update query count after successful query
        if (totalQueries !== null) {
          setTotalQueries(totalQueries + 1);
        }
        
        break; // Success! Exit retry loop

      } catch (error) {
        attempt++;
        
        if (attempt > maxRetries) {
          // Final failure after retries
          let errorMessage = '❌ Sorry, I encountered an error. ';
          
          if (error instanceof Error) {
            if (error.name === 'AbortError') {
              errorMessage += 'The request took too long. Please try a simpler question.';
            } else if (error.message.includes('Failed to fetch')) {
              errorMessage += 'Cannot connect to the server. Please check your internet connection.';
            } else if (error.message.includes('500')) {
              errorMessage += 'Server error. Please try again in a moment.';
            } else {
              errorMessage += 'Please try again.';
            }
          } else {
            errorMessage += 'Please try again.';
          }
          
          setMessages(prev => [...prev, {
            role: 'assistant',
            content: errorMessage
          }]);
        } else {
          // Wait before retry
          await new Promise(resolve => setTimeout(resolve, 1000));
        }
      }
    }
    
    setLoading(false);
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header with Clear Chat button and Query Count */}
      <header className="bg-white border-b px-6 py-4 shadow-sm">
        <div className="max-w-4xl mx-auto flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">🏥 HälsaVeda Copilot</h1>
            <p className="text-sm text-gray-600">
              AI-powered Swedish healthcare assistant
              {totalQueries && totalQueries > 0 && (
                <span className="ml-2 text-gray-500">
                  • {totalQueries.toLocaleString()} queries answered
                </span>
              )}
            </p>
          </div>
          {messages.length > 1 && (
            <button
              onClick={handleClearChat}
              className="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg text-gray-700 transition flex items-center gap-2"
              title="Clear conversation"
            >
              <span>🗑️</span>
              <span className="hidden sm:inline">Clear Chat</span>
            </button>
          )}
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-4xl mx-auto space-y-6">
          {messages.map((message, index) => (
            <div 
              key={index} 
              className={message.role === 'user' ? 'flex justify-end' : 'flex justify-start'}
            >
              <div 
                className={
                  message.role === 'user' 
                    ? 'max-w-3xl rounded-lg px-6 py-4 bg-blue-600 text-white' 
                    : 'max-w-3xl rounded-lg px-6 py-4 bg-white text-gray-900 shadow-md'
                }
              >
                <div className="whitespace-pre-wrap">{message.content}</div>
                
                {/* Sources */}
                {message.sources && message.sources.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <p className="text-sm font-semibold text-gray-700 mb-2">📚 Sources:</p>
                    <div className="space-y-1">
                      {message.sources.map((source, idx) => (
                        <div key={idx} className="text-sm">
                          <a 
                            href={source.url} 
                            target="_blank" 
                            rel="noopener noreferrer" 
                            className="text-blue-600 hover:underline font-medium"
                          >
                            [{idx + 1}] {source.title}
                          </a>
                          <span className="text-gray-500 ml-2">
                            (relevance: {Math.round(source.score * 100)}%)
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {/* Example Questions - Show when chat is empty */}
          {messages.length === 1 && !loading && (
            <div className="flex justify-center">
              <div className="max-w-2xl w-full">
                <p className="text-sm text-gray-600 mb-3 text-center font-medium">
                  Try asking:
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {exampleQuestions.map((question, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleExampleClick(question)}
                      className="text-left px-4 py-3 bg-white rounded-lg shadow-sm hover:shadow-md transition-all border border-gray-200 hover:border-blue-400 text-gray-700 text-sm hover:bg-blue-50"
                    >
                      <span className="mr-2">💬</span>
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
          
          {/* Loading indicator */}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-white rounded-lg px-6 py-4 shadow-md">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="bg-white border-t px-4 py-4">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
          <div className="flex space-x-4">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about Swedish healthcare..."
              className="flex-1 rounded-lg border border-gray-300 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
            >
              {loading ? 'Sending...' : 'Send'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
