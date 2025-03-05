from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Asana Webhook API is running", 200

@app.route("/webhook", methods=["POST"])
def asana_webhook():
    """Handles incoming webhook events from Asana"""

    # Handle Asana's handshake verification
    x_hook_secret = request.headers.get('X-Hook-Secret')
    
    if x_hook_secret:
        logger.info(f"Received handshake request from Asana. Returning X-Hook-Secret: {x_hook_secret}")
        response = jsonify({"message": "Handshake received"})
        response.headers['X-Hook-Secret'] = x_hook_secret
        return response, 200  # Asana requires 200 or 204 response

    # Log received event
    event_data = request.json
    logger.info(f"Received webhook event: {event_data}")

    return jsonify({"message": "Webhook received"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
