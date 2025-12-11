import React, { useState } from 'react';
import { Sparkles } from 'lucide-react';
import axios from 'axios';
import JobCard from '../components/JobCard';
import AdvancedSettings from '../components/AdvancedSettings';
import PromptPresets from '../components/PromptPresets';
import { useJobs } from '../contexts/JobsContext';
import { toast } from 'sonner';
import { api } from '../api/client';

const TextToVideo = () => {
    const [prompt, setPrompt] = useState('');
    const [loading, setLoading] = useState(false);
    const { jobs, addJob, updateJobStatus } = useJobs();

    // Filter only text_to_video jobs for this view
    const textToVideoJobs = jobs.filter(job => job.type === 'text_to_video');

    const [settings, setSettings] = useState({
        model: 'veo-3.1-fast-generate-preview',
        aspect_ratio: '16:9',
        resolution: '1080p',
        duration_seconds: 8
    });

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!prompt.trim()) {
            toast.error("Please enter a prompt");
            return;
        }

        setLoading(true);
        const toastId = toast.loading("Submitting job...");

        const newJob = {
            id: Date.now(),
            type: 'text_to_video',
            status: 'processing',
            prompt,
            timestamp: new Date().toISOString(),
            settings
        };

        addJob(newJob);

        try {
            const formData = new FormData();
            formData.append('prompt', prompt);
            Object.keys(settings).forEach(key => formData.append(key, settings[key]));

            const response = await api.textToVideo(formData);

            if (response.ok) {
                updateJobStatus(newJob.id, 'processing', response);
                toast.success("Job started successfully!", { id: toastId });
                setPrompt('');
            } else {
                updateJobStatus(newJob.id, 'failed');
                toast.error("Backend returned an error", { id: toastId });
            }
        } catch (err) {
            console.error("Failed to generate video", err);
            const errorMessage = err.response?.data?.detail || 'Failed to generate video';
            toast.error(errorMessage, { id: toastId });
            updateJobStatus(newJob.id, 'failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <div className="mb-8">
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Text → Video</h1>
                <p className="text-slate-500 dark:text-slate-400">Turn your imagination into cinematic videos.</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2 space-y-6">
                    <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-100 dark:border-slate-700 shadow-sm transition-colors duration-200">
                        <form onSubmit={handleSubmit}>
                            <div className="mb-4">
                                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Prompt</label>
                                <textarea
                                    value={prompt}
                                    onChange={(e) => setPrompt(e.target.value)}
                                    placeholder="Describe your video in detail..."
                                    className="w-full h-40 p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none resize-none transition-all text-slate-700 dark:text-slate-200 placeholder:text-slate-400 dark:placeholder:text-slate-500"
                                />
                                <PromptPresets onSelect={(style) => setPrompt(prev => prev ? `${prev}, ${style}` : style)} />
                            </div>

                            <AdvancedSettings settings={settings} setSettings={setSettings} showModel={true} />

                            <div className="flex justify-end">
                                <button
                                    type="submit"
                                    disabled={loading}
                                    className="flex items-center gap-2 bg-primary hover:bg-blue-700 text-white px-6 py-3 rounded-xl font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-primary/30"
                                >
                                    {loading ? (
                                        <span className="animate-pulse">Submitting...</span>
                                    ) : (
                                        <>
                                            <Sparkles size={18} />
                                            Generate Video
                                        </>
                                    )}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>

                <div className="space-y-4">
                    <h2 className="text-sm font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">Recent Jobs</h2>
                    {textToVideoJobs.length === 0 ? (
                        <div className="text-center py-10 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-dashed border-slate-200 dark:border-slate-700">
                            <p className="text-slate-400 dark:text-slate-500 text-sm">No jobs yet</p>
                        </div>
                    ) : (
                        textToVideoJobs.map(job => <JobCard key={job.id} job={job} />)
                    )}
                </div>
            </div>
        </div>
    );
};

export default TextToVideo;
