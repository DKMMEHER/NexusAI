import React from 'react';
import { useJobs } from '../contexts/JobsContext';
import { CheckCircle, AlertCircle, Clock, Video, Activity } from 'lucide-react';

const StatCard = ({ title, value, icon: Icon, color, bg }) => (
    <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-100 dark:border-slate-700 shadow-sm">
        <div className="flex items-center justify-between">
            <div>
                <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{title}</p>
                <p className="text-3xl font-bold text-slate-900 dark:text-white mt-2">{value}</p>
            </div>
            <div className={`p-4 rounded-xl ${bg} ${color}`}>
                <Icon size={28} />
            </div>
        </div>
    </div>
);

const VideoStats = () => {
    const { jobs } = useJobs();
    const [timeRange, setTimeRange] = React.useState('all');

    const filterByTimeRange = (job) => {
        if (timeRange === 'all') return true;

        const jobDate = new Date(job.timestamp);
        const now = new Date();
        const diffInMs = now - jobDate;
        const diffInHours = diffInMs / (1000 * 60 * 60);
        const diffInDays = diffInHours / 24;

        switch (timeRange) {
            case '1h': return diffInHours <= 1;
            case '24h': return diffInHours <= 24;
            case '7d': return diffInDays <= 7;
            case '28d': return diffInDays <= 28;
            case '90d': return diffInDays <= 90;
            default: return true;
        }
    };

    // Filter only video generation jobs and apply time range
    const RPM_LIMIT = 2;
    const RPD_LIMIT = 10;

    const calculateMetrics = (jobTimestamp) => {
        const jobDate = new Date(jobTimestamp);
        const oneMinuteAgo = new Date(jobDate.getTime() - 60000);
        const oneDayAgo = new Date(jobDate.getTime() - 24 * 60 * 60 * 1000);

        // Count jobs that occurred within 1 minute BEFORE this job
        const rpm = jobs.filter(j => {
            const t = new Date(j.timestamp);
            return t >= oneMinuteAgo && t <= jobDate;
        }).length;

        // Count jobs that occurred within 24 hours BEFORE this job
        const rpd = jobs.filter(j => {
            const t = new Date(j.timestamp);
            return t >= oneDayAgo && t <= jobDate;
        }).length;

        return { rpm, rpd };
    };

    const videoJobs = jobs
        .filter(j => ['text_to_video', 'image_to_video', 'reference_images', 'first_last_frames', 'extend_video'].includes(j.type))
        .filter(filterByTimeRange);

    const stats = {
        total: videoJobs.length,
        completed: videoJobs.filter(j => j.status === 'completed').length,
        processing: videoJobs.filter(j => j.status === 'processing' || j.status === 'queued').length,
        failed: videoJobs.filter(j => j.status === 'failed').length,
    };

    return (
        <div className="max-w-6xl mx-auto space-y-8">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
                        <Activity className="text-primary" />
                        Video Generation Analytics
                    </h1>
                    <p className="text-slate-500 dark:text-slate-400 mt-1">Track the performance and status of your video generation jobs.</p>
                </div>

                <select
                    value={timeRange}
                    onChange={(e) => setTimeRange(e.target.value)}
                    className="px-4 py-2 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-primary/20"
                >
                    <option value="all">All Time</option>
                    <option value="1h">Last Hour</option>
                    <option value="24h">Last 24 Hours</option>
                    <option value="7d">Last 7 Days</option>
                    <option value="28d">Last 28 Days</option>
                    <option value="90d">Last 90 Days</option>
                </select>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                    title="Total Videos"
                    value={stats.total}
                    icon={Video}
                    color="text-blue-600"
                    bg="bg-blue-50 dark:bg-blue-900/20"
                />
                <StatCard
                    title="Completed"
                    value={stats.completed}
                    icon={CheckCircle}
                    color="text-emerald-600"
                    bg="bg-emerald-50 dark:bg-emerald-900/20"
                />
                <StatCard
                    title="Processing"
                    value={stats.processing}
                    icon={Clock}
                    color="text-amber-600"
                    bg="bg-amber-50 dark:bg-amber-900/20"
                />
                <StatCard
                    title="Failed"
                    value={stats.failed}
                    icon={AlertCircle}
                    color="text-red-600"
                    bg="bg-red-50 dark:bg-red-900/20"
                />
            </div>

            {/* Recent Activity Log */}
            <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 shadow-sm overflow-hidden">
                <div className="p-6 border-b border-slate-100 dark:border-slate-700">
                    <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Recent Activity Log</h2>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                        <thead className="bg-slate-50 dark:bg-slate-900/50 text-slate-500 dark:text-slate-400">
                            <tr>
                                <th className="px-6 py-4 font-medium">Job ID</th>
                                <th className="px-6 py-4 font-medium">Type</th>
                                <th className="px-6 py-4 font-medium">Model</th>
                                <th className="px-6 py-4 font-medium" title="Observed Usage / Quota Limit">RPM</th>
                                <th className="px-6 py-4 font-medium">TPM</th>
                                <th className="px-6 py-4 font-medium" title="Observed Usage / Quota Limit">RPD</th>
                                <th className="px-6 py-4 font-medium">Status</th>
                                <th className="px-6 py-4 font-medium">Time</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
                            {videoJobs.length === 0 ? (
                                <tr>
                                    <td colSpan="8" className="px-6 py-8 text-center text-slate-500 dark:text-slate-400">
                                        No activity recorded yet.
                                    </td>
                                </tr>
                            ) : (
                                videoJobs.slice(0, 10).map((job) => {
                                    const { rpm, rpd } = calculateMetrics(job.timestamp);
                                    return (
                                        <tr key={job.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                                            <td className="px-6 py-4 font-mono text-slate-600 dark:text-slate-300">#{job.id}</td>
                                            <td className="px-6 py-4 text-slate-900 dark:text-white capitalize">{job.type.replace(/_/g, ' ')}</td>
                                            <td className="px-6 py-4 text-slate-600 dark:text-slate-300 text-xs font-mono">
                                                {job.settings?.model || 'veo-3.1-fast-generate-preview'}
                                            </td>
                                            <td className={`px-6 py-4 ${rpm >= RPM_LIMIT ? 'text-amber-600 font-medium' : 'text-slate-600 dark:text-slate-300'}`}>
                                                {rpm} <span className="text-slate-400 text-xs">/ {RPM_LIMIT}</span>
                                            </td>
                                            <td className="px-6 py-4 text-slate-600 dark:text-slate-300">N/A</td>
                                            <td className={`px-6 py-4 ${rpd >= RPD_LIMIT ? 'text-amber-600 font-medium' : 'text-slate-600 dark:text-slate-300'}`}>
                                                {rpd} <span className="text-slate-400 text-xs">/ {RPD_LIMIT}</span>
                                            </td>
                                            <td className="px-6 py-4">
                                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                                                    ${job.status === 'completed' ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400' :
                                                        job.status === 'failed' ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400' :
                                                            'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400'}`}>
                                                    {job.status}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 text-slate-500 dark:text-slate-400">
                                                {new Date(job.timestamp).toLocaleString()}
                                            </td>
                                        </tr>
                                    );
                                })
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default VideoStats;
