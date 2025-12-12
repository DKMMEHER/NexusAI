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
import VideoStats from './pages/VideoStats';
import ImageGallery from './pages/ImageGallery';
import ImageStats from './pages/ImageStats';
import DocumentsSummarization from './pages/DocumentsSummarization';
import YoutubeTranscript from './pages/YoutubeTranscript';
import Chat from './pages/Chat';
import ChatStats from './pages/ChatStats';
import YoutubeStats from './pages/YoutubeStats';
import DocumentsStats from './pages/DocumentsStats';
import Director from './pages/Director';
import { JobsProvider } from './contexts/JobsContext';
import { Toaster } from 'sonner';

import ErrorBoundary from './components/ErrorBoundary';

import Login from './pages/Login';
import { AuthProvider, useAuth } from './contexts/AuthContext';

// Protected Route Component
const PrivateRoute = ({ children }) => {
  const { currentUser } = useAuth();

  if (!currentUser) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

// Route without Layout (for Login)
const MinimalLayout = ({ children }) => (
  <div className="min-h-screen bg-black">
    {children}
  </div>
);

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <JobsProvider>
          <BrowserRouter>
            <Routes>
              {/* Public Routes */}
              <Route path="/login" element={
                <MinimalLayout>
                  <Login />
                </MinimalLayout>
              } />

              {/* Protected Routes */}
              <Route path="/*" element={
                <PrivateRoute>
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
                      <Route path="/image-generation" element={<Navigate to="/image-generation/generate" replace />} />
                      <Route path="/image-generation/:mode" element={<ImageGeneration />} />
                      <Route path="/image-gallery" element={<ImageGallery />} />
                      <Route path="/image-stats" element={<ImageStats />} />
                      <Route path="/documents-summarization" element={<DocumentsSummarization />} />
                      <Route path="/youtube-transcript" element={<YoutubeTranscript />} />
                      <Route path="/chat" element={<Chat />} />
                      <Route path="/director" element={<Director />} />

                      {/* Analytics Routes */}
                      <Route path="/chat-stats" element={<ChatStats />} />
                      <Route path="/youtube-stats" element={<YoutubeStats />} />
                      <Route path="/documents-stats" element={<DocumentsStats />} />
                    </Routes>
                  </Layout>
                </PrivateRoute>
              } />
            </Routes>
            <Toaster position="top-right" theme="system" richColors />
          </BrowserRouter>
        </JobsProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;
