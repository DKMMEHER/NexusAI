import React, { useState } from 'react';
import { useJobs } from '../contexts/JobsContext';
import JobCard from '../components/JobCard';
import { Grid, Trash2, Filter } from 'lucide-react';

const Gallery = () => {
    const { jobs, clearJobs } = useJobs();
    const [filter, setFilter] = useState('all');

    const filteredJobs = jobs.filter(job => {
        if (filter === 'all') return true;
        return job.type === filter;
    });

    const jobTypes = [
        { id: 'all', label: 'All Videos' },
        { id: 'text_to_video', label: 'Text to Video' },
        { id: 'image_to_video', label: 'Image to Video' },
        { id: 'reference_images', label: 'Reference Images' },
        { id: 'first_last', label: 'First + Last' },
        { id: 'extend_video', label: 'Extended' },
    ];

    return (
        <div>
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
                        <Grid className="text-primary" />
                        Video Gallery
                    </h1>
                    <p className="text-slate-500 dark:text-slate-400">Your generated masterpieces.</p>
                </div>

                <div className="flex items-center gap-3">
                    {jobs.length > 0 && (
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
                    <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-1">No videos found</h3>
                    <p className="text-slate-500 dark:text-slate-400">
                        {jobs.length === 0
                            ? "You haven't generated any videos yet."
                            : "No videos match the selected filter."}
                    </p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {filteredJobs.map(job => (
                        <JobCard key={job.id} job={job} />
                    ))}
                </div>
            )}
        </div>
    );
};

export default Gallery;
