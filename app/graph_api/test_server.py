"""
Graph Data API Test Script

Verifies all API endpoints are working correctly.

Usage:
    # Start the server first
    python -m app.graph_api.server --port 8081
    
    # Then run tests
    python -m app.graph_api.test_server
"""

import json
import sys
import urllib.request
import urllib.error
from typing import Tuple, Optional

# Test configuration
BASE_URL = "http://localhost:8081/api"
DB_NAME = "2025-12"


def make_request(path: str, method: str = "GET") -> Tuple[Optional[dict], int, Optional[str]]:
    """Make HTTP request and return (response_data, status_code, error)"""
    url = f"{BASE_URL}/{path}"
    if "?" in path:
        url = f"{BASE_URL}/{path}&db_name={DB_NAME}"
    else:
        url = f"{BASE_URL}/{path}?db_name={DB_NAME}"
    
    try:
        req = urllib.request.Request(url, method=method)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data, response.status, None
    except urllib.error.HTTPError as e:
        try:
            data = json.loads(e.read().decode())
        except:
            data = None
        return data, e.code, str(e)
    except Exception as e:
        return None, 0, str(e)


def test_endpoint(name: str, path: str, expected_keys: list = None) -> bool:
    """Test an endpoint and report results"""
    print(f"\n  Testing: {name}")
    print(f"  URL: {BASE_URL}/{path}")
    
    data, status, error = make_request(path)
    
    if error and status == 0:
        print(f"  ❌ Connection error: {error}")
        return False
    
    print(f"  Status: {status}")
    
    if status == 200:
        if expected_keys:
            missing = [k for k in expected_keys if k not in (data or {})]
            if missing:
                print(f"  ⚠️  Missing keys: {missing}")
                return False
        print(f"  ✅ OK")
        return True
    elif status == 404 and "error" in (data or {}):
        # 404 for resources is acceptable (e.g., entity not found)
        print(f"  ✅ OK (404 - resource not found)")
        return True
    else:
        print(f"  ❌ Failed: {data or error}")
        return False


def run_tests():
    """Run all API tests"""
    print("=" * 60)
    print("Graph Data API Test Suite")
    print("=" * 60)
    
    results = []
    
    # Test health
    print("\n📋 Health Check")
    results.append(test_endpoint(
        "Health",
        "health",
        ["status", "version", "timestamp"]
    ))
    
    # Test entities
    print("\n📋 Entity Endpoints")
    results.append(test_endpoint(
        "Search entities",
        "entities/search?limit=5",
        ["entities", "total", "limit", "offset", "has_more"]
    ))
    results.append(test_endpoint(
        "Get entity (may 404)",
        "entities/test_entity",
        []  # May return error for non-existent entity
    ))
    
    # Test communities
    print("\n📋 Community Endpoints")
    results.append(test_endpoint(
        "Search communities",
        "communities/search?limit=5",
        ["communities", "total"]
    ))
    results.append(test_endpoint(
        "Get community levels",
        "communities/levels",
        ["levels"]
    ))
    
    # Test relationships
    print("\n📋 Relationship Endpoints")
    results.append(test_endpoint(
        "Search relationships",
        "relationships/search?limit=5",
        ["relationships", "total"]
    ))
    
    # Test ego network
    print("\n📋 Ego Network Endpoints")
    results.append(test_endpoint(
        "Get ego network (may 404)",
        "ego/network/test_entity?max_hops=2&max_nodes=10",
        []  # May return error for non-existent entity
    ))
    
    # Test export
    print("\n📋 Export Endpoints")
    results.append(test_endpoint(
        "Export JSON",
        "export/json",
        ["nodes", "links", "metadata"]
    ))
    
    # Test statistics
    print("\n📋 Statistics Endpoints")
    results.append(test_endpoint(
        "Get statistics",
        "statistics",
        ["total_entities", "total_relationships"]
    ))
    
    # Test metrics
    print("\n📋 Metrics Endpoints")
    results.append(test_endpoint(
        "Get quality metrics",
        "metrics/quality",
        []  # Structure varies
    ))
    results.append(test_endpoint(
        "Get performance metrics",
        "metrics/performance",
        []  # May return error if no runs exist
    ))
    
    # Summary
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print(f"❌ {total - passed} tests failed")
        return 1


if __name__ == "__main__":
    # Check if server is running
    print("Checking if server is running...")
    data, status, error = make_request("health")
    
    if status == 0:
        print(f"❌ Cannot connect to server at {BASE_URL}")
        print("   Please start the server first:")
        print("   python -m app.graph_api.server --port 8081")
        sys.exit(1)
    
    print(f"✅ Server is running (status: {status})")
    
    # Run tests
    sys.exit(run_tests())

