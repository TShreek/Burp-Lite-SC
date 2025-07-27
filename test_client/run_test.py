#!/usr/bin/env python3
"""
Test Client for Burp-Lite
Sends a series of requests through the proxy to demonstrate functionality
"""
import requests
import json
import time
import random
import argparse
import sys

PROXY_URL = "http://localhost:8080"  # Default proxy URL
TARGET_URL = "http://localhost:5000"  # Direct to target (for comparison)

# Test data for messaging app
USERS = ["alice", "bob", "charlie", "dave", "eve"]
MESSAGES = [
    "Hello there!",
    "How are you doing?",
    "Just testing this messaging app",
    "This message will be intercepted by Burp-Lite",
    "Security testing in progress...",
    "This is a confidential message with password: MySecret123!",
    "My credit card is 4111-1111-1111-1111 (not really)",
    "API key for testing: sk_test_abcdef123456789",
    "JWT token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ"
]


def send_message(proxy=True):
    """Send a random message between two users"""
    sender = random.choice(USERS)
    receiver = random.choice([u for u in USERS if u != sender])
    message = random.choice(MESSAGES)
    
    payload = {
        "from": sender,
        "to": receiver,
        "message": message
    }
    
    url = f"{PROXY_URL if proxy else TARGET_URL}/send"
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        status = "✅" if response.status_code == 200 else "❌"
        print(f"{status} Sent message from {sender} to {receiver}: {response.status_code}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending message: {e}")
        return False


def get_inbox(username, proxy=True):
    """Get the inbox for a user"""
    url = f"{PROXY_URL if proxy else TARGET_URL}/inbox/{username}"
    
    try:
        response = requests.get(url)
        
        status = "✅" if response.status_code == 200 else "❌"
        message_count = len(response.json().get("inbox", [])) if response.status_code == 200 else 0
        print(f"{status} Got inbox for {username}: {message_count} messages")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting inbox: {e}")
        return False


def run_test_sequence(count=10, proxy=True, delay=1):
    """Run a sequence of test requests"""
    print(f"\n🚀 Starting test sequence with {'proxy' if proxy else 'direct'} mode")
    print(f"🎯 Target: {PROXY_URL if proxy else TARGET_URL}")
    
    successes = 0
    
    # Send some messages
    for i in range(count):
        if send_message(proxy):
            successes += 1
        time.sleep(delay)
    
    # Check inboxes
    for user in USERS:
        if get_inbox(user, proxy):
            successes += 1
        time.sleep(delay)
    
    # Try some error cases (if using proxy)
    if proxy:
        try:
            # Bad JSON
            response = requests.post(
                f"{PROXY_URL}/send",
                data="This is not JSON",
                headers={"Content-Type": "application/json"}
            )
            print(f"❌ Sent invalid JSON: {response.status_code}")
        except requests.exceptions.RequestException:
            pass
        
        # Invalid endpoint
        try:
            response = requests.get(f"{PROXY_URL}/not-found")
            print(f"❌ Requested invalid endpoint: {response.status_code}")
        except requests.exceptions.RequestException:
            pass
    
    total_requests = count + len(USERS) + (2 if proxy else 0)
    success_rate = (successes / total_requests) * 100
    
    print(f"\n✨ Test sequence completed: {successes}/{total_requests} successful ({success_rate:.1f}%)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test client for Burp-Lite proxy")
    parser.add_argument("-d", "--direct", action="store_true", help="Send requests directly to target (bypass proxy)")
    parser.add_argument("-c", "--count", type=int, default=10, help="Number of messages to send")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between requests in seconds")
    parser.add_argument("--proxy-url", type=str, default=PROXY_URL, help="Proxy URL")
    parser.add_argument("--target-url", type=str, default=TARGET_URL, help="Target URL")
    
    args = parser.parse_args()
    
    # Update global URLs if specified
    if args.proxy_url != PROXY_URL:
        PROXY_URL = args.proxy_url
    if args.target_url != TARGET_URL:
        TARGET_URL = args.target_url
    
    run_test_sequence(count=args.count, proxy=not args.direct, delay=args.delay)
