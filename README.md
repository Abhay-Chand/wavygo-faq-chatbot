# WavyGo FAQ Chatbot

A domain-specific FAQ chatbot for WavyGo built using Retrieval-Augmented Generation (RAG), LangChain, LangGraph, OpenAI, ChromaDB, and FastAPI.

The system is designed to answer WavyGo-related questions using information retrieved from the company's FAQ knowledge base. It uses a structured LangGraph workflow to retrieve relevant information, evaluate its relevance, generate grounded responses, and provide a fallback when the required information is unavailable.

---

## Overview

The WavyGo FAQ Chatbot is designed as a controlled question-answering system rather than a general-purpose chatbot.

Instead of allowing the language model to answer using its general knowledge, the system first retrieves relevant FAQ information from a vector database and then generates an answer based on that retrieved context.

The core workflow is:

```text
User Query
    |
    v
Query Classification
    |
    +-------------------+
    |                   |
    v                   v
Normal Query        FAQ Query
    |                   |
    v                   v
Normal Response    FAQ Retrieval
                        |
                        v
                  Relevance Check
                    /        \
                   /          \
                  v            v
             Relevant      Not Relevant
                |               |
                v               v
         Generate Answer      Fallback
                |               |
                +-------+-------+
                        |
                        v
                      Response
```

---

## Key Features

* Retrieval-Augmented Generation (RAG)
* Semantic FAQ retrieval using OpenAI embeddings
* Persistent ChromaDB vector store
* LangGraph-based workflow orchestration
* LangChain integration
* Relevance-based response generation
* Controlled fallback for unsupported questions
* Support contact escalation
* English and Hinglish FAQ support
* Modular RAG and chatbot architecture
* FastAPI backend foundation
* Separate scripts for testing retrieval, routing, similarity, and the complete graph

---

## Architecture

```text
                        +----------------+
                        |     Client     |
                        +-------+--------+
                                |
                                v
                        +---------------+
                        |    FastAPI    |
                        +-------+-------+
                                |
                                v
                     +----------------------+
                     |     LangGraph        |
                     |      Workflow        |
                     +----------+-----------+
                                |
                         Query Classification
                                |
                 +--------------+--------------+
                 |                             |
                 v                             v
          Normal Query                    FAQ Query
                 |                             |
                 v                             v
        Normal Response                FAQ Retrieval
                                              |
                                              v
                                      Relevance Check
                                         /       \
                                        /         \
                                       v           v
                                  Relevant     Irrelevant
                                      |             |
                                      v             v
                              Answer Generation  Fallback
                                      |             |
                                      +------+------+
                                             |
                                             v
                                          Response


                       RAG Pipeline
                           
                      FAQ Dataset
                           |
                           v
                  Document Processing
                           |
                           v
                     Text Splitting
                           |
                           v
                  OpenAI Embeddings
                           |
                           v
                       ChromaDB
                           |
                           v
                   Semantic Retrieval
```

---

## RAG Pipeline

The Retrieval-Augmented Generation pipeline consists of four primary stages.

### 1. FAQ Dataset

The FAQ knowledge base is stored in:

```text
data/faq/faq.json
```

The dataset contains questions and answers related to WavyGo services, including:

* Booking
* Cancellation
* Vehicle availability
* Documents and KYC
* Driving licence requirements
* Pickup and return
* Vehicle delivery
* Fuel
* Helmets
* Vehicle damage
* Breakdown
* Accidents
* Payments
* Pricing
* Customer support

The dataset also contains English and Hinglish-style queries to improve retrieval for realistic user inputs.

---

### 2. Document Processing

FAQ records are converted into LangChain documents.

The document content follows the structure:

```text
Question: <FAQ question>
Answer: <FAQ answer>
```

Metadata such as FAQ ID, category, and source is retained with the document.

The documents are processed using `RecursiveCharacterTextSplitter`.

Current configuration:

```text
Chunk Size: 500
Chunk Overlap: 50
```

---

### 3. Embeddings

The project uses OpenAI embeddings to convert FAQ documents and user queries into vector representations.

Default embedding model:

```text
text-embedding-3-small
```

The model can be configured using:

```env
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

---

### 4. Vector Database

The generated embeddings are stored in ChromaDB.

Default configuration:

```text
Collection: wavygo_faq
Directory: ./chroma_db
```

The vector database allows the system to perform semantic similarity search instead of relying only on exact keyword matching.

---

## Retrieval

The FAQ retriever performs similarity-based search against ChromaDB.

The current retrieval configuration uses:

```python
k = 4
```

The system retrieves the top matching FAQ documents together with their similarity distances.

The retrieved results are then evaluated using a relevance threshold.

```text
User Query
     |
     v
