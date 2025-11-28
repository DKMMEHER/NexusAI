import React from 'react';
import { useJobs } from '../contexts/JobsContext';
import { CheckCircle, AlertCircle, Clock, Image as ImageIcon, Activity, BarChart3 } from 'lucide-react';

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

const ImageStats = () => {
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

    // Filter only image generation jobs
    const imageJobsRaw = jobs.filter(j =>
        ['generate', 'edit', 'tryon', 'ads', 'merge', 'scenes', 'restore'].includes(j.type)
    );

    const imageJobs = imageJobsRaw.filter(filterByTimeRange);

    const stats = {
        total: imageJobs.length,
        completed: imageJobs.filter(j => j.status === 'completed').length,
        failed: imageJobs.filter(j => j.status === 'failed').length,
        totalImages: imageJobs.reduce((acc, job) => acc + (job.result?.images?.length || 0), 0)
    };

    // Calculate Model Usage
    const modelUsage = imageJobs.reduce((acc, job) => {
        const model = job.settings?.model || 'Unknown';
        acc[model] = (acc[model] || 0) + 1;
        return acc;
    }, {});

    const topModel = Object.entries(modelUsage).sort((a, b) => b[1] - a[1])[0];

    return (
        <div className="max-w-6xl mx-auto space-y-8">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
                        <BarChart3 className="text-primary" />
                        Image Analytics
                    </h1>
                    <p className="text-slate-500 dark:text-slate-400 mt-1">Track your creative output and performance.</p>
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
                    title="Total Jobs"
                    value={stats.total}
                    icon={Activity}
                    color="text-blue-600"
                    bg="bg-blue-50 dark:bg-blue-900/20"
                />
                <StatCard
                    title="Images Generated"
                    value={stats.totalImages}
                    icon={ImageIcon}
                    color="text-purple-600"
                    bg="bg-purple-50 dark:bg-purple-900/20"
                />
                <StatCard
                    title="Success Rate"
                    value={stats.total > 0 ? `${Math.round((stats.completed / stats.total) * 100)}%` : '0%'}
                    icon={CheckCircle}
                    color="text-emerald-600"
                    bg="bg-emerald-50 dark:bg-emerald-900/20"
                />
                <StatCard
                    title="Top Model"
                    value={topModel ? topModel[0].replace('gemini-', '').split('-')[0] : 'N/A'}
                    icon={Activity}
                    color="text-amber-600"
                    bg="bg-amber-50 dark:bg-amber-900/20"
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
                                <th className="px-6 py-4 font-medium">RPM</th>
                                <th className="px-6 py-4 font-medium">TPM</th>
                                <th className="px-6 py-4 font-medium">RPD</th>
                                <th className="px-6 py-4 font-medium">Status</th>
                                <th className="px-6 py-4 font-medium">Time</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
                            {imageJobs.length === 0 ? (
                                <tr>
                                    <td colSpan="8" className="px-6 py-8 text-center text-slate-500 dark:text-slate-400">
                                        No activity recorded yet.
                                    </td>
                                </tr>
                            ) : (
                                imageJobs.slice(0, 10).map((job) => (
                                    <tr key={job.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                                        <td className="px-6 py-4 text-slate-500 dark:text-slate-400 font-mono text-xs">
                                            {job.id.slice(-6)}
                                        </td>
                                        <td className="px-6 py-4 text-slate-900 dark:text-white capitalize">{job.type}</td>
                                        <td className="px-6 py-4 text-slate-600 dark:text-slate-300 text-xs font-mono">
                                            {job.settings?.model || 'N/A'}
                                        </td>
                                        <td className="px-6 py-4 text-slate-500 dark:text-slate-400">-</td>
                                        <td className="px-6 py-4 text-slate-500 dark:text-slate-400">-</td>
                                        <td className="px-6 py-4 text-slate-500 dark:text-slate-400">-</td>
                                        <td className="px-6 py-4">
                                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                                                ${job.status === 'completed' ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400' :
                                                    job.status === 'failed' ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400' :
                                                        'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400'}`}>
                                                {job.status}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-slate-500 dark:text-slate-400 text-xs">
                                            {new Date(job.timestamp).toLocaleString()}
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default ImageStats;
