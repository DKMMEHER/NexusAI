import React from 'react';
import { Link } from 'react-router-dom';
import { Video, Image, FileText, ArrowRight, Youtube, MessageSquare } from 'lucide-react';

const FeatureCard = ({ title, description, icon: Icon, to, active = false, color }) => {
    const CardContent = () => (
        <>
            <div className={`absolute -right-10 -top-10 h-40 w-40 rounded-full blur-3xl transition-all group-hover:scale-150 ${color} opacity-20`} />

            <div className="relative z-10">
                <div className="mb-6 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-slate-100 dark:bg-white/10 backdrop-blur-sm">
                    <Icon className="h-6 w-6 text-slate-900 dark:text-white" />
                </div>

                <h3 className="mb-3 text-2xl font-bold text-slate-900 dark:text-white">{title}</h3>
                <p className="mb-6 text-slate-500 dark:text-gray-400">{description}</p>

                {active ? (
                    <div className="inline-flex items-center gap-2 text-sm font-medium text-blue-600 dark:text-white transition-colors group-hover:text-blue-700 dark:group-hover:text-blue-400">
                        Launch App <ArrowRight className="h-4 w-4" />
                    </div>
                ) : (
                    <span className="inline-flex items-center gap-2 text-sm font-medium text-slate-400 dark:text-gray-500">
                        Coming Soon
                    </span>
                )}
            </div>
        </>
    );

    const cardClasses = `relative block h-full group overflow-hidden rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 p-8 transition-all hover:border-slate-300 dark:hover:border-white/20 hover:shadow-lg dark:hover:bg-white/10 ${!active && 'opacity-60 cursor-not-allowed'}`;

    if (active) {
        return (
            <Link to={to} className={cardClasses}>
                <CardContent />
            </Link>
        );
    }

    return (
        <div className={cardClasses}>
            <CardContent />
        </div>
    );
};

export default function Dashboard() {
    return (
        <div className="mx-auto max-w-7xl px-6 py-12">
            <div className="mb-16 text-center">
                <h1 className="mb-4 text-5xl font-bold tracking-tight text-slate-900 dark:text-white">
                    Nexus<span className="text-blue-600 dark:text-blue-500">AI</span>
                </h1>
                <p className="text-xl text-slate-500 dark:text-gray-400">
                    Unified Generative AI Suite for Video, Images, and Documents
                </p>
            </div>

            <div className="grid gap-8 md:grid-cols-3">
                <FeatureCard
                    title="Video Generation"
                    description="Create cinematic videos from text, images, or reference frames using Google Veo."
                    icon={Video}
                    to="/text-to-video"
                    active={true}
                    color="bg-blue-500"
                />

                <FeatureCard
                    title="Image Generation"
                    description="Generate stunning high-resolution images from detailed text prompts."
                    icon={Image}
                    to="/image-generation"
                    active={true}
                    color="bg-purple-500"
                />

                <FeatureCard
                    title="Documents Summarization"
                    description="Extract insights and summaries from PDFs, Docs, Slides, and more."
                    icon={FileText}
                    to="/documents-summarization"
                    active={true}
                    color="bg-green-500"
                />

                <FeatureCard
                    title="YouTube Transcript"
                    description="Get transcripts and summaries from YouTube videos instantly."
                    icon={Youtube}
                    to="/youtube-transcript"
                    active={true}
                    color="bg-red-500"
                />

                <FeatureCard
                    title="Chat & Q&A"
                    description="Have continuous conversations and ask questions to the AI Assistant."
                    icon={MessageSquare}
                    to="/chat"
                    active={true}
                    color="bg-indigo-500"
                />
            </div>
        </div>
    );
}
