import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import FileUploader from '../components/FileUploader';
import { useJobs } from '../contexts/JobsContext';
import {
    Image as ImageIcon,
    Wand2,
    Shirt,
    Megaphone,
    Layers,
    Clapperboard,
    History,
    Loader2,
    Download,
    AlertCircle,
    Globe
} from 'lucide-react';
import { toast } from 'sonner';

const ImageGeneration = () => {
    const { mode: urlMode } = useParams();
    const navigate = useNavigate();
    const { addJob } = useJobs();

    // Validate mode
    const validModes = ['generate', 'edit', 'tryon', 'ads', 'merge', 'scenes', 'restore'];
    const mode = validModes.includes(urlMode) ? urlMode : 'generate';

    useEffect(() => {
        if (!validModes.includes(urlMode)) {
            navigate('/image-generation/generate', { replace: true });
        }
    }, [urlMode, navigate]);

    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState([]);
    const [error, setError] = useState(null);

    // Form States
    const [prompt, setPrompt] = useState('');
    const [files, setFiles] = useState({});
    const [variations, setVariations] = useState(3);

    // New Advanced Settings
    const [selectedModel, setSelectedModel] = useState('gemini-2.5-flash-image');
    const [useGrounding, setUseGrounding] = useState(false);
    const [aspectRatio, setAspectRatio] = useState('1:1');

    // Reset state when mode changes
    useEffect(() => {
        setResults([]);
        setError(null);
        setFiles({});
        setPrompt('');
    }, [mode]);

    const models = [
        { id: 'gemini-2.5-flash-image', name: 'Gemini 2.5 Flash', desc: 'Fast & Stable', badge: 'Stable' },
        { id: 'gemini-2.5-flash-image-preview', name: 'Gemini 2.5 Flash Preview', desc: 'Latest Features', badge: 'Preview' },
        { id: 'gemini-3-pro-image-preview', name: 'Gemini 3 Pro', desc: 'High Quality & Reasoning', badge: 'Pro' }
    ];

    const modeConfig = {
        generate: { label: 'Generate Image', icon: ImageIcon, desc: 'Text to Image' },
        edit: { label: 'Edit Image', icon: Wand2, desc: 'Modify with Prompt' },
        tryon: { label: 'Virtual Try-On', icon: Shirt, desc: 'Product on Person' },
        ads: { label: 'Create Ads', icon: Megaphone, desc: 'Marketing Assets' },
        merge: { label: 'Merge Images', icon: Layers, desc: 'Combine up to 5 (14 for Pro)' },
        scenes: { label: 'Generate Scenes', icon: Clapperboard, desc: 'Scene Extension' },
        restore: { label: 'Restore Image', icon: History, desc: 'Fix Old Photos' },
    };

    const currentMode = modeConfig[mode];

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

        // Append Advanced Settings
        formData.append('model', selectedModel);
        if (useGrounding) formData.append('grounding', 'true');
        if (aspectRatio) formData.append('aspect_ratio', aspectRatio);

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
                    formData.append('model_image', files.model);
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

            const data = response;
            let finalResults = [];
            if (data.results) {
                finalResults = data.results;
            } else if (data.image) {
                finalResults = [{ image: data.image, mime: data.mime }];
            }
            setResults(finalResults);

            // Save to History
            const newJob = {
                id: Date.now().toString(),
                type: mode,
                status: 'completed',
                timestamp: new Date().toISOString(),
                settings: {
                    model: selectedModel,
                    prompt: prompt,
                    grounding: useGrounding,
                    aspectRatio: aspectRatio
                },
                result: {
                    images: finalResults
                }
            };
            addJob(newJob);

            toast.success("Generation successful!");
        } catch (err) {
            console.error(err);
            let msg = err.response?.data?.detail || err.message || "An error occurred";

            // Try to parse if msg is a JSON string
            if (typeof msg === 'string' && (msg.startsWith('{') || msg.startsWith('['))) {
                try {
                    const parsed = JSON.parse(msg);
                    if (parsed.error?.message) {
                        msg = parsed.error.message;
                    } else if (parsed.detail) {
                        msg = parsed.detail;
                    }
                } catch (e) {
                    // Not valid JSON, keep original message
                }
            }

            setError(msg);
            toast.error(msg);
        } finally {
            setLoading(false);
        }
    };

    const downloadImage = (base64Data, mimeType, index) => {
        const link = document.createElement('a');
        link.href = `data:${mimeType};base64,${base64Data}`;

        const now = new Date();
        const utc = now.getTime() + (now.getTimezoneOffset() * 60000);
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
        <div className="max-w-4xl mx-auto space-y-8">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900 dark:text-white flex items-center gap-3">
                        <span className="text-4xl">🍌</span> Nano Banana Studio
                    </h1>
                    <p className="text-slate-500 dark:text-slate-400 mt-2 text-lg">
                        {currentMode.desc}
                    </p>
                </div>

                {/* Global Model Selector */}
                <div className="bg-white dark:bg-slate-800 p-1.5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex items-center gap-2">
                    {models.map(m => (
                        <button
                            key={m.id}
                            onClick={() => setSelectedModel(m.id)}
                            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex flex-col items-start gap-0.5
                                ${selectedModel === m.id
                                    ? 'bg-primary text-white shadow-md'
                                    : 'text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700'
                                }`}
                        >
                            <span className="flex items-center gap-2">
                                {m.name}
                                {m.badge === 'Pro' && <span className="text-[10px] bg-yellow-400 text-yellow-900 px-1.5 rounded font-bold">PRO</span>}
                            </span>
                            <span className={`text-[10px] ${selectedModel === m.id ? 'text-white/80' : 'text-slate-400'}`}>{m.desc}</span>
                        </button>
                    ))}
                </div>
            </div>

            <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-100 dark:border-slate-700 shadow-sm">
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
                        <currentMode.icon className="text-primary" size={24} />
                        {currentMode.label}
                    </h2>

                    {/* Advanced Controls (Grounding & Ratio) */}
                    <div className="flex items-center gap-4">
                        {selectedModel.includes('gemini-3-pro') && (
                            <label className="flex items-center gap-2 cursor-pointer text-sm font-medium text-slate-600 dark:text-slate-300 bg-slate-50 dark:bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 hover:border-primary transition-colors">
                                <input
                                    type="checkbox"
                                    checked={useGrounding}
                                    onChange={(e) => setUseGrounding(e.target.checked)}
                                    className="w-4 h-4 text-primary rounded focus:ring-primary"
                                />
                                <Globe size={14} className="text-blue-500" />
                                Use Google Search
                            </label>
                        )}

                        <div className="flex items-center gap-2 bg-slate-50 dark:bg-slate-900 p-1 rounded-lg border border-slate-200 dark:border-slate-700">
                            <button
                                onClick={() => setAspectRatio('1:1')}
                                className={`p-1.5 rounded ${aspectRatio === '1:1' ? 'bg-white dark:bg-slate-700 shadow-sm text-primary' : 'text-slate-400 hover:text-slate-600'}`}
                                title="Square (1:1)"
                            >
                                <div className="w-4 h-4 border-2 border-current rounded-sm"></div>
                            </button>
                            <button
                                onClick={() => setAspectRatio('16:9')}
                                className={`p-1.5 rounded ${aspectRatio === '16:9' ? 'bg-white dark:bg-slate-700 shadow-sm text-primary' : 'text-slate-400 hover:text-slate-600'}`}
                                title="Cinematic (16:9)"
                            >
                                <div className="w-6 h-3.5 border-2 border-current rounded-sm"></div>
                            </button>
                        </div>
                    </div>
                </div>

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
                                label={`Upload Images (Max ${selectedModel.includes('gemini-3-pro') ? '14' : '5'})`}
                                multiple={true}
                                files={files.merge_files || []}
                                onFilesChange={(newFiles) => handleMultiFileChange('merge_files', newFiles)}
                            />
                            <p className="text-xs text-slate-400 mt-1">
                                {selectedModel.includes('gemini-3-pro')
                                    ? "Gemini 3 Pro allows merging up to 14 images!"
                                    : "Switch to Gemini 3 Pro to merge more than 5 images."}
                            </p>
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
                                Processing with {models.find(m => m.id === selectedModel)?.name}...
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
    );
};

export default ImageGeneration;
