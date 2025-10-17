#!/usr/bin/env python3
"""
Test script to verify all chart endpoints are working correctly.
"""

import requests
import json

def test_chart_endpoints():
    """Test all chart data endpoints."""
    base_url = "http://127.0.0.1:5000"
    
    chart_types = ['bar', 'line', 'scatter', 'histogram']
    
    print("🧪 Testing Chart Endpoints")
    print("=" * 40)
    
    for chart_type in chart_types:
        try:
            url = f"{base_url}/api/chart-data/{chart_type}"
            print(f"\n📊 Testing {chart_type.upper()} chart: {url}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS: {len(data)} records returned")
                
                # Check data structure
                if data and isinstance(data, list):
                    sample = data[0]
                    print(f"   Sample keys: {list(sample.keys())}")
                else:
                    print(f"   Data type: {type(data)}")
                    
            else:
                print(f"❌ FAILED: HTTP {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ CONNECTION ERROR: {e}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON ERROR: {e}")
        except Exception as e:
            print(f"❌ UNEXPECTED ERROR: {e}")
    
    print("\n" + "=" * 40)
    print("🏁 Chart endpoint testing completed")

if __name__ == "__main__":
    test_chart_endpoints()