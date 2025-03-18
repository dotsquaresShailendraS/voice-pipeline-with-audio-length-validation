from flask import Flask, jsonify, request

app = Flask(__name__)

MAX_WORDS = 150

@app.route("/flask-api", methods=['POST'])
def trim_text_api():
    
    data = request.get_json()
    text = data['text']
    words = text.split()
    # Calculate how many words to trim 
    total_words = len(words)
    if total_words <= MAX_WORDS:
        return jsonify({"message": data['text']}), 200  
    
    # Trim the words from both sides
    trimmed_words = words[:MAX_WORDS]
    
    # Join the words back into a string
    trimmed_text = ' '.join(trimmed_words)
    return jsonify({"message": trimmed_text}), 200

if __name__ == "__main__":
    app.run(debug=True)
