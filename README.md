# ILAPS RAG: Improving Legal Access for Post-conflict Survivors

## Project Overview

ILAPS RAG is a specialized document chatbot system designed to bridge the gap between post-conflict victims and critical legal information. By leveraging advanced Retrieval-Augmented Generation (RAG) technology, this system processes court decisions and judicial documents, making them accessible through a conversational interface that allows victims to easily access information about their cases and legal processes.

## The Challenge

In post-conflict scenarios, victims often face significant barriers when trying to access information about their legal cases:

- Complex legal documents that are difficult to understand
- Limited access to legal representation
- Geographical barriers to physically accessing courts
- Overwhelming volume of documentation
- Emotional burden of navigating bureaucratic processes

These challenges can lead to victims feeling disconnected from the justice process, potentially hindering reconciliation and healing in post-conflict societies.

## Our Solution

ILAPS RAG transforms how victims interact with legal information through a sophisticated technical pipeline:

### Key Technical Features

- **Automated Document Processing**: Extracts and processes court decisions and legal documents from Excel-based registries
- **Intelligent Document Understanding**: Uses Docling to preserve the hierarchical structure of legal documents
- **Vector Database Storage**: Employs PostgreSQL with pgvector for efficient similarity search
- **Contextual Retrieval**: Finds the most relevant legal information based on natural language queries
- **Conversational Interface**: Presents complex legal information in an accessible, conversational format

## Technical Implementation

### Core Components

- **ETL Pipeline**: Extracts documents from Excel sources, downloads PDFs, processes them with Docling, and generates embeddings
- **Vector Database**: PostgreSQL with pgvector extension for storing and retrieving document embeddings
- **RAG System**: RAGFlow for contextual retrieval and response generation
- **Document Processing**: Specialized handling of legal documents with preservation of structure and metadata

### Project Structure

```
ILAPS-RAG/
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

## Social Impact

### Empowering Victims

This project directly addresses the needs of post-conflict victims by:

1. **Democratizing Access to Justice**: Providing equal access to legal information regardless of location, education level, or resources

2. **Reducing Information Asymmetry**: Giving victims the same level of information access that was previously available only to those with legal expertise

3. **Supporting Emotional Well-being**: Reducing the stress and trauma associated with navigating complex legal systems by providing clear, accessible information

4. **Enabling Informed Participation**: Allowing victims to actively participate in their legal processes with better understanding

5. **Building Trust in Justice Systems**: Increasing transparency and accessibility of legal proceedings, which is crucial for post-conflict reconciliation

### Broader Societal Benefits

- **Scalable Justice**: The system can handle thousands of cases simultaneously, addressing the often overwhelming caseload in post-conflict settings

- **Historical Documentation**: Creates a searchable repository of legal decisions that serves both immediate needs and historical documentation

- **Reduced Burden on Legal Systems**: By answering common questions automatically, the system reduces the administrative burden on courts

- **Data-Driven Policy Insights**: Aggregate query patterns can inform policy decisions about victim needs and justice system improvements

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL with pgvector extension
- Required Python packages (see requirements.txt)

### Installation

1. Clone the repository

```bash
git clone https://github.com/yourusername/ilaps_rag.git
cd ilaps_rag/document-chat-rag
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Configure environment

- Update database configuration in `config/database.yaml`
- Adjust processing parameters in `config/processing.yaml` if needed
- Set up PostgreSQL with pgvector extension

### Running the Pipeline

```bash
python pipeline.py --excel-file path/to/your/excel_file.xlsx
```

For testing or development purposes, you can limit the number of documents processed:

```bash
python pipeline.py --excel-file path/to/your/excel_file.xlsx --max-documents 5
```

## Future Development

- **Multilingual Support**: Expanding to support multiple languages common in post-conflict regions
- **Voice Interface**: Adding voice capabilities for users with limited literacy
- **Mobile Application**: Developing a dedicated mobile app for improved accessibility
- **Automated Updates**: Implementing scheduled updates to incorporate new court decisions
- **Personalized Case Tracking**: Allowing victims to track updates specific to their cases

## Conclusion

ILAPS RAG represents a significant step forward in using technology to address the human challenges of post-conflict justice. By making legal information accessible, understandable, and contextually relevant, we aim to empower victims, strengthen justice systems, and contribute to the healing process in societies recovering from conflict.

By bridging technical innovation with human-centered design, this project demonstrates how advanced AI systems can be deployed to serve those most in need of support and information.

---

*This project is dedicated to improving access to justice for all victims of conflict, in the belief that information access is a fundamental right and a crucial step toward healing and reconciliation.*


