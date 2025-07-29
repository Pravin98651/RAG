#!/usr/bin/env python3
"""
FastAPI Backend for Insurance Policy RAG System with Groq LLM Integration
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
import httpx
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from loguru import logger
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our RAG system
from insurance_rag_no_spacy import InsuranceRAGSystem

# Configuration from environment variables
API_TOKEN = os.getenv("API_TOKEN", "c94dfd1ae12b50eb392cd6d1ef5f4578c561f54bacf6cd6849236cbfc2e8b673")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

# Validate required environment variables
if not GROQ_API_KEY:
    logger.warning("GROQ_API_KEY not found in environment variables. Please set it in .env file")

# Initialize FastAPI app
app = FastAPI(
    title="Insurance Policy RAG API",
    description="Retrieval-Augmented Generation API for Insurance Policy Documents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize RAG system
rag_system = None

# Pydantic models
class RunRequest(BaseModel):
    documents: str = Field(..., description="URL to the policy document")
    questions: List[str] = Field(..., description="List of questions to answer")

class RunResponse(BaseModel):
    answers: List[str] = Field(..., description="List of answers to the questions")

class HealthResponse(BaseModel):
    status: str = Field(..., description="API status")
    rag_system_ready: bool = Field(..., description="RAG system status")
    groq_ready: bool = Field(..., description="Groq API status")
    vector_db_ready: bool = Field(..., description="Vector database status")

# Authentication dependency
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API token"
        )
    return credentials.credentials

# Initialize RAG system with existing vector database
def initialize_rag_system():
    """Initialize the RAG system using existing vector database"""
    global rag_system
    try:
        logger.info("Initializing RAG system with existing vector database...")
        
        # Check if vector database exists
        vector_db_path = Path("./vector_db")
        if not vector_db_path.exists():
            logger.error("Vector database not found at ./vector_db")
            return False
        
        # Initialize RAG system with existing data
        rag_system = InsuranceRAGSystem("./Training_pdfs")
        
        # Check if vector database has data
        if not rag_system.has_data():
            logger.warning("Vector database appears to be empty or corrupted")
            logger.info("Attempting to process PDFs to populate vector database...")
            
            # Try to process PDFs if vector database is empty
            pdf_files = list(Path("./Training_pdfs").glob("*.pdf"))
            if pdf_files:
                logger.info(f"Found {len(pdf_files)} PDF files to process")
                rag_system.process_pdfs()
                
                # Check again after processing
                if not rag_system.has_data():
                    logger.error("Failed to populate vector database")
                    return False
            else:
                logger.error("No PDF files found in Training_pdfs directory")
                return False
        
        # Get statistics to verify the system is working
        stats = rag_system.get_statistics()
        logger.info(f"RAG system ready. Total chunks: {stats['total_chunks']}")
        
        return True
    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {e}")
        return False

# Groq API client
class GroqClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = GROQ_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_answer(self, question: str, context: str) -> str:
        """Generate answer using Groq LLM"""
        if not self.api_key:
            return "Error: Groq API key not configured. Please set GROQ_API_KEY in .env file."
        
        try:
            prompt = f"""You are an expert insurance policy analyst. Based on the following context from insurance policy documents, answer the question accurately and concisely.

Context:
{context}

Question: {question}

Answer:"""
            
            payload = {
                "model": "llama3-8b-8192",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 500
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"].strip()
                else:
                    logger.error(f"Groq API error: {response.status_code} - {response.text}")
                    return f"Error generating answer: {response.status_code}"
                    
        except Exception as e:
            logger.error(f"Error calling Groq API: {e}")
            return f"Error generating answer: {str(e)}"

# Initialize Groq client
groq_client = GroqClient(GROQ_API_KEY)

@app.on_event("startup")
async def startup_event():
    """Initialize systems on startup"""
    logger.info("Starting Insurance Policy RAG API...")
    
    # Initialize RAG system
    rag_ready = initialize_rag_system()
    if not rag_ready:
        logger.error("Failed to initialize RAG system")
    
    # Test Groq connection if API key is available
    if GROQ_API_KEY:
        try:
            test_response = await groq_client.generate_answer(
                "Test question", 
                "Test context"
            )
            logger.info("Groq API connection successful")
        except Exception as e:
            logger.error(f"Groq API connection failed: {e}")
    else:
        logger.warning("Groq API key not configured")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    global rag_system
    
    rag_ready = rag_system is not None
    groq_ready = GROQ_API_KEY is not None
    vector_db_ready = Path("./vector_db").exists()
    
    status_value = "healthy" if rag_ready and vector_db_ready else "degraded"
    
    return HealthResponse(
        status=status_value,
        rag_system_ready=rag_ready,
        groq_ready=groq_ready,
        vector_db_ready=vector_db_ready
    )

@app.post("/api/v1/hackrx/run", response_model=RunResponse)
async def run_submission(
    request: RunRequest,
    token: str = Depends(verify_token)
):
    """
    Process insurance policy questions using RAG + Groq LLM
    """
    global rag_system
    
    if rag_system is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG system not initialized"
        )
    
    if not GROQ_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Groq API key not configured"
        )
    
    try:
        logger.info(f"Processing {len(request.questions)} questions")
        
        answers = []
        
        for i, question in enumerate(request.questions):
            logger.info(f"Processing question {i+1}: {question}")
            
            # Get relevant context from RAG system
            results = rag_system.query(question, top_k=3)
            
            if not results:
                answers.append("No relevant information found in the policy documents.")
                continue
            
            # Combine context from top results
            context_parts = []
            for result in results:
                context_parts.append(f"Source: {result['metadata']['source_file']}")
                context_parts.append(f"Section: {result['metadata']['section_type']}")
                context_parts.append(f"Content: {result['content']}")
                context_parts.append("---")
            
            context = "\n".join(context_parts)
            
            # Generate answer using Groq
            answer = await groq_client.generate_answer(question, context)
            answers.append(answer)
            
            logger.info(f"Generated answer for question {i+1}")
        
        return RunResponse(answers=answers)
        
    except Exception as e:
        logger.error(f"Error processing submission: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing submission: {str(e)}"
        )

@app.get("/api/v1/stats")
async def get_stats(token: str = Depends(verify_token)):
    """Get RAG system statistics"""
    global rag_system
    
    if rag_system is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG system not initialized"
        )
    
    try:
        stats = rag_system.get_statistics()
        return {
            "total_documents": stats['total_documents'],
            "total_chunks": stats['total_chunks'],
            "vector_db_size": stats['vector_db_size'],
            "processed_files": stats['processed_files']
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting statistics: {str(e)}"
        )

@app.post("/api/v1/query")
async def query_rag(
    question: str,
    top_k: int = 5,
    token: str = Depends(verify_token)
):
    """Query the RAG system directly"""
    global rag_system
    
    if rag_system is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG system not initialized"
        )
    
    try:
        results = rag_system.query(question, top_k=top_k)
        
        formatted_results = []
        for result in results:
            formatted_results.append({
                "content": result['content'],
                "metadata": result['metadata'],
                "similarity_score": result['similarity_score']
            })
        
        return {
            "question": question,
            "results": formatted_results,
            "total_results": len(formatted_results)
        }
        
    except Exception as e:
        logger.error(f"Error querying RAG system: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error querying RAG system: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(
        "api_backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 