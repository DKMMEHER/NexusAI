# Integration Tests for NexusAI

This directory contains comprehensive integration tests for all NexusAI services.

## Overview

Integration tests verify that services work together correctly in a real-world scenario. Unlike unit tests that test individual components in isolation, integration tests ensure:

- Services can communicate with each other
- Database operations work correctly
- External API integrations function properly
- Error handling works across service boundaries
- Performance meets requirements

## Test Files

### 1. `test_image_generation_integration.py`
Tests for the Image Generation service:
- ✅ Full image generation workflow
- ✅ Different models (imagen-3.0-generate-001, imagen-3.0-fast-generate-001)
- ✅ Different aspect ratios (1:1, 16:9, 9:16, 4:3, 3:4)
- ✅ Safety filter levels
- ✅ Error handling (missing/empty prompts)
- ✅ Concurrent requests
- ✅ Database integration
- ✅ Performance testing

### 2. `test_chat_integration.py`
Tests for the Chat service:
- ✅ Simple chat interactions
- ✅ Conversation history management
- ✅ Tool integration (Google Search, Code Execution)
- ✅ Multiple tools simultaneously
- ✅ Different Gemini models
- ✅ Response cleaning (triple quotes removal)
- ✅ Database integration
- ✅ Error handling (empty messages, invalid history)
- ✅ Concurrent chat sessions
- ✅ Long conversation histories
- ✅ Performance testing

### 3. `test_director_integration.py`
Tests for the Director service (Video Creation):
- ✅ New movie job creation
- ✅ Movie creation with existing scenes (retake/edit flow)
- ✅ Script generation workflow
- ✅ Script approval process
- ✅ Movie status tracking
- ✅ User jobs retrieval
- ✅ External job saving (from TextToVideo)
- ✅ Database integration
- ✅ Authorization checks
- ✅ Concurrent movie creation
- ✅ Performance testing

### 4. `test_video_generation_integration.py`
Tests for the Video Generation service:
- ✅ Text-to-video workflow
- ✅ Image-to-video workflow
- ✅ Video extension workflow
- ✅ Status polling
- ✅ Save local workflow
- ✅ Different models (veo-3.1, veo-3.1-fast-generate-preview)
- ✅ Different durations (4s, 8s)
- ✅ Different resolutions (720p, 1080p)
- ✅ Different aspect ratios (16:9, 9:16, 1:1)
- ✅ Error handling (missing prompt, invalid duration, invalid operation)
- ✅ Concurrent requests
- ✅ Performance testing

### 5. `test_document_summarization_integration.py`
Tests for the Document Summarization service:
- ✅ Text summarization workflow
- ✅ PDF document summarization
- ✅ DOCX document summarization
- ✅ TXT file summarization
- ✅ Different Gemini models
- ✅ Very long documents
- ✅ Short documents
- ✅ Error handling (empty text, unsupported files, corrupted files)
- ✅ Database integration
- ✅ Concurrent requests
- ✅ Performance testing
- ✅ Summary quality checks

### 6. `test_youtube_transcript_integration.py`
Tests for the YouTube Transcript service:
- ✅ Transcript extraction workflow
- ✅ Transcript summarization
- ✅ Different YouTube URL formats
- ✅ Language-specific transcripts
- ✅ Transcripts with timestamps
- ✅ Error handling (invalid URL, video not found, no transcript, language unavailable)
- ✅ Database integration
- ✅ Long video transcripts
- ✅ Concurrent requests
- ✅ Performance testing
- ✅ Transcript formatting

### 7. `test_integration_deployment.py`
Tests for deployed environment:
- ✅ Gateway health checks
- ✅ Backend services health (via Nginx routing)
- ✅ Real API end-to-end tests (optional, requires API keys)
- ✅ Request validation and security
- ✅ CORS headers

## Running the Tests

### Run All Integration Tests
```bash
pytest tests/integration -v
```

### Run Specific Test File
```bash
pytest tests/integration/test_image_generation_integration.py -v
pytest tests/integration/test_chat_integration.py -v
pytest tests/integration/test_director_integration.py -v
pytest tests/integration/test_video_generation_integration.py -v
pytest tests/integration/test_document_summarization_integration.py -v
pytest tests/integration/test_youtube_transcript_integration.py -v
pytest tests/integration/test_integration_deployment.py -v
```

