import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const Login = () => {
    const { loginWithGoogle, loginWithGithub } = useAuth();
    const navigate = useNavigate();
    const [error, setError] = useState('');
    const [loadingProvider, setLoadingProvider] = useState(null);

    async function handleGoogleSignIn() {
        try {
            setError('');
            setLoadingProvider('google');
            await loginWithGoogle();
            navigate('/');
        } catch (err) {
            console.error("Login failed:", err);
            setError(`Failed to sign in: ${err.message}`);
        }
        setLoadingProvider(null);
    }

    async function handleGithubSignIn() {
        try {
            setError('');
            setLoadingProvider('github');
            await loginWithGithub();
            navigate('/');
        } catch (err) {
            console.error("Login failed:", err);
            setError(`Failed to sign in: ${err.message}`);
        }
        setLoadingProvider(null);
    }

    return (
        <div className="min-h-screen bg-black text-gray-100 flex items-center justify-center p-4 font-sans">
            <div className="w-full max-w-md bg-zinc-900/80 backdrop-blur-xl border border-zinc-700/50 rounded-2xl shadow-2xl p-8 space-y-8 animate-in fade-in zoom-in duration-500">

                {/* Header Section */}
                <div className="text-center space-y-2">
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 mb-4 shadow-lg shadow-purple-900/20">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-8 h-8 text-white">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" />
                        </svg>
                    </div>
                    <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-400 to-indigo-400">
                        NexusAI
                    </h1>
                    <p className="text-zinc-400">
                        Sign in to access your creative studio
                    </p>
                </div>

                {/* Error Message */}
                {error && (
                    <div className="bg-red-500/10 border border-red-500/20 text-red-400 text-sm p-3 rounded-lg text-center animate-pulse">
                        {error}
                    </div>
                )}

                <div className="space-y-4">
                    {/* Google Login Button */}
                    <button
                        onClick={handleGoogleSignIn}
                        disabled={loadingProvider !== null}
                        className="w-full group flex items-center justify-center gap-3 bg-white text-gray-900 hover:bg-gray-100 active:scale-[0.98] transition-all duration-200 font-medium py-3 px-4 rounded-xl shadow-lg hover:shadow-xl disabled:opacity-70 disabled:cursor-not-allowed"
                    >
                        {loadingProvider === 'google' ? (
                            <div className="w-5 h-5 border-2 border-gray-900 border-t-transparent rounded-full animate-spin" />
                        ) : (
                            <img
                                src="https://www.google.com/favicon.ico"
                                alt="Google"
                                className="w-5 h-5"
                            />
                        )}
                        <span>Continue with Google</span>
                    </button>

                    {/* GitHub Login Button */}
                    <button
                        onClick={handleGithubSignIn}
                        disabled={loadingProvider !== null}
                        className="w-full group flex items-center justify-center gap-3 bg-zinc-800 text-white hover:bg-zinc-700 active:scale-[0.98] transition-all duration-200 font-medium py-3 px-4 rounded-xl shadow-lg hover:shadow-xl disabled:opacity-70 disabled:cursor-not-allowed border border-zinc-700"
                    >
                        {loadingProvider === 'github' ? (
                            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        ) : (
                            <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
                                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                            </svg>
                        )}
                        <span>Continue with GitHub</span>
                    </button>
                </div>

                {/* Footer */}
                <div className="text-center text-xs text-zinc-600">
                    <p>By continuing, you agree to our Terms of Service and Privacy Policy.</p>
                </div>
            </div>
        </div>
    );
};

export default Login;
