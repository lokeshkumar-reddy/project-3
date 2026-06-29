import socketio
import eventlet
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

# Initialize socketio server
sio = socketio.Server(cors_allowed_origins='*')

# Define Socket.io events
@sio.event
def connect(sid, environ):
    print(f"Client connected: {sid}")
    # Immediately send the current database state to the newly connected client
    products = read_json_file('db_products.json', [])
    deleted = read_json_file('db_deleted.json', [])
    orders = read_json_file('db_orders.json', [])
    
    sio.emit('init_data', {
        'products': products,
        'deleted': deleted,
        'orders': orders
    }, room=sid)

@sio.event
def update_products(sid, data):
    print("Received update_products")
    write_json_file('db_products.json', data)
    # Broadcast to all clients except sender
    sio.emit('products_updated', data, skip_sid=sid)

@sio.event
def update_deleted(sid, data):
    print("Received update_deleted")
    write_json_file('db_deleted.json', data)
    sio.emit('deleted_updated', data, skip_sid=sid)

@sio.event
def update_orders(sid, data):
    print("Received update_orders")
    write_json_file('db_orders.json', data)
    sio.emit('orders_updated', data, skip_sid=sid)

@sio.event
def disconnect(sid):
    print(f"Client disconnected: {sid}")

# Define seed products
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

# Initialize files
if not os.path.exists('db_products.json') or not read_json_file('db_products.json', []):
    write_json_file('db_products.json', SEED_PRODUCTS)
read_json_file('db_deleted.json', [])
read_json_file('db_orders.json', [])

# Wrap with WSGI application to serve static files
app = socketio.WSGIApp(sio, static_files={
    '/': './index.html',
    '/index.html': './index.html',
    '/app.js': './app.js',
    '/style.css': './style.css',
    '/checkout.html': './checkout.html',
    '/checkout.js': './checkout.js',
    '/checkout.css': './checkout.css',
    '/worker.js': './worker.js',
    '/assets': './assets'
})

if __name__ == '__main__':
    print(f"HKGN Agencies Real-time Socket.io Server running on port {PORT}")
    eventlet.wsgi.server(eventlet.listen(('', PORT)), app)
