import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "restaurant-booking-secret-key")

# Admin credentials (in production, store in database)
ADMIN_EMAIL = "admin@restaurant.com"
ADMIN_PASSWORD_HASH = generate_password_hash("admin123")

def load_dishes():
    """Load dishes from JSON file"""
    try:
        with open('data/dishes.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_dishes(dishes):
    """Save dishes to JSON file"""
    os.makedirs('data', exist_ok=True)
    with open('data/dishes.json', 'w') as f:
        json.dump(dishes, f, indent=2)

def load_bookings():
    """Load bookings from JSON file"""
    try:
        with open('data/bookings.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_bookings(bookings):
    """Save bookings to JSON file"""
    os.makedirs('data', exist_ok=True)
    with open('data/bookings.json', 'w') as f:
        json.dump(bookings, f, indent=2)

@app.route('/')
def index():
    """Customer homepage showing available dishes"""
    dishes = load_dishes()
    return render_template('index.html', dishes=dishes)

@app.route('/book/<int:dish_id>')
def book_dish(dish_id):
    """Show booking form for a specific dish"""
    dishes = load_dishes()
    if dish_id >= len(dishes) or dishes[dish_id]['available_quantity'] <= 0:
        flash('This dish is not available for booking.', 'error')
        return redirect(url_for('index'))
    
    dish = dishes[dish_id]
    return render_template('booking.html', dish=dish, dish_id=dish_id)

@app.route('/book/<int:dish_id>', methods=['POST'])
def process_booking(dish_id):
    """Process the booking form submission"""
    dishes = load_dishes()
    
    # Validate dish availability
    if dish_id >= len(dishes) or dishes[dish_id]['available_quantity'] <= 0:
        flash('Sorry, this dish is no longer available.', 'error')
        return redirect(url_for('index'))
    
    # Get form data
    customer_name = request.form.get('customer_name', '').strip()
    contact_number = request.form.get('contact_number', '').strip()
    
    # Validate form data
    if not customer_name or not contact_number:
        flash('Please fill in all required fields.', 'error')
        return render_template('booking.html', dish=dishes[dish_id], dish_id=dish_id)
    
    # Create booking
    booking = {
        'customer_name': customer_name,
        'contact_number': contact_number,
        'dish_booked': dishes[dish_id]['dish_name'],
        'dish_price': dishes[dish_id]['price'],
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Save booking
    bookings = load_bookings()
    bookings.append(booking)
    save_bookings(bookings)
    
    # Reduce dish quantity
    dishes[dish_id]['available_quantity'] -= 1
    save_dishes(dishes)
    
    flash(f'Booking confirmed! You have successfully booked {dishes[dish_id]["dish_name"]}.', 'success')
    return redirect(url_for('index'))

@app.route('/admin/login')
def admin_login():
    """Admin login page"""
    return render_template('admin_login.html')

@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    """Process admin login"""
    email = request.form.get('email')
    password = request.form.get('password')
    
    if email == ADMIN_EMAIL and check_password_hash(ADMIN_PASSWORD_HASH, password):
        session['admin_logged_in'] = True
        flash('Welcome to the admin panel!', 'success')
        return redirect(url_for('admin_dashboard'))
    else:
        flash('Invalid email or password.', 'error')
        return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

def admin_required(f):
    """Decorator to require admin login"""
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please log in to access the admin panel.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    dishes = load_dishes()
    bookings = load_bookings()
    
    # Calculate statistics
    total_dishes = len(dishes)
    total_bookings = len(bookings)
    out_of_stock = sum(1 for dish in dishes if dish['available_quantity'] <= 0)
    
    stats = {
        'total_dishes': total_dishes,
        'total_bookings': total_bookings,
        'out_of_stock': out_of_stock,
        'recent_bookings': bookings[-5:] if bookings else []
    }
    
    return render_template('admin_dashboard.html', stats=stats)

@app.route('/admin/dishes')
@admin_required
def admin_dishes():
    """Admin dishes management"""
    dishes = load_dishes()
    return render_template('admin_dishes.html', dishes=dishes)

@app.route('/admin/dishes/add', methods=['POST'])
@admin_required
def admin_add_dish():
    """Add a new dish"""
    dish_name = request.form.get('dish_name', '').strip()
    description = request.form.get('description', '').strip()
    price = request.form.get('price', '').strip()
    available_quantity = request.form.get('available_quantity', '').strip()
    image_url = request.form.get('image_url', '').strip()
    
    # Validate required fields
    if not dish_name or not description or not price or not available_quantity:
        flash('Please fill in all required fields.', 'error')
        return redirect(url_for('admin_dishes'))
    
    try:
        price = float(price)
        available_quantity = int(available_quantity)
        if price < 0 or available_quantity < 0:
            raise ValueError()
    except ValueError:
        flash('Price and quantity must be valid positive numbers.', 'error')
        return redirect(url_for('admin_dishes'))
    
    # Add dish
    dishes = load_dishes()
    new_dish = {
        'dish_name': dish_name,
        'description': description,
        'price': price,
        'available_quantity': available_quantity,
        'image_url': image_url if image_url else None
    }
    dishes.append(new_dish)
    save_dishes(dishes)
    
    flash(f'Dish "{dish_name}" added successfully!', 'success')
    return redirect(url_for('admin_dishes'))

@app.route('/admin/dishes/update/<int:dish_id>', methods=['POST'])
@admin_required
def admin_update_dish(dish_id):
    """Update an existing dish"""
    dishes = load_dishes()
    
    if dish_id >= len(dishes):
        flash('Dish not found.', 'error')
        return redirect(url_for('admin_dishes'))
    
    dish_name = request.form.get('dish_name', '').strip()
    description = request.form.get('description', '').strip()
    price = request.form.get('price', '').strip()
    available_quantity = request.form.get('available_quantity', '').strip()
    image_url = request.form.get('image_url', '').strip()
    
    # Validate required fields
    if not dish_name or not description or not price or not available_quantity:
        flash('Please fill in all required fields.', 'error')
        return redirect(url_for('admin_dishes'))
    
    try:
        price = float(price)
        available_quantity = int(available_quantity)
        if price < 0 or available_quantity < 0:
            raise ValueError()
    except ValueError:
        flash('Price and quantity must be valid positive numbers.', 'error')
        return redirect(url_for('admin_dishes'))
    
    # Update dish
    dishes[dish_id] = {
        'dish_name': dish_name,
        'description': description,
        'price': price,
        'available_quantity': available_quantity,
        'image_url': image_url if image_url else None
    }
    save_dishes(dishes)
    
    flash(f'Dish "{dish_name}" updated successfully!', 'success')
    return redirect(url_for('admin_dishes'))

@app.route('/admin/dishes/delete/<int:dish_id>')
@admin_required
def admin_delete_dish(dish_id):
    """Delete a dish"""
    dishes = load_dishes()
    
    if dish_id >= len(dishes):
        flash('Dish not found.', 'error')
        return redirect(url_for('admin_dishes'))
    
    dish_name = dishes[dish_id]['dish_name']
    dishes.pop(dish_id)
    save_dishes(dishes)
    
    flash(f'Dish "{dish_name}" deleted successfully!', 'success')
    return redirect(url_for('admin_dishes'))

@app.route('/admin/bookings')
@admin_required
def admin_bookings():
    """Admin bookings view"""
    bookings = load_bookings()
    # Sort bookings by timestamp (newest first)
    bookings.sort(key=lambda x: x['timestamp'], reverse=True)
    return render_template('admin_bookings.html', bookings=bookings)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
