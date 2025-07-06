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
    try:
        print(f"=== SAVING DISHES ===")
        print(f"Attempting to save {len(dishes)} dishes")
        
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        print("✓ Data directory ready")
        
        # Check if file exists and is writable
        file_path = 'data/dishes.json'
        if os.path.exists(file_path):
            print(f"✓ File exists: {file_path}")
            # Check if file is writable
            if os.access(file_path, os.W_OK):
                print("✓ File is writable")
            else:
                print("✗ File is not writable!")
                raise PermissionError(f"Cannot write to {file_path}")
        else:
            print(f"Creating new file: {file_path}")
        
        # Save the data
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(dishes, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Successfully saved {len(dishes)} dishes to {file_path}")
        
        # Verify the save by reading back
        with open(file_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        print(f"✓ Verification: Read back {len(saved_data)} dishes")
        
    except Exception as e:
        print(f"✗ Error saving dishes: {e}")
        import traceback
        traceback.print_exc()
        raise

def load_bookings():
    """Load bookings from JSON file"""
    try:
        with open('data/bookings.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_bookings(bookings):
    """Save bookings to JSON file"""
    try:
        os.makedirs('data', exist_ok=True)
        with open('data/bookings.json', 'w') as f:
            json.dump(bookings, f, indent=2)
        print(f"Successfully saved {len(bookings)} bookings to data/bookings.json")
    except Exception as e:
        print(f"Error saving bookings: {e}")
        raise

def load_stock_history():
    """Load stock history from JSON file"""
    try:
        with open('data/stock_history.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_stock_history(history):
    """Save stock history to JSON file"""
    try:
        os.makedirs('data', exist_ok=True)
        with open('data/stock_history.json', 'w') as f:
            json.dump(history, f, indent=2)
        print(f"Successfully saved {len(history)} stock history entries to data/stock_history.json")
    except Exception as e:
        print(f"Error saving stock history: {e}")
        raise

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

@app.route('/test')
def test():
    """Test route to check if Flask is working"""
    return "Flask is working! Server is running correctly."

@app.route('/admin/test')
@admin_required
def admin_test():
    """Test route for admin area"""
    return "Admin area is working! You are logged in."

@app.route('/routes')
def list_routes():
    """List all available routes for debugging"""
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'rule': str(rule)
        })
    return {'routes': routes}

@app.route('/admin/login')
def admin_login():
    """Admin login page"""
    return render_template('admin_login_modern.html')

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
        return render_template('admin_login_modern.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin')
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard with enhanced statistics"""
    try:
        print("Loading dashboard data...")
        dishes = load_dishes()
        print(f"Loaded {len(dishes)} dishes")
        
        bookings = load_bookings()
        print(f"Loaded {len(bookings)} bookings")
        
        today_bookings = get_today_bookings()
        print(f"Today's bookings: {len(today_bookings)}")
        
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
        
        # Additional calculations for modern dashboard
        total_stock = sum(dish['available_quantity'] for dish in dishes)
        low_stock_count = sum(1 for dish in dishes if dish['available_quantity'] <= 5)
        
        print(f"Rendering dashboard template...")
        
        return render_template('admin_dashboard_modern.html', 
                             dishes=dishes,
                             today_bookings=today_bookings,
                             today_bookings_count=len(today_bookings),
                             today_revenue=daily_revenue,
                             total_stock=total_stock,
                             low_stock_count=low_stock_count,
                             stats=stats)
    except Exception as e:
        print(f"Error in admin_dashboard: {e}")
        import traceback
        traceback.print_exc()
        flash('An error occurred while loading the dashboard. Please try again.', 'error')
        return redirect(url_for('admin_login'))

@app.route('/admin/booking')
@admin_required
def admin_booking():
    """Show admin booking form"""
    dishes = load_dishes()
    # Filter only available dishes
    available_dishes = [dish for dish in dishes if dish['available_quantity'] > 0]
    return render_template('admin_booking_modern.html', dishes=available_dishes)

@app.route('/admin/booking', methods=['POST'])
@admin_required
def admin_process_booking():
    """Process admin booking form submission (multi-dish)"""
    dishes = load_dishes()
    # Get form data
    customer_name = request.form.get('customer_name', '').strip()
    contact_number = request.form.get('contact_number', '').strip()
    dish_ids = request.form.getlist('dish_ids')
    # Validate form data
    if not customer_name or not contact_number or not dish_ids:
        flash('Please fill in all required fields and select at least one dish.', 'error')
        return redirect(url_for('admin_booking'))
    bookings = load_bookings()
    errors = []
    success = []
    for dish_id_str in dish_ids:
        try:
            dish_id = int(dish_id_str)
            quantity = int(request.form.get(f'quantity_{dish_id}', '1'))
            if quantity <= 0:
                raise ValueError()
        except ValueError:
            errors.append(f'Invalid quantity for dish {dishes[dish_id]["dish_name"]}.')
            continue
        # Validate dish availability
        if dish_id >= len(dishes) or dishes[dish_id]['available_quantity'] < quantity:
            errors.append(f'Sorry, only {dishes[dish_id]["available_quantity"]} items available for {dishes[dish_id]["dish_name"]}.')
            continue
        # Create booking for this dish
        booking = {
            'customer_name': customer_name,
            'contact_number': contact_number,
            'dish_booked': dishes[dish_id]['dish_name'],
            'quantity': quantity,
            'dish_price': dishes[dish_id]['price'],
            'total_price': dishes[dish_id]['price'] * quantity,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        bookings.append(booking)
        # Reduce dish quantity
        dishes[dish_id]['available_quantity'] -= quantity
        success.append(f'{quantity}x {dishes[dish_id]["dish_name"]} (₹{booking["total_price"]:.2f})')
    save_bookings(bookings)
    save_dishes(dishes)
    if success:
        flash(f'Booking confirmed for {customer_name}! ' + ", ".join(success), 'success')
    if errors:
        flash(" ".join(errors), 'error')
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
    print(f"=== DISH UPDATE ROUTE ===")
    print(f"Updating dish ID: {dish_id}")
    print(f"Form data: {dict(request.form)}")
    
    dishes = load_dishes()
    
    if dish_id >= len(dishes):
        flash('Dish not found.', 'error')
        return redirect(url_for('admin_dishes'))
    
    # Get the existing dish to preserve dish_name and description
    existing_dish = dishes[dish_id]
    print(f"Existing dish: {existing_dish['dish_name']}")
    
    # Get form data (only price and quantity are in the form)
    price = request.form.get('price', '').strip()
    available_quantity = request.form.get('available_quantity', '').strip()
    
    print(f"Form price: '{price}', quantity: '{available_quantity}'")
    
    # Validate required fields (preserve dish_name and description from existing dish)
    if not price or not available_quantity:
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
    
    print(f"Validated - Price: {price}, Quantity: {available_quantity}")
    
    # Update dish (preserve dish_name and description from existing dish)
    dishes[dish_id] = {
        'dish_name': existing_dish['dish_name'],  # Keep existing dish name
        'description': existing_dish['description'],  # Keep existing description
        'price': price,
        'available_quantity': available_quantity,
        'image_url': existing_dish.get('image_url')  # Keep existing image URL
    }
    
    print(f"Updated dish data: {dishes[dish_id]}")
    
    # Save dishes
    save_dishes(dishes)
    
    print(f"✓ Dish updated successfully!")
    flash(f'Dish "{existing_dish["dish_name"]}" updated successfully!', 'success')
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
    try:
        print("Loading bookings...")
        bookings = load_bookings()
        print(f"Loaded {len(bookings)} bookings")
        
        # Get filter type from query parameters
        filter_type = request.args.get('filter', 'all')
        today = date.today()
        
        # Apply filters based on filter_type
        if filter_type == 'today':
            today_str = today.strftime('%Y-%m-%d')
            bookings = [b for b in bookings if b['timestamp'].startswith(today_str)]
        elif filter_type == 'week':
            week_ago = today - timedelta(days=7)
            bookings = [b for b in bookings if datetime.strptime(b['timestamp'].split(' ')[0], '%Y-%m-%d').date() >= week_ago]
        
        # Get today's bookings for stats
        today_bookings = get_today_bookings()
        print(f"Today's bookings: {len(today_bookings)}")
        
        # Calculate total revenue for filtered bookings
        total_revenue = 0
        for b in bookings:
            quantity = b.get('quantity', 1)
            dish_price = b.get('dish_price', 0)
            total_price = b.get('total_price', dish_price * quantity)
            total_revenue += total_price
        
        # Calculate average order value
        avg_order_value = total_revenue / len(bookings) if bookings else 0
        
        # Get today's date for display
        today = date.today().strftime('%Y-%m-%d')
        
        print(f"filter_type: {filter_type}, bookings before filter: {len(bookings)}")
        print(f"bookings after filter: {len(bookings)}")
        
        print(f"Rendering template with {len(bookings)} bookings, total_revenue: {total_revenue}, avg_order_value: {avg_order_value}")
        
        return render_template('admin_bookings.html', 
                             bookings=bookings,
                             today_bookings=today_bookings,
                             total_revenue=total_revenue,
                             avg_order_value=avg_order_value,
                             today=today,
                             active_filter=filter_type)
    except Exception as e:
        # Log the error and return a simple error page
        print(f"Error in admin_bookings: {e}")
        import traceback
        traceback.print_exc()
        flash('An error occurred while loading bookings. Please try again.', 'error')
        return redirect(url_for('admin_dashboard'))

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
    
    # Calculate revenue for different periods
    daily_revenue = calculate_revenue(today_bookings)
    yesterday_revenue = calculate_revenue(yesterday_bookings)
    monthly_revenue = calculate_revenue(bookings, month_start, today)
    yearly_revenue = calculate_revenue(bookings, year_start, today)
    
    # Calculate growth percentages
    daily_growth = 0
    if yesterday_revenue > 0:
        daily_growth = round(((daily_revenue - yesterday_revenue) / yesterday_revenue) * 100, 1)
    
    # Calculate orders for different periods
    daily_orders = len(today_bookings)
    weekly_orders = len([b for b in bookings if (today - datetime.strptime(b['timestamp'], '%Y-%m-%d %H:%M:%S').date()).days <= 7])
    monthly_orders = len([b for b in bookings if (today - datetime.strptime(b['timestamp'], '%Y-%m-%d %H:%M:%S').date()).days <= 30])
    yearly_orders = len([b for b in bookings if (today - datetime.strptime(b['timestamp'], '%Y-%m-%d %H:%M:%S').date()).days <= 365])
    
    # Calculate weekly revenue
    week_start = today - timedelta(days=today.weekday())
    weekly_revenue = calculate_revenue(bookings, week_start, today)
    
    # Calculate average order values
    daily_avg = daily_revenue / daily_orders if daily_orders > 0 else 0
    weekly_avg = weekly_revenue / weekly_orders if weekly_orders > 0 else 0
    monthly_avg = monthly_revenue / monthly_orders if monthly_orders > 0 else 0
    yearly_avg = yearly_revenue / yearly_orders if yearly_orders > 0 else 0
    
    # Calculate growth percentages for other periods (simplified)
    weekly_growth = 12.5  # Placeholder
    monthly_growth = 8.3   # Placeholder
    yearly_growth = 15.7   # Placeholder
    
    # Get daily revenue for the last 7 days for chart
    revenue_chart_data = []
    max_revenue = 0
    for i in range(6, -1, -1):
        target_date = date.today() - timedelta(days=i)
        day_bookings = [b for b in bookings if b['timestamp'].startswith(target_date.strftime('%Y-%m-%d'))]
        day_revenue = calculate_revenue(day_bookings)
        revenue_chart_data.append({
            'date': target_date.strftime('%m/%d'),
            'revenue': day_revenue
        })
        max_revenue = max(max_revenue, day_revenue)
    
    # Get top performing dishes
    dish_revenue = {}
    for booking in bookings:
        dish_name = booking['dish_booked']
        if dish_name not in dish_revenue:
            dish_revenue[dish_name] = {'revenue': 0, 'orders': 0}
        dish_revenue[dish_name]['revenue'] += booking.get('total_price', booking.get('dish_price', 0) * booking.get('quantity', 1))
        dish_revenue[dish_name]['orders'] += 1
    
    # Sort dishes by revenue and get top 5
    top_dishes = []
    total_revenue_all = sum(dish_revenue[dish]['revenue'] for dish in dish_revenue)
    for dish_name, data in sorted(dish_revenue.items(), key=lambda x: x[1]['revenue'], reverse=True)[:5]:
        percentage = (data['revenue'] / total_revenue_all * 100) if total_revenue_all > 0 else 0
        top_dishes.append({
            'name': dish_name,
            'revenue': round(data['revenue'], 2),
            'orders': data['orders'],
            'percentage': round(percentage, 1)
        })
    
    # Date range for filtering
    start_date = request.args.get('start_date', (today - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', today.strftime('%Y-%m-%d'))
    
    return render_template('admin_revenue.html', 
                         daily_revenue=round(daily_revenue, 2),
                         weekly_revenue=round(weekly_revenue, 2),
                         monthly_revenue=round(monthly_revenue, 2),
                         yearly_revenue=round(yearly_revenue, 2),
                         daily_orders=daily_orders,
                         weekly_orders=weekly_orders,
                         monthly_orders=monthly_orders,
                         yearly_orders=yearly_orders,
                         daily_avg=daily_avg,
                         weekly_avg=weekly_avg,
                         monthly_avg=monthly_avg,
                         yearly_avg=yearly_avg,
                         daily_growth=daily_growth,
                         weekly_growth=weekly_growth,
                         monthly_growth=monthly_growth,
                         yearly_growth=yearly_growth,
                         revenue_chart_data=revenue_chart_data,
                         max_revenue=max_revenue,
                         top_dishes=top_dishes,
                         start_date=start_date,
                         end_date=end_date)

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

@app.route('/admin/stock-calendar')
@admin_required
def admin_stock_calendar():
    """Stock management calendar interface"""
    selected_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    today_date = datetime.now().strftime('%Y-%m-%d')
    
    print(f"Stock calendar requested for date: {selected_date}, today: {today_date}")
    
    # Load stock history
    stock_history = load_stock_history()
    
    # For today's date, always use current dishes data
    if selected_date == today_date:
        print("Using current dishes data for today")
        current_dishes = load_dishes()
        date_stock = {
            'date': selected_date,
            'dishes': current_dishes
        }
    else:
        # For other dates, check stock history
        print("Checking stock history for historical data")
        date_stock = None
        for entry in stock_history:
            if entry['date'] == selected_date:
                date_stock = entry
                print(f"Found historical data for {selected_date}")
                break
        
        # If no historical data for this date, use current stock
        if not date_stock:
            print(f"No historical data found for {selected_date}, using current dishes")
            current_dishes = load_dishes()
            date_stock = {
                'date': selected_date,
                'dishes': current_dishes
            }
    
    print(f"Final date_stock has {len(date_stock['dishes'])} dishes")
    for dish in date_stock['dishes']:
        print(f"  - {dish['dish_name']}: {dish['available_quantity']}")
    
    return render_template('admin_stock_calendar.html', 
                         selected_date=selected_date,
                         date_stock=date_stock,
                         stock_history=stock_history,
                         today_date=today_date)

@app.route('/admin/update-stock-date', methods=['POST'])
@admin_required
def update_stock_date():
    """Update stock quantities for a specific date"""
    selected_date = None
    try:
        selected_date = request.form.get('selected_date')
        if not selected_date:
            flash('No date selected!', 'error')
            return redirect(url_for('admin_stock_calendar'))
        
        print(f"=== STOCK UPDATE DEBUG ===")
        print(f"Updating stock for date: {selected_date}")
        print(f"All form data: {dict(request.form)}")
        
        # Load current stock history
        stock_history = load_stock_history()
        print(f"Current stock history has {len(stock_history)} entries")
        
        # Find or create entry for this date
        date_entry = None
        for i, entry in enumerate(stock_history):
            if entry['date'] == selected_date:
                date_entry = entry
                date_index = i
                print(f"Found existing entry for {selected_date} at index {i}")
                break
        
        if not date_entry:
            # Create new entry
            dishes = load_dishes()
            print(f"Creating new entry for {selected_date} with {len(dishes)} dishes")
            date_entry = {
                'date': selected_date,
                'dishes': dishes.copy()
            }
            stock_history.append(date_entry)
            date_index = len(stock_history) - 1
        
        # Update quantities from form
        updated_count = 0
        print(f"Current dishes in date_entry before update:")
        for dish in date_entry['dishes']:
            print(f"  - {dish['dish_name']}: {dish['available_quantity']}")
        
        for dish in date_entry['dishes']:
            dish_name = dish['dish_name']
            quantity_key = f'quantity_{dish_name}'
            print(f"Looking for quantity key: {quantity_key}")
            
            if quantity_key in request.form:
                try:
                    old_quantity = dish['available_quantity']
                    new_quantity = int(request.form[quantity_key])
                    print(f"Found quantity for {dish_name}: {old_quantity} -> {new_quantity}")
                    
                    if old_quantity != new_quantity:
                        dish['available_quantity'] = new_quantity
                        updated_count += 1
                        print(f"✓ Updated {dish_name}: {old_quantity} -> {new_quantity}")
                    else:
                        print(f"- No change for {dish_name}: {old_quantity}")
                except ValueError as e:
                    print(f"✗ Error converting quantity for {dish_name}: {e}")
                    flash(f'Invalid quantity for {dish_name}', 'error')
            else:
                print(f"✗ Quantity key '{quantity_key}' not found in form data")
        
        print(f"Updated {updated_count} dishes")
        
        # Save updated history
        print("Saving stock history...")
        save_stock_history(stock_history)
        
        # If updating today's date, also update current dishes
        today = datetime.now().strftime('%Y-%m-%d')
        if selected_date == today:
            print("Updating current dishes file...")
            print("Dishes to save:")
            for dish in date_entry['dishes']:
                print(f"  - {dish['dish_name']}: {dish['available_quantity']}")
            # Save the dishes array directly, not the date_entry structure
            save_dishes(date_entry['dishes'])
            print("✓ Current dishes file updated")
        
        print("=== END STOCK UPDATE DEBUG ===")
        flash(f'Stock updated successfully for {selected_date}! ({updated_count} dishes updated)', 'success')
        
    except Exception as e:
        print(f"✗ Error in update_stock_date: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error updating stock: {str(e)}', 'error')
        if not selected_date:
            selected_date = datetime.now().strftime('%Y-%m-%d')
    
    return redirect(url_for('admin_stock_calendar', date=selected_date))

@app.route('/debug/data')
def debug_data():
    """Debug route to check current data"""
    try:
        dishes = load_dishes()
        bookings = load_bookings()
        stock_history = load_stock_history()
        
        return {
            'dishes': dishes,
            'bookings': bookings,
            'stock_history': stock_history,
            'dishes_count': len(dishes),
            'bookings_count': len(bookings),
            'stock_history_count': len(stock_history)
        }
    except Exception as e:
        return {'error': str(e)}

@app.route('/debug/save-test')
def debug_save_test():
    """Test route to verify data saving works"""
    try:
        # Test saving dishes
        test_dishes = [
            {
                'dish_name': 'Test Dish',
                'description': 'Test description',
                'price': 100.0,
                'available_quantity': 10,
                'image_url': None
            }
        ]
        save_dishes(test_dishes)
        
        # Test saving bookings
        test_bookings = [
            {
                'customer_name': 'Test Customer',
                'contact_number': '1234567890',
                'dish_booked': 'Test Dish',
                'quantity': 1,
                'dish_price': 100.0,
                'total_price': 100.0,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        ]
        save_bookings(test_bookings)
        
        return {
            'message': 'Test data saved successfully',
            'test_dishes': test_dishes,
            'test_bookings': test_bookings
        }
    except Exception as e:
        return {'error': str(e)}

@app.route('/debug/refresh-dishes')
def debug_refresh_dishes():
    """Debug route to refresh and check current dishes data"""
    try:
        # Reload dishes from file
        dishes = load_dishes()
        
        # Print current state
        print("Current dishes data:")
        for dish in dishes:
            print(f"  - {dish['dish_name']}: {dish['available_quantity']}")
        
        return {
            'message': 'Dishes data refreshed',
            'dishes': dishes,
            'dishes_count': len(dishes)
        }
    except Exception as e:
        return {'error': str(e)}

@app.route('/debug/force-update-dishes')
def debug_force_update_dishes():
    """Debug route to force update dishes with test data"""
    try:
        # Force update dishes with current quantities
        dishes = [
            {
                'dish_name': 'Chicken Mandi',
                'description': 'Traditional Arabian rice dish with tender chicken, aromatic spices, and perfectly cooked basmati rice',
                'price': 450.0,
                'available_quantity': 50,
                'image_url': None
            },
            {
                'dish_name': 'Lamb Mandi',
                'description': 'Succulent lamb slow-cooked with traditional spices, served with fragrant saffron rice',
                'price': 650.0,
                'available_quantity': 35,
                'image_url': None
            },
            {
                'dish_name': 'Fish Mandi',
                'description': 'Fresh fish marinated in aromatic spices, grilled to perfection and served with basmati rice',
                'price': 550.0,
                'available_quantity': 30,
                'image_url': None
            },
            {
                'dish_name': 'Mixed Grill Mandi',
                'description': 'A combination of chicken, lamb, and fish with traditional Mandi rice and special sauce',
                'price': 850.0,
                'available_quantity': 25,
                'image_url': None
            }
        ]
        
        save_dishes(dishes)
        
        return {
            'message': 'Dishes data force updated',
            'dishes': dishes,
            'dishes_count': len(dishes)
        }
    except Exception as e:
        return {'error': str(e)}

@app.route('/debug/test-update-dish/<dish_name>/<int:new_quantity>')
def debug_test_update_dish(dish_name, new_quantity):
    """Test route to directly update a dish quantity"""
    try:
        print(f"=== TEST UPDATE DISH ===")
        print(f"Updating {dish_name} to {new_quantity}")
        
        # Load current dishes
        dishes = load_dishes()
        print(f"Current dishes before update:")
        for dish in dishes:
            print(f"  - {dish['dish_name']}: {dish['available_quantity']}")
        
        # Find and update the dish
        updated = False
        for dish in dishes:
            if dish['dish_name'] == dish_name:
                old_quantity = dish['available_quantity']
                dish['available_quantity'] = new_quantity
                updated = True
                print(f"✓ Updated {dish_name}: {old_quantity} -> {new_quantity}")
                break
        
        if not updated:
            print(f"✗ Dish '{dish_name}' not found")
            return {'error': f'Dish {dish_name} not found'}
        
        # Save dishes
        print("Saving dishes...")
        save_dishes(dishes)
        
        # Reload to verify
        dishes_after = load_dishes()
        print(f"Dishes after save and reload:")
        for dish in dishes_after:
            print(f"  - {dish['dish_name']}: {dish['available_quantity']}")
        
        print("=== END TEST UPDATE DISH ===")
        
        return {
            'message': f'Successfully updated {dish_name} to {new_quantity}',
            'dishes': dishes_after
        }
    except Exception as e:
        print(f"✗ Error in test update: {e}")
        return {'error': str(e)}

@app.route('/debug/check-stock-calendar-data')
def debug_check_stock_calendar_data():
    """Debug route to check what data the stock calendar is loading"""
    try:
        selected_date = datetime.now().strftime('%Y-%m-%d')
        today_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"=== STOCK CALENDAR DATA CHECK ===")
        print(f"Selected date: {selected_date}")
        print(f"Today date: {today_date}")
        
        # Load current dishes
        current_dishes = load_dishes()
        print(f"Current dishes from file:")
        for dish in current_dishes:
            print(f"  - {dish['dish_name']}: {dish['available_quantity']}")
        
        # Load stock history
        stock_history = load_stock_history()
        print(f"Stock history has {len(stock_history)} entries")
        
        # Check if there's an entry for today
        today_entry = None
        for entry in stock_history:
            if entry['date'] == today_date:
                today_entry = entry
                print(f"Found stock history entry for today:")
                for dish in entry['dishes']:
                    print(f"  - {dish['dish_name']}: {dish['available_quantity']}")
                break
        
        if not today_entry:
            print("No stock history entry for today")
        
        # Simulate what the stock calendar would do
        if selected_date == today_date:
            print("Stock calendar would use current dishes data")
            date_stock = {
                'date': selected_date,
                'dishes': current_dishes
            }
        else:
            print("Stock calendar would check stock history")
            # ... rest of logic
        
        print("=== END STOCK CALENDAR DATA CHECK ===")
        
        return {
            'selected_date': selected_date,
            'today_date': today_date,
            'current_dishes': current_dishes,
            'stock_history_count': len(stock_history),
            'has_today_entry': today_entry is not None
        }
    except Exception as e:
        return {'error': str(e)}

@app.route('/debug/clear-today-stock-history')
def debug_clear_today_stock_history():
    """Debug route to clear stock history for today"""
    try:
        today_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"=== CLEAR TODAY STOCK HISTORY ===")
        print(f"Clearing stock history for: {today_date}")
        
        # Load current stock history
        stock_history = load_stock_history()
        print(f"Stock history before clearing: {len(stock_history)} entries")
        
        # Remove entries for today
        original_count = len(stock_history)
        stock_history = [entry for entry in stock_history if entry['date'] != today_date]
        removed_count = original_count - len(stock_history)
        
        print(f"Removed {removed_count} entries for today")
        print(f"Stock history after clearing: {len(stock_history)} entries")
        
        # Save updated history
        save_stock_history(stock_history)
        
        # Load current dishes to verify
        current_dishes = load_dishes()
        print(f"Current dishes after clearing history:")
        for dish in current_dishes:
            print(f"  - {dish['dish_name']}: {dish['available_quantity']}")
        
        print("=== END CLEAR TODAY STOCK HISTORY ===")
        
        return {
            'message': f'Cleared {removed_count} stock history entries for {today_date}',
            'stock_history_count': len(stock_history),
            'current_dishes': current_dishes
        }
    except Exception as e:
        return {'error': str(e)}

@app.route('/debug/test-form', methods=['GET', 'POST'])
def debug_test_form():
    """Debug route to test form submission"""
    if request.method == 'POST':
        print("=== FORM SUBMISSION TEST ===")
        print(f"Form data: {dict(request.form)}")
        
        # Test updating a specific dish
        dishes = load_dishes()
        print(f"Current dishes before update:")
        for dish in dishes:
            print(f"  - {dish['dish_name']}: {dish['available_quantity']}")
        
        # Try to update Chicken Mandi
        for dish in dishes:
            if dish['dish_name'] == 'Chicken Mandi':
                old_qty = dish['available_quantity']
                dish['available_quantity'] = 999  # Set to a test value
                print(f"Updated Chicken Mandi: {old_qty} -> 999")
                break
        
        save_dishes(dishes)
        print("Dishes saved!")
        
        # Reload to verify
        dishes = load_dishes()
        print(f"Current dishes after update:")
        for dish in dishes:
            print(f"  - {dish['dish_name']}: {dish['available_quantity']}")
        
        return {
            'message': 'Form test completed',
            'form_data': dict(request.form),
            'dishes_after_update': dishes
        }
    
    return '''
    <h1>Test Form</h1>
    <form method="POST">
        <input type="hidden" name="selected_date" value="2024-01-01">
        <input type="number" name="quantity_Chicken Mandi" value="50">
        <button type="submit">Test Submit</button>
    </form>
    '''

@app.route('/debug/direct-update/<dish_name>/<int:new_quantity>')
def debug_direct_update(dish_name, new_quantity):
    """Debug route to directly update a dish quantity"""
    try:
        print(f"=== DIRECT UPDATE TEST ===")
        print(f"Updating {dish_name} to {new_quantity}")
        
        dishes = load_dishes()
        print(f"Current dishes before update:")
        for dish in dishes:
            print(f"  - {dish['dish_name']}: {dish['available_quantity']}")
        
        # Find and update the dish
        updated = False
        for dish in dishes:
            if dish['dish_name'] == dish_name:
                old_qty = dish['available_quantity']
                dish['available_quantity'] = new_quantity
                print(f"✓ Updated {dish_name}: {old_qty} -> {new_quantity}")
                updated = True
                break
        
        if not updated:
            print(f"✗ Dish '{dish_name}' not found")
            return {'error': f'Dish {dish_name} not found'}
        
        # Save the dishes
        save_dishes(dishes)
        print("✓ Dishes saved to file")
        
        # Reload to verify
        dishes = load_dishes()
        print(f"Current dishes after update:")
        for dish in dishes:
            print(f"  - {dish['dish_name']}: {dish['available_quantity']}")
        
        return {
            'message': f'Successfully updated {dish_name} to {new_quantity}',
            'dishes': dishes
        }
        
    except Exception as e:
        print(f"✗ Error in direct update: {e}")
        return {'error': str(e)}

@app.route('/debug/test-dish-save')
def debug_test_dish_save():
    """Debug route to test dish saving functionality"""
    try:
        print("=== TESTING DISH SAVE ===")
        
        # Load current dishes
        dishes = load_dishes()
        print(f"Loaded {len(dishes)} dishes")
        
        # Make a small change to test
        if dishes:
            old_qty = dishes[0]['available_quantity']
            dishes[0]['available_quantity'] = old_qty + 1
            print(f"Changed {dishes[0]['dish_name']} from {old_qty} to {dishes[0]['available_quantity']}")
        
        # Try to save
        print("Attempting to save dishes...")
        save_dishes(dishes)
        print("✓ Save successful!")
        
        # Reload to verify
        dishes_after = load_dishes()
        print(f"Reloaded {len(dishes_after)} dishes")
        if dishes_after:
            print(f"First dish quantity: {dishes_after[0]['available_quantity']}")
        
        return {
            'message': 'Dish save test completed successfully',
            'dishes_count': len(dishes_after),
            'first_dish': dishes_after[0] if dishes_after else None
        }
        
    except Exception as e:
        print(f"✗ Error in dish save test: {e}")
        import traceback
        traceback.print_exc()
        return {'error': str(e)}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)