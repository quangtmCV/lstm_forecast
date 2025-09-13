#!/usr/bin/env python3
"""
Test script for web dashboard
"""

import sys
import os
sys.path.append('src')

from web_dashboard import WebDashboard, create_templates

def test_web_dashboard():
    """Test the web dashboard with sample data"""
    print("🧪 Testing Web Dashboard...")
    
    # Create templates
    create_templates()
    print("✅ Templates created")
    
    # Create dashboard
    dashboard = WebDashboard()
    print("✅ Dashboard initialized")
    
    # Sample forecast data
    sample_forecasts = [
        {'QV2M': 0.75, 'GWETROOT': 0.65},
        {'QV2M': 0.78, 'GWETROOT': 0.68},
        {'QV2M': 0.72, 'GWETROOT': 0.62}
    ]
    
    # Update forecast data
    dashboard.update_forecast(sample_forecasts)
    print("✅ Sample data loaded")
    
    print("\n🌐 Web dashboard is ready!")
    print("Open your browser and go to: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop the server")
    
    try:
        dashboard.run(debug=True)
    except KeyboardInterrupt:
        print("\n👋 Test completed")

if __name__ == "__main__":
    test_web_dashboard()
