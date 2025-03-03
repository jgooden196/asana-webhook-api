from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Railway! JP Asana Webhook API is running."

@app.route('/webhook', methods=['POST', 'GET'])
def asana_webhook():
    if request.method == 'GET':
        # Asana webhook validation request
        challenge = request.args.get('challenge')
        if challenge:
            return jsonify({'challenge': challenge})

    if request.method == 'POST':
        # Log the webhook event data
        data = request.json
        print("Webhook Event Received:", data)

        x_host_secret = request.headers.get('X-Host-Secret')  # Get the User-Agent header

        print("X-Host-Secret is ", x_host_secret)


        # You can process specific event types here
        return jsonify({"status": "received"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
