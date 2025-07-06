#!/usr/bin/env python3
"""
Get your network IP address for sharing the demo
"""
import socket
import subprocess
import platform

def get_local_ip():
    """Get the local IP address"""
    try:
        # Connect to a remote address to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def get_network_info():
    """Get network information"""
    local_ip = get_local_ip()
    
    print("=" * 50)
    print("🌐 NETWORK DEMO INFORMATION")
    print("=" * 50)
    print(f"📍 Your Local IP: {local_ip}")
    print(f"🔗 Demo URL: http://{local_ip}:5000/admin")
    print(f"🔐 Login: admin@restaurant.com / admin123")
    print()
    print("📱 Share this URL with your client!")
    print("=" * 50)
    
    return local_ip

if __name__ == "__main__":
    get_network_info() 