### Run Specific Test Class
```bash
pytest tests/integration/test_image_generation_integration.py::TestImageGenerationIntegration -v
```

### Run Specific Test Method
```bash
pytest tests/integration/test_chat_integration.py::TestChatIntegration::test_simple_chat_workflow -v
```

### Run with Coverage
```bash
pytest tests/integration --cov=. --cov-report=html
```

### Run with Detailed Output
```bash
pytest tests/integration -vv --tb=long
```

## Prerequisites

### For Local Testing (Mocked APIs)
- Python 3.8+
- All dependencies installed: `pip install -r requirements.txt`
- No API keys required (tests use mocks)

### For Real API Testing
- Set environment variables:
  ```bash
  export GEMINI_API_KEY=your_key_here
  export GOOGLE_CLOUD_PROJECT=your_project_id
  ```
- Services running (for deployment tests):
  ```bash
  docker-compose up
  # OR
  ./start_all.ps1
  ```

## Test Structure

Each integration test follows this pattern:

```python
class TestServiceIntegration:
    def test_health_endpoint(self):
        """Verify service is running"""
        
    def test_main_workflow(self, mock_api):
        """Test the primary use case"""
        
    def test_edge_cases(self):
        """Test boundary conditions"""
        
    def test_error_handling(self):
        """Test failure scenarios"""
        
    def test_database_integration(self):
        """Verify database operations"""
        
    def test_performance(self):
        """Ensure acceptable response times"""
```

## Mocking Strategy

Integration tests use mocks for external APIs to:
- ✅ Avoid API costs during testing
- ✅ Ensure consistent test results
- ✅ Test error scenarios that are hard to reproduce
- ✅ Speed up test execution

Mocked components:
- Gemini API (`genai`)
- Imagen API (`imagen`)
- Veo API (`client`)
- YouTube Transcript API (`YouTubeTranscriptApi`)
- Database (`db`)
- Storage (`storage`)

## CI/CD Integration

To integrate these tests into your CI/CD pipeline:

### Cloud Build (cloudbuild.yaml)
```yaml
steps:
  - name: 'python:3.11'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        pip install -r requirements.txt
        pytest tests/integration -v --tb=short
```

### GitHub Actions
```yaml
- name: Run Integration Tests
  run: |
    pip install -r requirements.txt
    pytest tests/integration -v
```

## Best Practices

1. **Isolation**: Each test should be independent and not rely on other tests
2. **Cleanup**: Use fixtures to clean up test data after tests
3. **Mocking**: Mock external APIs to avoid costs and ensure reliability
4. **Assertions**: Use clear, specific assertions with helpful error messages
5. **Documentation**: Document what each test is verifying
6. **Performance**: Set reasonable timeout expectations
7. **Error Cases**: Test both success and failure scenarios

## Troubleshooting

### Tests Fail with "Connection Refused"
- Ensure services are running: `docker-compose up` or `./start_all.ps1`
- Check port availability (8080, 8001-8006)

### Tests Fail with "Module Not Found"
- Install dependencies: `pip install -r requirements.txt`
- Ensure you're in the project root directory

### Tests Fail with "API Key Error"
- For mocked tests: This shouldn't happen (check fixtures)
- For real API tests: Set `GEMINI_API_KEY` environment variable

### Slow Test Execution
- Use mocked tests for development
- Run specific test files instead of all tests
- Use `-k` flag to run specific tests: `pytest -k "test_simple"`

## Contributing

When adding new features:
1. Add corresponding integration tests
2. Follow the existing test structure
3. Use appropriate mocks for external APIs
4. Document what the test verifies
5. Ensure tests pass before submitting PR

## Test Coverage Goals

- **Unit Tests**: 80%+ code coverage
- **Integration Tests**: Cover all major workflows
- **E2E Tests**: Cover critical user journeys

## Next Steps

1. ✅ Run all integration tests: `pytest tests/integration -v`
2. ✅ Check coverage: `pytest tests/integration --cov=. --cov-report=html`
3. ✅ Add to CI/CD pipeline
4. ✅ Monitor test execution times
5. ✅ Add more edge case tests as needed

## Contact

For questions or issues with integration tests, please open an issue or contact the development team.
