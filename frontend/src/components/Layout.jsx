import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Video, Image, Layers, Film, FastForward, Activity, Sun, Moon, Grid, LayoutDashboard, Wand2, Shirt, Megaphone, Clapperboard, History, FileText, BarChart3, GalleryHorizontal, Youtube, MessageSquare } from 'lucide-react';
import clsx from 'clsx';
import { api } from '../api/client';

const NavItem = ({ to, icon: Icon, label, highlight }) => {
    const location = useLocation();
    const isActive = location.pathname === to;

    return (
        <Link
            to={to}
            className={clsx(
                "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group",
                isActive
                    ? "bg-primary/10 text-primary font-medium"
                    : highlight
                        ? "text-purple-600 bg-purple-50 hover:bg-purple-100 font-medium"
                        : "text-slate-500 hover:bg-slate-50 hover:text-slate-900"
            )}
        >
            <Icon size={20} className={clsx(isActive ? "text-primary" : highlight ? "text-purple-600" : "text-slate-400 group-hover:text-slate-600")} />
            <span>{label}</span>
        </Link>
    );
};

const Layout = ({ children }) => {
    const location = useLocation();

    const [health, setHealth] = React.useState({
        image: false,
        video: false,
        docs: false,
        youtube: false,
        chat: false
    });

    React.useEffect(() => {
        const checkAllHealth = async () => {
            const [image, video, docs, youtube, chat] = await Promise.all([
                api.checkImageHealth(),
                api.checkVideoHealth(),
                api.checkDocsHealth(),
                api.checkYoutubeHealth(),
                api.checkChatHealth()
            ]);
            setHealth({ image, video, docs, youtube, chat });
        };

        checkAllHealth();
        const interval = setInterval(checkAllHealth, 30000); // Check every 30s
        return () => clearInterval(interval);
    }, []);

    const StatusIndicator = ({ online, port }) => (
        <div className="flex justify-between text-xs items-center">
            <div className="flex items-center gap-1.5">
                <div className={`w-1.5 h-1.5 rounded-full ${online ? 'bg-emerald-500' : 'bg-red-500'}`} />
                <span className="text-slate-500 dark:text-slate-400">
                    {port === 8000 ? 'Image Gen' :
                        port === 8002 ? 'Video Gen' :
                            port === 8003 ? 'Doc Sum' :
                                port === 8004 ? 'YouTube' : 'Chat'}
                </span>
            </div>
            <span className={`${online ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-500 dark:text-red-400'} font-mono`}>
                {port}
            </span>
        </div>
    );

    const [darkMode, setDarkMode] = React.useState(() => {
        if (typeof window !== 'undefined') {
            return localStorage.getItem('theme') === 'dark' ||
                (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches);
        }
        return false;
    });

    React.useEffect(() => {
        if (darkMode) {
            document.documentElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        }
    }, [darkMode]);

    // Helper to check if current path matches a list of base paths
    const isPathActive = (paths) => {
        const currentPath = location.pathname.replace(/\/$/, '') || '/';
        return paths.some(path => currentPath.startsWith(path));
    };

    return (
        <div className="min-h-screen bg-slate-50 dark:bg-slate-900 flex transition-colors duration-200">
            {/* Sidebar */}
            <aside className="w-64 bg-white dark:bg-slate-900 border-r border-slate-100 dark:border-slate-800 flex flex-col fixed h-full z-10 transition-colors duration-200">
                {/* Header */}
                <div className="p-6">
                    <div className="flex items-center gap-2 text-slate-900 dark:text-white font-bold text-xl">
                        <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center text-white shadow-lg shadow-primary/20">
                            <Video size={18} />
                        </div>
                        Veo Studio
                    </div>
                    <div className="text-xs text-slate-400 mt-1 ml-10">Creator Suite</div>
                </div>

                {/* Navigation */}
                <nav className="flex-1 px-4 space-y-1 mt-4 overflow-y-auto min-h-0">
                    {isPathActive(['/text-to-video', '/image-to-video', '/reference-images', '/first-last-frames', '/extend-video', '/gallery', '/video-stats']) ? (
                        <>
                            <NavItem to="/" icon={LayoutDashboard} label="Back to Dashboard" />
                            <NavItem to="/director" icon={Clapperboard} label="The Director" />
                            <div className="my-4 border-t border-slate-100 dark:border-slate-800" />
                            <div className="px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                                Video Tools
                            </div>
                            <NavItem to="/text-to-video" icon={Video} label="Text → Video" />
                            <NavItem to="/image-to-video" icon={Image} label="Image → Video" />
                            <NavItem to="/reference-images" icon={Layers} label="Reference Images" />
                            <NavItem to="/first-last-frames" icon={Film} label="First + Last" />
                            <NavItem to="/extend-video" icon={FastForward} label="Extend Video" />
                            <NavItem to="/gallery" icon={Grid} label="Gallery" />
                            <NavItem to="/video-stats" icon={Activity} label="Analytics" />
                        </>
                    ) : isPathActive(['/image-generation', '/image-gallery', '/image-stats']) ? (
                        <>
                            <NavItem to="/" icon={LayoutDashboard} label="Back to Dashboard" />
                            <NavItem to="/director" icon={Clapperboard} label="The Director" />
                            <div className="my-4 border-t border-slate-100 dark:border-slate-800" />
                            <div className="px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                                Image Tools
                            </div>
                            <NavItem to="/image-generation/generate" icon={Image} label="Generate Image" />
                            <NavItem to="/image-generation/edit" icon={Wand2} label="Edit Image" />
                            <NavItem to="/image-generation/tryon" icon={Shirt} label="Virtual Try-On" />
                            <NavItem to="/image-generation/ads" icon={Megaphone} label="Create Ads" />
                            <NavItem to="/image-generation/merge" icon={Layers} label="Merge Images" />
                            <NavItem to="/image-generation/scenes" icon={Clapperboard} label="Generate Scenes" />
                            <NavItem to="/image-generation/restore" icon={History} label="Restore Image" />
                            <div className="my-4 border-t border-slate-100 dark:border-slate-800" />
                            <NavItem to="/image-gallery" icon={Grid} label="Gallery" />
                            <NavItem to="/image-stats" icon={Activity} label="Analytics" />
                        </>
                    ) : isPathActive(['/documents-summarization', '/documents-stats']) ? (
                        <>
                            <NavItem to="/" icon={LayoutDashboard} label="Back to Dashboard" />
                            <NavItem to="/director" icon={Clapperboard} label="The Director" />
                            <div className="my-4 border-t border-slate-100 dark:border-slate-800" />
                            <div className="px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                                Document Tools
                            </div>
                            <NavItem to="/documents-summarization" icon={FileText} label="Summarization" />
                            <NavItem to="/documents-stats" icon={Activity} label="Analytics" />
                        </>
                    ) : isPathActive(['/youtube-transcript', '/youtube-stats']) ? (
                        <>
                            <NavItem to="/" icon={LayoutDashboard} label="Back to Dashboard" />
                            <NavItem to="/director" icon={Clapperboard} label="The Director" />
                            <div className="my-4 border-t border-slate-100 dark:border-slate-800" />
                            <div className="px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                                YouTube Tools
                            </div>
                            <NavItem to="/youtube-transcript" icon={Youtube} label="Transcript" />
                            <NavItem to="/youtube-stats" icon={Activity} label="Analytics" />
                        </>
                    ) : isPathActive(['/chat', '/chat-stats']) ? (
                        <>
                            <NavItem to="/" icon={LayoutDashboard} label="Back to Dashboard" />
                            <NavItem to="/director" icon={Clapperboard} label="The Director" />
                            <div className="my-4 border-t border-slate-100 dark:border-slate-800" />
                            <div className="px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                                Chat Tools
                            </div>
                            <NavItem to="/chat" icon={MessageSquare} label="Chat & Q&A" />
                            <NavItem to="/chat-stats" icon={Activity} label="Analytics" />
                        </>
                    ) : (
                        <>
                            <NavItem to="/" icon={LayoutDashboard} label="Dashboard" />
                            <NavItem to="/director" icon={Clapperboard} label="The Director" />
                            <div className="my-4 border-t border-slate-100 dark:border-slate-800" />
                            <div className="px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                                Apps
                            </div>
                            <NavItem to="/image-generation/generate" icon={Image} label="Image Generation" />
                            <NavItem to="/text-to-video" icon={Video} label="Video Generation" />
                            <NavItem to="/documents-summarization" icon={FileText} label="Documents Summarization" />
                            <NavItem to="/youtube-transcript" icon={Youtube} label="YouTube Transcript" />
                            <NavItem to="/chat" icon={MessageSquare} label="Chat & Q&A" />
                            <div className="my-4 border-t border-slate-100 dark:border-slate-800" />
                            <NavItem to="/image-gallery" icon={GalleryHorizontal} label="Image Gallery" />
                            <NavItem to="/gallery" icon={GalleryHorizontal} label="Video Gallery" />
                            <NavItem to="/image-stats" icon={BarChart3} label="Image Analytics" />
                            <NavItem to="/video-stats" icon={BarChart3} label="Video Analytics" />
                        </>
                    )}
                </nav>

                {/* Footer */}
                <div className="p-4 border-t border-slate-100 dark:border-slate-800 space-y-4">
                    <button
                        className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 transition-all duration-200"
                        onClick={() => setDarkMode(!darkMode)}
                    >
                        {darkMode ? <Sun size={20} /> : <Moon size={20} />}
                        <span>{darkMode ? 'Light Mode' : 'Dark Mode'}</span>
                    </button>

                    <div className="bg-slate-50 dark:bg-slate-800 rounded-xl p-4 transition-colors duration-200">
                        <div className="flex items-center gap-2 text-sm font-medium text-slate-700 dark:text-slate-200 mb-2">
                            <Activity size={16} className="text-emerald-500" />
                            System Status
                        </div>
                        <div className="space-y-1">
                            <StatusIndicator online={health.image} port={8000} />
                            <StatusIndicator online={health.video} port={8002} />
                            <StatusIndicator online={health.docs} port={8003} />
                            <StatusIndicator online={health.youtube} port={8004} />
                            <StatusIndicator online={health.chat} port={8005} />
                        </div>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 ml-64 p-8">
                <div className="max-w-5xl mx-auto">
                    {children}
                </div>
            </main>
        </div>
    );
};

export default Layout;
