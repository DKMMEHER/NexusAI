import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Video, Image, Layers, Film, FastForward, Activity, Sun, Moon, Grid, LayoutDashboard, Wand2, Shirt, Megaphone, Clapperboard, History } from 'lucide-react';
import clsx from 'clsx';

const NavItem = ({ to, icon: Icon, label }) => {
    const location = useLocation();
    const isActive = location.pathname === to;

    return (
        <Link
            to={to}
            className={clsx(
                "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group",
                isActive
                    ? "bg-primary/10 text-primary font-medium"
                    : "text-slate-500 hover:bg-slate-50 hover:text-slate-900"
            )}
        >
            <Icon size={20} className={clsx(isActive ? "text-primary" : "text-slate-400 group-hover:text-slate-600")} />
            <span>{label}</span>
        </Link>
    );
};

const Layout = ({ children }) => {
    const location = useLocation();
    const [darkMode, setDarkMode] = React.useState(() => {
        if (typeof window !== 'undefined') {
            return localStorage.getItem('theme') === 'dark' ||
                (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches);
        }
        return false;
    });

    React.useEffect(() => {
        console.log("Dark mode state changed:", darkMode);
        if (darkMode) {
            document.documentElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
            console.log("Added dark class");
        } else {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('theme', 'light');
            console.log("Removed dark class");
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
                <div className="p-6">
                    <div className="flex items-center gap-2 text-slate-900 dark:text-white font-bold text-xl">
                        <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center text-white shadow-lg shadow-primary/20">
                            <Video size={18} />
                        </div>
                        Veo Studio
                    </div>
                    <div className="text-xs text-slate-400 mt-1 ml-10">Creator Suite</div>
                </div>

                <nav className="flex-1 px-4 space-y-1 mt-4 overflow-y-auto min-h-0">
                    {isPathActive(['/text-to-video', '/image-to-video', '/reference-images', '/first-last-frames', '/extend-video', '/gallery', '/video-stats']) ? (
                        <>
                            <NavItem to="/" icon={LayoutDashboard} label="Back to Dashboard" />
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
                    ) : (
                        <>
                            <NavItem to="/" icon={LayoutDashboard} label="Dashboard" />
                        </>
                    )}
                </nav>

                <div className="p-4 border-t border-slate-100 dark:border-slate-800 space-y-4">
                    <button
                        onClick={() => setDarkMode(!darkMode)}
                        className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 transition-all duration-200"
                    >
                        {darkMode ? <Sun size={20} /> : <Moon size={20} />}
                        <span>{darkMode ? 'Light Mode' : 'Dark Mode'}</span>
                    </button>

                    <div className="bg-slate-50 dark:bg-slate-800 rounded-xl p-4 transition-colors duration-200">
                        <div className="flex items-center gap-2 text-sm font-medium text-slate-700 dark:text-slate-200 mb-2">
                            <Activity size={16} className="text-emerald-500" />
                            System Status
                        </div>
                        <div className="text-xs text-slate-500 dark:text-slate-400">Backend: Port 8002</div>
                        <div className="text-xs text-slate-500 dark:text-slate-400">Model: Veo 3.1</div>
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
