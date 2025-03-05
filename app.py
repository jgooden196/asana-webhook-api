from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def asana_webhook():
    # Check if Asana is sending the X-Hook-Secret header for handshake
    x_hook_secret = request.headers.get('X-Hook-Secret')
    
    if x_hook_secret:
        response = jsonify({"message": "Handshake received"})
        response.headers['X-Hook-Secret'] = x_hook_secret
        return response, 200  # Asana requires 200 or 204 response

    # Process actual webhook events here (we will handle this later)
    return jsonify({"message": "Webhook received"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
