import React, { useState, useRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Send, BrainCircuit, RefreshCw } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { postCopilotMessage, clearHistory } from '../store/slices/copilotSlice';
import { economistSuggestions } from '../mockData/inflationData';

export const Copilot = () => {
  const dispatch = useDispatch();
  const { messages, loading } = useSelector((state) => state.copilot);
  const [inputText, setInputText] = useState('');
  const chatEndRef = useRef(null);

  // Auto-scroll chat window
  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSendMessage = (textToSend) => {
    const query = textToSend || inputText;
    if (!query.trim() || loading) return;

    dispatch(postCopilotMessage(query));
    setInputText('');
  };

  const handleResetHistory = () => {
    dispatch(clearHistory());
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[calc(100vh-180px)]">
      {/* Configuration & Quick Suggestions */}
      <div className="lg:col-span-1 flex flex-col gap-6 h-full">
        <Card className="flex-1 flex flex-col justify-between overflow-y-auto">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <BrainCircuit size={18} className="text-cyan-400" />
              <h3 className="text-sm font-bold font-display text-white uppercase tracking-wider">Copilot Suggestions</h3>
            </div>
            <p className="text-xs text-slate-500 mb-6">Click any quick prompt to query the AI Economist regarding current macroeconomic trends.</p>

            <div className="space-y-3">
              {economistSuggestions.map((item, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSendMessage(item.q)}
                  disabled={loading}
                  className="w-full text-left p-3.5 rounded-xl bg-slate-950/40 border border-slate-900 hover:border-cyan-500/25 hover:bg-slate-900/10 text-xs font-semibold text-slate-300 hover:text-cyan-400 transition-all disabled:opacity-50"
                >
                  {item.label}
                  <span className="block text-[10px] text-slate-500 font-normal mt-1 truncate">{item.q}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="pt-6 border-t border-slate-900 mt-6 space-y-3.5">
            <div className="flex items-center justify-between text-2xs font-bold text-slate-500 uppercase tracking-wider">
              <span>Retrieval Status</span>
              <span className="text-emerald-400">RAG ground active</span>
            </div>
            <div className="flex items-center justify-between text-2xs font-bold text-slate-500 uppercase tracking-wider">
              <span>Token Budget</span>
              <span className="text-slate-400">Custom context applied</span>
            </div>
          </div>
        </Card>
      </div>

      {/* Main Chat Box Container */}
      <Card className="lg:col-span-3 flex flex-col h-full overflow-hidden p-0">
        {/* Chat header */}
        <div className="p-4 border-b border-slate-900 flex justify-between items-center bg-slate-950/15">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 flex items-center justify-center">
              <BrainCircuit size={20} className="animate-pulse" />
            </div>
            <div>
              <h3 className="text-sm font-bold font-display text-white">Macroeconomic Analyst Agent</h3>
              <p className="text-[10px] text-emerald-400 font-semibold flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" /> Online & Ingesting FRED
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button 
              onClick={handleResetHistory}
              className="p-2 text-slate-500 hover:text-white rounded-lg hover:bg-slate-900/40"
              title="Reset conversation"
            >
              <RefreshCw size={14} />
            </button>
          </div>
        </div>

        {/* Message Feed Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-5">
          {messages.map((msg, index) => {
            const isAI = msg.role === 'assistant';
            return (
              <div 
                key={index}
                className={`flex gap-4 max-w-3xl ${isAI ? '' : 'ml-auto flex-row-reverse'}`}
              >
                {/* Avatar icons */}
                <div className={`w-8.5 h-8.5 rounded-lg flex items-center justify-center shrink-0 font-extrabold text-xs border ${
                  isAI 
                    ? 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20' 
                    : 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20'
                }`}>
                  {isAI ? 'AI' : 'US'}
                </div>

                {/* Bubble content */}
                <div className="space-y-1">
                  <div className={`p-4 rounded-2xl text-xs leading-relaxed ${
                    isAI 
                      ? 'bg-slate-900/40 border border-slate-900 text-slate-200' 
                      : 'bg-cyan-500 text-slate-950 font-medium'
                  }`}>
                    {/* Render mock markdown features (strong headers, bullet points) */}
                    <div dangerouslySetInnerHTML={{ 
                      __html: (msg.content || '')
                        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                        .replace(/\* (.*?)\n/g, '&bull; $1<br/>') 
                    }} />
                  </div>
                  <span className="block text-[10px] text-slate-600 px-1">{msg.timestamp || 'Just now'}</span>
                </div>
              </div>
            );
          })}

          {/* Typing Indicator */}
          {loading && (
            <div className="flex gap-4 max-w-lg">
              <div className="w-8.5 h-8.5 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 flex items-center justify-center font-extrabold text-xs">
                AI
              </div>
              <div className="bg-slate-900/40 border border-slate-900 px-4 py-3 rounded-2xl flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-cyan-500/40 animate-bounce" />
                <span className="w-2 h-2 rounded-full bg-cyan-500/40 animate-bounce [animation-delay:0.2s]" />
                <span className="w-2 h-2 rounded-full bg-cyan-500/40 animate-bounce [animation-delay:0.4s]" />
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input box bar */}
        <div className="p-4 border-t border-slate-900 bg-slate-950/20">
          <form 
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="flex gap-2 items-center"
          >
            <input 
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Ask a macro economy query (e.g. 'What is the food forecast?')..."
              className="flex-1 bg-slate-950/60 border border-slate-900 rounded-xl px-4 py-3 text-xs text-slate-200 focus:outline-none focus:border-cyan-500/50 transition-colors"
              disabled={loading}
            />
            <Button 
              type="submit"
              className="p-3.5 rounded-xl flex items-center justify-center aspect-square"
              disabled={!inputText.trim() || loading}
            >
              <Send size={16} />
            </Button>
          </form>
        </div>
      </Card>
    </div>
  );
};

