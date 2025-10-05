from vertexai import init
from vertexai.generative_models import GenerativeModel

# Initialize Vertex AI
init(project="kaya-474008", location="us-central1")

# Load Gemini model
model = GenerativeModel("gemini-1.5-flash")

prompt = "Write a 1-sentence summary of the Kaya AI platform."
response = model.generate_content(prompt)

print("✅ Gemini Response:", response.text)
