# asana-webhook-api

🛠 Asana Webhook API - Project Setup Summary
📂 Project Overview
This is a Flask-based webhook listener hosted on Railway, designed to interact with Asana webhooks.
It supports registering webhooks, listening for events, and logging received Asana events.
The repository is structured to handle both one-time webhook registration and ongoing event processing.
📂 Repository Files & Their Purpose
File	Purpose
app.py	Main Flask application that listens for Asana webhooks. Handles handshake and logs incoming events.
config.py	Stores the Asana API access token for authentication.
logging_config.py	Configures logging for debugging and monitoring webhook requests.
register_webhook.py	One-time script to manually register a webhook for a single Asana project.
register_all_webhooks.py	Script that loops through all projects in a workspace and registers webhooks for each one.
manual_trigger.py	A utility script (purpose unknown, possibly for testing).
requirements.txt	Specifies dependencies: Flask (API handling), Requests (HTTP calls), Gunicorn (server deployment).
Procfile	Defines how the application is run on Railway (Gunicorn starts app.py).
README.md	Documentation (currently not filled in).
🌍 Deployment & Execution
The app is hosted on Railway.
app.py is the main entry point, running with Gunicorn.
Webhooks post data to /webhook, and logs are available in Railway HTTP logs.
Webhook registration scripts (register_webhook.py and register_all_webhooks.py) are run manually to set up Asana webhooks.
🚀 Next Steps for Expanding This Project
Improve webhook processing

Store incoming events in a database for tracking.
Filter out unnecessary events before processing.
Automate webhook creation for all projects

Run register_all_webhooks.py on a schedule (e.g., via a cron job or Railway trigger).
Enhance logging & monitoring

Use a logging system like CloudWatch, Loggly, or a simple database.
💡 How to Use This Summary
Save this summary in your notes or README.md for quick reference.
When starting a new chat, paste this so the AI knows your exact setup.
Use this structure for future projects to keep everything clear.
🚀 Let me know what you want to build next!
