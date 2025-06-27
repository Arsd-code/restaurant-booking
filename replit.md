# Restaurant Booking System

## Overview

This is a Flask-based restaurant inventory and booking system designed for admin-only operation. Customers call the restaurant and the admin enters bookings manually through the web interface. The system is specifically designed for Mandi restaurants with limited daily dish quantities. The application uses a simple file-based JSON storage system for data persistence.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Flask
- **UI Framework**: Bootstrap 5 with dark theme
- **Icons**: Font Awesome 6.0
- **Responsive Design**: Mobile-first approach using Bootstrap grid system

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Session Management**: Flask sessions with secret key
- **Authentication**: Simple password hashing using Werkzeug
- **Data Storage**: JSON file-based storage (dishes.json, bookings.json)
- **Server**: Gunicorn WSGI server for production deployment

### Data Storage
- **Storage Type**: File-based JSON storage
- **Data Files**: 
  - `data/dishes.json` - Stores dish information
  - `data/bookings.json` - Stores booking records
- **Structure**: Simple JSON arrays with object records

## Key Components

### Core Application (`app.py`)
- Main Flask application with route handlers
- Data management functions for dishes and bookings
- Admin authentication system
- Session management for admin access

### Templates
- **Base Template**: `base.html` - Common layout with navigation
- **Customer Pages**: `index.html`, `booking.html` - Customer-facing interface
- **Admin Pages**: `admin_login.html`, `admin_dashboard.html`, `admin_dishes.html`, `admin_bookings.html`

### Static Assets
- **Styling**: Custom CSS in `static/style.css`
- **External Dependencies**: Bootstrap and Font Awesome via CDN

### Configuration
- **Environment**: Python 3.11 with Nix package management
- **Dependencies**: Flask, Gunicorn, email-validator, psycopg2-binary (prepared for PostgreSQL)
- **Deployment**: Autoscale deployment target with Gunicorn

## Data Flow

### Customer Flow (Phone-based)
1. Customer calls the restaurant to place an order
2. Admin receives customer details over the phone
3. Admin enters booking information through the admin panel

### Admin Flow
1. Admin logs in via `/admin/login` with credentials (admin@restaurant.com / admin123)
2. Admin can view dashboard with statistics
3. Admin can make bookings on behalf of customers via `/admin/booking`
4. Admin can manage dishes (add, edit, delete) via `/admin/dishes`
5. Admin can view all bookings via `/admin/bookings`
6. Admin can logout to end session

### Booking Process
1. Admin receives customer call with order details
2. Admin selects customer's desired dish from available options
3. System automatically reduces dish quantity by 1
4. Booking is saved with timestamp and customer information
5. Admin can view confirmation and proceed with next order

## External Dependencies

### CDN Resources
- Bootstrap 5 (Dark theme from Replit CDN)
- Font Awesome 6.0 icons

### Python Packages
- **Flask**: Web framework
- **Werkzeug**: Password hashing and security utilities
- **Gunicorn**: Production WSGI server
- **email-validator**: Email validation
- **psycopg2-binary**: PostgreSQL adapter (prepared for future database migration)

## Deployment Strategy

### Development
- Local development using Flask's built-in server
- Debug mode enabled for development
- File-based storage for rapid prototyping

### Production
- Gunicorn WSGI server with auto-scaling
- Bound to 0.0.0.0:5000 for external access
- Reload enabled for development convenience
- Environment variables for configuration

### Infrastructure
- Nix package management for reproducible environments
- PostgreSQL package included for potential database migration
- OpenSSL for secure communications

## Recent Changes

- June 27, 2025: Converted system from customer-facing to admin-only operation
  - Removed public customer interface
  - Added admin booking form for phone orders
  - Updated navigation to focus on admin tasks
  - Root URL now redirects to admin login
  - Added sample Mandi dishes with realistic quantities
  - Enhanced admin dashboard with booking functionality

- June 27, 2025: Added advanced stock management and confirmation features
  - Implemented calendar-based stock editing system
  - Added date-based stock history tracking
  - Created confirmation modals for dish deletion
  - Updated pricing system to Indian Rupees (₹450-850)
  - Added stock calendar interface with past/future date editing
  - Enhanced revenue tracking with detailed analytics

## Changelog

- June 27, 2025: Initial setup
- June 27, 2025: Major architectural change - converted to admin-only booking system

## User Preferences

Preferred communication style: Simple, everyday language.
Restaurant focus: Mandi dishes with limited daily quantities
Operation model: Phone-based orders with admin data entry