Query Embedding
     |
     v
ChromaDB Similarity Search
     |
     v
Top 4 FAQ Documents
     |
     v
Similarity Distance
     |
     v
Relevance Evaluation
```

In the current ChromaDB implementation:

```text
Lower Distance  -> More Similar
Higher Distance -> Less Similar
```

The threshold is configurable through:

```env
FAQ_RELEVANCE_THRESHOLD=1.0
```

---

## LangGraph Workflow

The chatbot uses LangGraph to define the processing workflow as a state graph.

The main workflow components include:

```text
classify
normal_response
retrieve_faq
relevance_check
generate_answer
fallback
```

This allows the chatbot to explicitly control the transition between different stages instead of sending every query directly to an LLM.

The shared chatbot state contains information such as:

```text
user_message
intent
retrieved_documents
relevance_score
context_relevant
answer
contact_support
```

This state is passed between the different LangGraph nodes.

---

## Query Handling

The chatbot handles different types of user input.

### Normal Query

Example:

```text
User:
Hi
```

The system identifies it as a normal conversational query and returns a simple response.

---

### FAQ Query

Example:

```text
User:
How can I cancel my ride?
```

Processing:

```text
Query
  |
  v
FAQ Retrieval
  |
  v
Relevant FAQ
  |
  v
LLM
  |
  v
Grounded Answer
```

---

### Unsupported Query

Example:

```text
User:
What is the weather today?
```

If the query does not have relevant information in the WavyGo FAQ knowledge base, the system uses a controlled fallback instead of generating an unsupported answer.

Example:

```text
I couldn't find that information in the WavyGo FAQ.
```

Support contact information can then be provided through environment variables.

---

## Hallucination Control

The answer-generation prompt restricts the model to the retrieved FAQ context.

The model is instructed to:

* Use only the provided FAQ context
* Avoid external knowledge
* Avoid assumptions
* Avoid inventing information
* Avoid exposing internal implementation details
* Return a fallback when sufficient information is unavailable

The resulting architecture is:

```text
Retrieved Context
       |
       v
   LLM Prompt
       |
       v
Grounded Response
```

This approach reduces the possibility of the model generating information that is not supported by the WavyGo knowledge base.

---

## Project Structure

```text
wavygo-faq-chatbot/
|
├── app/
|   |
|   ├── api/
|   |   ├── __init__.py
|   |   └── chatbot.py
|   |
|   ├── chatbot/
|   |   ├── __init__.py
|   |   ├── fallback.py
|   |   ├── graph.py
|   |   ├── nodes.py
|   |   ├── prompts.py
|   |   ├── router.py
|   |   ├── schemas.py
|   |   └── state.py
|   |
|   ├── rag/
|   |   ├── __init__.py
|   |   ├── embeddings.py
|   |   ├── ingest.py
|   |   ├── retriever.py
|   |   └── vectorstore.py
|   |
|   ├── __init__.py
|   └── main.py
|
├── data/
|   └── faq/
|       └── faq.json
|
├── scripts/
|   ├── __init__.py
|   ├── build_index.py
|   ├── test_graph.py
|   ├── test_retrieval.py
|   ├── test_router.py
|   └── test_similarity.py
|
├── .env.example
├── .gitignore
├── requirements.txt
└── test.py
```

---

## Technology Stack

| Component              | Technology        |
| ---------------------- | ----------------- |
| Programming Language   | Python            |
| API Framework          | FastAPI           |
| LLM                    | OpenAI            |
| Embeddings             | OpenAI Embeddings |
| LLM Framework          | LangChain         |
| Workflow Orchestration | LangGraph         |
| Vector Database        | ChromaDB          |
| Data Format            | JSON              |
| Data Validation        | Pydantic          |
| Configuration          | python-dotenv     |
| ASGI Server            | Uvicorn           |

---

## Environment Variables

Create a `.env` file using `.env.example`.

```env
OPENAI_API_KEY=your_openai_api_key

OPENAI_MODEL=gpt-4o-mini

OPENAI_EMBEDDING_MODEL=text-embedding-3-small

SUPPORT_EMAIL=your_support_email

SUPPORT_PHONE=your_support_phone

