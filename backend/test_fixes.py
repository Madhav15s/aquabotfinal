#!/usr/bin/env python3
"""
Test script to verify all the fixes are working
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_status():
    """Test the status endpoint"""
    print("🔍 Testing Status Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data['status']}")
            print(f"📊 Services: {data['services']}")
        else:
            print(f"❌ Status failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Status error: {e}")

def test_vessel_tracking():
    """Test vessel tracking"""
    print("\n🚢 Testing Vessel Tracking...")
    try:
        payload = {
            "message": "Where is EVER GIVEN right now?",
            "user_id": "test_user",
            "use_context": True,
            "timestamp": "2024-01-15T10:00:00",
            "conversation_context": {"current_agent": "general"},
            "uploaded_documents": []
        }
        
        response = requests.post(f"{BASE_URL}/api/chat", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Agent: {data['agent']}")
            print(f"📝 Response: {data['text'][:100]}...")
        else:
            print(f"❌ Vessel tracking failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Vessel tracking error: {e}")

def test_cargo_matching():
    """Test cargo matching"""
    print("\n📦 Testing Cargo Matching...")
    try:
        payload = {
            "message": "cargo requirements for a voyage from singapore all the way through atlantic ocean",
            "user_id": "test_user",
            "use_context": True,
            "timestamp": "2024-01-15T10:00:00",
            "conversation_context": {"current_agent": "cargo_matching"},
            "uploaded_documents": []
        }
        
        response = requests.post(f"{BASE_URL}/api/chat", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Agent: {data['agent']}")
            print(f"📝 Response: {data['text'][:100]}...")
        else:
            print(f"❌ Cargo matching failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Cargo matching error: {e}")

def test_market_insights():
    """Test market insights"""
    print("\n📈 Testing Market Insights...")
    try:
        payload = {
            "message": "Bunker Prices",
            "user_id": "test_user",
            "use_context": True,
            "timestamp": "2024-01-15T10:00:00",
            "conversation_context": {"current_agent": "market_insights"},
            "uploaded_documents": []
        }
        
        response = requests.post(f"{BASE_URL}/api/chat", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Agent: {data['agent']}")
            print(f"📝 Response: {data['text'][:100]}...")
        else:
            print(f"❌ Market insights failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Market insights error: {e}")

def test_port_intelligence():
    """Test port intelligence"""
    print("\n🏠 Testing Port Intelligence...")
    try:
        payload = {
            "message": "port status",
            "user_id": "test_user",
            "use_context": True,
            "timestamp": "2024-01-15T10:00:00",
            "conversation_context": {"current_agent": "port_intelligence"},
            "uploaded_documents": []
        }
        
        response = requests.post(f"{BASE_URL}/api/chat", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Agent: {data['agent']}")
            print(f"📝 Response: {data['text'][:100]}...")
        else:
            print(f"❌ Port intelligence failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Port intelligence error: {e}")

def test_document_analysis():
    """Test document analysis"""
    print("\n📄 Testing Document Analysis...")
    try:
        payload = {
            "message": "What are the laytime clauses in the charter party?",
            "user_id": "test_user",
            "use_context": True,
            "timestamp": "2024-01-15T10:00:00",
            "conversation_context": {"current_agent": "general"},
            "uploaded_documents": []
        }
        
        response = requests.post(f"{BASE_URL}/api/chat", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Agent: {data['agent']}")
            print(f"📝 Response: {data['text'][:100]}...")
        else:
            print(f"❌ Document analysis failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Document analysis error: {e}")

def main():
    """Run all tests"""
    print("🧪 Testing IME Hub Maritime AI Assistant Fixes...")
    print("=" * 60)
    
    test_status()
    test_vessel_tracking()
    test_cargo_matching()
    test_market_insights()
    test_port_intelligence()
    test_document_analysis()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")

if __name__ == "__main__":
    main() 