# 🌟 Master Repository: Red_Chillies_AI_Job_Assessment

Welcome to the master repository containing complete solutions for a comprehensive technical evaluation bridging Generative AI, Computer Vision, and Full-Stack Engineering. This project includes four dedicated assessment modules, each housed in its own directory with specific documentation, source code, and workflows.

> ### ✅ **Compliance & Extra Initiative**
> 
> 
> * While the guidelines require candidates to complete a minimum of three assessments, **four assessments (1, 3, 4, and 5) have been completed** to be extra cautious and comprehensively demonstrate proficiency across both generative AI pipelines and technical tracks.
> * **Open-Source Compliance:** We have strictly complied with all conditions regarding the use of open-source tools, models, and frameworks (e.g., ComfyUI, Stable Diffusion XL, Florence-2, SAM 2, Ollama, Qdrant, and LangChain). All open-source assets are utilized respecting their original licenses, and no external proprietary APIs were used where local processing was required.
> 
> 

---

## 📂 Repository Architecture

```text
master-assessment-repo/
│
├── 🎨 assessment-1-image-processing/    # AI-based image extension and editing
├── 🎯 assessment-3-image-segmentation/  # Zero-shot object detection and masking
├── 📋 assessment-4-taskflow-kanban/     # Zero-dependency Kanban board
└── 🧠 assessment-5-RAG/                 # Local, privacy-focused RAG application

```

---

## 🚀 Project Showcases

### 🎨 Assessment 1: AI-Based Image Processing

A node-based generative AI workflow designed to perform complex, high-quality image manipulations.

* **✨ Capabilities:** Extends missing image backgrounds (outpainting), upscales resolutions, removes existing objects via masking, and adds new objects (e.g., a realistic bicycle) into scenes seamlessly.


* **🛠️ Tech Stack:** ComfyUI, Stable Diffusion XL (`Raymnants.3.0-sdxl.safetensors`), KSampler, and VAE encoding/decoding.


* **⚙️ Usage:** Load the `assessment1_workflow.json` into ComfyUI, provide an input image, and execute the branches to generate edits.


---
### 🎯 Assessment 3: Image Segmentation

An advanced zero-shot text-to-image segmentation workflow that cleanly isolates a specific target object (e.g., a water bottle) from its background.

* **✨ Capabilities:** Generates a highly accurate segmentation mask based on a text prompt ("Water Bottle") and produces a transparent RGBA cutout of the object.


* **🛠️ Tech Stack:** `microsoft/Florence-2-base` (for text-phrase grounding) and `sam2.1_hiera_large.safetensors` (for segmentation masks), executed via ComfyUI.


* **⚙️ Usage:** Requires specific custom nodes (`Florence2Run`, `Sam2Segmentation`, etc.) in ComfyUI to process the image and output the final cutout.

---

### 📋 Assessment 4: Taskflow — Color Pop Edition

A fully functional, client-side Kanban task management application built without any external dependencies, frameworks, or backend APIs.

* **✨ Capabilities:** Features smooth HTML5 drag-and-drop across four lifecycle columns, full CRUD operations, a real-time search/filter bar, and an overdue escalation engine that turns delayed tasks a vibrant crimson.


* **🛠️ Tech Stack:** Pure Semantic HTML5, CSS3 Custom Properties (Neo-Brutalist Light/Dark theme), and Vanilla ES6+ JavaScript.


* **⚙️ Usage:** State is synchronized locally via the browser's `localStorage` API. Simply open `index.html` in any modern web browser to run it instantly.

---

### 🧠 Assessment 5: Hybrid RAG Knowledge Assistant

A locally hosted Retrieval-Augmented Generation (RAG) application designed to securely query personal PDF and TXT documents without relying on external APIs.

* **✨ Capabilities:** Combines dense-vector similarity search with BM25 keyword retrieval, applies cross-encoder reranking, and uses conversational memory to accurately answer follow-up questions while citing its sources.


* **🛠️ Tech Stack:** Streamlit, LangChain, local Qdrant vector storage, Hugging Face embeddings (`BAAI/bge-small-en-v1.5`), and local LLM inference using Qwen 2.5 3B via Ollama.


* **⚙️ Usage:** Set up the Python environment (`requirements.txt`), ensure the local Ollama instance is running, and launch the app using `streamlit run app.py`.



---

## 🏁 Getting Started

Because this repository spans diverse technologies—from Python-based backends to pure client-side web applications and node-based AI workflows—there is no single global installation step.

To evaluate a specific assessment, navigate to its respective directory and consult its dedicated `README.md`:

| Assessment | Setup Instructions |
| --- | --- |
| **Assessments 1 & 3** | Ensure [ComfyUI](https://github.com/comfyanonymous/ComfyUI) is installed locally along with the referenced model checkpoints and custom nodes. |
| **Assessment 4** | Zero installation required. Simply open `index.html` directly in your favorite web browser. |
| **Assessment 5** | Create a Python virtual environment, install dependencies via `pip`, and ensure Ollama is installed and running locally on your machine. |

---
