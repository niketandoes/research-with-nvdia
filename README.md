# NVIDIA Autonomous Research Agent

An automated research agent powered by NVIDIA's Integrated API endpoints (`https://integrate.api.nvidia.com/v1`). It processes topics queued in a markdown file, generates detailed analytical reports using primary (`nvidia/nemotron-3-super-120b-a12b`) and fallback LLM models (e.g. `meta/llama-3.1-405b-instruct`), streams output in real-time, and saves sanitized markdown reports into an output directory.

---

## 🚀 Features

- **Primary Model Integration**: Powered by `nvidia/nemotron-3-super-120b-a12b` via NVIDIA NIM endpoints.
- **Docker Support**: Containerized execution ready for Linux environments with Docker & Docker Compose.
- **Markdown Queue Processing**: Automatically reads pending topics formatted as `- [ ] <topic>` in `research_queue.md` and marks completed items as `- [x]`.
- **NVIDIA API Integration**: Connects to high-performance LLM endpoints using the `openai` Python SDK configured with NVIDIA base URL.
- **Resilient Fallback Mechanism**: Automatically falls back to `meta/llama-3.1-405b-instruct` if primary request fails.
- **Robust Retry Logic**: Built-in exponential backoff via `tenacity` to gracefully handle API rate limits and connection timeouts.
- **Automated Output Organization**: Generates sanitized filenames from topic names and writes structured markdown files directly into `research_outputs/`.

---

## 📋 Prerequisites

- **NVIDIA API Key**: Obtain an API key from the [NVIDIA Build API Portal](https://build.nvidia.com).
- **Environment**: Linux with Docker and Docker Compose installed (or Python 3.8+ for direct execution).

---

## ⚙️ Configuration

Create or update the `.env` file in the root directory with your NVIDIA API key:

```env
NVIDIA_API_KEY=your_nvidia_api_key_here
```

---

## 🐳 Running with Docker (Recommended for Linux)

### Using Docker Compose

1. **Build and start the container**:
   ```bash
   docker-compose up --build
   ```

2. **Run in detached mode**:
   ```bash
   docker-compose up -d --build
   ```

### Using Docker CLI

1. **Build the Docker Image**:
   ```bash
   docker build -t nvidia-research-agent .
   ```

2. **Run the Container**:
   ```bash
   docker run --rm \
     --env-file .env \
     -v "$(pwd)/research_queue.md:/app/research_queue.md" \
     -v "$(pwd)/research_outputs:/app/research_outputs" \
     nvidia-research-agent
   ```

---

## 💻 Native Python Setup

1. **Create and Activate Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Agent**:
   ```bash
   python nvidia_research_agent.py
   ```

---

## 📖 Queue Management & Usage

### 1. Queueing Research Topics

Add topics to `research_queue.md` using standard markdown checkboxes:

```markdown
- [ ] Explain the fundamental differences between quantum computing and classical computing architectures.
- [ ] Overview of recent advances in AI agent orchestration frameworks.
```

### 2. Output Reports

All completed research reports will be automatically written to `./research_outputs/<topic_name>.md`, and `research_queue.md` will mark the topic as finished (`- [x]`).

---

## 🧪 Testing API Connectivity

Run the included test scripts to verify model response and API key status:

```bash
python test_nvidia.py
```

---

## 📂 Project Structure

```text
.
├── .env                       # Environment variables (NVIDIA_API_KEY)
├── Dockerfile                 # Docker container build script
├── docker-compose.yml         # Docker Compose orchestration
├── .dockerignore              # Excluded files for Docker build
├── requirements.txt           # Python dependencies
├── nvidia_research_agent.py   # Core autonomous research agent script
├── research_queue.md          # Input markdown file containing topic queue
├── research_outputs/          # Directory where generated markdown research reports are saved
├── test_nvidia.py             # Test script for nvidia/nemotron-3-super-120b-a12b
├── test_deepseek.py           # Test script for DeepSeek models
├── test_llama.py              # Test script for Llama models
└── test_mistral.py            # Test script for Mistral models
```
