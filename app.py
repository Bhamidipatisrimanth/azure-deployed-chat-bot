from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS
import os
import psycopg2
import requests
import time
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
CORS(app)

# ================== CONFIG ==================

DATABASE_URL = os.getenv('DATABASE_URL')

LLM_API_URL = os.getenv(
    'LLM_API_URL',
    "https://supermorose-nonvegetive-brooks.ngrok-free.dev/generate"
)

USE_LLM = os.getenv('USE_LLM', 'True').lower() == 'true'

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set")

# ================== CACHE ==================

CACHE = {}

# ================== DATABASE ==================

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)


def execute_query(query, params=None, fetch=False):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = query.replace('?', '%s')
    cursor.execute(query, params or ())

    result = None
    if fetch:
        columns = [desc[0] for desc in cursor.description]
        result = [dict(zip(columns, row)) for row in cursor.fetchall()]

    conn.commit()
    conn.close()

    return result

# ================== MEMORY ==================

def get_conversation_history(conversation_id, limit=5):
    messages = execute_query(
        'SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY timestamp DESC LIMIT ?',
        (conversation_id, limit * 2),
        fetch=True
    )

    history = [
        f"{msg['role'].capitalize()}: {msg['content']}"
        for msg in reversed(messages)
    ]

    return history

# ================== LLM ==================

def get_llm_response_api(user_message, conversation_id=None):
    try:
        key = user_message.strip().lower()

        # ⚡ CACHE CHECK
        if key in CACHE:
            print("⚡ Cache hit")
            return CACHE[key]

        history = []
        if conversation_id:
            history = get_conversation_history(conversation_id)

        payload = {
            "prompt": user_message,
            "history": history[-5:]
        }

        response = requests.post(LLM_API_URL, json=payload, timeout=30)

        if response.status_code == 200:
            answer = response.json().get('response', 'No response')

            # ⚡ STORE IN CACHE
            CACHE[key] = answer

            return answer
        else:
            return f"LLM API Error: {response.status_code}"

    except requests.exceptions.Timeout:
        return "LLM timeout. Try again."
    except requests.exceptions.ConnectionError:
        return "Cannot connect to LLM"
    except Exception as e:
        return f"LLM Error: {str(e)}"


def get_llm_response(user_message, conversation_id=None):
    if USE_LLM:
        return get_llm_response_api(user_message, conversation_id)
    return "LLM disabled"

# ================== ROUTES ==================

@app.route('/')
def index():
    return render_template('index.html')


# -------- NORMAL CHAT --------
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json

        user_id = data.get('user_id', 'anonymous')
        user_message = data.get('message', '').strip()
        conversation_id = data.get('conversation_id')

        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400

        # Create conversation
        if not conversation_id:
            result = execute_query(
                'INSERT INTO conversations (user_id) VALUES (?) RETURNING id',
                (user_id,),
                fetch=True
            )
            conversation_id = result[0]['id']

        # Save user message
        execute_query(
            'INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)',
            (conversation_id, 'user', user_message)
        )

        # Get response
        assistant_response = get_llm_response(user_message, conversation_id)

        # Save assistant response
        execute_query(
            'INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)',
            (conversation_id, 'assistant', assistant_response)
        )

        return jsonify({
            "response": assistant_response,
            "conversation_id": conversation_id
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------- STREAMING CHAT --------
@app.route('/api/chat-stream', methods=['POST'])
def chat_stream():
    try:
        data = request.json

        user_id = data.get('user_id', 'anonymous')
        user_message = data.get('message', '').strip()
        conversation_id = data.get('conversation_id')

        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400

        def generate():
            response_text = get_llm_response(user_message, conversation_id)

            for word in response_text.split():
                yield word + " "
                time.sleep(0.05)

        return Response(generate(), mimetype='text/plain')

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------- HISTORY --------
@app.route('/api/history/<int:conversation_id>', methods=['GET'])
def get_history(conversation_id):
    try:
        messages = execute_query(
            'SELECT role, content, timestamp FROM messages WHERE conversation_id = ? ORDER BY timestamp',
            (conversation_id,),
            fetch=True
        )

        return jsonify({"messages": messages})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------- USER CONVERSATIONS --------
@app.route('/api/conversations/<user_id>', methods=['GET'])
def get_user_conversations(user_id):
    try:
        conversations = execute_query(
            'SELECT id, created_at FROM conversations WHERE user_id = ? ORDER BY created_at DESC',
            (user_id,),
            fetch=True
        )

        return jsonify({"conversations": conversations})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------- HEALTH --------
@app.route('/health', methods=['GET'])
def health():
    try:
        execute_query("SELECT 1", fetch=True)

        return jsonify({
            "status": "healthy",
            "database": "connected",
            "llm": "enabled" if USE_LLM else "disabled"
        })

    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500
