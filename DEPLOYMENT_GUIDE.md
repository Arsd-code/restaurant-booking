# 🚀 Restaurant Booker - Client Demo Deployment Guide

## Quick Start (Choose One Option)

### Option 1: Instant Local Demo (Recommended for Immediate Demo)
```bash
# Double-click this file or run in terminal:
deploy.bat
```

### Option 2: Manual Local Demo
```bash
# Install dependencies
pip install -r requirements.txt

# Start server
python run_server.py
```

### Option 3: Network Demo (Access from other devices)
```bash
# Start server on network
python run_server.py

# Find your IP address and share:
# http://YOUR_IP_ADDRESS:5000/admin
```

## 🔐 Demo Access
- **URL**: http://localhost:5000/admin
- **Email**: admin@restaurant.com  
- **Password**: admin123

## 📊 What to Show Your Client

### 1. Admin Dashboard
- Show the overview with today's bookings and revenue
- Demonstrate the modern, clean interface

### 2. Booking Management
- Create a new booking for a customer
- Show how stock automatically updates
- Display booking history and details

### 3. Inventory Management
- Show current stock levels for each dish
- Demonstrate adding/editing dishes
- Show stock calendar with historical data

### 4. Revenue Analytics
- Display daily revenue reports
- Show date-range revenue analysis
- Export booking data to CSV

### 5. Stock Calendar
- Show historical stock tracking
- Demonstrate daily stock management
- Display booking patterns

## 🌐 Professional Deployment Options

### For Permanent Client Demo:

#### A. Railway (Recommended - Free & Easy)
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Get instant public URL (e.g., https://your-app.railway.app)

#### B. Render (Free Tier)
1. Go to [render.com](https://render.com)
2. Sign up and create "Web Service"
3. Connect your GitHub repository
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `gunicorn app:app`
6. Deploy and get public URL

#### C. Vercel (Alternative)
1. Go to [vercel.com](https://vercel.com)
2. Import your GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `gunicorn app:app`
5. Deploy automatically

## 📱 Demo Tips for Success

### Before the Demo:
1. **Add Sample Data**: Create a few bookings and adjust stock levels
2. **Test All Features**: Ensure everything works smoothly
3. **Prepare Your Script**: Know what you want to demonstrate

### During the Demo:
1. **Start with Dashboard**: Show the overview first
2. **Create Live Booking**: Demonstrate the booking process
3. **Show Stock Updates**: Highlight real-time inventory changes
4. **Display Reports**: Show revenue and analytics
5. **Answer Questions**: Be ready to explain features

### Key Features to Highlight:
- ✅ Modern, responsive design
- ✅ Real-time stock management
- ✅ Comprehensive booking system
- ✅ Revenue analytics and reporting
- ✅ Easy-to-use admin interface
- ✅ No database setup required
- ✅ Scalable and customizable

## 🔧 Troubleshooting

### Common Issues:
1. **Port 5000 in use**: Change port in `run_server.py`
2. **Dependencies missing**: Run `pip install -r requirements.txt`
3. **Permission errors**: Run as administrator on Windows

### For Network Access:
1. **Windows Firewall**: Allow Python through firewall
2. **Router Settings**: Forward port 5000 if needed
3. **IP Address**: Use `ipconfig` to find your local IP

## 📞 Support
If you need help with deployment, the system is designed to be simple and reliable. All data is stored locally in JSON files, making it perfect for demos and small-scale use. 