import React, { useState, useEffect } from 'react';
import { Clapperboard, Loader2, Play, Film, CheckCircle, AlertCircle, Download } from 'lucide-react';
import { api } from '../api/client';

const Director = () => {
    const [topic, setTopic] = useState('');
    const [duration, setDuration] = useState(60);
    const [model, setModel] = useState('veo-3.1-fast-generate-preview');
    const [resolution, setResolution] = useState('720p');
    const [aspectRatio, setAspectRatio] = useState('16:9');

    const [jobId, setJobId] = useState(null);
    const [jobStatus, setJobStatus] = useState(null);
    const [localScenes, setLocalScenes] = useState([]); // Editable scenes
    const [loading, setLoading] = useState(false);
    const [isApproving, setIsApproving] = useState(false);
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!topic) return;

        setLoading(true);
        setError(null);
        setJobStatus(null);
        setJobId(null);

        try {
            const response = await api.director.createMovie({
                topic,
                duration_seconds: parseInt(duration),
                model,
                resolution,
                aspect_ratio: aspectRatio
            });
            setJobId(response.job_id);
        } catch (err) {
            console.error(err);
            setError("Failed to start movie production.");
        } finally {
            setLoading(false);
        }
    };

    const handleApprove = async () => {
        if (!jobId) return;
        setIsApproving(true);
        try {
            // Send the edited scenes for approval
            await api.director.approveScript(jobId, localScenes);
            // Status polling will pick up the change to 'filming'
        } catch (err) {
            console.error("Failed to approve script", err);
            setError("Failed to start filming.");
            setIsApproving(false);
        }
    };

    const handleSceneChange = (index, field, value) => {
        const updatedScenes = [...localScenes];
        // Handle updates to the nested 'prompt' object
        updatedScenes[index] = {
            ...updatedScenes[index],
            prompt: {
                ...updatedScenes[index].prompt,
                [field]: value
            }
        };
        setLocalScenes(updatedScenes);
    };

    const handleNestedSceneChange = (index, parent, field, value) => {
        const updatedScenes = [...localScenes];
        updatedScenes[index] = {
            ...updatedScenes[index],
            [parent]: { ...updatedScenes[index][parent], [field]: value }
        };
        setLocalScenes(updatedScenes);
    };

    useEffect(() => {
        if (!jobId) return;

        const pollStatus = async () => {
            try {
                const status = await api.director.getMovieStatus(jobId);
                setJobStatus(status);

                // Initialize localScenes logic moved to separate useEffect
                // to avoid closure staleness issues in polling loop

                if (status.status === 'completed' || status.status === 'failed') {
                    return; // Stop polling
                }
            } catch (err) {
                console.error("Failed to poll status", err);
                if (err.response && err.response.status === 404) {
                    setError("Job not found. The server may have restarted.");
                    setJobStatus(null);
                    setJobId(null);
                }
            }
        };

        pollStatus(); // Initial call
        const interval = setInterval(pollStatus, 3000); // Poll every 3s

        return () => clearInterval(interval);
    }, [jobId]);

    // Sync localScenes when jobStatus changes to waiting_for_approval
    useEffect(() => {
        if (jobStatus && jobStatus.status === 'waiting_for_approval' && jobStatus.scenes && localScenes.length === 0) {
            console.log("Syncing localScenes with:", jobStatus.scenes);
            setLocalScenes(jobStatus.scenes);
        }
    }, [jobStatus, localScenes.length]);

    // Calculate progress percentage based on status if not provided
    const getProgress = () => {
        if (!jobStatus) return 0;
        if (jobStatus.progress) return jobStatus.progress;

        switch (jobStatus.status) {
            case 'starting': return 5;
            case 'scripting': return 10;
            case 'waiting_for_approval': return 15;
            case 'filming': return 40;
            case 'stitching': return 90;
            case 'completed': return 100;
            default: return 0;
        }
    };

    return (
        <div className="max-w-7xl mx-auto space-y-8">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900 dark:text-white flex items-center gap-3">
                        <Clapperboard className="text-purple-600" size={32} />
                        The Director
                    </h1>
                    <p className="text-slate-500 dark:text-slate-400 mt-2 text-lg">
                        Automated AI Movie Production from a single prompt.
                    </p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Input Section */}
                <div className="space-y-6">
                    <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 shadow-sm border border-slate-100 dark:border-slate-700">
                        <form onSubmit={handleSubmit} className="space-y-6">
                            <div>
                                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                                    Movie Topic / Concept
                                </label>
                                <textarea
                                    value={topic}
                                    onChange={(e) => setTopic(e.target.value)}
                                    placeholder="E.g., A cinematic documentary about the life of Mahatma Gandhi..."
                                    className="w-full px-4 py-3 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-500 transition-all h-48 resize-none"
                                    required
                                />
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                                        Duration (Seconds)
                                    </label>
                                    <input
                                        type="number"
                                        min="10"
                                        max="600"
                                        value={duration}
                                        onChange={(e) => setDuration(e.target.value)}
                                        className="w-full px-4 py-3 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-500 transition-all"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                                        Resolution
                                    </label>
                                    <select
                                        value={resolution}
                                        onChange={(e) => setResolution(e.target.value)}
                                        className="w-full px-4 py-3 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-500 transition-all"
                                    >
                                        <option value="1080p">1080p</option>
                                        <option value="720p">720p</option>
                                    </select>
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                                        Model
                                    </label>
                                    <select
                                        value={model}
                                        onChange={(e) => setModel(e.target.value)}
                                        className="w-full px-4 py-3 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-500 transition-all"
                                    >
                                        <option value="veo-3.1-fast-generate-preview">Fast (Preview)</option>
                                        <option value="veo-3.1-generate-preview">Quality (Standard)</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                                        Aspect Ratio
                                    </label>
                                    <select
                                        value={aspectRatio}
                                        onChange={(e) => setAspectRatio(e.target.value)}
                                        className="w-full px-4 py-3 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-500 transition-all"
                                    >
                                        <option value="16:9">16:9 (Landscape)</option>
                                        <option value="9:16">9:16 (Portrait)</option>
                                    </select>
                                </div>
                            </div>

                            <button
                                type="submit"
                                disabled={loading || (jobStatus && jobStatus.status !== 'completed' && jobStatus.status !== 'failed')}
                                className="w-full py-3 px-4 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-medium transition-all shadow-lg shadow-purple-600/25 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="animate-spin" size={20} />
                                        Starting Production...
                                    </>
                                ) : (
                                    <>
                                        <Film size={20} />
                                        Generate Script
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

                {/* Status & Output Section */}
                <div className="space-y-6">
                    {jobStatus ? (
                        <div className="bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-sm border border-slate-100 dark:border-slate-700 space-y-8">
                            {/* Progress Bar */}
                            <div>
                                <div className="flex justify-between text-sm font-medium mb-2">
                                    <span className="text-slate-700 dark:text-slate-300 capitalize">
                                        Status: {jobStatus.status}
                                    </span>
                                    <span className="text-purple-600">{getProgress()}%</span>
                                </div>
                                <div className="w-full bg-slate-100 dark:bg-slate-700 rounded-full h-2.5 overflow-hidden">
                                    <div
                                        className="bg-purple-600 h-2.5 rounded-full transition-all duration-500 ease-out"
                                        style={{ width: `${getProgress()}%` }}
                                    ></div>
                                </div>
                            </div>

                            {/* Scenes List */}
                            {jobStatus.scenes && jobStatus.scenes.length > 0 && (
                                <div>
                                    <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">Production Log</h3>
                                    <div className="max-h-[80vh] overflow-y-auto custom-scrollbar space-y-3 pr-2">
                                        {/* Use localScenes if available (for editing), otherwise jobStatus.scenes */}
                                        {(jobStatus.status === 'waiting_for_approval' ? localScenes : jobStatus.scenes).map((scene, index) => (
                                            <div key={scene.id || index} className="flex items-start gap-3 p-3 bg-slate-50 dark:bg-slate-900 rounded-xl border border-slate-100 dark:border-slate-700">
                                                <div className="mt-1">
                                                    {scene.status === 'done' ? (
                                                        <CheckCircle className="text-emerald-500" size={18} />
                                                    ) : scene.status === 'generating' ? (
                                                        <Loader2 className="text-purple-500 animate-spin" size={18} />
                                                    ) : scene.status === 'failed' ? (
                                                        <AlertCircle className="text-red-500" size={18} />
                                                    ) : (
                                                        <div className="w-4.5 h-4.5 rounded-full border-2 border-slate-300 dark:border-slate-600" />
                                                    )}
                                                </div>
                                                <div className="flex-1 min-w-0">
                                                    <div className="flex justify-between items-start mb-2">
                                                        <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                                                            {scene.scene_heading || `Scene ${scene.id}`}
                                                        </h4>
                                                        <span className="text-xs text-slate-500 bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded-full">
                                                            {scene.duration}s
                                                        </span>
                                                    </div>

                                                    {/* Editable Fields for Waiting for Approval */}
                                                    {jobStatus.status === 'waiting_for_approval' ? (
                                                        <div className="space-y-3">
                                                            <div>
                                                                <label className="text-xs font-semibold text-slate-500 dark:text-slate-400 block mb-1">Scene Description</label>
                                                                <textarea
                                                                    value={scene.prompt?.scene_description || ''}
                                                                    onChange={(e) => handleSceneChange(index, 'scene_description', e.target.value)}
                                                                    className="w-full text-xs p-2 rounded border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-1 focus:ring-purple-500"
                                                                    rows={3}
                                                                />
                                                            </div>
                                                            {/* JSON Prompt Display for Review */}
                                                            <div className="mt-2">
                                                                <details className="text-xs">
                                                                    <summary className="cursor-pointer font-semibold text-slate-500 hover:text-purple-600 transition-colors">
                                                                        View Full JSON Prompt
                                                                    </summary>
                                                                    <pre className="mt-2 p-3 bg-slate-800 text-slate-200 rounded-lg overflow-x-auto font-mono text-[10px] whitespace-pre">
                                                                        {JSON.stringify(scene.prompt, null, 2)}
                                                                    </pre>
                                                                </details>
                                                            </div>
                                                        </div>
                                                    ) : (
                                                        /* Read-Only View */
                                                        <div className="mt-2 space-y-2 text-xs text-slate-600 dark:text-slate-400">
                                                            {scene.prompt?.scene_description && (
                                                                <p><span className="font-semibold text-slate-700 dark:text-slate-300">Description:</span> {scene.prompt.scene_description}</p>
                                                            )}

                                                            {/* Visual Details */}
                                                            {scene.prompt?.visual_details && (
                                                                <div className="bg-slate-100 dark:bg-slate-800 p-2 rounded-lg border border-slate-200 dark:border-slate-700">
                                                                    <span className="font-semibold text-purple-600 block mb-1">Visual Details:</span>
                                                                    <ul className="list-disc list-inside pl-1 space-y-1">
                                                                        <li><span className="font-medium">Env:</span> {scene.prompt.visual_details.environment}</li>
                                                                        <li><span className="font-medium">Char:</span> {scene.prompt.visual_details.character}</li>
                                                                    </ul>
                                                                </div>
                                                            )}

                                                            {/* JSON Prompt Display */}
                                                            <div className="mt-2">
                                                                <details className="text-xs">
                                                                    <summary className="cursor-pointer font-semibold text-slate-500 hover:text-purple-600 transition-colors">
                                                                        View JSON Prompt
                                                                    </summary>
                                                                    <pre className="mt-2 p-3 bg-slate-800 text-slate-200 rounded-lg overflow-x-auto font-mono text-[10px] whitespace-pre">
                                                                        {JSON.stringify(scene.prompt, null, 2)}
                                                                    </pre>
                                                                </details>
                                                            </div>

                                                            {/* Camera */}
                                                            {scene.prompt?.camera_direction && (
                                                                <p><span className="font-semibold text-slate-700 dark:text-slate-300">Camera:</span> {scene.prompt.camera_direction.movement}, {scene.prompt.camera_direction.framing}, {scene.prompt.camera_direction.focus}</p>
                                                            )}

                                                            {/* Audio */}
                                                            {scene.prompt?.audio_design && (
                                                                <div className="grid grid-cols-2 gap-2">
                                                                    {scene.prompt.audio_design.music && <p><span className="font-semibold">Music:</span> {scene.prompt.audio_design.music.style}</p>}
                                                                    {scene.prompt.audio_design.ambient_sfx && <p><span className="font-semibold">SFX:</span> {scene.prompt.audio_design.ambient_sfx.environment}</p>}
                                                                </div>
                                                            )}
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Approval Button */}
                            {jobStatus.status === 'waiting_for_approval' && (
                                <div className="pt-4 border-t border-slate-200 dark:border-slate-700">
                                    <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-xl mb-4 text-sm text-blue-700 dark:text-blue-300 flex items-start gap-2">
                                        <AlertCircle size={16} className="mt-0.5 shrink-0" />
                                        <p>
                                            Review the script above. If you are happy with the scenes, click "Start Filming" to begin video generation.
                                        </p>
                                    </div>
                                    <button
                                        className="w-full py-3 px-4 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-medium transition-all shadow-lg shadow-emerald-600/25 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                                        onClick={handleApprove}
                                        disabled={isApproving}
                                    >
                                        {isApproving ? (
                                            <>
                                                <Loader2 className="animate-spin" size={20} />
                                                Starting Filming...
                                            </>
                                        ) : (
                                            <>
                                                <Play size={20} />
                                                Start Filming
                                            </>
                                        )}
                                    </button>
                                </div>
                            )}

                            {/* Final Output */}
                            {jobStatus.status === 'completed' && jobStatus.final_video_path && (
                                <div className="pt-6 border-t border-slate-200 dark:border-slate-700">
                                    <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">Final Movie</h3>
                                    <div className="aspect-video bg-black rounded-xl overflow-hidden relative group">
                                        <video
                                            src={`http://127.0.0.1:8006/videos/${jobStatus.final_video_path.split(/[\\/]/).pop()}`}
                                            controls
                                            className="w-full h-full"
                                        />
                                    </div>
                                    <div className="mt-4 text-center space-y-3">
                                        <p className="text-sm text-emerald-600 dark:text-emerald-400 font-medium flex items-center justify-center gap-2">
                                            <CheckCircle size={16} />
                                            Production Completed Successfully!
                                        </p>
                                        <a
                                            href={`http://127.0.0.1:8006/videos/${jobStatus.final_video_path.split(/[\\/]/).pop()}`}
                                            download
                                            className="inline-flex items-center gap-2 px-4 py-2 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-lg text-sm font-medium hover:opacity-90 transition-opacity"
                                        >
                                            <Download size={16} />
                                            Download Movie
                                        </a>
                                    </div>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="h-full min-h-[400px] bg-slate-50 dark:bg-slate-800/50 rounded-2xl border-2 border-dashed border-slate-200 dark:border-slate-700 flex flex-col items-center justify-center text-slate-400 dark:text-slate-500 p-8 text-center">
                            <Clapperboard size={48} className="mb-4 opacity-50" />
                            <p className="text-lg font-medium">Ready for Action</p>
                            <p className="text-sm mt-2 max-w-xs">
                                Enter a topic and start production to see the magic happen.
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Director;
