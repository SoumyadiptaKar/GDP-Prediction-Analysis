#!/usr/bin/env python3
"""
Production WSGI entry point for GDP Analytics
"""
import os
from app import create_app

# Get configuration from environment
config_name = os.environ.get('FLASK_ENV', 'production')

# Create application instance
application = create_app(config_name)

# For compatibility with some hosting services
app = application

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port)