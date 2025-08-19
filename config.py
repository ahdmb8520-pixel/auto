"""
Configuration settings for the Vehicle Repair Workshop Management System
"""
import os
from pathlib import Path

# Application settings
APP_NAME = "Vehicle Repair Workshop Management"
APP_VERSION = "1.0.0"
DEFAULT_COMPANY_NAME = "Auto Repair Shop"

# Database settings
DB_PATH = "workshop.db"

# GUI settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
MIN_WINDOW_WIDTH = 1000
MIN_WINDOW_HEIGHT = 600

# Theme settings
DEFAULT_THEME = "flatly"
DARK_THEME = "darkly"
LIGHT_THEME = "flatly"

# Colors
COLORS = {
    'primary': '#007bff',
    'secondary': '#6c757d',
    'success': '#28a745',
    'danger': '#dc3545',
    'warning': '#ffc107',
    'info': '#17a2b8',
    'light': '#FFFFFF',
    'dark': '#343a40'
}

# Fonts
FONTS = {
    'default': ('Segoe UI', 10),
    'header': ('Segoe UI', 12, 'bold'),
    'title': ('Segoe UI', 14, 'bold'),
    'small': ('Segoe UI', 8)
}

# File paths
ASSETS_DIR = Path("assets")
LOGOS_DIR = ASSETS_DIR / "logos"
EXPORTS_DIR = Path("exports")

# Create directories if they don't exist
ASSETS_DIR.mkdir(exist_ok=True)
LOGOS_DIR.mkdir(exist_ok=True)
EXPORTS_DIR.mkdir(exist_ok=True)

# Services and Parts predefined lists
DEFAULT_SERVICES = [
    "Oil Change",
    "Brake Repair",
    "Transmission Service",
    "Engine Diagnostics",
    "Tire Rotation",
    "Wheel Alignment",
    "Air Filter Replacement",
    "Battery Test/Replacement",
    "Coolant Service",
    "Exhaust Repair",
    "Suspension Repair",
    "Air Conditioning Service"
]

DEFAULT_PARTS = [
    "Engine Oil",
    "Oil Filter",
    "Air Filter",
    "Brake Pads",
    "Brake Rotors",
    "Battery",
    "Spark Plugs",
    "Transmission Fluid",
    "Coolant",
    "Tires",
    "Windshield Wipers",
    "Belts and Hoses"
]
