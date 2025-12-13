import React, { useState, useRef } from 'react';
import { Upload, FileText, Loader2, AlertCircle, FileType, X } from 'lucide-react';
import { api } from '../api/client';
import ReactMarkdown from 'react-markdown';
import { useAuth } from '../contexts/AuthContext';

const DocumentsSummarization = () => {
    const { currentUser } = useAuth();
    const [files, setFiles] = useState([]);
    const [prompt, setPrompt] = useState('');
    const [selectedModel, setSelectedModel] = useState('gemini-2.5-flash');
    const [loading, setLoading] = useState(false);
    const [summary, setSummary] = useState(null);
    const [error, setError] = useState(null);
    const fileInputRef = useRef(null);

    const handleFileChange = (e) => {
        const selectedFiles = Array.from(e.target.files);
        if (selectedFiles.length > 0) {
            setFiles(prev => [...prev, ...selectedFiles]);
            setError(null);
            setSummary(null);
        }
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        e.stopPropagation();
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        const droppedFiles = Array.from(e.dataTransfer.files);
        if (droppedFiles.length > 0) {
            setFiles(prev => [...prev, ...droppedFiles]);
            setError(null);
            setSummary(null);
        }
    };

    const removeFile = (index) => {
        setFiles(prev => prev.filter((_, i) => i !== index));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (files.length === 0) {
            setError("Please select at least one file to summarize.");
            return;
        }

        setLoading(true);
        setError(null);
        setSummary(null);

        const formData = new FormData();
        files.forEach(file => {
            formData.append('files', file);
        });

        if (prompt) {
            formData.append('prompt', prompt);
        }

        formData.append('model', selectedModel);

        if (currentUser) {
            formData.append('user_id', currentUser.uid);
        }

        try {
            const response = await api.documents.summarize(formData);
            setSummary(response.summary);
        } catch (err) {
            console.error("Summarization failed:", err);
            const errorMessage = err.response?.data?.detail || err.message || "Failed to summarize document.";
            setError(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    const clearFiles = () => {
        setFiles([]);
        setSummary(null);
        setError(null);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
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
                        <FileText className="text-primary" size={32} />
                        Documents Summarization
                    </h1>
                    <p className="text-slate-500 dark:text-slate-400 mt-2 text-lg">
                        Upload documents to get instant, AI-powered summaries.
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
                                    ? 'bg-primary text-white shadow-md'
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
                            {/* File Upload Area */}
                            <div
                                className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200 cursor-pointer
                                    ${files.length > 0 ? 'border-emerald-500 bg-emerald-50/50 dark:bg-emerald-900/10' : 'border-slate-200 dark:border-slate-700 hover:border-primary hover:bg-slate-50 dark:hover:bg-slate-800/50'}`}
                                onDragOver={handleDragOver}
                                onDrop={handleDrop}
                                onClick={() => files.length === 0 && fileInputRef.current?.click()}
                            >
                                <input
                                    type="file"
                                    ref={fileInputRef}
                                    className="hidden"
                                    onChange={handleFileChange}
                                    multiple
                                />

                                {files.length > 0 ? (
                                    <div className="space-y-3">
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                                                {files.length} file{files.length !== 1 ? 's' : ''} selected
                                            </span>
                                            <div className="flex gap-2">
                                                <button
                                                    type="button"
                                                    onClick={(e) => { e.stopPropagation(); fileInputRef.current?.click(); }}
                                                    className="text-xs text-primary hover:text-primary/80 font-medium"
                                                >
                                                    Add More
                                                </button>
                                                <button
                                                    type="button"
                                                    onClick={(e) => { e.stopPropagation(); clearFiles(); }}
                                                    className="text-xs text-red-500 hover:text-red-600 font-medium"
                                                >
                                                    Clear All
                                                </button>
                                            </div>
                                        </div>

                                        <div className="max-h-48 overflow-y-auto space-y-2 pr-2 custom-scrollbar">
                                            {files.map((file, index) => (
                                                <div key={index} className="flex items-center justify-between bg-white dark:bg-slate-800 p-2 rounded-lg border border-slate-100 dark:border-slate-700 shadow-sm">
                                                    <div className="flex items-center gap-2 overflow-hidden">
                                                        <div className="w-8 h-8 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 rounded-lg flex items-center justify-center shrink-0">
                                                            <FileType size={16} />
                                                        </div>
                                                        <div className="text-sm font-medium text-slate-900 dark:text-white truncate">
                                                            {file.name}
                                                        </div>
                                                    </div>
                                                    <button
                                                        type="button"
                                                        onClick={(e) => { e.stopPropagation(); removeFile(index); }}
                                                        className="p-1 text-slate-400 hover:text-red-500 transition-colors"
                                                    >
                                                        <X size={14} />
                                                    </button>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                ) : (
                                    <div className="space-y-3">
                                        <div className="w-12 h-12 bg-slate-100 dark:bg-slate-700 text-slate-400 rounded-xl flex items-center justify-center mx-auto">
                                            <Upload size={24} />
                                        </div>
                                        <div>
                                            <p className="text-sm font-medium text-slate-700 dark:text-slate-300">
                                                Click to upload or drag & drop
                                            </p>
                                            <p className="text-xs text-slate-500 dark:text-slate-500 mt-1">
                                                PDF, DOCX, PPTX, TXT, HTML, etc.
                                            </p>
                                        </div>
                                    </div>
                                )}
                            </div>

                            {/* Optional Prompt */}
                            <div>
                                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                                    Custom Instructions (Optional)
                                </label>
                                <textarea
                                    value={prompt}
                                    onChange={(e) => setPrompt(e.target.value)}
                                    placeholder="E.g., Focus on the financial results..."
                                    className="w-full px-4 py-3 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary/20 resize-none h-24"
                                />
                            </div>

                            {/* Submit Button */}
                            <button
                                type="submit"
                                disabled={loading || files.length === 0}
                                className="w-full py-3 px-4 bg-primary hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl font-medium transition-all duration-200 flex items-center justify-center gap-2 shadow-lg shadow-primary/25"
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="animate-spin" size={20} />
                                        Summarizing...
                                    </>
                                ) : (
                                    <>
                                        <FileText size={20} />
                                        Summarize Document
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
                <div className="lg:col-span-3">
                    {summary ? (
                        <div className="bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-sm border border-slate-100 dark:border-slate-700 min-h-[500px] max-h-[800px] overflow-y-auto custom-scrollbar">
                            <div className="prose dark:prose-invert max-w-none">
                                <ReactMarkdown components={{
                                    p: ({ node, ...props }) => <p className="text-slate-700 dark:text-slate-300 mb-4" {...props} />,
                                    h1: ({ node, ...props }) => <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-4 mt-6" {...props} />,
                                    h2: ({ node, ...props }) => <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-3 mt-5" {...props} />,
                                    h3: ({ node, ...props }) => <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2 mt-4" {...props} />,
                                    ul: ({ node, ...props }) => <ul className="list-disc list-inside mb-4 space-y-1 text-slate-700 dark:text-slate-300" {...props} />,
                                    ol: ({ node, ...props }) => <ol className="list-decimal list-inside mb-4 space-y-1 text-slate-700 dark:text-slate-300" {...props} />,
                                    li: ({ node, ...props }) => <li className="text-slate-700 dark:text-slate-300" {...props} />,
                                    strong: ({ node, ...props }) => <strong className="text-slate-900 dark:text-white font-bold" {...props} />,
                                    blockquote: ({ node, ...props }) => <blockquote className="border-l-4 border-slate-200 dark:border-slate-700 pl-4 italic text-slate-600 dark:text-slate-400 my-4" {...props} />,
                                }}>{summary}</ReactMarkdown>
                            </div>
                        </div>
                    ) : (
                        <div className="h-full min-h-[400px] bg-slate-50 dark:bg-slate-800/50 rounded-2xl border-2 border-dashed border-slate-200 dark:border-slate-700 flex flex-col items-center justify-center text-slate-400 dark:text-slate-500 p-8 text-center">
                            <FileText size={48} className="mb-4 opacity-50" />
                            <p className="text-lg font-medium">No summary generated yet</p>
                            <p className="text-sm mt-2 max-w-xs">
                                Upload a document and click summarize to see the AI-generated insights here.
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default DocumentsSummarization;
