import React from 'react';

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null, errorInfo: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        console.error("Uncaught error:", error, errorInfo);
        this.setState({ error, errorInfo });
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen flex items-center justify-center bg-red-50 p-4">
                    <div className="max-w-2xl w-full bg-white rounded-xl shadow-lg p-8 border border-red-100">
                        <h1 className="text-2xl font-bold text-red-600 mb-4">Something went wrong</h1>
                        <p className="text-slate-600 mb-6">The application encountered an unexpected error.</p>

                        <div className="bg-slate-900 rounded-lg p-4 overflow-x-auto mb-6">
                            <code className="text-red-400 text-sm font-mono">
                                {this.state.error && this.state.error.toString()}
                            </code>
                            {this.state.errorInfo && (
                                <pre className="text-slate-500 text-xs mt-2 overflow-x-auto">
                                    {this.state.errorInfo.componentStack}
                                </pre>
                            )}
                        </div>

                        <button
                            onClick={() => window.location.reload()}
                            className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-colors"
                        >
                            Reload Application
                        </button>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
