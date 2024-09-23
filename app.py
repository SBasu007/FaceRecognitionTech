from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import face_recognition
from supabase import create_client, Client
import requests
from pyngrok import ngrok
from io import BytesIO

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


url = 'https://nugiatmiookgymvefbiz.supabase.co'
key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im51Z2lhdG1pb29rZ3ltdmVmYml6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjY5OTAzNjcsImV4cCI6MjA0MjU2NjM2N30.dScggB_4aimy3lBNOD7mTx0RdLetBptk7RmnCzlSBSM'
supabase: Client = create_client(url, key)

def fetch_criminals():
    response = supabase.table('criminals').select('name, image_url').execute()
    return response.data

criminals_data = fetch_criminals()

def prepare_face_encodings(criminals_data):
    encodings = []
    names = []
    for criminal in criminals_data:
        response = requests.get(criminal['image_url'])
        image = face_recognition.load_image_file(BytesIO(response.content))
        encoding = face_recognition.face_encodings(image)
        if encoding:
            encodings.append(encoding[0])
            names.append(criminal['name'])
    return encodings, names

encodings, names = prepare_face_encodings(criminals_data)

@app.route('/recognize', methods=['POST'])
def recognize_face():
    data = request.json
    image_url = data.get('image_url')
    response = requests.get(image_url)
    input_image = face_recognition.load_image_file(BytesIO(response.content))
    input_encodings = face_recognition.face_encodings(input_image)

    matches_info = []
    for input_encoding in input_encodings:
        results = face_recognition.compare_faces(encodings, input_encoding)
        for i, match in enumerate(results):
            if match:
                matches_info.append((names[i], criminals_data[i]['image_url']))

    return jsonify(matches_info)

if __name__ == '__main__':
    public_url = ngrok.connect(5000)  # Expose port 5000 to public
    print("Public URL:", public_url)
    app.run()
