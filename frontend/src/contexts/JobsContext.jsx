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

    useEffect(() => {
        localStorage.setItem('veo_jobs', JSON.stringify(jobs));
    }, [jobs]);

    const addJob = (job) => {
        setJobs(prev => [job, ...prev]);
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