CHROMA_PERSIST_DIRECTORY=./chroma_db

FAQ_RELEVANCE_THRESHOLD=1.0
```

Do not commit `.env` or expose API keys in the repository.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Abhay-Chand/wavygo-faq-chatbot.git

cd wavygo-faq-chatbot
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv venv

venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv

source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create `.env`:

```bash
copy .env.example .env
```

Linux/macOS:

```bash
cp .env.example .env
```

Then add the required OpenAI API key and configuration values.

---

## Build the Vector Index

Before using the RAG system, build the ChromaDB index:

```bash
python -m scripts.build_index
```

The process is:

```text
FAQ JSON
   |
   v
Document Creation
   |
   v
Text Splitting
   |
   v
OpenAI Embeddings
   |
   v
ChromaDB
```

The generated vector database is persisted locally.

---

## Run the Application

Start the FastAPI application using:

```bash
uvicorn app.main:app --reload
```

The application will be available through the local FastAPI server.

The root endpoint provides a basic service status response.

---

## Testing

The repository contains dedicated scripts for testing individual components.

### Test Similarity Search

```bash
python -m scripts.test_similarity
```

This can be used to inspect retrieved documents and their similarity scores.

### Test Router

```bash
python -m scripts.test_router
```

Tests the chatbot routing behavior.

### Test Retrieval

```bash
python -m scripts.test_retrieval
```

Tests the FAQ retrieval layer independently.

### Test Complete Graph

```bash
python -m scripts.test_graph
```

Tests the complete LangGraph workflow.

---

## Example

### Input

```text
How can I cancel my ride?
```

### Processing

```text
User Query
    |
    v
Query Classification
    |
    v
FAQ Retrieval
    |
    v
Similarity Evaluation
    |
    v
Relevant FAQ Context
    |
    v
OpenAI LLM
    |
    v
Final Answer
```

### Output

```text
You can cancel your ride through the booking section of the WavyGo application.
```

---

## Design Principles

### Domain Restriction

The chatbot is designed specifically for WavyGo FAQ-related queries.

### Grounded Generation

The LLM receives retrieved FAQ information as context before generating the answer.

### Modular Architecture

RAG, chatbot logic, workflow orchestration, API logic, and configuration are separated into independent modules.

### Explicit Workflow

LangGraph provides an explicit state-based workflow for routing, retrieval, relevance checking, generation, and fallback.

### Graceful Fallback

When sufficient information cannot be retrieved, the system does not force an answer.

Instead, it falls back to a controlled response and can provide support contact information.

---

## Limitations

The current implementation is focused on the FAQ chatbot use case.

Potential improvements include:

* LLM-based intent classification
* Query rewriting
* Hybrid keyword and semantic retrieval
* Reranking
* Retrieval evaluation metrics
* Conversation memory
* Streaming responses
* Authentication
* Rate limiting
* API documentation
* Structured logging
* Monitoring and observability
* Docker deployment
* CI/CD
* Cloud deployment

---

## Future Improvements

### Retrieval

* Add hybrid search
* Add reranking
* Improve multilingual retrieval
* Introduce retrieval evaluation datasets
* Measure Recall@K, Precision@K, and MRR
* Automatically optimize relevance thresholds

### AI Workflow

* Add LLM-based query classification
* Add query rewriting
* Add conversation context
* Improve multilingual and Hinglish query handling

### Backend

* Add production chatbot API endpoint
* Add request validation
* Add authentication
* Add rate limiting
* Add structured API documentation

### Deployment

* Dockerize the application
* Add CI/CD
* Deploy the API to cloud infrastructure
* Add monitoring and tracing
* Move from local ChromaDB to a managed vector database when required

---

## What This Project Demonstrates

This project demonstrates practical implementation of:

```text
Python
    |
    +-- LangChain
    |
    +-- LangGraph
    |
    +-- OpenAI
    |
    +-- RAG
    |
    +-- Embeddings
    |
    +-- Vector Databases
    |
    +-- Semantic Search
    |
    +-- Prompt Engineering
    |
    +-- FastAPI
    |
    +-- AI Application Testing
```

The project focuses on building a controlled RAG application where retrieval, workflow orchestration, relevance evaluation, and response generation are implemented as separate components.

---

## Author

**Khushbu Joshi**

B.Tech in computer Science and Engineering

AI Engineer | Data Engineer | AI/ML Practitioner


---

## License

See the repository license for usage and distribution terms.

