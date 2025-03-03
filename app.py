from flask import Flask, request, jsonify, Response

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

        x_hook_secret = request.headers.get('X-Hook-Secret')  # Get the User-Agent header

        response = Response("This is a custom response:" + x_hook_secret )
        response.headers["X-Hook-Secret"] = x_hook_secret

        print("X-Hook-Secret is ", x_hook_secret)


        # You can process specific event types here
        return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
