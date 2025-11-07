# CyberSentinel-AI-SVM

CyberSentinel is a Flask-powered insider-threat monitoring platform that blends traditional anomaly detection (Isolation Forest and One-Class SVM) with LLM-based insights delivered through the Hugging Face inference router.

## Features
- Secure authentication with bcrypt-hashed passwords and session management
- Admin dashboard with real-time alert metrics, activity charts, and user management
- User dashboard for personal alert history and recent security activities
- AI microservice exposing manual anomaly analysis and retraining endpoints
- Responsive dark "hacker" UI theme with Bootstrap 5.3 and Font Awesome icons served locally

## Setup
1. Create and activate a virtual environment (optional but recommended).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment variables:
   - Copy `.env.example` to `.env` and adjust credentials or API keys as needed.
4. Initialise the MySQL schema:
   - Import `database/schema.sql` (includes sample data) into your MySQL server.
5. Run the Flask app:
   ```bash
   python app.py
   ```
6. Access the application at [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

## Environment Variables
Refer to `.env.example` for the full list. At minimum, configure database credentials and `SECRET_KEY`. To enable LLM insights for alerts, provide a valid `HF_API_KEY` with access to the Hugging Face inference router (create one at https://huggingface.co/settings/tokens and grant the `inference` scope). Tokens issued through Hugging Face can expire; if you start receiving `401 Unauthorized` responses from the router, generate a new token and update your `.env`.

## Project Structure
Refer to the directory tree below for an overview of the modules and their responsibilities.

```
CyberSentinel-AI-SVM/
+-- app.py               # Flask application factory, blueprint registration
+-- config.py            # Environment-driven configuration object
+-- database/            # Connection helpers, schema, and sample data
+-- routes/              # Auth, admin, user, and AI endpoints
+-- services/            # Domain services for users, alerts, and reporting
+-- ai_engine/           # Data preprocessing and anomaly detection models
+-- templates/           # Jinja templates for the dark UI theme
+-- static/              # CSS, JavaScript, and local asset bundles
```

## Development Notes
- The AI engine automatically warms up from historical activity logs on startup. Populate `activity_logs` with data to improve accuracy.
- Update `static/js/charts.js` for additional chart widgets, or extend the services for more sophisticated alert workflows.
- Contributions should include relevant unit or integration tests where applicable.
