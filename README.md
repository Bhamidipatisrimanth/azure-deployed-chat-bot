# Azure-Deployed-Chat-Botzz
# 🚀 AI Chatbot Deployment Project

## 📌 Overview

This project is a production-style AI chatbot system built using Flask, PostgreSQL, and an external LLM API hosted on Google Colab. The chatbot supports persistent conversation history, cloud deployment, response streaming, and caching for improved performance.

The application is deployed on a cloud VM and communicates with a remotely hosted LLM through API requests.

---

# 🧠 Features

- Real-time chatbot interface
- Flask backend API
- PostgreSQL database integration
- Persistent conversation history
- External LLM integration via ngrok
- Gunicorn production server
- Streaming chatbot responses
- In-memory response caching
- Cloud deployment on Azure VM
- REST API architecture

---

# 🏗️ System Architecture

```text
User (Browser)
        ↓
Flask Backend (Gunicorn)
        ↓
PostgreSQL Database
        ↓
External LLM API (Google Colab + ngrok)
```

## ⚙️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Backend** | Python, Flask, Gunicorn, Requests |
| **Database** | PostgreSQL |
| **Frontend** | HTML5, CSS3, JavaScript |
| **AI / LLM** | Google Colab, ngrok |
| **Deployment** | Azure Virtual Machine (Ubuntu) |

---

## 📂 Project Structure
```text
chatbot/
│
├── app.py              # Flask Application logic
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (Private)
├── azure_schema.sql    # Database schema for PostgreSQL
│
├── templates/
│   └── index.html      # Main UI
│
├── static/             # CSS and JS files
│
└── README.md           # Project documentation
```
## Setup Instructions
Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```
Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```
Install Dependencies
```bash
pip install -r requirements.txt
```
Configure Environment Variables
create .env
```env
DATABASE_URL=postgresql://USERNAME:PASSWORD@HOST:5432/chatbotdb
LLM_API_URL=https://YOUR-NGROK-URL/generate
USE_LLM=True
```
PostgreSQL Setup
Run Schema:
``` bash
psql postgresql://USERNAME:PASSWORD@HOST:5432/chatbotdb < azure_schema.sql
```
Run Application
```bash
gunicorn app:app --bind 0.0.0.0:5000
```
## API Endpoints
```http
POST /api/chat
```
Request
```json
{
  "user_id": "user123",
  "message": "Hello",
  "conversation_id": 1
}
```
Streaming Chat Endpoint
```http
POST /api/chat-stream
```
Health Check
```http
GET /health
```
Response
```json
{
  "status": "healthy",
  "database": "connected",
  "llm": "enabled"
}
```
## Performance Improvements
--> Streaming Responses

Implemented streaming responses for improved user experience and reduced perceived latency.

--> In-Memory Caching

Added caching to reduce repeated LLM API calls and improve response speed.

--> Context Limiting

Conversation history is limited to recent messages to optimize latency.

## Cloud Deployment

The chatbot backend is deployed on an Azure Ubuntu VM using Gunicorn as the production WSGI server.

* Deployment Components
* Azure VM
* PostgreSQL
* Gunicorn
* Flask
* External LLM API
## Learning Outcomes

This project helped in understanding:

* REST API development
* Cloud deployment
* PostgreSQL integration
* Gunicorn production serving
* LLM API integration
* Streaming responses
* Caching mechanisms
* Chatbot architecture design
## Future Improvements
* RAG integration
* Redis caching
* Real token streaming
* Multi-user authentication
* Docker deployment
* Vector database integration
* PDF/document ingestion
