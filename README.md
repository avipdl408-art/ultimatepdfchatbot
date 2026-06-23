# chatbotpro
Here is a comprehensive, professional `README.md` file tailored specifically for your project. It includes setup instructions, features, and guidance on how to configure each of the three backends.

---

# 📚 NexusPDF AI Workspace

NexusPDF AI Workspace is a premium, production-ready Streamlit application built to perform cross-document intelligence and conversational QA across multiple PDF files simultaneously.

It features an elegant dark glassmorphism interface, supports batch or granular processing, and features a dynamic backend switcher allowing you to toggle between **Local Open-Source LLMs (via Ollama)**, **Groq Cloud API**, or **Google Gemini API**. It also features built-in localized safety filters for sensitive topics with crisis resources specialized for Nepal.

---

## ✨ Key Features

* **🎨 Premium Dark Aesthetic:** Glassmorphic UI with vibrant state indicators and intuitive layout flows.
* **📂 Granular & Batch Document Processing:** View structural PDF cards individually, or parse your entire uploaded catalog with a single click using either standard `PyPDF` loaders or `LlamaParse`.
* **🤖 Triple-Engine Switcher:** Select your computing environment dynamically in the sidebar:
* **Ollama:** Run completely local, free, private instances of models like `Llama3`.
* **Groq Cloud API:** Blazing-fast inference utilizing `llama-3.1-8b-instant` or `llama-3.3-70b-versatile`.
* **Google Gemini API:** Cloud capabilities running `gemini-1.5-pro` or `gemini-1.5-flash`.


* **💬 Dynamic Conversation Router:** Seamlessly switches between an analytical document-reading bot and a standard companion chatbot based on your uploads.
* **🛡️ Robust Crisis Guardrails:** Active keyword-monitoring triggers specialized safety overrides, rendering empathetic messaging and localized helplines for Nepal (`1166`, `9813473506`) when needed.
* **🔐 Session Control:** Built-in authentication security door paired with session-clearing memory handles.

---

## 🚀 Setup & Installation

### 1. Clone or Create Project Folder

Place the code file named `ultimate.py` in a designated directory on your machine:

```bash
cd "C:\Users\avipd\Desktop\gen ai\Gen-ai-testing-"

```

### 2. Set Up a Virtual Environment (Recommended)

```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Mac/Linux:
source .venv/bin/activate

```

### 3. Install Dependencies

Install all required libraries for the Streamlit UI, Document Parsing extensions, and the 3 AI Engines:

```bash
pip install streamlit langchain-groq langchain-google-genai langchain-community llama-parse pypdf

```

---

## 🛠️ Engine Prerequisites

Before initializing the website interface, make sure your preferred provider is configured correctly:

### Option A: Running Locally via Ollama (Free & Offline)

1. Download and install the desktop engine from **[ollama.com](https://ollama.com)**.
2. Open your standard command prompt/terminal and run the background instance pull command:
```bash
ollama run llama3

```


3. Keep that terminal open. The application will naturally look for this connection loop at `http://localhost:11434`.

### Option B: Running Groq Cloud API

1. Create an account at **[console.groq.com](https://console.groq.com/)**.
2. Generate an API Key under the **API Keys** section.
3. Paste it directly into the secure masked password field when picking Groq in the application sidebar.

### Option C: Running Google Gemini API

1. Obtain an API access token from **[Google AI Studio](https://aistudio.google.com/)**.
2. Paste the access key value inside the sidebar field under the Gemini provider selection.

---

## 🎮 Running the Application

To bypass standard network conflicts or map to custom environments, run the application on your designated port (e.g., **`8080`**):

```bash
streamlit run ultimate.py --server.port 8080

```

Once running, navigate to `http://localhost:8080` in your web browser.

### 🔑 Default Credentials

* **Username:** `admin`
* **Password:** `password`

*(To change this configuration, locate the `login_screen()` wrapper function within `ultimate.py` to hardcode your custom authentication credentials).*

---

## 📂 Project Directory Structure

```text
├── .venv/                      # Python virtual environment
├── ultimate.py                 # Core application script file
└── README.md                   # Setup documentation framework

```

---

## 🛡️ Safety & Guardrails Specification

The framework uses an automated token evaluation engine. When keywords like *depression*, *self-harm*, or *suicide* are registered in the conversation flow, the generation halts regular operation and renders a standard care payload including:

* **National Suicide Prevention Helpline (Nepal):** `1166`
* **TUTH Mental Health Helpline:** `9813473506`
* **TPO Nepal Toll-Free Support:** `16600102005`

##  Login
Username= admin
Password= password
