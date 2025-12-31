import requests
import json

url = "http://localhost:8000/api/test/start-v3"
payload = {
    "student_id": "test_student",
    "class_level": 11,
    "subject": "Chemistry",
    "chapter_number": 1,
    "topic_id": "all",
    "num_questions": 5,
    "difficulty": "mixed",
    "auto_generate": True
}

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    with open("verify_output.txt", "w") as f:
        try:
            f.write(json.dumps(response.json(), indent=2))
        except:
            f.write(response.text)
    print("Output written to verify_output.txt")
except Exception as e:
    print(f"Error: {e}")
