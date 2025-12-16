import React, { useState, useEffect } from 'react';
import { Sparkles, X, Video } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';
import axios from 'axios';
import JobCard from '../components/JobCard';
import FileUploader from '../components/FileUploader';
import AdvancedSettings from '../components/AdvancedSettings';
import { useAuth } from '../contexts/AuthContext';
import { useJobs } from '../contexts/JobsContext';
import { toast } from 'sonner';
import { api } from '../api/client';

const ExtendVideo = () => {
    const [prompt, setPrompt] = useState('');
    const [files, setFiles] = useState([]);
    const [loading, setLoading] = useState(false);
    const { jobs, addJob, updateJobStatus } = useJobs();
    const { currentUser } = useAuth(); // Get current user
    const [searchParams, setSearchParams] = useSearchParams();
    const jobId = searchParams.get('jobId');
    const [selectedJob, setSelectedJob] = useState(null);

    // Filter only extend_video jobs
    const extendJobs = jobs.filter(job => job.type === 'extend_video');

    const [settings, setSettings] = useState({
        model: 'veo-3.1-fast-generate-preview',
        aspect_ratio: '16:9',
        resolution: '1080p',
        duration_seconds: 8
    });

    useEffect(() => {
        console.log("ExtendVideo: jobId from URL:", jobId);
        console.log("ExtendVideo: Available jobs:", jobs);

        if (jobId) {
            // Use loose equality to match string/number
            const job = jobs.find(j => j.id == jobId);
            console.log("ExtendVideo: Found job:", job);

            if (job) {
                setSelectedJob(job);
            } else {
                console.warn("ExtendVideo: Job ID found in URL but no matching job in context");
            }
        }
    }, [jobId, jobs]);

    const clearSelectedJob = () => {
        setSelectedJob(null);
        setSearchParams({});
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!prompt.trim()) {
            toast.error("Please enter a prompt");
            return;
        }

        // Check if we have either a selected job OR a file
        if (!selectedJob && files.length === 0) {
            toast.error("Please upload a video or select one from gallery");
            return;
        }

        setLoading(true);
        const toastId = toast.loading("Submitting job...");

        const newJob = {
            id: Date.now(),
            type: 'extend_video',
            status: 'processing',
            prompt,
            timestamp: new Date().toISOString(),
            settings
        };

        addJob(newJob);

        try {
            const formData = new FormData();
            formData.append('prompt', prompt);

            if (selectedJob) {
                // Send previous operation name
                const opName = selectedJob.result?.operation_name;
                if (!opName) {
                    throw new Error("Selected job has no operation name");
                }
                formData.append('previous_operation_name', opName);
            } else {
                formData.append('base_video', files[0]);
            }

            if (currentUser) {
                formData.append('user_id', currentUser.uid); // Pass user_id
            }

            Object.keys(settings).forEach(key => formData.append(key, settings[key]));

            const response = await api.extendVideo(formData);

            if (response.ok) {
                updateJobStatus(newJob.id, 'processing', response);
                toast.success("Job started successfully!", { id: toastId });
                setPrompt('');
                setFiles([]);
                clearSelectedJob();
            } else {
                updateJobStatus(newJob.id, 'failed');
                toast.error("Backend returned an error", { id: toastId });
            }
        } catch (err) {
            console.error("Failed to generate video", err);
            const errorMessage = err.response?.data?.detail || err.message || 'Failed to generate video';
            toast.error(errorMessage, { id: toastId });
            updateJobStatus(newJob.id, 'failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <div className="mb-8">
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Extend Video</h1>
                <p className="text-slate-500 dark:text-slate-400">Continue the story by extending your existing videos.</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2 space-y-6">
                    <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-100 dark:border-slate-700 shadow-sm transition-colors duration-200">
                        <form onSubmit={handleSubmit} className="space-y-6">

                            {selectedJob ? (
                                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-800 rounded-xl p-4 relative">
                                    <button
                                        type="button"
                                        onClick={clearSelectedJob}
                                        className="absolute top-2 right-2 p-1 hover:bg-blue-100 dark:hover:bg-blue-800 rounded-full text-slate-500 dark:text-slate-400 transition-colors"
                                    >
                                        <X size={16} />
                                    </button>
                                    <div className="flex gap-4 items-center">
                                        <div className="w-24 h-16 bg-black rounded-lg overflow-hidden flex-shrink-0 border border-slate-200 dark:border-slate-700">
                                            <video
                                                src={api.getDownloadUrl(selectedJob.result?.operation_name)}
                                                className="w-full h-full object-cover"
                                            />
                                        </div>
                                        <div>
                                            <div className="flex items-center gap-2 mb-1">
                                                <Video size={16} className="text-blue-500" />
                                                <span className="font-medium text-slate-900 dark:text-white text-sm">Extending from Gallery</span>
                                            </div>
                                            <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-1">
                                                Job ID: {selectedJob.id}
                                            </p>
                                            <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-1 italic">
                                                "{selectedJob.prompt}"
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            ) : (
                                <FileUploader
                                    label="Base Video (MP4, MOV, WEBM)"
                                    accept="video/*"
                                    files={files}
                                    onFilesChange={setFiles}
                                />
                            )}

                            <div>
                                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Prompt</label>
                                <textarea
                                    value={prompt}
                                    onChange={(e) => setPrompt(e.target.value)}
                                    placeholder="Describe what happens next..."
                                    className="w-full h-32 p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none resize-none transition-all text-slate-700 dark:text-slate-200 placeholder:text-slate-400 dark:placeholder:text-slate-500"
                                />
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
                                            Generate Extension
                                        </>
                                    )}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>

                <div className="space-y-4">
                    <h2 className="text-sm font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">Recent Jobs</h2>
                    {extendJobs.length === 0 ? (
                        <div className="text-center py-10 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-dashed border-slate-200 dark:border-slate-700">
                            <p className="text-slate-400 dark:text-slate-500 text-sm">No jobs yet</p>
                        </div>
                    ) : (
                        extendJobs.map(job => <JobCard key={job.id} job={job} />)
                    )}
                </div>
            </div>
        </div>
    );
};

export default ExtendVideo;
