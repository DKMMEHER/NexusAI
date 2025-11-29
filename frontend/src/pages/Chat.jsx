import React, { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, Loader2, Trash2, Settings, Search, Code, Check, ChevronDown, Sparkles } from 'lucide-react';
import { api } from '../api/client';
import { toast } from 'sonner';

const Chat = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [showSettings, setShowSettings] = useState(false);
    const [showModelDropdown, setShowModelDropdown] = useState(false);

    // Settings State
    const [selectedModel, setSelectedModel] = useState("gemini-2.0-flash-exp");
    const [enableSearch, setEnableSearch] = useState(false);
    const [enableCode, setEnableCode] = useState(false);

    const messagesEndRef = useRef(null);
    const dropdownRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setShowModelDropdown(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMessage = { role: 'user', content: input };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            const formData = new FormData();
            formData.append('message', input);

            // Send History
            const historyToSend = JSON.stringify(messages);
            formData.append('history', historyToSend);

            // Send Model
            formData.append('model', selectedModel);

            // Send Tools
            const tools = [];
            if (enableSearch) tools.push("google_search");
            if (enableCode) tools.push("code_execution");
            if (tools.length > 0) {
                formData.append('tools', JSON.stringify(tools));
            }

            const response = await api.chat(formData);

            const botMessage = { role: 'model', content: response.response };
            setMessages(prev => [...prev, botMessage]);
        } catch (error) {
            console.error("Chat error:", error);
            toast.error("Failed to send message. Please try again.");
        } finally {
            setIsLoading(false);
        }
    };

    const clearChat = () => {
        setMessages([]);
        toast.success("Chat history cleared");
    };

    const models = [
        { id: "gemini-2.0-flash-exp", name: "Gemini 2.0 Flash", badge: "Experimental" },
        { id: "gemini-2.0-flash-thinking-exp-1219", name: "Gemini 2.0 Flash Thinking", badge: "Reasoning" },
        { id: "gemini-3-pro-preview", name: "Gemini 3 Pro", badge: "Preview" },
    ];

    const selectedModelData = models.find(m => m.id === selectedModel) || models[0];

    return (
        <div className="flex flex-col h-[calc(100vh-8rem)] bg-white dark:bg-slate-900 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800 overflow-hidden relative">
            {/* Header */}
            <div className="p-4 border-b border-slate-200 dark:border-slate-800 flex justify-between items-center bg-slate-50 dark:bg-slate-800/50">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white shadow-lg shadow-indigo-500/20">
                        <Sparkles size={20} />
                    </div>
                    <div>
                        <h2 className="font-semibold text-slate-900 dark:text-white leading-tight">AI Assistant</h2>

                        {/* Custom Model Dropdown */}
                        <div className="relative" ref={dropdownRef}>
                            <button
                                onClick={() => setShowModelDropdown(!showModelDropdown)}
                                className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400 hover:text-primary dark:hover:text-primary transition-colors mt-0.5 group"
                            >
                                <span className="font-medium">{selectedModelData.name}</span>
                                {selectedModelData.badge && (
                                    <span className="px-1.5 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-[10px] font-medium text-slate-500">
                                        {selectedModelData.badge}
                                    </span>
                                )}
                                <ChevronDown size={12} className={`transition-transform duration-200 ${showModelDropdown ? 'rotate-180' : ''}`} />
                            </button>

                            {/* Dropdown Menu */}
                            {showModelDropdown && (
                                <div className="absolute top-full left-0 mt-2 w-64 bg-white dark:bg-slate-800 rounded-xl shadow-xl border border-slate-200 dark:border-slate-700 p-1.5 z-50 animate-in fade-in slide-in-from-top-2 max-h-96 overflow-y-auto">
                                    <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider px-2 py-1.5 sticky top-0 bg-white dark:bg-slate-800 z-10">Select Model</div>
                                    {models.map(model => (
                                        <button
                                            key={model.id}
                                            onClick={() => {
                                                setSelectedModel(model.id);
                                                setShowModelDropdown(false);
                                            }}
                                            className={`w-full flex items-center justify-between px-2 py-2 rounded-lg text-sm transition-colors ${selectedModel === model.id
                                                    ? 'bg-primary/10 text-primary'
                                                    : 'text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700'
                                                }`}
                                        >
                                            <div className="flex flex-col items-start gap-0.5">
                                                <span className="font-medium">{model.name}</span>
                                                {model.badge && (
                                                    <span className="text-[10px] text-slate-400">{model.badge}</span>
                                                )}
                                            </div>
                                            {selectedModel === model.id && <Check size={14} />}
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    <button
                        onClick={() => setShowSettings(!showSettings)}
                        className={`p-2 rounded-lg transition-colors ${showSettings ? 'bg-primary/10 text-primary' : 'text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'}`}
                        title="Agent Settings"
                    >
                        <Settings size={18} />
                    </button>
                    <button
                        onClick={clearChat}
                        className="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                        title="Clear Chat"
                    >
                        <Trash2 size={18} />
                    </button>
                </div>
            </div>

            {/* Settings Panel */}
            {showSettings && (
                <div className="absolute top-16 right-4 z-20 w-72 bg-white dark:bg-slate-800 rounded-xl shadow-xl border border-slate-200 dark:border-slate-700 p-4 animate-in fade-in slide-in-from-top-2">
                    <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-3">Configuration</h3>

                    <div className="space-y-4">
                        <div>
                            <p className="text-xs text-slate-400 mb-2">
                                Select the model from the header dropdown.
                            </p>
                        </div>

                        <div className="border-t border-slate-100 dark:border-slate-700 pt-3">
                            <label className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-2 block">Agent Capabilities</label>
                            <div className="space-y-2">
                                <button
                                    onClick={() => setEnableSearch(!enableSearch)}
                                    className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors border ${enableSearch
                                            ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800 text-blue-700 dark:text-blue-300'
                                            : 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:border-slate-300'
                                        }`}
                                >
                                    <div className={`w-6 h-6 rounded flex items-center justify-center ${enableSearch ? 'bg-blue-100 dark:bg-blue-800' : 'bg-slate-100 dark:bg-slate-700'}`}>
                                        <Search size={14} />
                                    </div>
                                    <span className="flex-1 text-left">Google Search</span>
                                    {enableSearch && <Check size={14} />}
                                </button>

                                <button
                                    onClick={() => setEnableCode(!enableCode)}
                                    className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors border ${enableCode
                                            ? 'bg-emerald-50 dark:bg-emerald-900/20 border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-300'
                                            : 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:border-slate-300'
                                        }`}
                                >
                                    <div className={`w-6 h-6 rounded flex items-center justify-center ${enableCode ? 'bg-emerald-100 dark:bg-emerald-800' : 'bg-slate-100 dark:bg-slate-700'}`}>
                                        <Code size={14} />
                                    </div>
                                    <span className="flex-1 text-left">Code Execution</span>
                                    {enableCode && <Check size={14} />}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-slate-400 space-y-4">
                        <div className="w-16 h-16 rounded-2xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
                            <Bot size={32} />
                        </div>
                        <p>Start a conversation with the AI Assistant</p>
                    </div>
                ) : (
                    messages.map((msg, index) => (
                        <div
                            key={index}
                            className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                            {msg.role === 'model' && (
                                <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary shrink-0 mt-1">
                                    <Bot size={16} />
                                </div>
                            )}
                            <div
                                className={`max-w-[80%] rounded-2xl px-4 py-3 ${msg.role === 'user'
                                        ? 'bg-primary text-white rounded-tr-none'
                                        : 'bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 rounded-tl-none'
                                    }`}
                            >
                                <p className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</p>
                            </div>
                            {msg.role === 'user' && (
                                <div className="w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center text-slate-500 shrink-0 mt-1">
                                    <User size={16} />
                                </div>
                            )}
                        </div>
                    ))
                )}
                {isLoading && (
                    <div className="flex gap-3 justify-start">
                        <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary shrink-0 mt-1">
                            <Bot size={16} />
                        </div>
                        <div className="bg-slate-100 dark:bg-slate-800 rounded-2xl rounded-tl-none px-4 py-3 flex items-center gap-2">
                            <Loader2 size={16} className="animate-spin text-slate-400" />
                            <span className="text-xs text-slate-400">Thinking...</span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900">
                <form onSubmit={handleSend} className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Type your message..."
                        className="flex-1 px-4 py-3 rounded-xl bg-slate-50 dark:bg-slate-800 border-none focus:ring-2 focus:ring-primary/20 text-slate-900 dark:text-white placeholder-slate-400 outline-none transition-all"
                        disabled={isLoading}
                    />
                    <button
                        type="submit"
                        disabled={!input.trim() || isLoading}
                        className="p-3 rounded-xl bg-primary text-white hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                        <Send size={20} />
                    </button>
                </form>
            </div>
        </div>
    );
};

export default Chat;
