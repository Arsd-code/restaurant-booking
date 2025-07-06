# Restaurant Booker - Inventory & Booking System

A modern web-based restaurant inventory and booking system for Mandi restaurants.

## 🚀 Quick Start (Local Demo)

### Option 1: Simple Python Server
```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python run_server.py
```

### Option 2: Using Gunicorn (Production)
```bash
# Install dependencies
pip install -r requirements.txt

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🔐 Admin Access
- **URL**: http://localhost:5000/admin
- **Email**: admin@restaurant.com
- **Password**: admin123

## 📊 Features
- **Admin Dashboard**: Overview of bookings, revenue, and stock
- **Booking Management**: Create and manage customer bookings
- **Inventory Management**: Track dish availability and stock levels
- **Revenue Analytics**: Daily and date-range revenue reports
- **Stock Calendar**: Historical stock tracking and management

## 🌐 Deployment Options

### 1. Local Network Demo
```bash
# Make accessible on your local network
python run_server.py
# Then access via: http://YOUR_IP:5000/admin
```

### 2. Cloud Deployment (Recommended for Client Demo)

#### A. Railway (Free & Easy)
1. Go to [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Deploy automatically
4. Get a public URL instantly

#### B. Render (Free Tier)
1. Go to [render.com](https://render.com)
2. Create new Web Service
3. Connect your repository
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `gunicorn app:app`

#### C. Heroku (Paid)
1. Install Heroku CLI
2. Create `Procfile`:
   ```
   web: gunicorn app:app
   ```
3. Deploy: `heroku create && git push heroku main`

### 3. VPS Deployment
```bash
# On your VPS
git clone <your-repo>
cd RestaurantBooker
pip install -r requirements.txt
gunicorn -w 4 -b 0.0.0.0:80 app:app
```

## 🔧 Configuration

### Environment Variables
- `PORT`: Server port (default: 5000)
- `HOST`: Server host (default: 0.0.0.0)
- `SESSION_SECRET`: Flask session secret (optional)

### Data Storage
- All data is stored in JSON files in the `data/` directory
- No database setup required
- Perfect for demos and small-scale use

## 📱 Client Demo Tips

1. **Prepare Sample Data**: Add some bookings and stock data before the demo
2. **Test All Features**: Ensure booking, inventory, and reporting work
3. **Use Modern UI**: The system has a modern, responsive interface
4. **Show Real-time Updates**: Demonstrate live stock updates and booking management

## 🛠️ Development

### Project Structure
```
RestaurantBooker/
├── app.py              # Main Flask application
├── run_server.py       # Production server runner
├── requirements.txt    # Python dependencies
├── data/              # JSON data storage
│   ├── dishes.json
│   ├── bookings.json
│   └── stock_history.json
├── templates/         # HTML templates
└── static/           # CSS and static files
```

### Adding Features
- All routes are in `app.py`
- Templates use modern HTML/CSS
- Data is stored in JSON for simplicity

## 🚨 Security Notes
- Change default admin credentials for production
- Use environment variables for secrets
- Consider adding rate limiting for production use 