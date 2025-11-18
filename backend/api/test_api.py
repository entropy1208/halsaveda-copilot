import requests
import json

API_URL = "http://localhost:8000"

# Test 1: Health check
print("="*70)
print("Test 1: Health Check")
print("="*70)
response = requests.get(f"{API_URL}/health")
print(json.dumps(response.json(), indent=2))

# Test 2: Stats
print("\n" + "="*70)
print("Test 2: System Stats")
print("="*70)
response = requests.get(f"{API_URL}/api/stats")
print(json.dumps(response.json(), indent=2))

# Test 3: Chat
print("\n" + "="*70)
print("Test 3: Chat")
print("="*70)

questions = [
    "What should I do for a cold?",
    "When should I see a doctor for fever?",
    "Hur behandlar man förkylning?"
]

for question in questions:
    print(f"\n❓ Question: {question}")
    
    response = requests.post(
        f"{API_URL}/api/chat",
        json={"question": question, "top_k": 2}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n🤖 Answer:\n{data['answer']}")
        print(f"\n📚 Sources:")
        for i, source in enumerate(data['sources'], 1):
            print(f"   [{i}] {source['title']} (score: {source['score']:.3f})")
    else:
        print(f"❌ Error: {response.status_code}")
    
    print("\n" + "-"*70)

print("\n✅ API tests complete!")