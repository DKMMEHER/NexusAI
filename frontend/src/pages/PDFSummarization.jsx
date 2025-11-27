import React from 'react';
import { FileText, Construction } from 'lucide-react';

export default function PDFSummarization() {
    return (
        <div className="flex min-h-[60vh] flex-col items-center justify-center text-center">
            <div className="mb-6 rounded-full bg-green-500/10 p-8">
                <FileText className="h-16 w-16 text-green-500" />
            </div>
            <h1 className="mb-4 text-4xl font-bold text-slate-900 dark:text-white">PDF Summarization</h1>
            <p className="mb-8 max-w-md text-lg text-slate-500 dark:text-gray-400">
                Powerful document analysis and summarization tools are coming your way.
            </p>

            <div className="flex items-center gap-2 rounded-full bg-slate-100 px-4 py-2 text-sm font-medium text-slate-600 dark:bg-white/5 dark:text-gray-400">
                <Construction className="h-4 w-4" />
                Under Construction
            </div>
        </div>
    );
}
