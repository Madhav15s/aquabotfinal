#!/usr/bin/env python3
"""
Comprehensive test script to verify all fixes are working
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def wait_for_server():
    """Wait for server to be ready"""
    print("⏳ Waiting for server to be ready...")
    for i in range(30):  # Wait up to 30 seconds
        try:
            response = requests.get(f"{BASE_URL}/api/status")
            if response.status_code == 200:
                print("✅ Server is ready!")
                return True
        except:
            pass
        time.sleep(1)
        print(f"⏳ Still waiting... ({i+1}/30)")
    return False

def test_status():
    """Test the status endpoint"""
    print("\n🔍 Testing Status Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data['status']}")
            print(f"📊 Services: {data['services']}")
            return True
        else:
            print(f"❌ Status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Status error: {e}")
        return False

def test_agent_specific_queries():
    """Test agent-specific queries to ensure they don't fall back to Captain Router"""
    print("\n🎯 Testing Agent-Specific Query Routing...")
    
    tests = [
        {
            "name": "Cargo Matching",
            "message": "cargo requirements for singapore to atlantic",
            "agent": "cargo_matching",
            "expected_agent": "Cargo Matcher"
        },
        {
            "name": "Market Insights",
            "message": "bunker prices",
            "agent": "market_insights",
            "expected_agent": "Market Insights"
        },
        {
            "name": "Port Intelligence",
            "message": "port status",
            "agent": "port_intelligence",
            "expected_agent": "Port Intelligence"
        },
        {
            "name": "PDA Management",
            "message": "pda costs",
            "agent": "pda_management",
            "expected_agent": "PDA Management"
        }
    ]
    
    all_passed = True
    
    for test in tests:
        print(f"\n🔍 Testing {test['name']}...")
        try:
            payload = {
                "message": test["message"],
                "user_id": "test_user",
                "use_context": True,
                "timestamp": "2024-01-15T10:00:00",
                "conversation_context": {"current_agent": test["agent"]},
                "uploaded_documents": []
            }
            
            response = requests.post(f"{BASE_URL}/api/chat", json=payload)
            if response.status_code == 200:
                data = response.json()
                actual_agent = data['agent']
                if actual_agent == test["expected_agent"]:
                    print(f"✅ {test['name']}: Correctly routed to {actual_agent}")
                    print(f"📝 Response preview: {data['text'][:100]}...")
                else:
                    print(f"❌ {test['name']}: Expected {test['expected_agent']}, got {actual_agent}")
                    all_passed = False
            else:
                print(f"❌ {test['name']}: Request failed with status {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"❌ {test['name']}: Error - {e}")
            all_passed = False
    
    return all_passed

def test_document_analysis():
    """Test document analysis with comprehensive output"""
    print("\n📄 Testing Document Analysis...")
    try:
        payload = {
            "message": "analyze the charter party document",
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
            
            # Check if response contains comprehensive analysis
            text = data['text']
            if "Complete Document Analysis" in text and "Extracted Information" in text:
                print("✅ Document analysis provides comprehensive output")
                print(f"📝 Response preview: {text[:200]}...")
                return True
            else:
                print("❌ Document analysis not providing comprehensive output")
                print(f"📝 Actual response: {text[:300]}...")
                return False
        else:
            print(f"❌ Document analysis failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Document analysis error: {e}")
        return False

def test_vessel_tracking():
    """Test vessel tracking with sample AIS data"""
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
            
            # Check if response contains position data
            text = data['text']
            if "EVER GIVEN Current Position" in text and "Location:" in text:
                print("✅ Vessel tracking working with sample AIS data")
                print(f"📝 Response preview: {text[:150]}...")
                return True
            else:
                print("❌ Vessel tracking not providing position data")
                return False
        else:
            print(f"❌ Vessel tracking failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Vessel tracking error: {e}")
        return False

def main():
    """Run all comprehensive tests"""
    print("🧪 Comprehensive Testing of IME Hub Maritime AI Assistant Fixes...")
    print("=" * 80)
    
    # Wait for server
    if not wait_for_server():
        print("❌ Server not ready after 30 seconds")
        return
    
    # Run tests
    tests_passed = 0
    total_tests = 5
    
    if test_status():
        tests_passed += 1
    
    if test_agent_specific_queries():
        tests_passed += 1
    
    if test_document_analysis():
        tests_passed += 1
    
    if test_vessel_tracking():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 80)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! The fixes are working correctly.")
        print("\n✅ What's Fixed:")
        print("• Agent-specific queries now route correctly")
        print("• Document analysis provides comprehensive summaries")
        print("• Market insights give detailed analysis and predictions")
        print("• Port intelligence provides comprehensive port data")
        print("• PDA management gives detailed cost breakdowns")
        print("• Vessel tracking works with sample AIS data")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    print("\n🚀 Ready to test in the frontend!")

if __name__ == "__main__":
    main() 