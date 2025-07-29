import os
import re
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime

# PDF Processing
import pypdf2
import pdfplumber

# NLP and ML
import nltk
from sentence_transformers import SentenceTransformer
import spacy

# Vector Database
import chromadb
from chromadb.config import Settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Download spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy model...")
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

class SimpleInsuranceChunker:
    """
    Simplified chunking strategy for insurance policy documents
    """
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Insurance-specific keywords for semantic chunking
        self.section_keywords = [
            'policy', 'coverage', 'exclusions', 'terms', 'conditions',
            'premium', 'deductible', 'claim', 'benefits', 'limitations',
            'definitions', 'general conditions', 'special conditions',
            'schedule', 'endorsement', 'rider', 'clause', 'provision'
        ]
    
    def extract_text_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Extract text from PDF with basic structure"""
        text_content = []
        tables = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Extract text
                    text = page.extract_text()
                    if text:
                        # Split into lines and process
                        lines = text.split('\n')
                        for line_num, line in enumerate(lines):
                            line = line.strip()
                            if line:
                                # Detect section headers
                                is_header = self._is_section_header(line)
                                text_content.append({
                                    'page': page_num + 1,
                                    'line': line_num + 1,
                                    'text': line,
                                    'is_header': is_header,
                                    'section_type': self._classify_section(line)
                                })
                    
                    # Extract tables (simplified)
                    page_tables = page.extract_tables()
                    for table_num, table in enumerate(page_tables):
                        if table and len(table) > 1:
                            table_text = '\n'.join(['\t'.join(row) for row in table if any(cell for cell in row)])
                            tables.append({
                                'page': page_num + 1,
                                'table_index': table_num,
                                'text': table_text
                            })
                            
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
        
        return {
            'text_content': text_content,
            'tables': tables,
            'total_pages': len(pdf.pages) if 'pdf' in locals() else 0
        }
    
    def _is_section_header(self, text: str) -> bool:
        """Detect if text is a section header"""
        # Check for numbered sections
        if re.match(r'^\d+\.?\d*\s+[A-Z]', text):
            return True
        
        # Check for all caps headers
        if text.isupper() and len(text) > 3 and len(text) < 100:
            return True
        
        # Check for insurance-specific keywords
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.section_keywords)
    
    def _classify_section(self, text: str) -> str:
        """Classify the type of section"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['coverage', 'cover', 'insured']):
            return 'coverage'
        elif any(word in text_lower for word in ['exclusion', 'excluded', 'not covered']):
            return 'exclusion'
        elif any(word in text_lower for word in ['definition', 'defined', 'means']):
            return 'definition'
        elif any(word in text_lower for word in ['condition', 'term', 'provision']):
            return 'condition'
        elif any(word in text_lower for word in ['premium', 'payment', 'cost']):
            return 'premium'
        elif any(word in text_lower for word in ['claim', 'claimant', 'notification']):
            return 'claim'
        elif any(word in text_lower for word in ['schedule', 'table', 'summary']):
            return 'schedule'
        else:
            return 'general'
    
    def create_chunks(self, extracted_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create chunks from extracted data"""
        chunks = []
        
        # Process text content
        text_content = extracted_data['text_content']
        current_chunk = []
        current_section = 'general'
        
        for item in text_content:
            text = item['text']
            
            # Start new chunk if section changes
            if item['is_header'] and item['section_type'] != current_section:
                if current_chunk:
                    chunks.append(self._create_chunk_metadata(current_chunk, current_section))
                current_chunk = [text]
                current_section = item['section_type']
            else:
                current_chunk.append(text)
            
            # Check if chunk size limit reached
            chunk_text = ' '.join(current_chunk)
            if len(chunk_text.split()) > self.chunk_size:
                # Split at sentence boundaries
                sentences = self._split_into_sentences(chunk_text)
                temp_chunk = []
                
                for sentence in sentences:
                    temp_chunk.append(sentence)
                    temp_text = ' '.join(temp_chunk)
                    if len(temp_text.split()) > self.chunk_size:
                        if temp_chunk:
                            chunks.append(self._create_chunk_metadata(temp_chunk[:-1], current_section))
                        temp_chunk = [sentence]
                
                current_chunk = temp_chunk
        
        # Add remaining chunk
        if current_chunk:
            chunks.append(self._create_chunk_metadata(current_chunk, current_section))
        
        # Process tables as separate chunks
        for table in extracted_data['tables']:
            table_chunk = {
                'content': table['text'],
                'type': 'table',
                'metadata': {
                    'page': table['page'],
                    'table_index': table['table_index']
                }
            }
            chunks.append(table_chunk)
        
        return chunks
    
    def _create_chunk_metadata(self, text_list: List[str], section_type: str) -> Dict[str, Any]:
        """Create chunk with metadata"""
        content = ' '.join(text_list)
        return {
            'content': content,
            'type': 'text',
            'metadata': {
                'section_type': section_type,
                'word_count': len(content.split()),
                'char_count': len(content),
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using spaCy"""
        doc = nlp(text)
        return [sent.text.strip() for sent in doc.sents]

class SimpleInsuranceEmbedder:
    """
    Simplified embedding system for insurance policy documents
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        
        # Insurance-specific vocabulary
        self.insurance_terms = [
            'premium', 'deductible', 'coverage', 'exclusion', 'claim',
            'policyholder', 'beneficiary', 'endorsement', 'rider',
            'underwriting', 'actuary', 'indemnity', 'subrogation'
        ]
    
    def create_embeddings(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create embeddings for chunks"""
        enhanced_chunks = []
        
        for chunk in chunks:
            content = chunk['content']
            
            # Extract basic features
            features = self._extract_features(content)
            
            # Create embedding
            embedding = self.model.encode(content, convert_to_tensor=True)
            
            # Enhance chunk with features
            enhanced_chunk = {
                **chunk,
                'embedding': embedding.cpu().numpy(),
                'features': features,
                'semantic_score': self._calculate_semantic_score(content)
            }
            
            enhanced_chunks.append(enhanced_chunk)
        
        return enhanced_chunks
    
    def _extract_features(self, text: str) -> Dict[str, Any]:
        """Extract basic features from text"""
        text_lower = text.lower()
        
        # Count insurance terms
        term_counts = {term: text_lower.count(term) for term in self.insurance_terms}
        
        # Extract numerical values
        amounts = re.findall(r'\$[\d,]+(?:\.\d{2})?', text)
        percentages = re.findall(r'\d+(?:\.\d+)?%', text)
        dates = re.findall(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text)
        
        # Calculate text statistics
        words = text.split()
        sentences = text.split('.')
        
        return {
            'insurance_terms': term_counts,
            'amounts': amounts,
            'percentages': percentages,
            'dates': dates,
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_sentence_length': len(words) / len(sentences) if sentences else 0,
            'has_table_data': any(char.isdigit() for char in text),
            'has_legal_terms': any(term in text_lower for term in ['shall', 'must', 'required', 'obligation'])
        }
    
    def _calculate_semantic_score(self, text: str) -> float:
        """Calculate semantic relevance score"""
        text_lower = text.lower()
        
        # Base score from insurance terms
        term_score = sum(1 for term in self.insurance_terms if term in text_lower)
        
        # Boost for legal/contractual language
        legal_boost = sum(1 for word in ['shall', 'must', 'required', 'obligation', 'liability'] if word in text_lower)
        
        # Boost for numerical data
        numerical_boost = len(re.findall(r'\d+', text)) * 0.1
        
        # Normalize score
        total_score = (term_score + legal_boost + numerical_boost) / max(len(text.split()), 1)
        
        return min(total_score, 1.0)

class SimpleInsuranceRAGSystem:
    """
    Simplified RAG system for insurance policy documents
    """
    
    def __init__(self, pdf_directory: str, vector_db_path: str = "./vector_db"):
        self.pdf_directory = Path(pdf_directory)
        self.vector_db_path = Path(vector_db_path)
        self.vector_db_path.mkdir(exist_ok=True)
        
        # Initialize components
        self.chunker = SimpleInsuranceChunker()
        self.embedder = SimpleInsuranceEmbedder()
        
        # Initialize vector database
        self.client = chromadb.PersistentClient(path=str(self.vector_db_path))
        self.collection = self.client.get_or_create_collection(
            name="insurance_policies",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Cache for processed documents
        self.processed_docs = {}
    
    def process_pdfs(self) -> None:
        """Process all PDFs in the directory"""
        pdf_files = list(self.pdf_directory.glob("*.pdf"))
        
        for pdf_file in pdf_files:
            logger.info(f"Processing {pdf_file.name}")
            
            try:
                # Extract and chunk
                extracted_data = self.chunker.extract_text_from_pdf(str(pdf_file))
                chunks = self.chunker.create_chunks(extracted_data)
                
                # Create embeddings
                enhanced_chunks = self.embedder.create_embeddings(chunks)
                
                # Store in vector database
                self._store_chunks(enhanced_chunks, pdf_file.name)
                
                # Cache processed data
                self.processed_docs[pdf_file.name] = {
                    'chunks': enhanced_chunks,
                    'metadata': {
                        'file_path': str(pdf_file),
                        'file_size': pdf_file.stat().st_size,
                        'total_pages': extracted_data['total_pages'],
                        'total_chunks': len(enhanced_chunks),
                        'processed_at': datetime.now().isoformat()
                    }
                }
                
                logger.info(f"Successfully processed {pdf_file.name} - {len(enhanced_chunks)} chunks")
                
            except Exception as e:
                logger.error(f"Error processing {pdf_file.name}: {e}")
    
    def _store_chunks(self, chunks: List[Dict[str, Any]], source_file: str) -> None:
        """Store chunks in vector database"""
        for i, chunk in enumerate(chunks):
            # Prepare metadata
            metadata = {
                'source_file': source_file,
                'chunk_index': i,
                'chunk_type': chunk['type'],
                'section_type': chunk['metadata'].get('section_type', 'general'),
                'word_count': chunk['metadata'].get('word_count', 0),
                **chunk.get('features', {})
            }
            
            # Add to collection
            self.collection.add(
                embeddings=[chunk['embedding'].tolist()],
                documents=[chunk['content']],
                metadatas=[metadata],
                ids=[f"{source_file}_{i}"]
            )
    
    def query(self, question: str, top_k: int = 5, filter_metadata: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Query the RAG system"""
        # Create query embedding
        query_embedding = self.embedder.model.encode(question, convert_to_tensor=True)
        
        # Prepare where clause for filtering
        where_clause = None
        if filter_metadata:
            where_clause = filter_metadata
        
        # Search in vector database
        results = self.collection.query(
            query_embeddings=[query_embedding.cpu().numpy().tolist()],
            n_results=top_k,
            where=where_clause,
            include=['documents', 'metadatas', 'distances']
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'similarity_score': 1 - results['distances'][0][i],  # Convert distance to similarity
                'rank': i + 1
            })
        
        return formatted_results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics"""
        stats = {
            'total_documents': len(self.processed_docs),
            'total_chunks': sum(len(doc['chunks']) for doc in self.processed_docs.values()),
            'processed_files': list(self.processed_docs.keys()),
            'vector_db_size': len(self.collection.get()['ids']) if self.collection.count() > 0 else 0
        }
        
        # Add per-file statistics
        file_stats = {}
        for filename, data in self.processed_docs.items():
            file_stats[filename] = {
                'chunks': len(data['chunks']),
                'pages': data['metadata']['total_pages'],
                'file_size_mb': data['metadata']['file_size'] / (1024 * 1024)
            }
        
        stats['file_statistics'] = file_stats
        return stats

def main():
    """Main function to demonstrate the simplified RAG system"""
    # Initialize the RAG system
    rag_system = SimpleInsuranceRAGSystem("./Training_pdfs")
    
    # Process all PDFs
    print("Processing PDFs...")
    rag_system.process_pdfs()
    
    # Get statistics
    stats = rag_system.get_statistics()
    print(f"\nSystem Statistics:")
    print(json.dumps(stats, indent=2))
    
    # Example queries
    example_queries = [
        "What are the coverage limits?",
        "What is excluded from coverage?",
        "How much is the premium?",
        "What are the claim procedures?",
        "What are the policy terms and conditions?"
    ]
    
    print(f"\nExample Queries and Results:")
    for query in example_queries:
        print(f"\nQuery: {query}")
        results = rag_system.query(query, top_k=3)
        
        for i, result in enumerate(results, 1):
            print(f"  {i}. Score: {result['similarity_score']:.3f}")
            print(f"     Source: {result['metadata']['source_file']}")
            print(f"     Section: {result['metadata']['section_type']}")
            print(f"     Content: {result['content'][:200]}...")
            print()

if __name__ == "__main__":
    main() 