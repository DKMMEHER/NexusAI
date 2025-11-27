import requests
import base64

# Valid 1x1 PNG
valid_png_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
valid_png = base64.b64decode(valid_png_b64)

with open('dummy1.png', 'wb') as f: f.write(valid_png)
with open('dummy2.png', 'wb') as f: f.write(valid_png)

url = "http://127.0.0.1:8002/image/virtual_try_on"
files = [
    ('product', ('dummy1.png', open('dummy1.png', 'rb'), 'image/png')),
    ('person', ('dummy2.png', open('dummy2.png', 'rb'), 'image/png'))
]
data = {'prompt': 'Test'}

try:
    response = requests.post(url, files=files, data=data)
    print(f"Status Code: {response.status_code}")
    import json
    try:
        err_json = json.loads(response.text)
        if "error" in err_json and isinstance(err_json["error"], str):
             inner_err = json.loads(err_json["error"])
             print(f"Inner Error: {json.dumps(inner_err, indent=2)}")
        else:
             print(f"Response Body: {response.text}")
    except Exception as parse_err:
        print(f"Could not parse error JSON: {parse_err}")
        print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")
