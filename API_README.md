# Insurance Policy RAG API Documentation

## Overview

The Insurance Policy RAG API is a FastAPI-based backend that combines Retrieval-Augmented Generation (RAG) with Groq LLM to provide accurate answers to insurance policy questions. The system processes insurance policy documents and uses semantic search to find relevant information, then generates comprehensive answers using Groq's LLM.

## Features

- ✅ **RAG Integration**: Combines semantic search with LLM generation
- ✅ **Groq LLM**: Fast and accurate answer generation
- ✅ **Authentication**: Bearer token authentication
- ✅ **Health Monitoring**: System health and status endpoints
- ✅ **Comprehensive Logging**: Detailed request/response logging
- ✅ **CORS Support**: Cross-origin resource sharing enabled
- ✅ **Async Processing**: Non-blocking request handling

## Quick Start

### 1. Setup Environment

```bash
# Install dependencies
pip install -r requirements_api.txt

# Setup environment
python setup_api.py
```

### 2. Configure API Key

Edit the `.env` file and add your Groq API key:

```env
GROQ_API_KEY=your-actual-groq-api-key-here
```

### 3. Start the Server

```bash
python api_backend.py
```

The API will be available at: `http://localhost:8000`

### 4. Test the API

```bash
python test_api_client.py
```

## API Endpoints

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication
All endpoints require Bearer token authentication:
```
Authorization: Bearer c94dfd1ae12b50eb392cd6d1ef5f4578c561f54bacf6cd6849236cbfc2e8b673
```

### Endpoints

#### 1. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "rag_system_ready": true,
  "groq_ready": true
}
```

#### 2. Main Submission Endpoint
```http
POST /hackrx/run
```

**Request Body:**
```json
{
  "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
  "questions": [
    "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
    "What is the waiting period for pre-existing diseases (PED) to be covered?",
    "Does this policy cover maternity expenses, and what are the conditions?"
  ]
}
```

**Response:**
```json
{
  "answers": [
    "A grace period of thirty days is provided for premium payment after the due date to renew or continue the policy without losing continuity benefits.",
    "There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre-existing diseases and their direct complications to be covered.",
    "Yes, the policy covers maternity expenses, including childbirth and lawful medical termination of pregnancy. To be eligible, the female insured person must have been continuously covered for at least 24 months."
  ]
}
```

#### 3. System Statistics
```http
GET /stats
```

**Response:**
```json
{
  "total_documents": 6,
  "total_chunks": 1250,
  "vector_db_size": 1250,
  "processed_files": [
    "policy1.pdf",
    "policy2.pdf",
    "policy3.pdf"
  ]
}
```

#### 4. Direct RAG Query
```http
POST /query
```

**Request Body:**
```json
{
  "question": "What is the grace period for premium payment?",
  "top_k": 3
}
```

**Response:**
```json
{
  "question": "What is the grace period for premium payment?",
  "results": [
    {
      "content": "Grace period of thirty days is provided...",
      "metadata": {
        "source_file": "policy1.pdf",
        "section_type": "premium",
        "chunk_type": "text"
      },
      "similarity_score": 0.85
    }
  ],
  "total_results": 3
}
```

## Architecture

### Components

1. **RAG System** (`insurance_rag_no_spacy.py`)
   - PDF processing and text extraction
   - Semantic chunking and embedding
   - Vector database (ChromaDB)
   - Similarity search

2. **Groq LLM Integration**
   - Async HTTP client for Groq API
   - Context-aware prompt engineering
   - Error handling and retry logic

3. **FastAPI Backend**
   - RESTful API endpoints
   - Authentication middleware
   - CORS support
   - Request/response validation

### Data Flow

1. **Request Processing**
   ```
   Client Request → FastAPI → Authentication → RAG Query → Groq LLM → Response
   ```

2. **RAG Pipeline**
   ```
   Question → Embedding → Vector Search → Context Retrieval → LLM Generation → Answer
   ```

3. **Error Handling**
   ```
   Error → Logging → HTTP Status Code → Client Response
   ```

## Configuration

### Environment Variables

```env
# Groq API Configuration
GROQ_API_KEY=your-groq-api-key-here

