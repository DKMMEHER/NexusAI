import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock, CheckCircle, AlertCircle, Loader2, Download, Sparkles } from 'lucide-react';
import { api } from '../api/client';
import { useJobs } from '../contexts/JobsContext';
import { toast } from 'sonner';

const statusConfig = {
    queued: { icon: Clock, color: 'text-slate-500', bg: 'bg-slate-100' },
    processing: { icon: Loader2, color: 'text-blue-500', bg: 'bg-blue-50', animate: true },
    completed: { icon: CheckCircle, color: 'text-emerald-500', bg: 'bg-emerald-50' },
    failed: { icon: AlertCircle, color: 'text-red-500', bg: 'bg-red-50' },
};

const JobCard = ({ job }) => {
    const [status, setStatus] = React.useState(job.status);
    const [isPolling, setIsPolling] = React.useState(job.status === 'queued' || job.status === 'processing');
    const { updateJobStatus } = useJobs();
    const navigate = useNavigate();

    useEffect(() => {
        let interval;
        const pollStatus = async () => {
            // We need an operation name to poll. If we only have a local ID (timestamp), we can't poll Google.
            const operationName = job.result?.operation_name;

            if (!operationName) {
                // If we don't have an operation name yet, but status is processing, 
                // it might be because we just submitted it and haven't received the op name yet?
                // Or maybe we did receive it but it's not in job.result?
                // In our current flow, we save response.data (which has operation_name) into job.result.
                // So if it's missing, we can't poll.
                return;
            }

            try {
                const res = await api.getJobStatus(operationName);
                if (res.ok) {
                    const status = res.status; // COMPLETE, POLLING, ERROR

                    if (status === 'COMPLETE') {
                        // Preserve operation_name from the existing job result or the current polling scope
                        updateJobStatus(job.id, 'completed', { ...res, operation_name: operationName });
                        setStatus('completed');
                        setIsPolling(false);
                        toast.success("Video generation complete!");
                    } else if (status === 'ERROR') {
                        updateJobStatus(job.id, 'failed', res);
                        setStatus('failed');
                        setIsPolling(false);
                        toast.error(`Job failed: ${res.message}`);
                    } else {
                        // Still polling
                        setStatus('processing');
                    }
                }
            } catch (err) {
                console.error("Polling failed", err);
                // Don't stop polling immediately on one error, but maybe backoff?
                // For now, we'll keep polling unless it's a 404 or persistent error
            }
        };

        if (isPolling && (job.status === 'processing' || job.status === 'queued')) {
            pollStatus(); // Initial poll
            interval = setInterval(pollStatus, 5000); // Poll every 5s
        }

        return () => clearInterval(interval);
    }, [isPolling, job.id, job.status, job.result, updateJobStatus]);

    const config = statusConfig[status] || statusConfig.queued;
    const Icon = config.icon;

    return (
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-100 dark:border-slate-700 p-4 shadow-sm hover:shadow-md transition-all duration-200">
            <div className="flex justify-between items-start mb-3">
                <div className="flex items-center gap-2">
                    <div className={`p-1.5 rounded-lg ${config.bg} ${config.color}`}>
                        <Icon size={16} className={config.animate ? "animate-spin" : ""} />
                    </div>
                    <span className="text-sm font-medium text-slate-700 dark:text-slate-200 capitalize">{status}</span>
                </div>
                <span className="text-xs text-slate-400 font-mono">{String(job.id).slice(0, 8)}</span>
            </div>

            <p className="text-sm text-slate-600 dark:text-slate-300 line-clamp-2 mb-4 h-10">
                {job.prompt || "No prompt provided"}
            </p>

            {status === 'completed' && (
                <div className="space-y-3">
                    <div className="rounded-lg overflow-hidden bg-black aspect-video border border-slate-100 dark:border-slate-700">
                        <video
                            controls
                            className="w-full h-full object-contain"
                            src={api.getDownloadUrl(job.result?.operation_name || job.id)}
                        >
                            Your browser does not support the video tag.
                        </video>
                    </div>

                    <div className="flex gap-2">
                        <a
                            href={api.getDownloadUrl(job.result?.operation_name || job.id)}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex-1 flex items-center justify-center gap-2 py-2 bg-slate-50 dark:bg-slate-900 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 rounded-lg text-sm font-medium transition-colors border border-transparent dark:border-slate-700"
                        >
                            <Download size={14} />
                            Download
                        </a>
                        <button
                            onClick={() => {
                                navigate(`/extend-video?jobId=${job.id}`);
                            }}
                            className="flex items-center justify-center gap-2 px-3 py-2 bg-blue-50 dark:bg-blue-900/30 hover:bg-blue-100 dark:hover:bg-blue-900/50 text-blue-600 dark:text-blue-400 rounded-lg text-sm font-medium transition-colors"
                            title="Extend this video"
                        >
                            <Sparkles size={14} />
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default JobCard;
