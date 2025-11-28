import React, { useState } from 'react';
import { useJobs } from '../contexts/JobsContext';
import { Grid, Trash2, Filter, Download, Image as ImageIcon } from 'lucide-react';

const ImageGallery = () => {
    const { jobs, clearJobs } = useJobs();
    const [filter, setFilter] = useState('all');

    // Filter for Image Generation jobs only
    const imageJobs = jobs.filter(job =>
        ['generate', 'edit', 'tryon', 'ads', 'merge', 'scenes', 'restore'].includes(job.type)
    );

    const filteredJobs = imageJobs.filter(job => {
        if (filter === 'all') return true;
        return job.type === filter;
    });

    const jobTypes = [
        { id: 'all', label: 'All Images' },
        { id: 'generate', label: 'Generated' },
        { id: 'edit', label: 'Edited' },
        { id: 'tryon', label: 'Try-On' },
        { id: 'ads', label: 'Ads' },
        { id: 'merge', label: 'Merged' },
        { id: 'scenes', label: 'Scenes' },
        { id: 'restore', label: 'Restored' },
    ];

    const downloadImage = (base64Data, mimeType, timestamp) => {
        const link = document.createElement('a');
        link.href = `data:${mimeType};base64,${base64Data}`;
        const date = new Date(timestamp).toISOString().replace(/[:.]/g, '-');
        link.download = `image_${date}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    return (
        <div>
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
                        <Grid className="text-primary" />
                        Image Gallery
                    </h1>
                    <p className="text-slate-500 dark:text-slate-400">Your generated masterpieces.</p>
                </div>

                <div className="flex items-center gap-3">
                    {imageJobs.length > 0 && (
                        <button
                            onClick={() => {
                                if (window.confirm('Are you sure you want to clear your history? This cannot be undone.')) {
                                    clearJobs();
                                }
                            }}
                            className="flex items-center gap-2 px-4 py-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors text-sm font-medium"
                        >
                            <Trash2 size={16} />
                            Clear History
                        </button>
                    )}
                </div>
            </div>

            {/* Filters */}
            <div className="flex flex-wrap gap-2 mb-8">
                {jobTypes.map(type => (
                    <button
                        key={type.id}
                        onClick={() => setFilter(type.id)}
                        className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${filter === type.id
                            ? 'bg-primary text-white shadow-lg shadow-primary/30'
                            : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700'
                            }`}
                    >
                        {type.label}
                    </button>
                ))}
            </div>

            {/* Grid */}
            {filteredJobs.length === 0 ? (
                <div className="text-center py-20 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-dashed border-slate-200 dark:border-slate-700">
                    <div className="w-16 h-16 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Filter size={24} className="text-slate-400" />
                    </div>
                    <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-1">No images found</h3>
                    <p className="text-slate-500 dark:text-slate-400">
                        {imageJobs.length === 0
                            ? "You haven't generated any images yet."
                            : "No images match the selected filter."}
                    </p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    {filteredJobs.map((job) => (
                        job.result?.images?.map((img, imgIdx) => (
                            <div key={`${job.id}-${imgIdx}`} className="group relative bg-white dark:bg-slate-800 rounded-2xl overflow-hidden border border-slate-100 dark:border-slate-700 shadow-sm hover:shadow-md transition-all">
                                <div className="aspect-square relative overflow-hidden bg-slate-100 dark:bg-slate-900">
                                    <img
                                        src={`data:${img.mime};base64,${img.image}`}
                                        alt={job.settings?.prompt || "Generated Image"}
                                        className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                                    />
                                    <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                                        <button
                                            onClick={() => downloadImage(img.image, img.mime, job.timestamp)}
                                            className="p-2 bg-white/20 backdrop-blur-md rounded-full text-white hover:bg-white/30 transition-colors"
                                            title="Download"
                                        >
                                            <Download size={20} />
                                        </button>
                                    </div>
                                    <div className="absolute top-2 right-2 px-2 py-1 bg-black/50 backdrop-blur-md rounded-md text-xs font-medium text-white">
                                        {job.type}
                                    </div>
                                </div>
                                <div className="p-4">
                                    <p className="text-sm text-slate-600 dark:text-slate-300 line-clamp-2 mb-2" title={job.settings?.prompt}>
                                        {job.settings?.prompt || "No prompt"}
                                    </p>
                                    <div className="flex items-center justify-between text-xs text-slate-400">
                                        <span>{new Date(job.timestamp).toLocaleDateString()}</span>
                                        <span>{job.settings?.model?.split('-')[1] || 'Gemini'}</span>
                                    </div>
                                </div>
                            </div>
                        ))
                    ))}
                </div>
            )}
        </div>
    );
};

export default ImageGallery;