# API Configuration
API_TOKEN=c94dfd1ae12b50eb392cd6d1ef5f4578c561f54bacf6cd6849236cbfc2e8b673

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

### RAG System Configuration

```python
# Chunking parameters
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50

# Embedding model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Vector database
VECTOR_DB_PATH = "./vector_db"
```

## Performance

### Expected Response Times

- **Health Check**: < 100ms
- **Statistics**: < 200ms
- **Direct Query**: < 500ms
- **Run Submission**: 2-5 seconds (depending on number of questions)

### System Requirements

- **CPU**: 4+ cores recommended
- **RAM**: 8GB+ recommended
- **Storage**: 2GB+ for vector database
- **Network**: Stable internet for Groq API

## Error Handling

### HTTP Status Codes

- `200`: Success
- `401`: Unauthorized (invalid token)
- `422`: Validation error
- `500`: Internal server error
- `503`: Service unavailable

### Common Error Responses

```json
{
  "detail": "Invalid API token"
}
```

```json
{
  "detail": "RAG system not initialized"
}
```

```json
{
  "detail": "Error generating answer: API rate limit exceeded"
}
```

## Monitoring and Logging

### Log Levels

- **INFO**: Normal operations
- **WARNING**: Non-critical issues
- **ERROR**: Critical errors
- **DEBUG**: Detailed debugging information

### Log Format

```
2024-01-15 10:30:45 | INFO | Processing 3 questions
2024-01-15 10:30:46 | INFO | Generated answer for question 1
2024-01-15 10:30:47 | ERROR | Groq API error: 429
```

## Development

### Running in Development Mode

```bash
python api_backend.py
```

### Running with Uvicorn

```bash
uvicorn api_backend:app --host 0.0.0.0 --port 8000 --reload
```

### API Documentation

Access interactive API documentation at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Testing

### Automated Tests

```bash
python test_api_client.py
```

### Manual Testing

```bash
# Health check
curl -X GET "http://localhost:8000/health"

# Run submission
curl -X POST "http://localhost:8000/api/v1/hackrx/run" \
  -H "Authorization: Bearer c94dfd1ae12b50eb392cd6d1ef5f4578c561f54bacf6cd6849236cbfc2e8b673" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": "https://example.com/policy.pdf",
    "questions": ["What is the grace period?"]
  }'
```

## Troubleshooting

### Common Issues

1. **RAG System Not Initialized**
   - Check if PDF files exist in `Training_pdfs/`
   - Verify vector database permissions

2. **Groq API Errors**
   - Verify API key is correct
   - Check internet connection
   - Monitor rate limits

3. **Authentication Errors**
   - Verify Bearer token is correct
   - Check token format in request headers

4. **Performance Issues**
   - Monitor system resources
   - Check vector database size
   - Optimize chunk size if needed

### Debug Mode

Enable debug logging by setting environment variable:
```bash
export LOG_LEVEL=DEBUG
```

## Security

### Authentication
- Bearer token authentication required
- Token validation on all protected endpoints
- Secure token storage in environment variables

### CORS
- Configured for cross-origin requests
- Customizable origins in production

### Input Validation
- Pydantic models for request validation
- SQL injection protection
- XSS protection through proper encoding

## Production Deployment

### Docker Support

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements_api.txt .
RUN pip install -r requirements_api.txt

COPY . .
EXPOSE 8000

CMD ["python", "api_backend.py"]
```

### Environment Variables

```env
# Production settings
GROQ_API_KEY=your-production-groq-key
API_TOKEN=your-production-api-token
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
```

### Reverse Proxy

Configure nginx or similar for production:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Support

For issues and questions:
1. Check the logs for error details
2. Verify API configuration
3. Test with the provided test client
4. Review this documentation

## License

This project is licensed under the MIT License. 