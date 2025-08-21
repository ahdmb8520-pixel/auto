"""
Main application file for Vehicle Repair Workshop Management System
"""
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

import config
from database import DatabaseManager
from frames import *
import utils

class WorkshopApp:
    """Main application class"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.current_frame = None
        self.frames = {}
        
        # Initialize theme settings from database
        self.current_theme = self.db_manager.get_setting('theme', config.DEFAULT_THEME)
        
        # Create main window
        self.root = ttkb.Window(themename=self.current_theme)
        self.setup_main_window()
        self.create_widgets()
        self.show_frame('customers')  # Show customers frame by default
        
    def setup_main_window(self):
        """Setup the main application window"""
        # Get company name from settings
        company_name = self.db_manager.get_setting('company_name', config.DEFAULT_COMPANY_NAME)
        self.root.title(f"{company_name} - {config.APP_NAME}")
        
        # Set window size and position
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.root.minsize(config.MIN_WINDOW_WIDTH, config.MIN_WINDOW_HEIGHT)
        
        # Center window
        utils.center_window(self.root, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # Set icon if available
        try:
            icon_path = config.LOGOS_DIR / "icon.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except:
            pass
    
    def create_widgets(self):
        """Create the main application widgets"""
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.create_content_area()
        
        # Create status bar
        self.create_status_bar()
    
    def create_sidebar(self):
        """Create the navigation sidebar"""
        sidebar_frame = ttk.Frame(self.root, width=200, style='info.TFrame')
        sidebar_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 2))
        sidebar_frame.grid_propagate(False)
        
        # Company logo/name
        header_frame = ttk.Frame(sidebar_frame, style='info.TFrame')
        header_frame.pack(fill=X, padx=10, pady=10)
        
        # Try to load company logo
        logo_path = config.LOGOS_DIR / "logo.png"
        if logo_path.exists():
            try:
                logo_image = utils.load_image(str(logo_path), (150, 100))
                if logo_image:
                    logo_label = ttk.Label(header_frame, image=logo_image, style='info.TLabel')
                    logo_label.image = logo_image  # Keep a reference
                    logo_label.pack()
            except:
                pass
        
        # Company name
        company_name = self.db_manager.get_setting('company_name', config.DEFAULT_COMPANY_NAME)
        company_label = ttk.Label(header_frame, text=company_name, 
                                 font=config.FONTS['title'], style='')
        company_label.pack(pady=(5, 0))
        
        # Navigation buttons
        nav_frame = ttk.Frame(sidebar_frame, style='info.TFrame')
        nav_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Define navigation items
        nav_items = [
            ('customers', 'Customers', '👥'),
            ('vehicles', 'Vehicles', '🚗'),
            ('work_orders', 'Work Orders', '🔧'),
            ('invoices', 'Invoices', '📄'),
            ('appointments', 'Appointments', '📅'),
            #('services_parts', 'Services', '🔧'),
            ('reports', 'Reports', '📊'),
            ('settings', 'Settings', '⚙️')
        ]
        
        self.nav_buttons = {}
        
        for frame_name, display_name, icon in nav_items:
            btn_text = f"{icon} {display_name}"
            btn = ttk.Button(nav_frame, text=btn_text, 
                           command=lambda f=frame_name: self.show_frame(f),
                           bootstyle='outline-info', width=18)
            btn.pack(fill=X, pady=2)
            self.nav_buttons[frame_name] = btn
    
    def create_content_area(self):
        """Create the main content area"""
        self.content_frame = ttk.Frame(self.root)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=2)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
    
    def create_status_bar(self):
        """Create the status bar"""
        status_frame = ttk.Frame(self.root, style='secondary.TFrame')
        status_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(2, 0))
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, 
                               style='secondary.TLabel')
        status_label.pack(side=LEFT, padx=10, pady=2)
        
        # Add current date/time
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        time_label = ttk.Label(status_frame, text=current_time, style='secondary.TLabel')
        time_label.pack(side=RIGHT, padx=10, pady=2)
    
    def show_frame(self, frame_name):
        """Show the specified frame"""
        # Update navigation button styles
        for name, btn in self.nav_buttons.items():
            if name == frame_name:
                btn.configure(bootstyle='info')
            else:
                btn.configure(bootstyle='outline-info')
        
        # Hide current frame
        if self.current_frame:
            self.current_frame.pack_forget()
        
        # Create or show the requested frame
        if frame_name not in self.frames:
            self.create_frame(frame_name)
        
        self.current_frame = self.frames[frame_name]
        self.current_frame.pack(fill=BOTH, expand=True)
        
        # Update status
        frame_titles = {
            'customers': 'Customer Management',
            'vehicles': 'Vehicle Management',
            'work_orders': 'Work Order Management',
            'invoices': 'Invoice Management',
            'appointments': 'Appointment Management',
            #'services_parts': 'ServicesPartsFrame',
            'reports': 'Reports and Statistics',
            'settings': 'Application Settings'
        }
        self.status_var.set(f"Current: {frame_titles.get(frame_name, frame_name.title())}")
    
    def create_frame(self, frame_name):
        """Create a specific frame"""
        frame_classes = {
            'customers': CustomersFrame,
            'vehicles': VehiclesFrame,
            'work_orders': WorkOrdersFrame,
            'invoices': InvoicesFrame,
            'appointments': AppointmentsFrame,
            #'services_parts': ServicesPartsFrame,
            'reports': ReportsFrame,
            'settings': SettingsFrame
        }
        
        if frame_name in frame_classes:
            frame_class = frame_classes[frame_name]
            self.frames[frame_name] = frame_class(self.content_frame, self.db_manager, self)
        else:
            # Create a placeholder frame
            placeholder = ttk.Frame(self.content_frame)
            label = ttk.Label(placeholder, text=f"{frame_name.title()} - Coming Soon", 
                            font=config.FONTS['title'])
            label.pack(expand=True)
            self.frames[frame_name] = placeholder
    
    def refresh_current_frame(self):
        """Refresh the current frame"""
        if self.current_frame and hasattr(self.current_frame, 'refresh'):
            self.current_frame.refresh()
    
    def update_theme(self, theme_name):
        """Update application theme"""
        self.current_theme = theme_name
        self.db_manager.set_setting('theme', theme_name)
        
        # Show restart message
        utils.show_info("Theme Changed", 
                       "Theme has been updated. Please restart the application to see changes.")
    
    def update_company_info(self):
        """Update company information in the interface"""
        # This would be called from settings when company info is updated
        company_name = self.db_manager.get_setting('company_name', config.DEFAULT_COMPANY_NAME)
        self.root.title(f"{company_name} - {config.APP_NAME}")
        
        # Refresh sidebar to update company name
        # For simplicity, we could just show a message to restart
        utils.show_info("Company Information Updated", 
                       "Company information has been updated. Please restart the application to see changes.")
    
    def run(self):
        """Start the application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.close_application()
        except Exception as e:
            utils.show_error("Application Error", f"An unexpected error occurred: {e}")
    
    def close_application(self):
        """Close the application"""
        self.root.quit()
        self.root.destroy()

def main():
    """Main function to start the application"""
    try:
        # Create application instance
        app = WorkshopApp()
        
        # Start the application
        app.run()
        
    except Exception as e:
        # Show error if app fails to start
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        utils.show_error("Startup Error", f"Failed to start application: {e}")
        root.destroy()

if __name__ == "__main__":
    main()
