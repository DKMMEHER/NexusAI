import React from 'react';

const PRESETS = [
    { label: "Cinematic", value: "cinematic style, dramatic lighting, 4k, high detailed" },
    { label: "Anime", value: "anime style, vibrant colors, studio ghibli inspired, high quality" },
    { label: "3D Render", value: "3d render, unreal engine 5, pixar style, 8k, ray tracing" },
    { label: "Cyberpunk", value: "cyberpunk, neon lights, futuristic city, high contrast, sci-fi" },
    { label: "Vintage", value: "vintage 1950s film, film grain, black and white, classic movie" },
    { label: "Oil Painting", value: "oil painting style, textured, artistic, impressionist" },
    { label: "Fantasy", value: "fantasy world, magical, ethereal, dreamlike, highly detailed" },
    { label: "Drone Shot", value: "drone shot, aerial view, wide angle, smooth motion" }
];

const PromptPresets = ({ onSelect }) => {
    return (
        <div className="mt-3">
            <p className="text-xs text-gray-400 mb-2 font-medium uppercase tracking-wider">Style Presets</p>
            <div className="flex flex-wrap gap-2">
                {PRESETS.map((preset) => (
                    <button
                        key={preset.label}
                        onClick={() => onSelect(preset.value)}
                        className="px-3 py-1.5 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 rounded-full text-xs text-slate-600 dark:text-slate-300 transition-all duration-200"
                        type="button"
                    >
                        {preset.label}
                    </button>
                ))}
            </div>
        </div>
    );
};

export default PromptPresets;
