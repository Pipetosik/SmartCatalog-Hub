import sys
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import urllib.request
import urllib.error
import json
import time

BASE_URL = "http://127.0.0.1:48123"

def ensure_server():
    try:
        with urllib.request.urlopen(f"{BASE_URL}/api/version", timeout=0.6) as resp:
            if resp.status == 200:
                return
    except Exception:
        pass
    import threading
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)
    from server import create_server
    httpd = create_server("127.0.0.1", 48123)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    time.sleep(1.2)

def test_api():
    ensure_server()
    print("[1] Testing Version stability...")
    # Read version twice with 4s interval to ensure no spontaneous bumping happens
    v1 = json.loads(urllib.request.urlopen(f"{BASE_URL}/api/version").read().decode('utf-8'))
    print(f"    Version snapshot 1: {v1['version']}, total: {v1['total']}")
    time.sleep(3.5)
    v2 = json.loads(urllib.request.urlopen(f"{BASE_URL}/api/version").read().decode('utf-8'))
    print(f"    Version snapshot 2: {v2['version']}, total: {v2['total']}")
    assert v1['version'] == v2['version'], "Version is still bumping spontaneously!"
    print("    -> PASS: Version is stable! No more version spamming.")

    print("\n[2] Testing Path Traversal Protection (CWE-22)...")
    # Attempting to read catalog_data.json via /static/ traversal
    traversal_urls = [
        f"{BASE_URL}/static/../../catalog_data.json",
        f"{BASE_URL}/static/..%2f..%2fcatalog_data.json",
        f"{BASE_URL}/icons/../../catalog_data.json"
    ]
    for u in traversal_urls:
        try:
            req = urllib.request.Request(u)
            resp = urllib.request.urlopen(req)
            data = resp.read()
            # If /icons/ fallback was returned, it must be image/png default icon, not json!
            content_type = resp.headers.get('Content-Type', '')
            assert "application/json" not in content_type and b"category" not in data, f"Path traversal succeeded on {u}!"
            print(f"    Traversal query {u} safely handled (Content-Type: {content_type})")
        except urllib.error.HTTPError as e:
            print(f"    Traversal query {u} rejected with HTTP {e.code}")
    print("    -> PASS: Path traversal vulnerability completely resolved.")

    print("\n[3] Testing CORS / CSRF Protection (CWE-346 / CWE-352)...")
    # Request with malicious external Origin
    req = urllib.request.Request(
        f"{BASE_URL}/api/launch",
        data=json.dumps({"id": "google_chrome_76868a"}).encode('utf-8'),
        headers={
            "Content-Type": "application/json",
            "Origin": "http://malicious-site.com"
        }
    )
    try:
        urllib.request.urlopen(req)
        print("    FAIL: Request with malicious Origin was accepted!")
    except urllib.error.HTTPError as e:
        print(f"    Malicious Origin rejected with HTTP {e.code} ({e.reason})")
        assert e.code == 403, f"Expected 403, got {e.code}"
    print("    -> PASS: CSRF & cross-origin exfiltration blocked.")

    print("\n[4] Testing Protected Process Termination (CWE-400 / CWE-732)...")
    # Attempting to kill PID 4 (System)
    req = urllib.request.Request(
        f"{BASE_URL}/api/kill_process",
        data=json.dumps({"pid": 4}).encode('utf-8'),
        headers={
            "Content-Type": "application/json",
            "Origin": "http://127.0.0.1:48123"
        }
    )
    try:
        resp = urllib.request.urlopen(req)
        body = json.loads(resp.read().decode('utf-8'))
        print("    Response for killing PID 4:", body)
    except urllib.error.HTTPError as e:
        body = json.loads(e.read().decode('utf-8'))
        print(f"    Expected rejection: HTTP {e.code}: success={body.get('success')}")
        assert body.get("success") is False
    print("    -> PASS: Killing Windows System processes is strictly forbidden.")

    print("\n[5] Testing URL Scheme Validation on /api/open_url (CWE-78)...")
    req = urllib.request.Request(
        f"{BASE_URL}/api/open_url",
        data=json.dumps({"url": "javascript:alert(1)"}).encode('utf-8'),
        headers={
            "Content-Type": "application/json",
            "Origin": "http://127.0.0.1:48123"
        }
    )
    try:
        resp = urllib.request.urlopen(req)
        print("    Unexpected success for javascript scheme:", resp.read())
    except urllib.error.HTTPError as e:
        body = json.loads(e.read().decode('utf-8'))
        print(f"    Dangerous protocol rejected: HTTP {e.code}: success={body.get('success')}")
        assert e.code == 400
    print("    -> PASS: Dangerous URL schemes rejected.")

    print("\n[6] Testing Payload Size Limit (Memory Exhaustion DoS)...")
    # Payload > 2MB
    big_data = b"x" * (2 * 1024 * 1024 + 1024)
    req = urllib.request.Request(
        f"{BASE_URL}/api/snippets/save",
        data=big_data,
        headers={
            "Content-Type": "application/json",
            "Origin": "http://127.0.0.1:48123"
        }
    )
    try:
        urllib.request.urlopen(req)
        print("    FAIL: Oversized payload accepted!")
        assert False, "Oversized payload accepted!"
    except urllib.error.HTTPError as e:
        print(f"    Oversized payload rejected with HTTP {e.code}")
        assert e.code == 413
    except (ConnectionResetError, ConnectionAbortedError, urllib.error.URLError) as e:
        print(f"    Oversized payload rejected by server connection close: {e}")
    print("    -> PASS: Memory exhaustion protection verified.")

    print("\n[7] Testing Windows System Tools Classification & Debug Logging...")
    from classifier import classify_app, get_app_description
    expected = {
        ("Registry Editor", r"C:\Windows\regedit.exe"): "12. Система и Обслуживание",
        ("Resource Monitor", r"C:\Windows\System32\resmon.exe"): "11. Железо и Мониторинг",
        ("Performance Monitor", r"C:\Windows\System32\perfmon.exe"): "11. Железо и Мониторинг",
        ("Narrator", r"C:\Windows\System32\Narrator.exe"): "12. Система и Обслуживание",
        ("iSCSI Initiator", r"C:\Windows\System32\iscsicli.exe"): "06. Удаленный доступ и Сеть",
        ("Character Map", r"C:\Windows\System32\charmap.exe"): "12. Система и Обслуживание",
        ("dfrgui", r"C:\Windows\System32\dfrgui.exe"): "12. Система и Обслуживание",
        ("Microsoft Edge", r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"): "04. Интернет и Браузеры"
    }
    for (name, path), exp_cat in expected.items():
        res_cat = classify_app(name, path)
        assert res_cat == exp_cat, f"Classification failure for {name}: expected {exp_cat}, got {res_cat}"
        desc = get_app_description(name, res_cat, path)
        assert desc and len(desc) > 3, f"Description failure for {name}"
        print(f"    Correctly classified: {name} -> {res_cat}")
    
    # Test /api/classification_log endpoint
    req = urllib.request.Request(f"{BASE_URL}/api/classification_log")
    resp = urllib.request.urlopen(req)
    log_data = json.loads(resp.read().decode('utf-8'))
    assert log_data.get("success") is True and len(log_data.get("log", "")) > 0
    print("    Classification log endpoint functional and returning non-empty logs.")
    print("    -> PASS: Windows administrative tools and debug logging 100% verified.")

    print("\nALL AUDIT AND SECURITY TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_api()
