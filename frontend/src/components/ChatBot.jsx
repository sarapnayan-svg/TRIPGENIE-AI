import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Bot,
  User,
  Sparkles,
  ShieldCheck,
  Loader2,
  HelpCircle,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  RotateCcw,
  MapPin,
  Calendar,
  Wallet,
  Users,
  Check,
  Compass,
} from 'lucide-react';
import { sendChatMessage } from '../services/api';

const QUICK_SUGGESTIONS = [
  { label: 'Make Day 3 cheaper', icon: '💸', prompt: 'Make Day 3 cheaper.' },
  { label: 'Replace scuba diving', icon: '🏄', prompt: 'Replace scuba diving with another activity.' },
  { label: 'Suggest veg restaurants', icon: '🥗', prompt: 'Suggest vegetarian restaurants.' },
  { label: 'Can I do this in 4 days?', icon: '⏱️', prompt: 'Can I complete this itinerary in 4 days?' },
  { label: 'Hotel closest to beach', icon: '🏖️', prompt: 'Which hotel is closest to the beach?' },
  { label: 'Reduce budget to ₹70k', icon: '📉', prompt: 'Reduce my budget to ₹70,000.' },
];

export default function ChatBot({ tripPlan, formData, destinationData, tripContext: passedContext }) {
  const destination = tripPlan?.destination || formData?.destination || passedContext?.destination || 'Goa';
  const durationDays = tripPlan?.days?.length || formData?.days || (Array.isArray(passedContext?.days) ? passedContext.days.length : passedContext?.days) || 5;
  const userBudget = tripPlan?.budget_breakdown?.user_budget || formData?.budget || passedContext?.budget || 50000;
  const travelersCount = formData?.travelers || passedContext?.travelers || 2;
  const travelStyle = formData?.travelStyle || passedContext?.travel_style || 'balanced';

  // Consolidated trip context for the backend
  const tripContext = {
    destination,
    days: tripPlan?.days || [],
    days_count: durationDays,
    budget: userBudget,
    travelers: travelersCount,
    travel_style: travelStyle,
    hotel_preference: formData?.hotelPreference || 'standard',
    transport_preference: formData?.transportPreference || 'private_cab',
    selected_activities: formData?.selectedActivities || [],
    summary: tripPlan?.summary || '',
  };

  const getInitialMessage = () => ({
    id: 'welcome',
    role: 'assistant',
    content: `Hello! I'm TripGenie, your conversational AI travel assistant. 🧞‍♂️\n\nI have loaded your active trip plan for **${destination}** (${durationDays} Days • ₹${Math.round(userBudget).toLocaleString('en-IN')} Budget • ${travelersCount} Travelers).\n\nAsk me anything! You can ask to rebalance your budget, replace activities, make a specific day cheaper, or find the best vegetarian restaurants!`,
    sources: [],
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
  });

  const [messages, setMessages] = useState([getInitialMessage()]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorNotice, setErrorNotice] = useState(null);
  const [expandedSources, setExpandedSources] = useState({});
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  // Update initial welcome message when destination or days changes
  useEffect(() => {
    setMessages((prev) => {
      if (prev.length === 1 && prev[0].id === 'welcome') {
        return [getInitialMessage()];
      }
      return prev;
    });
  }, [destination, durationDays, userBudget, travelersCount]);

  const handleClearChat = () => {
    if (messages.length <= 1 || window.confirm('Reset conversation history with TripGenie?')) {
      setMessages([getInitialMessage()]);
      setErrorNotice(null);
    }
  };

  const handleSend = async (textToSend) => {
    const text = (textToSend || input).trim();
    if (!text || loading) return;

    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInput('');
    setLoading(true);
    setErrorNotice(null);

    try {
      // Build conversation history (excluding initial welcome card)
      const history = newMessages
        .filter((m) => m.id !== 'welcome')
        .map((m) => ({ role: m.role, content: m.content }));

      const res = await sendChatMessage(text, tripContext, history);

      if (res.success && res.data) {
        const assistantMessage = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: res.data.reply,
          sources: res.data.sources || [],
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } else {
        const errText = res.error || 'Could not connect to FastAPI assistant.';
        setErrorNotice(errText);
        const errorMessage = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: `⚠️ ${errText}\n\nPlease verify that the backend server is running at http://127.0.0.1:8000.`,
          sources: [],
          isError: true,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    } catch (err) {
      setErrorNotice(err.message);
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `⚠️ Error communicating with assistant: ${err.message}`,
        sources: [],
        isError: true,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const toggleSource = (msgId) => {
    setExpandedSources((prev) => ({ ...prev, [msgId]: !prev[msgId] }));
  };

  // Helper to render bold markdown and clean bullet points
  const formatMessageText = (text) => {
    if (!text) return '';
    return text.split('\n').map((line, idx) => {
      // Parse **bold**
      const parts = line.split(/(\*\*.*?\*\*)/g);
      const formattedParts = parts.map((part, pIdx) => {
        if (part.startsWith('**') && part.endsWith('**')) {
          return <strong key={pIdx} className="font-bold text-ink">{part.slice(2, -2)}</strong>;
        }
        return part;
      });

      // Render bullet list lines with styled dot
      if (line.trim().startsWith('•') || line.trim().startsWith('-')) {
        return (
          <div key={idx} className="flex items-start gap-2 my-1">
            <span className="text-brand-500 font-bold mt-0.5">•</span>
            <span className="flex-1">{formattedParts}</span>
          </div>
        );
      }

      // Empty line spacer
      if (!line.trim()) {
        return <div key={idx} className="h-2" />;
      }

      return (
        <div key={idx} className="my-0.5">
          {formattedParts}
        </div>
      );
    });
  };

  return (
    <section id="chat" className="scroll-mt-24 max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 mb-24">
      <div className="bg-white rounded-3xl shadow-card border border-sand-dark overflow-hidden flex flex-col h-[720px]">
        
        {/* Chat Header */}
        <div className="p-4 sm:p-6 bg-gradient-to-r from-brand-900 via-brand-800 to-indigo-950 text-white flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3.5">
            <div className="w-12 h-12 rounded-2xl bg-white/15 backdrop-blur-md flex items-center justify-center text-2xl shadow-inner border border-white/20 flex-shrink-0">
              🧞‍♂️
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="font-display font-extrabold text-lg sm:text-xl leading-tight">
                  TripGenie AI Copilot
                </h2>
                <span className="px-2.5 py-0.5 rounded-full bg-emerald-400/20 text-emerald-300 text-[10px] font-bold border border-emerald-400/30">
                  RAG Grounded
                </span>
              </div>
              <p className="text-xs text-brand-200 mt-0.5">
                Conversational trip assistant aware of your active itinerary & budget
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2.5 self-end sm:self-auto">
            {/* Clear Chat Button */}
            <button
              onClick={handleClearChat}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/10 hover:bg-white/20 text-xs font-semibold text-brand-100 hover:text-white transition-all"
              title="Reset conversation"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Clear Chat</span>
            </button>

            <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/10 text-xs font-semibold text-brand-100 border border-white/10">
              <Sparkles className="w-3.5 h-3.5 text-amber-300 animate-pulse" />
              <span>Context Aware</span>
            </div>
          </div>
        </div>

        {/* Active Trip Context Bar */}
        <div className="bg-sand/80 px-4 sm:px-6 py-2.5 border-b border-sand-dark flex flex-wrap items-center justify-between gap-2 text-xs">
          <div className="flex items-center gap-1.5 text-ink font-bold">
            <Compass className="w-3.5 h-3.5 text-brand-600" />
            <span>Active Trip Context:</span>
          </div>

          <div className="flex flex-wrap items-center gap-2 text-[11px] text-ink-muted">
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-white border border-sand-dark font-semibold text-ink">
              <MapPin className="w-3 h-3 text-brand-500" />
              {destination}
            </span>
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-white border border-sand-dark font-semibold text-ink">
              <Calendar className="w-3 h-3 text-brand-500" />
              {durationDays} Days
            </span>
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-white border border-sand-dark font-semibold text-ink">
              <Wallet className="w-3 h-3 text-emerald-600" />
              ₹{Math.round(userBudget).toLocaleString('en-IN')}
            </span>
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-white border border-sand-dark font-semibold text-ink">
              <Users className="w-3 h-3 text-brand-500" />
              {travelersCount} Guests
            </span>
          </div>
        </div>

        {/* Messages Scroll Area */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4 bg-sand/25">
          {messages.map((msg) => {
            const isUser = msg.role === 'user';
            const hasSources = msg.sources && msg.sources.length > 0;
            const isSourcesOpen = !!expandedSources[msg.id];

            return (
              <div
                key={msg.id}
                className={`flex gap-3 max-w-[88%] sm:max-w-[80%] ${
                  isUser ? 'ml-auto flex-row-reverse' : 'mr-auto'
                }`}
              >
                {/* Avatar */}
                <div
                  className={`w-9 h-9 rounded-2xl flex items-center justify-center flex-shrink-0 text-sm font-bold shadow-sm ${
                    isUser
                      ? 'bg-gradient-to-tr from-brand-600 to-indigo-600 text-white'
                      : msg.isError
                      ? 'bg-rose-100 text-rose-700'
                      : 'bg-brand-100 text-brand-800'
                  }`}
                >
                  {isUser ? <User className="w-4 h-4" /> : msg.isError ? '!' : '🧞'}
                </div>

                {/* Message Bubble */}
                <div className="flex flex-col">
                  <div
                    className={`p-4 sm:p-5 rounded-2xl text-sm leading-relaxed shadow-sm ${
                      isUser
                        ? 'bg-gradient-to-r from-brand-600 to-indigo-600 text-white rounded-tr-none'
                        : msg.isError
                        ? 'bg-rose-50 text-rose-950 border border-rose-200 rounded-tl-none'
                        : 'bg-white text-ink border border-sand-dark rounded-tl-none'
                    }`}
                  >
                    {isUser ? msg.content : formatMessageText(msg.content)}
                  </div>

                  {/* Timestamp & Sources Row */}
                  <div className={`mt-1 flex items-center gap-2 ${isUser ? 'justify-end' : 'justify-start'}`}>
                    <span className="text-[10px] text-ink-muted">{msg.timestamp}</span>

                    {/* RAG Source Citation Toggle */}
                    {!isUser && hasSources && (
                      <button
                        type="button"
                        onClick={() => toggleSource(msg.id)}
                        aria-expanded={isSourcesOpen}
                        aria-label={`Toggle ${msg.sources.length} RAG grounding sources`}
                        className="inline-flex items-center gap-1 text-[11px] font-bold text-brand-600 hover:text-brand-800 transition-colors focus:outline-none focus:ring-1 focus:ring-brand-500 rounded"
                      >
                        <ShieldCheck className="w-3.5 h-3.5 text-brand-600" />
                        <span>{msg.sources.length} RAG Sources</span>
                        {isSourcesOpen ? (
                          <ChevronUp className="w-3 h-3" />
                        ) : (
                          <ChevronDown className="w-3 h-3" />
                        )}
                      </button>
                    )}
                  </div>

                  {/* Expanded Sources Drawer */}
                  {!isUser && hasSources && isSourcesOpen && (
                    <div className="mt-2.5 p-3.5 rounded-2xl bg-white border border-brand-200 text-xs text-ink space-y-2 shadow-sm animate-in fade-in duration-150">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-bold text-brand-700 uppercase tracking-wider">
                          Grounded Knowledge Evidence (RAG):
                        </span>
                      </div>
                      {msg.sources.map((s, idx) => (
                        <div key={idx} className="p-2.5 bg-sand/60 rounded-xl text-[11px] border border-sand-dark/60 leading-relaxed">
                          <span className="font-bold text-brand-700 uppercase text-[9px] mr-1.5 px-1.5 py-0.5 rounded bg-brand-50 border border-brand-200">
                            {s.category || 'Travel Chunk'}
                          </span>
                          <span>{s.text}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })}

          {/* Typing Loading Indicator */}
          {loading && (
            <div className="flex gap-3 max-w-[80%] mr-auto items-center">
              <div className="w-9 h-9 rounded-2xl bg-brand-100 text-brand-700 flex items-center justify-center text-sm font-bold shadow-sm">
                🧞
              </div>
              <div className="p-4 rounded-2xl bg-white border border-sand-dark text-xs text-ink-muted flex items-center gap-3 shadow-sm">
                <Loader2 className="w-4 h-4 animate-spin text-brand-600" />
                <span className="font-medium text-ink">TripGenie is consulting knowledge base & trip context...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Quick Suggestion Pills */}
        <div className="px-4 py-3 bg-white border-t border-sand-dark flex items-center gap-2 overflow-x-auto scrollbar-none">
          <span className="text-[11px] font-bold text-ink-muted flex items-center gap-1 flex-shrink-0 mr-1">
            <HelpCircle className="w-3.5 h-3.5 text-brand-500" />
            <span>Try asking:</span>
          </span>
          {QUICK_SUGGESTIONS.map((item, idx) => (
            <button
              key={idx}
              disabled={loading}
              onClick={() => handleSend(item.prompt)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-sand/90 hover:bg-brand-50 hover:text-brand-700 text-ink text-xs font-semibold border border-sand-dark hover:border-brand-200 whitespace-nowrap transition-all duration-150 flex-shrink-0 disabled:opacity-50"
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="p-4 bg-white border-t border-sand-dark flex items-center gap-3"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            placeholder={`Ask TripGenie about ${destination}, budgeting, restaurant swaps, or timing...`}
            className="flex-1 px-4 py-3.5 rounded-2xl border border-sand-dark focus:border-brand-500 focus:ring-2 focus:ring-brand-100 text-sm font-medium text-ink transition-all disabled:bg-sand/50"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="w-12 h-12 rounded-2xl bg-brand-600 hover:bg-brand-700 active:bg-brand-800 disabled:bg-sand-dark text-white disabled:text-ink-muted flex items-center justify-center transition-all flex-shrink-0 shadow-sm disabled:cursor-not-allowed"
            aria-label="Send message"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
          </button>
        </form>

      </div>
    </section>
  );
}
