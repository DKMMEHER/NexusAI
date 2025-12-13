import React, { useState, useEffect } from 'react';
import { BarChart3 } from 'lucide-react';
import { api } from '../api/client';
import { useAuth } from '../contexts/AuthContext';

const DocumentsStats = () => {
    const { currentUser } = useAuth();
    const [analyticsData, setAnalyticsData] = useState([]);
    const [timeRange, setTimeRange] = useState('all');

    const fetchAnalytics = async () => {
        if (!currentUser) return;
        try {
            const data = await api.documents.getAnalytics(currentUser.uid);
            setAnalyticsData(data);
        } catch (error) {
            console.error("Failed to fetch analytics", error);
        }
    };

    useEffect(() => {
        fetchAnalytics();
        const interval = setInterval(fetchAnalytics, 5000);
        return () => clearInterval(interval);
    }, [currentUser]);

    const filterByTimeRange = (job) => {
        if (timeRange === 'all') return true;

        const jobDate = new Date(job.time);
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

    const filteredData = analyticsData.filter(filterByTimeRange);

    return (
        <div className="max-w-7xl mx-auto space-y-8">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900 dark:text-white flex items-center gap-3">
                        <BarChart3 className="text-blue-500" size={32} />
                        Document Analytics
                    </h1>
                    <p className="text-slate-500 dark:text-slate-400 mt-2 text-lg">
                        Track your document summarization history and usage.
                    </p>
                </div>

                <select
                    value={timeRange}
                    onChange={(e) => setTimeRange(e.target.value)}
                    className="px-4 py-2 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                >
                    <option value="all">All Time</option>
                    <option value="1h">Last Hour</option>
                    <option value="24h">Last 24 Hours</option>
                    <option value="7d">Last 7 Days</option>
                    <option value="28d">Last 28 Days</option>
                    <option value="90d">Last 90 Days</option>
                </select>
            </div>

            <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden shadow-sm">
                <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left">
                        <thead className="bg-slate-50 dark:bg-slate-700/50 text-slate-500 dark:text-slate-400 font-medium border-b border-slate-200 dark:border-slate-700">
                            <tr>
                                <th className="px-6 py-4">Job ID</th>
                                <th className="px-6 py-4">Type</th>
                                <th className="px-6 py-4">Model</th>
                                <th className="px-6 py-4">RPM</th>
                                <th className="px-6 py-4">TPM</th>
                                <th className="px-6 py-4">RPD</th>
                                <th className="px-6 py-4">Status</th>
                                <th className="px-6 py-4">Time</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
                            {filteredData.length === 0 ? (
                                <tr>
                                    <td colSpan="8" className="px-6 py-12 text-center text-slate-400">
                                        No analytics data available for this period.
                                    </td>
                                </tr>
                            ) : (
                                filteredData.map((job) => (
                                    <tr key={job.job_id} className="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
                                        <td className="px-6 py-4 font-mono text-xs text-slate-500">{job.job_id}</td>
                                        <td className="px-6 py-4">
                                            <span className="px-2.5 py-1 rounded-full text-[10px] font-medium bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
                                                {job.type}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-slate-700 dark:text-slate-300 font-medium">{job.model}</td>
                                        <td className="px-6 py-4 text-slate-500">{job.rpm}</td>
                                        <td className="px-6 py-4 text-slate-500">{job.tpm}</td>
                                        <td className="px-6 py-4 text-slate-500">{job.rpd}</td>
                                        <td className="px-6 py-4">
                                            <span className={`flex items-center gap-2 ${job.status === 'Success' ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'
                                                }`}>
                                                <span className={`w-2 h-2 rounded-full ${job.status === 'Success' ? 'bg-emerald-500' : 'bg-red-500'
                                                    }`} />
                                                {job.status}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-slate-500 whitespace-nowrap">{job.time}</td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div >
        </div >
    );
};

export default DocumentsStats;
