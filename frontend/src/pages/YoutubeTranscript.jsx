import React, { useState } from 'react';
import { Youtube, Loader2, AlertCircle, FileText } from 'lucide-react';
import { api } from '../api/client';
import ReactMarkdown from 'react-markdown';

const YoutubeTranscript = () => {
    const [url, setUrl] = useState('');
    const [selectedModel, setSelectedModel] = useState('gemini-2.5-flash');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!url) return;

        setLoading(true);
        setError(null);
        setResult(null);

        const formData = new FormData();
        formData.append('url', url);
        formData.append('model', selectedModel);

        try {
            const response = await api.youtube.getTranscript(formData);
            setResult(response);
        } catch (err) {
            console.error(err);
            console.error(err);
            const errorMessage = err.response?.data?.detail || err.message || "Failed to fetch transcript. Please check the URL and try again.";
            setError(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    const models = [
        { id: 'gemini-2.5-flash', name: 'Gemini 2.5 Flash', desc: 'Fast & Cost-Effective', badge: 'Flash' },
        { id: 'gemini-2.5-pro', name: 'Gemini 2.5 Pro', desc: 'High Quality & Reasoning', badge: 'Pro' },
        { id: 'gemini-3-pro-preview', name: 'Gemini 3.0 Pro Preview', desc: 'Next Gen Reasoning', badge: 'Preview' }
    ];

    return (
        <div className="max-w-7xl mx-auto space-y-8">
            {/* Header with Model Selector */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900 dark:text-white flex items-center gap-3">
                        <Youtube className="text-red-600" size={32} />
                        YouTube Transcript
                    </h1>
                    <p className="text-slate-500 dark:text-slate-400 mt-2 text-lg">
                        Get transcripts and summaries from YouTube videos instantly.
                    </p>
                </div>

                {/* Model Selector */}
                <div className="bg-white dark:bg-slate-800 p-1.5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex items-center gap-2">
                    {models.map(m => (
                        <button
                            key={m.id}
                            type="button"
                            onClick={() => setSelectedModel(m.id)}
                            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex flex-col items-start gap-0.5
                                ${selectedModel === m.id
                                    ? 'bg-red-600 text-white shadow-md'
                                    : 'text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700'
                                }`}
                        >
                            <span className="flex items-center gap-2">
                                {m.name}
                                {m.badge === 'Pro' && <span className="text-[10px] bg-yellow-400 text-yellow-900 px-1.5 rounded font-bold">PRO</span>}
                            </span>
                            <span className={`text-[10px] ${selectedModel === m.id ? 'text-white/80' : 'text-slate-400'}`}>{m.desc}</span>
                        </button>
                    ))}
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
                {/* Input Section */}
                <div className="lg:col-span-1 space-y-6">
                    <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 shadow-sm border border-slate-100 dark:border-slate-700">
                        <form onSubmit={handleSubmit} className="space-y-6">
                            <div>
                                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                                    YouTube URL
                                </label>
                                <input
                                    type="url"
                                    value={url}
                                    onChange={(e) => setUrl(e.target.value)}
                                    placeholder="https://www.youtube.com/watch?v=..."
                                    className="w-full px-4 py-3 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 transition-all"
                                    required
                                />
                            </div>

                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full py-3 px-4 bg-red-600 hover:bg-red-700 text-white rounded-xl font-medium transition-all shadow-lg shadow-red-600/25 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="animate-spin" size={20} />
                                        Processing...
                                    </>
                                ) : (
                                    <>
                                        <FileText size={20} />
                                        Get Transcript
                                    </>
                                )}
                            </button>

                            {error && (
                                <div className="p-4 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-xl text-sm flex items-start gap-2">
                                    <AlertCircle size={16} className="mt-0.5 shrink-0" />
                                    {error}
                                </div>
                            )}
                        </form>
                    </div>
                </div>

                {/* Output Section */}
                <div className="lg:col-span-3 space-y-8">
                    {result ? (
                        <>
                            {/* Summary Card */}
                            <div className="bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-sm border border-slate-100 dark:border-slate-700">
                                <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
                                    <FileText className="text-red-500" size={24} />
                                    AI Summary
                                </h2>
                                <div className="prose dark:prose-invert max-w-none">
                                    <ReactMarkdown components={{
                                        p: ({ node, ...props }) => <p className="text-slate-700 dark:text-slate-300 mb-4" {...props} />,
                                        h1: ({ node, ...props }) => <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-4 mt-6" {...props} />,
                                        h2: ({ node, ...props }) => <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-3 mt-5" {...props} />,
                                        li: ({ node, ...props }) => <li className="text-slate-700 dark:text-slate-300" {...props} />,
                                        strong: ({ node, ...props }) => <strong className="text-slate-900 dark:text-white font-bold" {...props} />,
                                    }}>{result.summary}</ReactMarkdown>
                                </div>
                            </div>

                            {/* Transcript Card */}
                            <div className="bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-sm border border-slate-100 dark:border-slate-700">
                                <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
                                    <FileText className="text-slate-400" size={24} />
                                    Full Transcript
                                </h2>
                                <div className="max-h-96 overflow-y-auto custom-scrollbar p-4 bg-slate-50 dark:bg-slate-900 rounded-xl text-sm text-slate-600 dark:text-slate-400 leading-relaxed whitespace-pre-wrap">
                                    {result.transcript}
                                </div>
                            </div>
                        </>
                    ) : (
                        <div className="h-full min-h-[400px] bg-slate-50 dark:bg-slate-800/50 rounded-2xl border-2 border-dashed border-slate-200 dark:border-slate-700 flex flex-col items-center justify-center text-slate-400 dark:text-slate-500 p-8 text-center">
                            <Youtube size={48} className="mb-4 opacity-50" />
                            <p className="text-lg font-medium">No transcript generated yet</p>
                            <p className="text-sm mt-2 max-w-xs">
                                Enter a YouTube URL to get the transcript and AI summary.
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default YoutubeTranscript;
