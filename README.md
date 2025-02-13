[![🚀 Netlify Deployment](https://img.shields.io/badge/Deployed%20on-Netlify-00C7B7.svg)](https://netlify.com)
[![☁️ GCP Powered](https://img.shields.io/badge/Powered%20by-Google%20Cloud-4285F4.svg)](https://cloud.google.com)
[![🤖 Mistral](https://img.shields.io/badge/AI-Mistral--large2-blue.svg)](https://mistral.ai)
[![YouTube](https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=YouTube&logoColor=white)](https://youtu.be/E1OxAEY-fZ8)


# 🌟 InspireIt - Bringing Inspirations to Life!

InspireIt is a distributed research assistance platform created to revolutionize the academic research process. It leverages Google Cloud Platform's Vertex AI and Cloud Storage to provide intelligent research ideation and paper development capabilities.

## 🏗️ System Architecture

```mermaid
graph TD
    UI[Web Interface] --> |HTTP| API[API Layer]
    API --> |Request| VAI[Vertex AI]
    VAI --> |Storage| GCS[Cloud Storage]
    GCS --> |Dataset| ARXIV[arXiv Papers]
    VAI --> |Embeddings| RAG[RAG System]
    RAG --> |Query| ARXIV[arXiv Papers]
    ARXIV --> |Retrieved Data| RAG
    RAG --> |Context| LLM[LLM Models]
    LLM --> |Generated Response| API
    API --> |Response| UI
```

## ✨ Features

### 🔍 **Intelligent Idea Generation**
The platform excels at generating cross-domain research ideas by leveraging its RAG architecture powered by arXiv papers. It analyzes research opportunities, identifies potential drawbacks, and provides innovation potential scoring.

### 📚 **Research Enhancement Tools**
Users can access automated paper summaries, reference management, and citation suggestions. The system maintains standardized citation formats and performs cross-reference validation to ensure academic integrity.

### 🛠 **Interactive Development Pipeline**
The platform provides step-by-step idea refinement with real-time feedback integration. Researchers can track their progress and compare different versions of their work as it develops.

## 🚀 Getting Started

InspireIt provides three main entry points through its interface:

1. **Get Started** - Launches the idea generation pipeline
2. **Analyze Now** - Enables review of existing research ideas
3. **Explore** - Opens an AI-powered chat interface for research exploration

## 🏗 Technology Stack

InspireIt is built on modern cloud infrastructure:

- **Google Cloud Platform**
  - Vertex AI for model serving and inference
  - Cloud Storage for data management
  - Agent Builder for conversation orchestration
- **Mistral-large2** for natural language processing
- **Netlify** for deployment and hosting
- **RAG architecture** utilizing arXiv papers

## 🎯 Target Audience

InspireIt serves various segments of the research community:

The platform is designed for academic researchers, including PhD students and faculty members, industry professionals in R&D, research institutions, and students engaged in academic writing and research projects.

## 📩 Get in Touch

Have questions, suggestions, bug reports? Reach out through:

- 📧 [inspireit.ed@gmail.com]

## 🏆 Sponsors

InspireIt is powered by Google Cloud Platform and deployed on Netlify. We appreciate their infrastructure support in making this project possible.
