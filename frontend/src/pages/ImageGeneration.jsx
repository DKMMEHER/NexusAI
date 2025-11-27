import React, { useState } from 'react';
import { api } from '../api/client';
import FileUploader from '../components/FileUploader';
import {
    Image as ImageIcon,
    Wand2,
    Shirt,
    Megaphone,
    Layers,
    Clapperboard,
    History,
    Upload,
    Loader2,
    Download,
    AlertCircle
} from 'lucide-react';
import { toast } from 'sonner';

const ImageGeneration = () => {
    const [mode, setMode] = useState('generate');
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState([]);
    const [error, setError] = useState(null);

    // Form States
    const [prompt, setPrompt] = useState('');
    const [files, setFiles] = useState({});
    const [variations, setVariations] = useState(3);

    const modes = [
        { id: 'generate', label: 'Generate Image', icon: ImageIcon, desc: 'Text to Image' },
        { id: 'edit', label: 'Edit Image', icon: Wand2, desc: 'Modify with Prompt' },
        { id: 'tryon', label: 'Virtual Try-On', icon: Shirt, desc: 'Product on Person' },
        { id: 'ads', label: 'Create Ads', icon: Megaphone, desc: 'Marketing Assets' },
        { id: 'merge', label: 'Merge Images', icon: Layers, desc: 'Combine up to 5' },
        { id: 'scenes', label: 'Generate Scenes', icon: Clapperboard, desc: 'Scene Extension' },
        { id: 'restore', label: 'Restore Image', icon: History, desc: 'Fix Old Photos' },
    ];

    const handleFileChange = (key, newFiles) => {
        if (newFiles && newFiles.length > 0) {
            setFiles(prev => ({ ...prev, [key]: newFiles[0] }));
        } else {
            setFiles(prev => {
                const newObj = { ...prev };
                delete newObj[key];
                return newObj;
            });
        }
    };

    const handleMultiFileChange = (key, newFiles) => {
        setFiles(prev => ({ ...prev, [key]: newFiles }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setResults([]);

        const formData = new FormData();
        if (prompt) formData.append('prompt', prompt);

        try {
            let response;
            switch (mode) {
                case 'generate':
                    response = await api.generateImage(formData);
                    break;
                case 'edit':
                    if (!files.file) throw new Error("Please upload an image to edit.");
                    formData.append('file', files.file);
                    response = await api.editImage(formData);
                    break;
                case 'tryon':
                    if (!files.product || !files.person) throw new Error("Please upload both product and person images.");
                    formData.append('product', files.product);
                    formData.append('person', files.person);
                    response = await api.virtualTryOn(formData);
                    break;
                case 'ads':
                    if (!files.model || !files.product) throw new Error("Please upload both model and product images.");
                    formData.append('model', files.model);
                    formData.append('product', files.product);
                    if (variations) formData.append('variations', variations);
                    response = await api.createAds(formData);
                    break;
                case 'merge':
                    if (!files.merge_files || files.merge_files.length < 2) throw new Error("Please upload at least 2 images to merge.");
                    files.merge_files.forEach(f => formData.append('files', f));
                    response = await api.mergeImages(formData);
                    break;
                case 'scenes':
                    if (!files.scene) throw new Error("Please upload a scene image.");
                    formData.append('scene', files.scene);
                    response = await api.generateScenes(formData);
                    break;
                case 'restore':
                    if (!files.file) throw new Error("Please upload an image to restore.");
                    formData.append('file', files.file);
                    response = await api.restoreImage(formData);
                    break;
                default:
                    throw new Error("Unknown mode selected.");
            }

            const data = response.data;
            if (data.results) {
                setResults(data.results);
            } else if (data.image) {
                setResults([{ image: data.image, mime: data.mime }]);
            }

            toast.success("Generation successful!");
        } catch (err) {
            console.error(err);
            const msg = err.response?.data?.detail || err.message || "An error occurred";
            setError(msg);
            toast.error(msg);
        } finally {
            setLoading(false);
        }
    };

    const downloadImage = (base64Data, mimeType, index) => {
        const link = document.createElement('a');
        link.href = `data:${mimeType};base64,${base64Data}`;

        // Manual IST Calculation (UTC + 5:30)
        const now = new Date();
        const utc = now.getTime() + (now.getTimezoneOffset() * 60000); // Convert to UTC
        const istOffset = 5.5 * 60 * 60 * 1000;
        const istDate = new Date(utc + istOffset);

        const year = istDate.getFullYear();
        const month = String(istDate.getMonth() + 1).padStart(2, '0');
        const day = String(istDate.getDate()).padStart(2, '0');
        const hour = String(istDate.getHours()).padStart(2, '0');
        const minute = String(istDate.getMinutes()).padStart(2, '0');
        const second = String(istDate.getSeconds()).padStart(2, '0');

        const filename = `image_${year}_${month}_${day}_${hour}_${minute}_${second}.png`;

        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    return (
        <div className="max-w-7xl mx-auto space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-slate-900 dark:text-white flex items-center gap-3">
                    <span className="text-4xl">🍌</span> Nano Banana Studio
                </h1>
                <p className="text-slate-500 dark:text-slate-400 mt-2 text-lg">
                    Creative image generation and editing suite powered by Gemini.
                </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                {/* Sidebar - Mode Selection */}
                <div className="lg:col-span-3 space-y-2">
                    {modes.map((m) => (
                        <button
                            key={m.id}
                            onClick={() => { setMode(m.id); setResults([]); setError(null); setFiles({}); setPrompt(''); }}
                            className={`w-full flex items-center gap-3 p-4 rounded-xl transition-all text-left
                                ${mode === m.id
                                    ? 'bg-primary text-white shadow-lg shadow-primary/25'
                                    : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700'
                                }`}
                        >
                            <m.icon size={20} />
                            <div>
                                <div className="font-semibold">{m.label}</div>
                                <div className={`text-xs ${mode === m.id ? 'text-white/80' : 'text-slate-400'}`}>{m.desc}</div>
                            </div>
                        </button>
                    ))}
                </div>

                {/* Main Content - Form & Results */}
                <div className="lg:col-span-9 space-y-6">
                    <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-100 dark:border-slate-700 shadow-sm">
                        <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
                            {modes.find(m => m.id === mode)?.icon && React.createElement(modes.find(m => m.id === mode).icon, { className: "text-primary" })}
                            {modes.find(m => m.id === mode)?.label}
                        </h2>

                        <form onSubmit={handleSubmit} className="space-y-6">
                            {/* Dynamic Inputs based on Mode */}

                            {/* File Uploads */}
                            {(mode === 'edit' || mode === 'restore') && (
                                <div>
                                    <FileUploader
                                        label="Upload Image"
                                        files={files.file ? [files.file] : []}
                                        onFilesChange={(newFiles) => handleFileChange('file', newFiles)}
                                    />
                                </div>
                            )}

                            {mode === 'tryon' && (
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <FileUploader
                                            label="Product Image"
                                            files={files.product ? [files.product] : []}
                                            onFilesChange={(newFiles) => handleFileChange('product', newFiles)}
                                        />
                                    </div>
                                    <div>
                                        <FileUploader
                                            label="Person Image"
                                            files={files.person ? [files.person] : []}
                                            onFilesChange={(newFiles) => handleFileChange('person', newFiles)}
                                        />
                                    </div>
                                </div>
                            )}

                            {mode === 'ads' && (
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <FileUploader
                                            label="Model Image"
                                            files={files.model ? [files.model] : []}
                                            onFilesChange={(newFiles) => handleFileChange('model', newFiles)}
                                        />
                                    </div>
                                    <div>
                                        <FileUploader
                                            label="Product Image"
                                            files={files.product ? [files.product] : []}
                                            onFilesChange={(newFiles) => handleFileChange('product', newFiles)}
                                        />
                                    </div>
                                </div>
                            )}

                            {mode === 'merge' && (
                                <div>
                                    <FileUploader
                                        label="Upload Images (Max 5)"
                                        multiple={true}
                                        files={files.merge_files || []}
                                        onFilesChange={(newFiles) => handleMultiFileChange('merge_files', newFiles)}
                                    />
                                </div>
                            )}

                            {mode === 'scenes' && (
                                <div>
                                    <FileUploader
                                        label="Scene Image"
                                        files={files.scene ? [files.scene] : []}
                                        onFilesChange={(newFiles) => handleFileChange('scene', newFiles)}
                                    />
                                </div>
                            )}

                            {/* Prompt Input */}
                            <div>
                                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                                    {mode === 'generate' ? 'Prompt' : 'Instructions (Optional)'}
                                </label>
                                <textarea
                                    value={prompt}
                                    onChange={(e) => setPrompt(e.target.value)}
                                    placeholder={mode === 'generate' ? "Describe the image you want to generate..." : "Add specific instructions..."}
                                    className="w-full px-4 py-3 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all resize-none h-32 text-slate-700 dark:text-slate-200 placeholder:text-slate-400 dark:placeholder:text-slate-500"
                                />
                            </div>

                            {/* Submit Button */}
                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full py-4 bg-primary hover:bg-primary/90 text-white rounded-xl font-semibold shadow-lg shadow-primary/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="animate-spin" />
                                        Processing...
                                    </>
                                ) : (
                                    <>
                                        <Wand2 size={20} />
                                        {mode === 'generate' ? 'Generate' : 'Process'}
                                    </>
                                )}
                            </button>
                        </form>
                    </div>

                    {/* Error Message */}
                    {error && (
                        <div className="p-4 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-xl flex items-center gap-3">
                            <AlertCircle />
                            {error}
                        </div>
                    )}

                    {/* Results Grid */}
                    {results.length > 0 && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {results.map((res, idx) => (
                                <div key={idx} className="group relative bg-white dark:bg-slate-800 rounded-2xl overflow-hidden border border-slate-100 dark:border-slate-700 shadow-sm">
                                    <img
                                        src={`data:${res.mime};base64,${res.image}`}
                                        alt={`Result ${idx + 1}`}
                                        className="w-full h-auto object-cover"
                                    />
                                    <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-4">
                                        <button
                                            onClick={(e) => { e.stopPropagation(); downloadImage(res.image, res.mime, idx); }}
                                            className="p-3 bg-white/10 backdrop-blur-md rounded-full text-white hover:bg-white/20 transition-colors"
                                            title="Download"
                                        >
                                            <Download size={24} />
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ImageGeneration;
