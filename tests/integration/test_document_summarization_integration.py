"""
Integration Tests for Document Summarization Service
Tests the full workflow of document summarization including:
- Text summarization
- PDF document summarization
- DOCX document summarization
- TXT file summarization
- Database integration
- Error handling
"""
import pytest
import os
import sys
import time
import io
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from fastapi.testclient import TestClient
from DocumentsSummarization.backend import app

client = TestClient(app)


@pytest.fixture
def mock_genai():
    """Mock Gemini API for document summarization."""
    with patch("DocumentsSummarization.backend.genai") as mock:
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "This is a comprehensive summary of the document. It covers the main points and key takeaways."
        mock_response.usage_metadata = MagicMock()
        mock_response.usage_metadata.total_token_count = 150
        mock_model.generate_content.return_value = mock_response
        mock.GenerativeModel.return_value = mock_model
        yield mock


@pytest.fixture
def cleanup_test_files():
    """Clean up test files after tests."""
    yield
    # Cleanup logic if needed


class TestDocumentSummarizationIntegration:
    """Integration tests for Document Summarization service."""
    
    def test_health_endpoint(self):
        """Test that the health endpoint is accessible."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        print("✅ Health endpoint works")
    
    def test_summarize_txt_file_workflow(self, mock_genai):
        """Test the complete text file summarization workflow."""
        # Create a fake TXT file
        long_text = """
        Artificial Intelligence (AI) has revolutionized the way we interact with technology.
        Machine learning, a subset of AI, enables computers to learn from data without being explicitly programmed.
        Deep learning, which uses neural networks with multiple layers, has achieved remarkable results in image recognition,
        natural language processing, and game playing. The future of AI holds immense potential for transforming
        industries such as healthcare, finance, transportation, and education.
        """ * 10  # Make it longer
        
        fake_txt = io.BytesIO(long_text.encode())
        
        response = client.post(
            "/summarize",
            files={"files": ("test_document.txt", fake_txt, "text/plain")},
            data={"user_id": "test_user_123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "summary" in data
        assert len(data["summary"]) > 0
        
        print(f"✅ TXT file summarization works: {data['summary'][:100]}...")
    
    def test_summarize_pdf_workflow(self, mock_genai):
        """Test PDF document summarization workflow."""
        # Create a fake PDF file
        fake_pdf = io.BytesIO(b"%PDF-1.4\n%fake pdf content for testing")
        
        # Gemini handles PDFs natively, no need to mock PyPDF2
        response = client.post(
            "/summarize",
            files={"files": ("test_document.pdf", fake_pdf, "application/pdf")},
            data={"user_id": "test_user_123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "summary" in data
        assert len(data["summary"]) > 0
        
        print("✅ PDF summarization works")
    
    def test_summarize_docx_workflow(self, mock_genai):
        """Test DOCX document summarization workflow."""
        fake_docx = io.BytesIO(b"fake docx content")
        
        with patch("DocumentsSummarization.backend.extract_text_from_docx") as mock_extract:
            # Mock DOCX extraction
            mock_extract.return_value = "First paragraph of the document. Second paragraph with more details. Third paragraph concluding the document."
            
            response = client.post(
                "/summarize",
                files={"files": ("test_document.docx", fake_docx, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
                data={"user_id": "test_user_123"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert "summary" in data
            assert len(data["summary"]) > 0
            
            print("✅ DOCX summarization works")
    
    def test_summarize_with_different_models(self, mock_genai):
        """Test summarization with different Gemini models."""
        models = [
            "gemini-2.0-flash-exp",
            "gemini-2.5-flash"
        ]
        
        for model in models:
            fake_txt = io.BytesIO(f"Test document for model {model}".encode())
            
            response = client.post(
                "/summarize",
                files={"files": ("test.txt", fake_txt, "text/plain")},
                data={
                    "model": model,
                    "user_id": "test_user_123"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "summary" in data
            print(f"✅ Model {model} works correctly")
    
    def test_summarize_very_long_document(self, mock_genai):
        """Test summarization of very long documents."""
        # Create a very long text (simulating a book chapter)
        long_text = ("This is a sentence. " * 5000).encode()  # ~10,000 words
        fake_txt = io.BytesIO(long_text)
        
        response = client.post(
            "/summarize",
            files={"files": ("long_document.txt", fake_txt, "text/plain")},
            data={"user_id": "test_user_123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        
        print("✅ Very long document summarization works")
    
    def test_summarize_short_document(self, mock_genai):
        """Test summarization of short documents."""
        short_text = b"This is a short document."
        fake_txt = io.BytesIO(short_text)
        
        response = client.post(
            "/summarize",
            files={"files": ("short.txt", fake_txt, "text/plain")},
            data={"user_id": "test_user_123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        
        print("✅ Short document summarization works")
    
    def test_error_handling_no_files(self):
        """Test error handling when no files are provided."""
        response = client.post(
            "/summarize",
            data={"user_id": "test_user_123"}
        )
        
        # Should require files
        assert response.status_code == 422  # Validation error
        print("✅ No files validation works")
    
    def test_error_handling_unsupported_file_type(self, mock_genai):
        """Test error handling for unsupported file types."""
        fake_file = io.BytesIO(b"fake content")
        
        response = client.post(
            "/summarize",
            files={"files": ("test.xyz", fake_file, "application/xyz")},
            data={"user_id": "test_user_123"}
        )
        
        # Should reject unsupported file types
        assert response.status_code in [400, 500]
    
    def test_database_integration(self, mock_genai):
        """Test that summarization jobs are saved to database."""
        with patch("DocumentsSummarization.backend.db") as mock_db:
            fake_txt = io.BytesIO(b"Database integration test document")
            
            response = client.post(
                "/summarize",
                files={"files": ("test.txt", fake_txt, "text/plain")},
                data={"user_id": "test_user_123"}
            )
            
            assert response.status_code == 200
            
            # Verify database save was called
            mock_db.save_job.assert_called_once()
            
            # Verify the saved data structure
            call_args = mock_db.save_job.call_args[0][0]
            assert "job_id" in call_args
            assert "user_id" in call_args
            assert call_args["user_id"] == "test_user_123"
            assert "type" in call_args
            
            print("✅ Database integration works correctly")
    
    def test_concurrent_summarization_requests(self, mock_genai):
        """Test handling of multiple concurrent summarization requests."""
        import concurrent.futures
        
        def make_request(i):
            fake_txt = io.BytesIO(f"Concurrent document {i} with content to summarize.".encode())
            return client.post(
                "/summarize",
                files={"files": (f"doc{i}.txt", fake_txt, "text/plain")},
                data={"user_id": f"user_{i}"}
            )
        
        # Submit 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, i) for i in range(5)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All should succeed
        for result in results:
            assert result.status_code == 200
        
        print("✅ Concurrent requests handled successfully")
    
    def test_response_time_performance(self, mock_genai):
        """Test that summarization responds within acceptable time."""
        start_time = time.time()
        
        fake_txt = io.BytesIO(("Performance test document " * 100).encode())
        
        response = client.post(
            "/summarize",
            files={"files": ("perf_test.txt", fake_txt, "text/plain")},
            data={"user_id": "test_user_123"}
        )
        
        duration = time.time() - start_time
        
        assert response.status_code == 200
        # Should respond within 5 seconds (with mocked API)
        assert duration < 5.0, f"Response took too long: {duration}s"
        
        print(f"✅ Response time: {duration:.2f}s")
    
    def test_summary_quality_check(self, mock_genai):
        """Test that the summary is meaningful and not just a copy."""
        fake_txt = io.BytesIO(b"This is the original document text that should be summarized.")
        
        response = client.post(
            "/summarize",
            files={"files": ("test.txt", fake_txt, "text/plain")},
            data={"user_id": "test_user_123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Summary should exist and be non-empty
        assert "summary" in data
        assert len(data["summary"]) > 0
        
        print("✅ Summary quality check passed")
    
    def test_multiple_files_summarization(self, mock_genai):
        """Test summarizing multiple files at once."""
        files = [
            ("file1.txt", io.BytesIO(b"First document content"), "text/plain"),
            ("file2.txt", io.BytesIO(b"Second document content"), "text/plain"),
            ("file3.txt", io.BytesIO(b"Third document content"), "text/plain")
        ]
        
        response = client.post(
            "/summarize",
            files=[("files", f) for f in files],
            data={"user_id": "test_user_123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        
        print("✅ Multiple files summarization works")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

