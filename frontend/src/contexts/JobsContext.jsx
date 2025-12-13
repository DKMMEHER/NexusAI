import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../api/client';
import { useAuth } from './AuthContext';

const JobsContext = createContext();

export const useJobs = () => {
    const context = useContext(JobsContext);
    if (!context) {
        throw new Error('useJobs must be used within a JobsProvider');
    }
    return context;
};

export const JobsProvider = ({ children }) => {
    const { currentUser } = useAuth();
    const [jobs, setJobs] = useState([]);

    const MAX_JOBS = 50; // Increased limit for combined history

    // Load jobs from backend when user logs in
    useEffect(() => {
        if (currentUser) {
            Promise.all([
                api.director.getMyJobs(currentUser.uid).catch(err => {
                    console.error("Failed to fetch director jobs:", err);
                    return [];
                }),
                api.getMyImages(currentUser.uid).catch(err => {
                    console.error("Failed to fetch image jobs:", err);
                    return [];
                })
            ]).then(([directorJobs, imageJobs]) => {
                // Ensure arrays
                const dJobs = Array.isArray(directorJobs) ? directorJobs : [];
                const iJobs = Array.isArray(imageJobs) ? imageJobs : [];

                const combined = [...dJobs, ...iJobs];

                // Sort by timestamp (newest first)
                const sorted = combined.sort((a, b) => {
                    const timeA = new Date(a.created_at || a.timestamp || 0);
                    const timeB = new Date(b.created_at || b.timestamp || 0);
                    return timeB - timeA;
                });

                setJobs(sorted);
            });
        } else {
            setJobs([]);
        }
    }, [currentUser]);

    const addJob = async (job) => {
        // Optimistic update
        setJobs(prev => {
            const newJobs = [job, ...prev];
            return newJobs.slice(0, MAX_JOBS);
        });

        // Persist to backend if user is logged in
        if (currentUser) {
            // Logic to determine if we need to manually save this job to Director External Service.
            // Image Generation jobs are saved by the Image Generation Backend automatically.
            // Director Movie jobs are saved by Director Backend automatically.
            // TextToVideo jobs (and potentially others in future) are NOT saved automatically.

            const isImageJob = ['generate', 'edit', 'tryon', 'ads', 'merge', 'scenes', 'restore'].includes(job.type);
            const isDirectorMovie = job.type === 'director_movie';

            if (!isImageJob && !isDirectorMovie) {
                // Map simple job to MovieJob structure
                const movieJob = {
                    job_id: String(job.id),
                    type: job.type || 'external',
                    topic: job.prompt || 'Untitled',
                    status: job.status,
                    created_at: job.timestamp || new Date().toISOString(),
                    user_id: currentUser.uid,
                    model: job.settings?.model || 'unknown',
                    resolution: job.settings?.resolution || '720p',
                    aspect_ratio: job.settings?.aspect_ratio || '16:9'
                };

                try {
                    await api.director.saveExternalJob(movieJob);
                } catch (err) {
                    console.error("Failed to save external job:", err);
                }
            }
        }
    };

    const updateJobStatus = (jobId, status, result = null) => {
        setJobs(prev => prev.map(job =>
            job.id === jobId
                ? { ...job, status, ...(result && { result }) }
                : job
        ));
    };

    const clearJobs = () => {
        setJobs([]);
        // Ideally we would also clear backend, but that's a destructive operation.
        // For now, allow clearing local view.
    };

    const removeJob = (jobId) => {
        setJobs(prev => prev.filter(job => job.id !== jobId));
    };

    return (
        <JobsContext.Provider value={{ jobs, addJob, updateJobStatus, clearJobs, removeJob }}>
            {children}
        </JobsContext.Provider>
    );
};
