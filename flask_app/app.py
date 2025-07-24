from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory message store (for demo)
messages = []

@app.route('/')
def index():
    return "📬 Flask Messaging App Running"

@app.route('/send', methods=['POST'])
def send_message():
    data = request.get_json()
    if not data or not all(k in data for k in ('from', 'to', 'message')):
        return jsonify({"error": "Missing fields"}), 400

    messages.append(data)
    print("📨 Message received:", data)
    return jsonify({"status": "Message received", "data": data}), 200

@app.route('/inbox/<username>', methods=['GET'])
def get_inbox(username):
    inbox = [msg for msg in messages if msg['to'] == username]
    return jsonify({"inbox": inbox}), 200

if __name__ == '__main__':
    print("✅ Flask app running on port 5000")
    app.run(port=5000)

