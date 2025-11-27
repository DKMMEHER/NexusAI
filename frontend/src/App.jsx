import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import TextToVideo from './pages/TextToVideo';
import ImageToVideo from './pages/ImageToVideo';
import ReferenceImages from './pages/ReferenceImages';
import FirstLastFrames from './pages/FirstLastFrames';
import ExtendVideo from './pages/ExtendVideo';
import Gallery from './pages/Gallery';
import ImageGeneration from './pages/ImageGeneration';
import PDFSummarization from './pages/PDFSummarization';
import VideoStats from './pages/VideoStats';
import { JobsProvider } from './contexts/JobsContext';
import { Toaster } from 'sonner';

function App() {
  return (
    <JobsProvider>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/text-to-video" element={<TextToVideo />} />
            <Route path="/image-to-video" element={<ImageToVideo />} />
            <Route path="/reference-images" element={<ReferenceImages />} />
            <Route path="/first-last-frames" element={<FirstLastFrames />} />
            <Route path="/extend-video" element={<ExtendVideo />} />
            <Route path="/gallery" element={<Gallery />} />
            <Route path="/video-stats" element={<VideoStats />} />
            <Route path="/image-generation" element={<ImageGeneration />} />
            <Route path="/pdf-summarization" element={<PDFSummarization />} />
          </Routes>
        </Layout>
        <Toaster position="top-right" theme="system" richColors />
      </BrowserRouter>
    </JobsProvider>
  );
}

export default App;
