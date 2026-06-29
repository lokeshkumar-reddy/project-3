import http.server
import socketserver
import os
import json

PORT = 8000

# Helper to read/write JSON databases safely
def read_json_file(filepath, default_val):
    if not os.path.exists(filepath):
        write_json_file(filepath, default_val)
        return default_val
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default_val

def write_json_file(filepath, data):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error writing to {filepath}: {e}")
        return False

class StoreAPIRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers to all responses
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        # Handle preflight CORS requests
        self.send_response(200, "OK")
        self.end_headers()

    def do_GET(self):
        # Intercept database API endpoints
        if self.path == '/api/products':
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            data = read_json_file('db_products.json', [])
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
        elif self.path == '/api/deleted':
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            data = read_json_file('db_deleted.json', [])
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
        elif self.path == '/api/orders':
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            data = read_json_file('db_orders.json', [])
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
        else:
            # Fallback to serving static files
            super().do_GET()

    def do_POST(self):
        # Handle database updates
        if self.path in ['/api/products', '/api/deleted', '/api/orders']:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                parsed_data = json.loads(post_data.decode('utf-8'))
                
                # Save to corresponding file
                filename = 'db_products.json' if self.path == '/api/products' else (
                    'db_deleted.json' if self.path == '/api/deleted' else 'db_orders.json'
                )
                
                success = write_json_file(filename, parsed_data)
                
                if success:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": True}).encode('utf-8'))
                else:
                    self.send_response(500)
                    self.end_headers()
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(str(e).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    SEED_PRODUCTS = [
      {
        "id": 1,
        "name": "Urea Fertiliser (50kg Bag)",
        "category": "fertilisers",
        "price": 350,
        "stock": 25,
        "image": "🌾",
        "description": "High-quality nitrogenous fertiliser essential for boosting leafy green crop growth and crop health."
      },
      {
        "id": 2,
        "name": "DAP Fertiliser (50kg Bag)",
        "category": "fertilisers",
        "price": 1350,
        "stock": 18,
        "image": "📦",
        "description": "Diammonium Phosphate containing rich phosphate content for healthy root systems and early crop vigor."
      },
      {
        "id": 3,
        "name": "Organic Neem Oil Pesticide (1 Litre)",
        "category": "pesticides",
        "price": 280,
        "stock": 45,
        "image": "🧪",
        "description": "Cold-pressed pure organic neem oil pesticide. Safe bio-control against aphids, whiteflies, and scale pests."
      },
      {
        "id": 4,
        "name": "Hybrid Tomato Seeds (100g Pack)",
        "category": "seeds",
        "price": 150,
        "stock": 30,
        "image": "🍅",
        "description": "High germination rate hybrid tomato seeds, resistant to common wilt and leaf curl diseases."
      },
      {
        "id": 5,
        "name": "BT Cotton Seeds (450g Pack)",
        "category": "seeds",
        "price": 860,
        "stock": 12,
        "image": "🌱",
        "description": "Premium BT cotton seeds providing resistance to bollworms, ensuring high cotton crop yield."
      }
    ]

    # Initialize databases if they don't exist or are empty
    products = read_json_file('db_products.json', [])
    if not products:
        write_json_file('db_products.json', SEED_PRODUCTS)
        
    read_json_file('db_deleted.json', [])
    read_json_file('db_orders.json', [])
    
    # Run the server
    handler = StoreAPIRequestHandler
    # Allow address reuse to prevent "address already in use" errors during quick restarts
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"HKGN Agencies API Server running on port {PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
