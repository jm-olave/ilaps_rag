# Legal Document Chatbot Project

## Overview

A document chatbot system designed to answer query prompts based on extensive legal PDF documents. The system implements a complete RAG (Retrieval-Augmented Generation) pipeline with automated document processing, chunking, embedding generation, and intelligent querying capabilities.

## Architecture

```
Excel File → PDF Download → Docling Chunking → Embeddings → Vector DB → RAGFlow → Chatbot
```

## Tech Stack

### Core Components
- **Document Processing**: Docling (chunking pipeline)
- **Vector Database**: PostgreSQL with pgvector extension
- **RAG System**: RAGFlow for scalable RAG implementation
- **Document Source**: Excel file containing PDF download links
- **Document Type**: Legal PDFs (extensive documents)

### Future Features
- **Automation**: Time-based scheduler for automated data extraction
- **Scalability**: Designed for handling large document collections

## Project Structure

```
document-chat-rag/
├── src/
│   ├── etl/
│   │   ├── excel_reader.py          # Excel file processing
│   │   ├── pdf_downloader.py        # PDF download from URLs
│   │   ├── docling_processor.py     # Document chunking with Docling
│   │   └── embedding_generator.py   # Generate and store embeddings
│   ├── database/
│   │   ├── vector_store.py          # PostgreSQL + pgvector operations
│   │   └── migrations/              # Database schema migrations
│   ├── rag/
│   │   ├── ragflow_integration.py   # RAGFlow system integration
│   │   └── query_processor.py       # Query handling and response generation
│   └── utils/
│       ├── config.py                # Configuration management
│       └── logging.py               # Logging utilities
├── data/
│   ├── raw/                         # Raw downloaded PDFs
│   ├── processed/                   # Processed chunks
│   └── excel/                       # Excel files with PDF links
├── config/
│   ├── database.yaml               # Database configuration
│   └── processing.yaml             # Processing parameters
├── tests/
│   ├── test_etl.py
│   ├── test_database.py
│   └── test_rag.py
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── requirements.txt
├── README.md
└── QWEN.md                       # This file
```

## MVP Pipeline (ETL Process)

### Phase 1: Data Ingestion
1. **Excel Processing**
   - Read Excel file containing PDF download links
   - Extract metadata (document names, categories, dates, etc.)
   - Validate URLs and prepare download queue

2. **PDF Download**
   - Download PDFs from extracted URLs
   - Implement retry logic for failed downloads
   - Store PDFs with consistent naming convention
   - Log download status and errors

3. **Document Processing with Docling**
   - Process downloaded PDFs through Docling
   - Generate structured chunks with metadata
   - Preserve document hierarchy and context
   - Extract key legal document elements (headers, sections, clauses)

4. **Embedding Generation**
   - Generate embeddings for each chunk
   - Store embeddings in PostgreSQL with pgvector
   - Maintain chunk-to-document relationships
   - Index for efficient similarity search

### Phase 2: RAG Implementation
1. **RAGFlow Integration**
   - Set up RAGFlow for scalable RAG processing
   - Configure retrieval parameters
   - Implement query routing and context assembly

2. **Query Processing**
   - Accept user queries
   - Retrieve relevant chunks using vector similarity
   - Generate contextual responses
   - Implement response ranking and filtering

## Database Schema (PostgreSQL + pgvector)

```sql
-- Documents table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    source_url TEXT,
    download_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_size BIGINT,
    document_type VARCHAR(100),
    metadata JSONB
);

-- Chunks table with vector embeddings
CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536), -- Adjust dimension based on embedding model
    chunk_metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create vector index for similarity search
CREATE INDEX ON document_chunks USING ivfflat (embedding vector_cosine_ops);
```

## Configuration

### Environment Variables
```bash
# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=legal_docs
POSTGRES_USER=username
POSTGRES_PASSWORD=password

# Docling
DOCLING_API_KEY=your_api_key
DOCLING_MODEL=default

# RAGFlow
RAGFLOW_ENDPOINT=http://localhost:8080
RAGFLOW_API_KEY=your_ragflow_key

# Embeddings
EMBEDDING_MODEL=text-embedding-ada-002
OPENAI_API_KEY=your_openai_key
```

### Processing Parameters
```yaml
# processing.yaml
chunking:
  max_chunk_size: 1000
  overlap: 200
  preserve_structure: true

embedding:
  model: "text-embedding-ada-002"
  batch_size: 100
  dimensions: 1536

retrieval:
  similarity_threshold: 0.7
  max_results: 10
```

## Implementation Phases

### Phase 1: MVP (Current Focus)
- ✅ Excel reader for PDF links
- ✅ PDF downloader with error handling
- ✅ Docling integration for chunking
- ✅ PostgreSQL + pgvector setup
- ✅ Basic embedding generation and storage

### Phase 2: RAG System
- 🔄 RAGFlow integration
- 🔄 Query processing pipeline
- 🔄 Response generation and ranking
- 🔄 Basic web interface

### Phase 3: Production Features
- ⏳ Automated scheduling system
- ⏳ Advanced error handling and monitoring
- ⏳ Performance optimization
- ⏳ User authentication and authorization
- ⏳ Advanced analytics and logging

### Phase 4: Scale & Automation
- ⏳ Horizontal scaling capabilities
- ⏳ Advanced caching strategies
- ⏳ Real-time document updates
- ⏳ Multi-tenant support

## Key Considerations

### Legal Document Processing
- **Structure Preservation**: Maintain legal document hierarchy (sections, subsections, clauses)
- **Citation Tracking**: Preserve references and cross-references between documents
- **Metadata Extraction**: Extract key legal metadata (dates, parties, case numbers, etc.)
- **Version Control**: Handle document versions and amendments

### Scalability Considerations
- **Batch Processing**: Process documents in batches to handle large volumes
- **Incremental Updates**: Support adding new documents without full reprocessing
- **Caching**: Implement caching for frequently accessed chunks
- **Monitoring**: Track processing times, success rates, and system performance

### Data Quality
- **Validation**: Implement data validation at each pipeline stage
- **Error Handling**: Robust error handling with detailed logging
- **Recovery**: Ability to resume processing from failure points
- **Quality Checks**: Automated quality checks for chunk relevance and completeness

## Getting Started

1. **Setup Database**
   ```bash
   # Install PostgreSQL and pgvector extension
   sudo apt-get install postgresql postgresql-contrib
   pip install pgvector
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   - Copy `.env.example` to `.env`
   - Update configuration files in `config/`

4. **Run ETL Pipeline**
   ```bash
   python src/etl/pipeline.py --excel-file data/excel/document_links.xlsx
   ```

5. **Start RAG System**
   ```bash
   python src/rag/server.py
   ```

## Monitoring & Observability

- **Logging**: Structured logging for all pipeline stages
- **Metrics**: Track processing times, success rates, and query performance
- **Alerts**: Set up alerts for pipeline failures and performance degradation
- **Dashboard**: Create monitoring dashboard for system health

## Security Considerations

- **Data Privacy**: Ensure legal document confidentiality
- **Access Control**: Implement proper authentication and authorization
- **Audit Trail**: Maintain logs of all document access and queries
- **Encryption**: Encrypt sensitive data at rest and in transit

---

*This document will be updated as the project evolves and new requirements are identified.*