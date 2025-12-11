# NexusAI

**NexusAI** is a comprehensive Generative AI suite that integrates multiple AI modalities into a single, unified local dashboard. Built with **React**, **FastAPI**, and powered by **Google Gemini & Veo**, it allows users to generate images, videos, movies, transcripts, and more.

## 🚀 Features

### 1. 🎬 The Director (Movie Maker)
*   **End-to-End Movie Generation**: Create short films from a simple text prompt.
*   **Auto-Scripting**: Uses Gemini to write screenplays with scenes, visual descriptions, and narration.
*   **AI Cinematography**: Controls camera angles, lighting, and movement.
*   **Video Generation**: Powered by **Google Veo 3.1** (Preview).
*   **Voiceover**: Validates language support (e.g., Hindi, English) for narration.
*   **Structure**: Database-backed job management with auto-save.

### 2. 📹 Video Generation
*   **Text-to-Video**: Generate high-quality 720p videos.
*   **Image-to-Video**: Animate static images.
*   **Video Extension**: Extend existing clips seamlessly.
*   **Backend**: Google Veo 3.1 integration.

### 3. 🎨 Image Generation
*   **Text-to-Image**: Generate high-fidelity images using Google's Imagen 3.
*   **Advanced Settings**: Aspect ratio, style controls (Cinematic, Photorealistic, etc.).

### 4. 📄 Document Summarization
*   **Upload & Summarize**: Process PDF/Text documents and extract key insights using Gemini 1.5 Pro.

### 5. 📺 YouTube Transcript & Chat
*   **Video Analysis**: Extract transcripts from YouTube videos.
*   **Q&A**: Chat with the video content to ask specific questions.

### 6. 💬 AI Chat
*   **General Purpose Assistant**: A clean chat interface for general queries and coding help.

---

## 🛠️ Technology Stack

*   **Frontend**: React (Vite), Tailwind CSS, Lucide React Icons.
*   **Backend Microservices**: Python (FastAPI).
    *   Separate services for each domain (Director, Video, Image, etc.) for modularity.
*   **AI Models**:
    *   **Text/Logic**: Gemini 1.5 Pro / Flash.
    *   **Video**: Veo 3.1 (Preview).
    *   **Image**: Imagen 3.
*   **Infrastructure**:
    *   **Docker & Docker Compose**: Unified containerization.
    *   **Nginx**: Reverse proxy for routing requests to microservices.
    *   **FFmpeg**: Video stitching and processing.

---

## 📦 Installation & Setup

### Prerequisites
*   **Docker Desktop** installed and running.
*   **Google Cloud Project** with Vertex AI enabled OR **Google AI Studio API Key**.

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/NexusAI.git
cd NexusAI
```

### 2. Configure Environment
Create a `.env` file in the root directory (or link an external one in `docker-compose.yml`):

```env
# Required for AI Features
GEMINI_API_KEY=your_api_key_here

# Optional: For Vertex AI usage (if not using API Key)
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_CLOUD_LOCATION=us-central1
```

### 3. Run with Docker
Start the entire suite with a single command:

```bash
docker-compose up --build
```

Access the application at: **http://localhost:8080**

### 4. Stop the Application
```bash
docker-compose down
```

---

## 📂 Project Structure

```
NexusAI/
├── Director/                 # Movie Maker Service
├── VideoGeneration/          # Veo Integration Service
├── ImageGeneration/          # Imagen Service
├── DocumentsSummarization/   # Doc Analysis Service
├── YoutubeTranscript/        # YouTube Tools
├── Chat/                     # Chatbot Service
├── frontend/                 # React Dashboard
├── Generated_Video/          # Shared Volume for outputs
├── Dockerfile                # Unified container definition
├── docker-compose.yml        # Orchestration config
├── nginx.conf                # Routing configuration
└── start.sh                  # Container entrypoint
```

## 🗺️ Roadmap

*   [ ] **UI Improvements**: Enhanced aesthetics and user experience.
*   [ ] **Prompt Presets**: Pre-defined styles for quicker creation.
*   [ ] **User Authentication**: Secure login and user management.
*   [ ] **Cloud Deployment**: Support for Render, AWS, GCP, Azure.
*   [ ] **Advanced Video Features**: Motion control, masking, and camera path customization.

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
