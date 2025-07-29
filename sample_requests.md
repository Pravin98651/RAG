# Sample API Requests for Testing

## 1. Health Check
```bash
curl -X GET "http://localhost:8000/health"
```

## 2. Get Statistics
```bash
curl -X GET "http://localhost:8000/api/v1/stats" \
  -H "Authorization: Bearer c94dfd1ae12b50eb392cd6d1ef5f4578c561f54bacf6cd6849236cbfc2e8b673"
```

## 3. Direct RAG Query (without LLM)
```bash
curl -X POST "http://localhost:8000/api/v1/query?question=What is the grace period for premium payment?&top_k=3" \
  -H "Authorization: Bearer c94dfd1ae12b50eb392cd6d1ef5f4578c561f54bacf6cd6849236cbfc2e8b673"
```

## 4. LLM Integration Test (Main Endpoint)
```bash
curl -X POST "http://localhost:8000/api/v1/hackrx/run" \
  -H "Authorization: Bearer c94dfd1ae12b50eb392cd6d1ef5f4578c561f54bacf6cd6849236cbfc2e8b673" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
      "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
      "What is the waiting period for pre-existing diseases (PED) to be covered?",
      "Does this policy cover maternity expenses, and what are the conditions?"
    ]
  }'
```

## 5. Simple Question Test
```bash
curl -X POST "http://localhost:8000/api/v1/hackrx/run" \
  -H "Authorization: Bearer c94dfd1ae12b50eb392cd6d1ef5f4578c561f54bacf6cd6849236cbfc2e8b673" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": "https://example.com/policy.pdf",
    "questions": [
      "What is the grace period for premium payment?"
    ]
  }'
```

## 6. PowerShell Examples

### Health Check
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET
```

### Get Statistics
```powershell
$headers = @{
    "Authorization" = "Bearer c94dfd1ae12b50eb392cd6d1ef5f4578c561f54bacf6cd6849236cbfc2e8b673"
}
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/stats" -Method GET -Headers $headers
```

### LLM Integration Test
```powershell
$headers = @{
    "Authorization" = "Bearer c94dfd1ae12b50eb392cd6d1ef5f4578c561f54bacf6cd6849236cbfc2e8b673"
    "Content-Type" = "application/json"
}

$body = @{
    documents = "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D"
    questions = @(
        "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
        "What is the waiting period for pre-existing diseases (PED) to be covered?",
        "Does this policy cover maternity expenses, and what are the conditions?"
    )
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/hackrx/run" -Method POST -Headers $headers -Body $body
```

## 7. Python Requests Examples

### Health Check
```python
import requests

response = requests.get("http://localhost:8000/health")
print(response.json())
```

### LLM Integration Test
```python
import requests
import json

headers = {
    "Authorization": "Bearer c94dfd1ae12b50eb392cd6d1ef5f4578c561f54bacf6cd6849236cbfc2e8b673",
    "Content-Type": "application/json"
}

payload = {
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
        "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
        "What is the waiting period for pre-existing diseases (PED) to be covered?",
        "Does this policy cover maternity expenses, and what are the conditions?"
    ]
}

response = requests.post(
    "http://localhost:8000/api/v1/hackrx/run",
    headers=headers,
    json=payload
)

print(json.dumps(response.json(), indent=2))
```

## Expected Responses

### Health Check Response
```json
{
  "status": "healthy",
  "rag_system_ready": true,
  "groq_ready": true,
  "vector_db_ready": true
}
```

### Stats Response
```json
{
  "total_documents": 6,
  "total_chunks": 2808,
  "vector_db_size": 2808,
  "processed_files": [
    "ICIHLIP22012V012223.pdf",
    "CHOTGDP23004V012223.pdf",
    "EDLHLGA23009V012223.pdf",
    "Arogya Sanjeevani Policy - CIN - U10200WB1906GOI001713 1.pdf",
    "BAJHLIP23020V012223.pdf",
    "HDFHLIP23024V072223.pdf"
  ]
}
```

### LLM Integration Response
```json
{
  "answers": [
    "A grace period of thirty days is provided for premium payment after the due date to renew or continue the policy without losing continuity benefits.",
    "There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre-existing diseases and their direct complications to be covered.",
    "Yes, the policy covers maternity expenses, including childbirth and lawful medical termination of pregnancy. To be eligible, the female insured person must have been continuously covered for at least 24 months."
  ]
}
```

## Testing Steps

1. **Start the server**: `python api_backend.py`
2. **Test health**: Use the health check request
3. **Test stats**: Use the stats request
4. **Test direct query**: Use the direct query request
5. **Test LLM integration**: Use the LLM integration request
6. **Verify responses**: Check that all responses are as expected

## Troubleshooting

- If health check fails: Server is not running
- If stats fail: Authentication issue or RAG system not initialized
- If LLM integration fails: Check Groq API key in .env file
- If direct query fails: Vector database issue 