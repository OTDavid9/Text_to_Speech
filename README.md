# Text_to_Speech

# Kokoro TTS (Text-to-Speech) Service

A FastAPI-based Text-to-Speech (TTS) service using the Kokoro TTS model.  
It provides an API to convert text to audio using multiple voice options and a web-based client for easy interaction.  
The service is persistent with systemd and publicly accessible via NGINX reverse proxy.

---

## 🚀 Features

- ✅ FastAPI backend for TTS generation
- ✅ Multiple dynamic voice selections
- ✅ Web client (HTML + JavaScript)
- ✅ CORS enabled
- ✅ Persistent background service using systemd
- ✅ Public exposure via NGINX reverse proxy

---

## 📂 Project Structure

```text
.
├── app.py                 # FastAPI application
├── voice_choices.json     # Available voice options
├── templates/
│   └── index.html         # Web client interface
├── static/                # Static files (optional)
├── .env                   # Environment variables
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation

##  Setup Instructions
1. Clone the Repository
bash
Copy
Edit
git clone <your-repository-url>
cd <project-directory>
2. Create and Activate a Virtual Environment
bash
Copy
Edit
python3 -m venv .venv
source .venv/bin/activate
3. Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt
4. Run the FastAPI Server Locally
bash
Copy
Edit
uvicorn app:app --host 0.0.0.0 --port 8000
5. Run the FastAPI Server Persistently with systemd
Create a systemd Service File
ini
Copy
Edit
# /etc/systemd/system/tts.service

[Unit]
Description=Kokoro TTS Service
After=network.target

[Service]
User=your-username
WorkingDirectory=/path/to/your/project
ExecStart=/path/to/your/project/.venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
Enable and Start the Service
bash
Copy
Edit
sudo systemctl enable tts.service
sudo systemctl start tts.service
6. Configure NGINX Reverse Proxy
Example Configuration
nginx
Copy
Edit
server {
    listen 80;
    server_name your-public-ip;

    location / {
        proxy_pass http://localhost:11434;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Content-Type "application/json";
    }

    location /tts/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        rewrite ^/tts/(.*)$ /$1 break;
    }
}
Activate the NGINX Configuration
bash
Copy
Edit
sudo ln -s /etc/nginx/sites-available/ollama_tts /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
🌐 Access the Web Client
Open your browser and navigate to:

arduino
Copy
Edit
http://your-public-ip/tts
📡 API Endpoints
POST /generate-audio
Description: Generate audio from input text.

Request Body:

json
Copy
Edit
{
    "text": "Your text here",
    "voice": "Selected voice name"
}
Response: Audio stream (WAV)

GET /voices
Description: Fetch available voice options.

Response:

json
Copy
Edit
{
    "Voice Name 1": "Voice ID 1",
    "Voice Name 2": "Voice ID 2",
    ...
}
⚙️ Environment Configuration
Set your FastAPI base URL in the .env file:

env
Copy
Edit
API_BASE_URL=http://127.0.0.1:8000
For production, set it to:

env
Copy
Edit
API_BASE_URL=http://your-public-ip/tts
✅ Notes
Ensure your VM’s firewall allows port 80.

For secure deployment, consider using HTTPS with Certbot and Let’s Encrypt.

You can combine multiple NGINX services in a single configuration file or keep them separate.

📜 License
MIT License

🙏 Credits
Kokoro TTS Model

FastAPI

Uvicorn

NGINX

yaml
Copy
Edit

---

If you would like, I can help you create the actual badges (like build status, license badge, etc.) and a deployment diagram next!







