import axios from 'axios';

const client = axios.create({
    baseURL: '/', // Proxy handles the rest
    headers: {
        'Content-Type': 'multipart/form-data', // Default for file uploads, but axios handles it if data is FormData
    },
});

const handleResponse = (response) => response.data;

export const api = {
    // Video Generation
    textToVideo: (formData) => client.post('/text_to_video', formData).then(handleResponse),
    imageToVideo: (formData) => client.post('/image_to_video', formData).then(handleResponse),
    referenceImages: (formData) => client.post('/video_from_reference_images', formData).then(handleResponse),
    firstLastFrames: (formData) => client.post('/video_from_first_last_frames', formData).then(handleResponse),
    extendVideo: (formData) => client.post('/extend_veo_video', formData).then(handleResponse),
    getStatus: (operationName) => client.get(`/status/${operationName}`).then(handleResponse),
    getJobStatus: (operationName) => client.get(`/status/${operationName}`).then(handleResponse),
    getDownloadUrl: (operationName) => `/download/${operationName}`,

    // Image Generation
    generateImage: (formData) => client.post('/image/generate', formData).then(handleResponse),
    editImage: (formData) => client.post('/image/edit', formData).then(handleResponse),
    virtualTryOn: (formData) => client.post('/image/virtual_try_on', formData).then(handleResponse),
    createAds: (formData) => client.post('/image/create_ads', formData).then(handleResponse),
    mergeImages: (formData) => client.post('/image/merge_images', formData).then(handleResponse),
    generateScenes: (formData) => client.post('/image/generate_scenes', formData).then(handleResponse),
    restoreImage: (formData) => client.post('/image/restore_old_image', formData).then(handleResponse),

    // Document Summarization
    documents: {
        summarize: (formData) => client.post('/summarize', formData).then(handleResponse),
        getAnalytics: () => client.get('/api/documents/analytics').then(handleResponse),
    },

    // YouTube Transcript
    youtube: {
        getTranscript: (formData) => client.post('/transcript', formData).then(handleResponse),
        getAnalytics: () => client.get('/api/youtube/analytics').then(handleResponse),
    },

    // Chat
    chat: (formData) => client.post('/chat', formData).then(handleResponse),

    // Health Checks
    checkImageHealth: () => client.get('/image/').then(() => true).catch(() => false),
    checkVideoHealth: () => client.get('/status/').then(() => true).catch(() => false),
    checkDocsHealth: () => client.get('/summarize/').then(() => true).catch(() => false),
    checkYoutubeHealth: () => client.get('/transcript/').then(() => true).catch(() => false),
    checkChatHealth: () => client.get('/chat/').then(() => true).catch(() => false),

    // Director
    director: {
        createMovie: (data) => client.post('/director/create_movie', data, {
            headers: { 'Content-Type': 'application/json' }
        }).then(handleResponse),
        getMovieStatus: (jobId) => client.get(`/director/movie_status/${jobId}`).then(handleResponse),
        approveScript: (jobId, scenes) => client.post(`/director/approve_script/${jobId}`, { scenes }, {
            headers: { 'Content-Type': 'application/json' }
        }).then(handleResponse),
    },
};
