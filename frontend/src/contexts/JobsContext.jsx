import React, { createContext, useContext, useState, useEffect } from 'react';

const JobsContext = createContext();

export const useJobs = () => {
    const context = useContext(JobsContext);
    if (!context) {
        throw new Error('useJobs must be used within a JobsProvider');
    }
    return context;
};

export const JobsProvider = ({ children }) => {
    const [jobs, setJobs] = useState(() => {
        if (typeof window !== 'undefined') {
            const savedJobs = localStorage.getItem('veo_jobs');
            return savedJobs ? JSON.parse(savedJobs) : [];
        }
        return [];
    });

    const MAX_JOBS = 20;

    useEffect(() => {
        try {
            localStorage.setItem('veo_jobs', JSON.stringify(jobs));
        } catch (error) {
            console.error("Failed to save jobs to localStorage:", error);
            // If quota exceeded, try to save fewer jobs
            if (error.name === 'QuotaExceededError' || error.code === 22) {
                const reducedJobs = jobs.slice(0, 5); // Keep only 5 latest
                try {
                    localStorage.setItem('veo_jobs', JSON.stringify(reducedJobs));
                    setJobs(reducedJobs); // Update state to match storage
                } catch (retryError) {
                    console.error("Still failed to save reduced jobs:", retryError);
                }
            }
        }
    }, [jobs]);

    const addJob = (job) => {
        setJobs(prev => {
            const newJobs = [job, ...prev];
            return newJobs.slice(0, MAX_JOBS);
        });
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
        localStorage.removeItem('veo_jobs');
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
