#!/usr/bin/env python3
"""
Production server runner for Restaurant Booker
"""
import os
import sys
from app import app

if __name__ == '__main__':
    # Production settings
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"🚀 Starting Restaurant Booker Server...")
    print(f"📍 Server will be available at: http://{host}:{port}")
    print(f"🔐 Admin login: admin@restaurant.com / admin123")
    print(f"📊 Admin panel: http://{host}:{port}/admin")
    print(f"🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        app.run(
            host=host,
            port=port,
            debug=False,  # Set to False for production
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
        sys.exit(0) 