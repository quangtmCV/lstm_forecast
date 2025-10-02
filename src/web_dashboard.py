#!/usr/bin/env python3
"""
Web Dashboard for LSTM Weather Forecast
Simple web interface to display forecast results
"""

from flask import Flask, render_template, jsonify, request
import json
import os
from datetime import datetime, timedelta
import threading
import time

class WebDashboard:
    """Web dashboard for weather forecast results"""
    
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.forecast_data = {}
        self.setup_routes()
        
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main dashboard page"""
            return render_template('dashboard.html', 
                                 forecast_data=self.forecast_data,
                                 current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        @self.app.route('/api/forecast')
        def api_forecast():
            """API endpoint for forecast data"""
            return jsonify(self.forecast_data)
        
        @self.app.route('/api/status')
        def api_status():
            """API endpoint for system status"""
            return jsonify({
                'status': 'running',
                'last_update': datetime.now().isoformat(),
                'has_forecast': len(self.forecast_data) > 0
            })
    
    def update_forecast(self, forecasts, base_date=None):
        """Update forecast data"""
        if base_date is None:
            base_date = datetime.now().date()
            
        self.forecast_data = {
            'forecasts': [],
            'last_update': datetime.now().isoformat(),
            'base_date': base_date.isoformat()
        }
        
        for i, forecast in enumerate(forecasts):
            forecast_date = base_date + timedelta(days=i+1)
            self.forecast_data['forecasts'].append({
                'date': forecast_date.isoformat(),
                'date_formatted': forecast_date.strftime('%Y-%m-%d'),
                'day_name': forecast_date.strftime('%A'),
                'qv2m': round(forecast.get('QV2M', 0), 4),
                'gwetroot': round(forecast.get('GWETROOT', 0), 4),
                'irrigation_net_mm': round(forecast.get('IRRIGATION_NET_MM', 0.0), 2),
                'irrigation_gross_mm': round(forecast.get('IRRIGATION_GROSS_MM', 0.0), 2),
                'depletion_frac': round(forecast.get('DEPLETION_FRAC', 0.0), 3)
            })
    
    def run(self, debug=False):
        """Run the web server"""
        print(f"🌐 Starting web dashboard at http://{self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, debug=debug, use_reloader=False)
    
    def run_async(self):
        """Run web server in background thread"""
        def run_server():
            self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False)
        
        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()
        time.sleep(1)  # Give server time to start
        print(f"🌐 Web dashboard started at http://{self.host}:{self.port}")
        return thread

def create_templates():
    """Create HTML templates for the web dashboard"""
    
    # Create templates directory
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # Dashboard HTML template
    dashboard_html = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LSTM Weather Forecast Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .status-bar {
            background: #f8f9fa;
            padding: 15px 30px;
            border-bottom: 1px solid #e9ecef;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .status-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #28a745;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .forecast-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            padding: 30px;
        }
        
        .forecast-card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            border: 1px solid #e9ecef;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .forecast-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.15);
        }
        
        .forecast-date {
            font-size: 1.4em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }
        
        .forecast-day {
            color: #7f8c8d;
            font-size: 1em;
            margin-bottom: 20px;
        }
        
        .forecast-metrics {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        
        .metric {
            text-align: center;
            padding: 15px;
            border-radius: 8px;
            background: #f8f9fa;
        }
        
        .metric-label {
            font-size: 0.9em;
            color: #6c757d;
            margin-bottom: 8px;
            font-weight: 500;
        }
        
        .metric-value {
            font-size: 1.8em;
            font-weight: bold;
            color: #2c3e50;
        }
        
        .qv2m {
            background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
            color: white;
        }
        
        .qv2m .metric-label,
        .qv2m .metric-value {
            color: white;
        }
        
        .gwetroot {
            background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
            color: white;
        }
        
        .gwetroot .metric-label,
        .gwetroot .metric-value {
            color: white;
        }
        
        .no-data {
            text-align: center;
            padding: 60px 30px;
            color: #6c757d;
        }
        
        .no-data h3 {
            font-size: 1.5em;
            margin-bottom: 10px;
        }
        
        .refresh-btn {
            background: linear-gradient(135deg, #fd79a8 0%, #e84393 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1em;
            font-weight: 500;
            transition: transform 0.2s ease;
        }
        
        .refresh-btn:hover {
            transform: scale(1.05);
        }
        
        .footer {
            background: #2c3e50;
            color: white;
            padding: 20px 30px;
            text-align: center;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌤️ LSTM Weather Forecast</h1>
            <p>Hệ thống dự báo thời tiết thông minh</p>
        </div>
        
        <div class="status-bar">
            <div class="status-item">
                <div class="status-dot"></div>
                <span>Hệ thống đang hoạt động</span>
            </div>
            <div class="status-item">
                <span>Cập nhật lần cuối: {{ current_time }}</span>
            </div>
            <button class="refresh-btn" onclick="refreshData()">🔄 Làm mới</button>
        </div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Đang tải dữ liệu...</p>
        </div>
        
        <div class="forecast-grid" id="forecastGrid">
            {% if forecast_data.forecasts %}
                {% for forecast in forecast_data.forecasts %}
                <div class="forecast-card">
                    <div class="forecast-date">{{ forecast.date_formatted }}</div>
                    <div class="forecast-day">{{ forecast.day_name }}</div>
                    <div class="forecast-metrics">
                        <div class="metric qv2m">
                            <div class="metric-label">💧 Độ ẩm tương đối</div>
                            <div class="metric-value">{{ forecast.qv2m }}</div>
                        </div>
                        <div class="metric gwetroot">
                            <div class="metric-label">🌱 Độ ẩm đất</div>
                            <div class="metric-value">{{ forecast.gwetroot }}</div>
                        </div>
                        <div class="metric" style="background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%); color: white;">
                            <div class="metric-label" style="color: white;">🚿 Lượng tưới (NET, mm)</div>
                            <div class="metric-value" style="color: white;">{{ forecast.irrigation_net_mm }}</div>
                        </div>
                        <div class="metric" style="background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%); color: white;">
                            <div class="metric-label" style="color: white;">🚜 Lượng tưới (GROSS, mm)</div>
                            <div class="metric-value" style="color: white;">{{ forecast.irrigation_gross_mm }}</div>
                        </div>
                        <div class="metric" style="background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%); color: white;">
                            <div class="metric-label" style="color: white;">📉 Mức cạn kiệt AWC</div>
                            <div class="metric-value" style="color: white;">{{ forecast.depletion_frac }}</div>
                        </div>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <div class="no-data">
                    <h3>📊 Chưa có dữ liệu dự báo</h3>
                    <p>Hệ thống đang chờ dữ liệu mới. Vui lòng thử lại sau.</p>
                </div>
            {% endif %}
        </div>
        
        <div class="footer">
            <p>© 2025 LSTM Weather Forecast System | Powered by AI & NASA POWER API</p>
        </div>
    </div>

    <script>
        function refreshData() {
            document.getElementById('loading').style.display = 'block';
            document.getElementById('forecastGrid').style.display = 'none';
            
            fetch('/api/forecast')
                .then(response => response.json())
                .then(data => {
                    setTimeout(() => {
                        location.reload();
                    }, 1000);
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('forecastGrid').style.display = 'grid';
                });
        }
        
        // Auto refresh every 5 minutes
        setInterval(refreshData, 300000);
        
        // Show loading on page load
        window.addEventListener('load', function() {
            document.getElementById('loading').style.display = 'none';
        });
    </script>
</body>
</html>"""
    
    # Write dashboard template
    with open(os.path.join(templates_dir, 'dashboard.html'), 'w', encoding='utf-8') as f:
        f.write(dashboard_html)
    
    print("✅ Web templates created successfully")

if __name__ == "__main__":
    # Test the web dashboard
    create_templates()
    dashboard = WebDashboard()
    
    # Sample forecast data for testing
    sample_forecasts = [
        {'QV2M': 0.75, 'GWETROOT': 0.65},
        {'QV2M': 0.78, 'GWETROOT': 0.68}
    ]
    dashboard.update_forecast(sample_forecasts)
    
    print("🌐 Starting web dashboard...")
    dashboard.run(debug=True)
