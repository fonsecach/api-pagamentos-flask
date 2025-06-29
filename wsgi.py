"""WSGI entry point for the Flask application."""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from app import create_app
    
    # Create the application instance
    application = create_app()
    
    # For compatibility with different WSGI servers
    app = application
    
    if __name__ == "__main__":
        application.run(debug=True)
        
except Exception as e:
    print(f"Error loading application: {e}")
    import traceback
    traceback.print_exc()
    raise