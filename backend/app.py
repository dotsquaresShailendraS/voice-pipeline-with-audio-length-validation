from flask import Flask, jsonify, request

app = Flask(__name__)

MAX_WORDS = 150

@app.route("/trim-response", methods=['POST'])
def trim_text_api():
    
    data = request.get_json()
    # Check if 'text' key is provided in the JSON data
    if 'text' not in data:
        return jsonify({"error": "No text provided"}), 400
    
    text = data['text']
    words = text.split()
    # Calculate how many words to trim from each side
    total_words = len(words)
    if total_words <= MAX_WORDS:
        return jsonify({"message": data['text']}), 200  
    
    # Calculate how many words to remove from both sides
    words_to_trim = total_words - MAX_WORDS
    words_to_remove_from_each_side = words_to_trim // 2
    
    # Trim the words from both sides
    trimmed_words = words[words_to_remove_from_each_side: total_words - words_to_remove_from_each_side]
    
    # Join the words back into a string
    trimmed_text = ' '.join(trimmed_words)
    return jsonify({"message": trimmed_text}), 200

if __name__ == "__main__":
    app.run(debug=True)
