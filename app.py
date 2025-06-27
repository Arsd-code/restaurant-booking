import os
import json
import logging
import csv
from datetime import datetime, date, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
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

def load_stock_history():
    """Load stock history from JSON file"""
    try:
        with open('data/stock_history.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_stock_history(history):
    """Save stock history to JSON file"""
    os.makedirs('data', exist_ok=True)
    with open('data/stock_history.json', 'w') as f:
        json.dump(history, f, indent=2)

def get_today_bookings():
    """Get today's bookings"""
    bookings = load_bookings()
    today = date.today().strftime('%Y-%m-%d')
    return [b for b in bookings if b['timestamp'].startswith(today)]

def calculate_revenue(bookings, start_date=None, end_date=None):
    """Calculate revenue for given date range"""
    if start_date and end_date:
        filtered_bookings = []
        for booking in bookings:
            booking_date = datetime.strptime(booking['timestamp'], '%Y-%m-%d %H:%M:%S').date()
            if start_date <= booking_date <= end_date:
                filtered_bookings.append(booking)
        bookings = filtered_bookings
    
    return sum(booking.get('dish_price', 0) * booking.get('quantity', 1) for booking in bookings)

def archive_daily_stock():
    """Archive today's stock data for historical reference"""
    dishes = load_dishes()
    today_bookings = get_today_bookings()
    today = date.today().strftime('%Y-%m-%d')
    
    stock_history = load_stock_history()
    
    # Group bookings by dish
    dish_bookings = {}
    for booking in today_bookings:
        dish_name = booking['dish_booked']
        if dish_name not in dish_bookings:
            dish_bookings[dish_name] = {'count': 0, 'revenue': 0}
        dish_bookings[dish_name]['count'] += booking.get('quantity', 1)
        dish_bookings[dish_name]['revenue'] += booking.get('dish_price', 0) * booking.get('quantity', 1)
    
    # Create archive entry for each dish
    for dish in dishes:
        dish_name = dish['dish_name']
        booked_quantity = dish_bookings.get(dish_name, {}).get('count', 0)
        revenue = dish_bookings.get(dish_name, {}).get('revenue', 0)
        
        # Check if entry already exists for today
        existing_entry = next((entry for entry in stock_history 
                             if entry['date'] == today and entry['dish_name'] == dish_name), None)
        
        if not existing_entry:
            stock_history.append({
                'date': today,
                'dish_name': dish_name,
                'opening_stock': dish['available_quantity'] + booked_quantity,
                'booked_quantity': booked_quantity,
                'closing_stock': dish['available_quantity'],
                'revenue': revenue
            })
    
    save_stock_history(stock_history)

def admin_required(f):
    """Decorator to require admin login"""
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please log in to access the admin panel.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def index():
    """Redirect to admin login - no public customer interface"""
    return redirect(url_for('admin_login'))

@app.route('/admin/login')
def admin_login():
    """Admin login page"""
    return render_template('admin_login.html')

@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    """Process admin login"""
    email = request.form.get('email')
    password = request.form.get('password')
    
    if email == ADMIN_EMAIL and password and check_password_hash(ADMIN_PASSWORD_HASH, password):
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
    return redirect(url_for('admin_login'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard with enhanced statistics"""
    dishes = load_dishes()
    bookings = load_bookings()
    today_bookings = get_today_bookings()
    
    # Calculate statistics
    total_dishes = len(dishes)
    total_bookings = len(bookings)
    out_of_stock = sum(1 for dish in dishes if dish['available_quantity'] <= 0)
    
    # Revenue calculations
    today = date.today()
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)
    
    daily_revenue = calculate_revenue(today_bookings)
    monthly_revenue = calculate_revenue(bookings, month_start, today)
    yearly_revenue = calculate_revenue(bookings, year_start, today)
    
    # Dish statistics with booking counts
    dish_stats = []
    for i, dish in enumerate(dishes):
        dish_name = dish['dish_name']
        today_dish_bookings = [b for b in today_bookings if b['dish_booked'] == dish_name]
        booked_today = sum(b.get('quantity', 1) for b in today_dish_bookings)
        
        dish_stats.append({
            'id': i,
            'dish_name': dish_name,
            'price': dish['price'],
            'available_quantity': dish['available_quantity'],
            'booked_today': booked_today,
            'remaining_quantity': dish['available_quantity'],
            'status': 'Out of Stock' if dish['available_quantity'] <= 0 else 'Available'
        })
    
    stats = {
        'total_dishes': total_dishes,
        'total_bookings': len(today_bookings),
        'out_of_stock': out_of_stock,
        'daily_revenue': daily_revenue,
        'monthly_revenue': monthly_revenue,
        'yearly_revenue': yearly_revenue,
        'recent_bookings': bookings[-5:] if bookings else [],
        'dish_stats': dish_stats
    }
    
    return render_template('admin_dashboard.html', stats=stats)

@app.route('/admin/booking')
@admin_required
def admin_booking():
    """Show admin booking form"""
    dishes = load_dishes()
    # Filter only available dishes
    available_dishes = [dish for dish in dishes if dish['available_quantity'] > 0]
    return render_template('admin_booking.html', dishes=available_dishes)

@app.route('/admin/booking', methods=['POST'])
@admin_required
def admin_process_booking():
    """Process admin booking form submission"""
    dishes = load_dishes()
    
    # Get form data
    customer_name = request.form.get('customer_name', '').strip()
    contact_number = request.form.get('contact_number', '').strip()
    dish_id = request.form.get('dish_id', '').strip()
    quantity = request.form.get('quantity', '1').strip()
    
    # Validate form data
    if not customer_name or not contact_number or not dish_id:
        flash('Please fill in all required fields.', 'error')
        return redirect(url_for('admin_booking'))
    
    try:
        dish_id = int(dish_id)
        quantity = int(quantity)
        if quantity <= 0:
            raise ValueError()
    except ValueError:
        flash('Invalid dish selection or quantity.', 'error')
        return redirect(url_for('admin_booking'))
    
    # Validate dish availability
    if dish_id >= len(dishes) or dishes[dish_id]['available_quantity'] < quantity:
        flash(f'Sorry, only {dishes[dish_id]["available_quantity"]} items available for this dish.', 'error')
        return redirect(url_for('admin_booking'))
    
    # Create booking
    booking = {
        'customer_name': customer_name,
        'contact_number': contact_number,
        'dish_booked': dishes[dish_id]['dish_name'],
        'quantity': quantity,
        'dish_price': dishes[dish_id]['price'],
        'total_price': dishes[dish_id]['price'] * quantity,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Save booking
    bookings = load_bookings()
    bookings.append(booking)
    save_bookings(bookings)
    
    # Reduce dish quantity
    dishes[dish_id]['available_quantity'] -= quantity
    save_dishes(dishes)
    
    flash(f'Booking confirmed for {customer_name}! {quantity}x {dishes[dish_id]["dish_name"]} (₹{booking["total_price"]:.2f})', 'success')
    return redirect(url_for('admin_booking'))

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
    """Admin bookings view with filtering"""
    bookings = load_bookings()
    
    # Get filter parameters
    date_filter = request.args.get('date')
    dish_filter = request.args.get('dish')
    
    # Apply filters
    if date_filter:
        bookings = [b for b in bookings if b['timestamp'].startswith(date_filter)]
    
    if dish_filter:
        bookings = [b for b in bookings if b['dish_booked'] == dish_filter]
    
    # Sort bookings by timestamp (newest first)
    bookings.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Get unique dishes for filter dropdown
    all_bookings = load_bookings()
    unique_dishes = list(set(b['dish_booked'] for b in all_bookings))
    
    # Calculate total revenue for filtered bookings
    total_revenue = sum(b.get('total_price', b.get('dish_price', 0) * b.get('quantity', 1)) for b in bookings)
    
    return render_template('admin_bookings.html', 
                         bookings=bookings, 
                         unique_dishes=unique_dishes,
                         total_revenue=total_revenue,
                         current_date_filter=date_filter,
                         current_dish_filter=dish_filter)

@app.route('/admin/export')
@admin_required
def export_bookings():
    """Export bookings data as CSV"""
    bookings = load_bookings()
    
    # Get filter parameters
    date_filter = request.args.get('date')
    dish_filter = request.args.get('dish')
    
    # Apply filters
    if date_filter:
        bookings = [b for b in bookings if b['timestamp'].startswith(date_filter)]
    
    if dish_filter:
        bookings = [b for b in bookings if b['dish_booked'] == dish_filter]
    
    # Create CSV response
    output = []
    output.append(['Customer Name', 'Contact Number', 'Dish', 'Quantity', 'Price per Item', 'Total Price', 'Booking Time'])
    
    for booking in bookings:
        quantity = booking.get('quantity', 1)
        price_per_item = booking.get('dish_price', 0)
        total_price = booking.get('total_price', price_per_item * quantity)
        
        output.append([
            booking['customer_name'],
            booking['contact_number'],
            booking['dish_booked'],
            quantity,
            f"₹{price_per_item:.2f}",
            f"₹{total_price:.2f}",
            booking['timestamp']
        ])
    
    # Generate CSV content
    csv_content = []
    for row in output:
        csv_content.append(','.join(f'"{str(cell)}"' for cell in row))
    
    csv_string = '\n'.join(csv_content)
    
    response = make_response(csv_string)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=bookings_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    return response

@app.route('/admin/revenue')
@admin_required
def admin_revenue():
    """Revenue tracking page"""
    bookings = load_bookings()
    
    # Calculate revenue by different periods
    today = date.today()
    yesterday = date(today.year, today.month, today.day - 1) if today.day > 1 else date(today.year, today.month - 1, 30)
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)
    
    today_bookings = get_today_bookings()
    yesterday_bookings = [b for b in bookings if b['timestamp'].startswith(yesterday.strftime('%Y-%m-%d'))]
    
    revenue_stats = {
        'today': calculate_revenue(today_bookings),
        'yesterday': calculate_revenue(yesterday_bookings),
        'this_month': calculate_revenue(bookings, month_start, today),
        'this_year': calculate_revenue(bookings, year_start, today),
        'all_time': calculate_revenue(bookings)
    }
    
    # Get daily revenue for the last 7 days
    daily_revenue = []
    for i in range(6, -1, -1):
        target_date = date.today() - timedelta(days=i)
        day_bookings = [b for b in bookings if b['timestamp'].startswith(target_date.strftime('%Y-%m-%d'))]
        daily_revenue.append({
            'date': target_date.strftime('%Y-%m-%d'),
            'revenue': calculate_revenue(day_bookings)
        })
    
    return render_template('admin_revenue.html', 
                         revenue_stats=revenue_stats, 
                         daily_revenue=daily_revenue)

@app.route('/admin/stock-reset', methods=['POST'])
@admin_required
def reset_daily_stock():
    """Reset stock quantities for new day"""
    # Archive current day's data
    archive_daily_stock()
    
    # Reset all dish quantities (admin will set new quantities)
    dishes = load_dishes()
    reset_quantities = request.form.getlist('reset_quantity')
    
    for i, dish in enumerate(dishes):
        if i < len(reset_quantities):
            try:
                new_quantity = int(reset_quantities[i])
                dish['available_quantity'] = new_quantity
            except ValueError:
                pass
    
    save_dishes(dishes)
    flash('Daily stock has been reset successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)