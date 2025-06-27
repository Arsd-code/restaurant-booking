# Restaurant Booking System

## Overview

This is a Flask-based restaurant booking system that allows customers to view available dishes and make bookings, while providing administrators with tools to manage dishes and view bookings. The application uses a simple file-based JSON storage system for data persistence.

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

### Customer Flow
1. Customer visits homepage (`/`) to view available dishes
2. Customer selects a dish and navigates to booking page
3. Customer fills out booking form with personal details
4. Booking is saved to JSON file and dish quantity is decremented

### Admin Flow
1. Admin logs in via `/admin/login` with credentials
2. Admin can view dashboard with statistics
3. Admin can manage dishes (add, edit, delete) via `/admin/dishes`
4. Admin can view all bookings via `/admin/bookings`
5. Admin can logout to end session

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

## Changelog

- June 27, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.