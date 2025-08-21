"""
Database operations for the Vehicle Repair Workshop Management System
"""
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import config

class DatabaseManager:
    def __init__(self, db_path: str = config.DB_PATH):
        self.db_path = db_path
        self.init_database()
        
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database with all required tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create customers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT UNIQUE NOT NULL,
                    address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create vehicles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vehicles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    license_plate TEXT UNIQUE NOT NULL,
                    brand TEXT NOT NULL,
                    model TEXT NOT NULL,
                    customer_phone TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_phone) REFERENCES customers (phone)
                )
            ''')
            
            # Create work_orders table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS work_orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vehicle_id INTEGER NOT NULL,
                    entry_date DATE NOT NULL,
                    status TEXT DEFAULT 'Open',
                    total_cost REAL DEFAULT 0,
                    payment_status TEXT DEFAULT 'Unpaid',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (vehicle_id) REFERENCES vehicles (id)
                )
            ''')
            
            # Create services table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS services (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    work_order_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    quantity INTEGER DEFAULT 1,
                    price REAL NOT NULL,
                    FOREIGN KEY (work_order_id) REFERENCES work_orders (id)
                )
            ''')
            
            # Create spare_parts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS spare_parts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    work_order_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    quantity INTEGER DEFAULT 1,
                    price REAL NOT NULL,
                    FOREIGN KEY (work_order_id) REFERENCES work_orders (id)
                )
            ''')
            
            # Create invoices table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    work_order_id INTEGER NOT NULL,
                    invoice_date DATE NOT NULL,
                    total_amount REAL NOT NULL,
                    status TEXT DEFAULT 'Unpaid',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (work_order_id) REFERENCES work_orders (id)
                )
            ''')
            
            # Create settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            ''')
            # Create service templates table
            cursor.execute('''
                            CREATE TABLE IF NOT EXISTS service_templates (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT UNIQUE NOT NULL,
                                description TEXT,
                                default_price REAL DEFAULT 0,
                                category TEXT DEFAULT 'General',
                                is_active INTEGER DEFAULT 1,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )
                        ''')

            # Create spare part templates table
            cursor.execute('''
                            CREATE TABLE IF NOT EXISTS spare_part_templates (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT UNIQUE NOT NULL,
                                description TEXT,
                                default_price REAL DEFAULT 0,
                                category TEXT DEFAULT 'General',
                                supplier TEXT,
                                part_number TEXT,
                                is_active INTEGER DEFAULT 1,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )
                        ''')
            
            # Create appointments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS appointments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    date DATETIME NOT NULL
                )
            ''')
            
            conn.commit()
            
    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Execute a SELECT query and return results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return affected rows"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
    
    def get_last_insert_id(self) -> int:
        """Get the last inserted row ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            return cursor.lastrowid
    
    # Customer operations
    def add_customer(self, name: str, phone: str, address: str = "") -> int:
        """Add a new customer"""
        query = "INSERT INTO customers (name, phone, address) VALUES (?, ?, ?)"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (name, phone, address))
            conn.commit()
            return cursor.lastrowid
    
    def get_customers(self) -> List[sqlite3.Row]:
        """Get all customers"""
        query = "SELECT * FROM customers ORDER BY name"
        return self.execute_query(query)
    
    def search_customers(self, search_term: str) -> List[sqlite3.Row]:
        """Search customers by name or phone"""
        query = "SELECT * FROM customers WHERE name LIKE ? OR phone LIKE ? ORDER BY name"
        return self.execute_query(query, (f"%{search_term}%", f"%{search_term}%"))
    
    def update_customer(self, customer_id: int, name: str, phone: str, address: str) -> int:
        """Update customer information"""
        query = "UPDATE customers SET name = ?, phone = ?, address = ? WHERE id = ?"
        return self.execute_update(query, (name, phone, address, customer_id))
    
    def delete_customer(self, customer_id: int) -> int:
        """Delete a customer"""
        query = "DELETE FROM customers WHERE id = ?"
        return self.execute_update(query, (customer_id,))
    
    # Vehicle operations
    def add_vehicle(self, license_plate: str, brand: str, model: str, customer_phone: str) -> int:
        """Add a new vehicle"""
        query = "INSERT INTO vehicles (license_plate, brand, model, customer_phone) VALUES (?, ?, ?, ?)"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (license_plate, brand, model, customer_phone))
            conn.commit()
            return cursor.lastrowid
    
    def get_vehicles(self) -> List[sqlite3.Row]:
        """Get all vehicles with customer information"""
        query = '''
            SELECT v.*, c.name as customer_name 
            FROM vehicles v 
            JOIN customers c ON v.customer_phone = c.phone 
            ORDER BY v.license_plate
        '''
        return self.execute_query(query)
    
    def search_vehicles(self, search_term: str) -> List[sqlite3.Row]:
        """Search vehicles by license plate"""
        query = '''
            SELECT v.*, c.name as customer_name 
            FROM vehicles v 
            JOIN customers c ON v.customer_phone = c.phone 
            WHERE v.license_plate LIKE ? OR v.brand LIKE ? OR v.model LIKE ?
            ORDER BY v.license_plate
        '''
        return self.execute_query(query, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
    
    def update_vehicle(self, vehicle_id: int, license_plate: str, brand: str, model: str, customer_phone: str) -> int:
        """Update vehicle information"""
        query = "UPDATE vehicles SET license_plate = ?, brand = ?, model = ?, customer_phone = ? WHERE id = ?"
        return self.execute_update(query, (license_plate, brand, model, customer_phone, vehicle_id))
    
    def delete_vehicle(self, vehicle_id: int) -> int:
        """Delete a vehicle"""
        query = "DELETE FROM vehicles WHERE id = ?"
        return self.execute_update(query, (vehicle_id,))
    
    # Work order operations
    def add_work_order(self, vehicle_id: int, entry_date: str, status: str = "Open") -> int:
        """Add a new work order"""
        query = "INSERT INTO work_orders (vehicle_id, entry_date, status) VALUES (?, ?, ?)"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (vehicle_id, entry_date, status))
            conn.commit()
            return cursor.lastrowid
    
    def get_work_orders(self) -> List[sqlite3.Row]:
        """Get all work orders with vehicle and customer information"""
        query = '''
            SELECT wo.*, v.license_plate, v.brand, v.model, c.name as customer_name, c.phone as customer_phone
            FROM work_orders wo
            JOIN vehicles v ON wo.vehicle_id = v.id
            JOIN customers c ON v.customer_phone = c.phone
            ORDER BY wo.entry_date DESC
        '''
        return self.execute_query(query)
    
    def get_work_order_details(self, work_order_id: int) -> Optional[sqlite3.Row]:
        """Get detailed work order information"""
        query = '''
            SELECT wo.*, v.license_plate, v.brand, v.model, c.name as customer_name, c.phone as customer_phone
            FROM work_orders wo
            JOIN vehicles v ON wo.vehicle_id = v.id
            JOIN customers c ON v.customer_phone = c.phone
            WHERE wo.id = ?
        '''
        results = self.execute_query(query, (work_order_id,))
        return results[0] if results else None
    
    def update_work_order_status(self, work_order_id: int, status: str) -> int:
        """Update work order status"""
        query = "UPDATE work_orders SET status = ? WHERE id = ?"
        return self.execute_update(query, (status, work_order_id))
    
    def update_work_order_payment_status(self, work_order_id: int, payment_status: str) -> int:
        """Update work order payment status"""
        query = "UPDATE work_orders SET payment_status = ? WHERE id = ?"
        return self.execute_update(query, (payment_status, work_order_id))
    
    def calculate_work_order_total(self, work_order_id: int) -> float:
        """Calculate and update work order total cost"""
        # Get services total
        services_query = "SELECT SUM(quantity * price) as total FROM services WHERE work_order_id = ?"
        services_result = self.execute_query(services_query, (work_order_id,))
        services_total = services_result[0]['total'] or 0
        
        # Get parts total
        parts_query = "SELECT SUM(quantity * price) as total FROM spare_parts WHERE work_order_id = ?"
        parts_result = self.execute_query(parts_query, (work_order_id,))
        parts_total = parts_result[0]['total'] or 0
        
        total_cost = services_total + parts_total
        
        # Update work order total
        update_query = "UPDATE work_orders SET total_cost = ? WHERE id = ?"
        self.execute_update(update_query, (total_cost, work_order_id))
        
        return total_cost
    
    # Service operations
    def add_service(self, work_order_id: int, name: str, description: str, quantity: int, price: float) -> int:
        """Add a service to work order"""
        query = "INSERT INTO services (work_order_id, name, description, quantity, price) VALUES (?, ?, ?, ?, ?)"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (work_order_id, name, description, quantity, price))
            conn.commit()
            service_id = cursor.lastrowid
            
        # Recalculate work order total
        self.calculate_work_order_total(work_order_id)
        return service_id
    
    def get_services_by_work_order(self, work_order_id: int) -> List[sqlite3.Row]:
        """Get all services for a work order"""
        query = "SELECT * FROM services WHERE work_order_id = ? ORDER BY name"
        return self.execute_query(query, (work_order_id,))
    
    def delete_service(self, service_id: int, work_order_id: int) -> int:
        """Delete a service and recalculate total"""
        query = "DELETE FROM services WHERE id = ?"
        result = self.execute_update(query, (service_id,))
        self.calculate_work_order_total(work_order_id)
        return result
    
    # Spare parts operations
    def add_spare_part(self, work_order_id: int, name: str, description: str, quantity: int, price: float) -> int:
        """Add a spare part to work order"""
        query = "INSERT INTO spare_parts (work_order_id, name, description, quantity, price) VALUES (?, ?, ?, ?, ?)"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (work_order_id, name, description, quantity, price))
            conn.commit()
            part_id = cursor.lastrowid
            
        # Recalculate work order total
        self.calculate_work_order_total(work_order_id)
        return part_id
    
    def get_spare_parts_by_work_order(self, work_order_id: int) -> List[sqlite3.Row]:
        """Get all spare parts for a work order"""
        query = "SELECT * FROM spare_parts WHERE work_order_id = ? ORDER BY name"
        return self.execute_query(query, (work_order_id,))
    
    def delete_spare_part(self, part_id: int, work_order_id: int) -> int:
        """Delete a spare part and recalculate total"""
        query = "DELETE FROM spare_parts WHERE id = ?"
        result = self.execute_update(query, (part_id,))
        self.calculate_work_order_total(work_order_id)
        return result
    
    # Invoice operations
    def create_invoice(self, work_order_id: int) -> int:
        """Create an invoice from a work order"""
        # Get work order total
        work_order = self.get_work_order_details(work_order_id)
        if not work_order:
            raise ValueError("Work order not found")
        
        query = "INSERT INTO invoices (work_order_id, invoice_date, total_amount) VALUES (?, ?, ?)"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (work_order_id, datetime.now().strftime('%Y-%m-%d'), work_order['total_cost']))
            conn.commit()
            return cursor.lastrowid
    
    def get_invoices(self) -> List[sqlite3.Row]:
        """Get all invoices with work order and customer information"""
        query = '''
            SELECT i.*, wo.entry_date, v.license_plate, c.name as customer_name, c.phone as customer_phone
            FROM invoices i
            JOIN work_orders wo ON i.work_order_id = wo.id
            JOIN vehicles v ON wo.vehicle_id = v.id
            JOIN customers c ON v.customer_phone = c.phone
            ORDER BY i.invoice_date DESC
        '''
        return self.execute_query(query)
    
    def update_invoice_status(self, invoice_id: int, status: str) -> int:
        """Update invoice status"""
        query = "UPDATE invoices SET status = ? WHERE id = ?"
        return self.execute_update(query, (status, invoice_id))
    
    # Appointment operations
    def add_appointment(self, name: str, description: str, date_str: str) -> int:
        """Add a new appointment"""
        query = "INSERT INTO appointments (name, description, date) VALUES (?, ?, ?)"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (name, description, date_str))
            conn.commit()
            return cursor.lastrowid
    
    def get_appointments(self) -> List[sqlite3.Row]:
        """Get all appointments ordered by date"""
        query = "SELECT * FROM appointments ORDER BY date DESC, id DESC"
        return self.execute_query(query)
    
    def search_appointments(self, search_term: str) -> List[sqlite3.Row]:
        """Search appointments by name or date"""
        query = "SELECT * FROM appointments WHERE name LIKE ? OR date LIKE ? ORDER BY date DESC, id DESC"
        like = f"%{search_term}%"
        return self.execute_query(query, (like, like))
    
    def update_appointment(self, appointment_id: int, name: str, description: str, date_str: str) -> int:
        """Update an appointment"""
        query = "UPDATE appointments SET name = ?, description = ?, date = ? WHERE id = ?"
        return self.execute_update(query, (name, description, date_str, appointment_id))
    
    def delete_appointment(self, appointment_id: int) -> int:
        """Delete an appointment"""
        query = "DELETE FROM appointments WHERE id = ?"
        return self.execute_update(query, (appointment_id,))
    
    # Settings operations
    def get_setting(self, key: str, default: str = "") -> str:
        """Get a setting value"""
        query = "SELECT value FROM settings WHERE key = ?"
        result = self.execute_query(query, (key,))
        return result[0]['value'] if result else default
    
    def set_setting(self, key: str, value: str) -> int:
        """Set a setting value"""
        query = "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)"
        return self.execute_update(query, (key, value))

        # Service Template operations
        def add_service_template(self, name: str, description: str = "", default_price: float = 0,
                                 category: str = "General") -> int:
            """Add a service template"""
            query = "INSERT INTO service_templates (name, description, default_price, category) VALUES (?, ?, ?, ?)"
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (name, description, default_price, category))
                conn.commit()
                return cursor.lastrowid

        def get_service_templates(self, active_only: bool = True) -> List[sqlite3.Row]:
            """Get all service templates"""
            if active_only:
                query = "SELECT * FROM service_templates WHERE is_active = 1 ORDER BY category, name"
            else:
                query = "SELECT * FROM service_templates ORDER BY category, name"
            return self.execute_query(query)

        def update_service_template(self, template_id: int, name: str, description: str,
                                    default_price: float, category: str) -> int:
            """Update service template"""
            query = "UPDATE service_templates SET name = ?, description = ?, default_price = ?, category = ? WHERE id = ?"
            return self.execute_update(query, (name, description, default_price, category, template_id))

        def delete_service_template(self, template_id: int) -> int:
            """Delete service template"""
            query = "DELETE FROM service_templates WHERE id = ?"
            return self.execute_update(query, (template_id,))

        def toggle_service_template_status(self, template_id: int) -> int:
            """Toggle service template active status"""
            query = "UPDATE service_templates SET is_active = 1 - is_active WHERE id = ?"
            return self.execute_update(query, (template_id,))

        # Spare Part Template operations
        def add_spare_part_template(self, name: str, description: str = "", default_price: float = 0,
                                    category: str = "General", supplier: str = "", part_number: str = "") -> int:
            """Add a spare part template"""
            query = "INSERT INTO spare_part_templates (name, description, default_price, category, supplier, part_number) VALUES (?, ?, ?, ?, ?, ?)"
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (name, description, default_price, category, supplier, part_number))
                conn.commit()
                return cursor.lastrowid

        def get_spare_part_templates(self, active_only: bool = True) -> List[sqlite3.Row]:
            """Get all spare part templates"""
            if active_only:
                query = "SELECT * FROM spare_part_templates WHERE is_active = 1 ORDER BY category, name"
            else:
                query = "SELECT * FROM spare_part_templates ORDER BY category, name"
            return self.execute_query(query)

        def update_spare_part_template(self, template_id: int, name: str, description: str,
                                       default_price: float, category: str, supplier: str, part_number: str) -> int:
            """Update spare part template"""
            query = "UPDATE spare_part_templates SET name = ?, description = ?, default_price = ?, category = ?, supplier = ?, part_number = ? WHERE id = ?"
            return self.execute_update(query,
                                       (name, description, default_price, category, supplier, part_number, template_id))

        def delete_spare_part_template(self, template_id: int) -> int:
            """Delete spare part template"""
            query = "DELETE FROM spare_part_templates WHERE id = ?"
            return self.execute_update(query, (template_id,))

        def toggle_spare_part_template_status(self, template_id: int) -> int:
            """Toggle spare part template active status"""
            query = "UPDATE spare_part_templates SET is_active = 1 - is_active WHERE id = ?"
            return self.execute_update(query, (template_id,))

        def get_service_categories(self) -> List[str]:
            """Get all unique service categories"""
            query = "SELECT DISTINCT category FROM service_templates WHERE is_active = 1 ORDER BY category"
            results = self.execute_query(query)
            return [row['category'] for row in results]

        def get_part_categories(self) -> List[str]:
            """Get all unique spare part categories"""
            query = "SELECT DISTINCT category FROM spare_part_templates WHERE is_active = 1 ORDER BY category"
            results = self.execute_query(query)
            return [row['category'] for row in results]

    # Reports operations
    def get_repair_statistics(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Get repair statistics for a date range"""
        date_filter = ""
        params = []
        
        if start_date and end_date:
            date_filter = "WHERE wo.entry_date BETWEEN ? AND ?"
            params = [start_date, end_date]
        
        # Get total and completed work orders
        query = f'''
            SELECT 
                COUNT(*) as total_orders,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed_orders,
                SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) as open_orders,
                SUM(total_cost) as total_revenue,
                AVG(total_cost) as avg_order_value
            FROM work_orders wo
            {date_filter}
        '''
        
        result = self.execute_query(query, params)
        stats = dict(result[0]) if result else {}
        
        # Get most used services
        services_query = f'''
            SELECT s.name, COUNT(*) as usage_count, SUM(s.quantity) as total_quantity
            FROM services s
            JOIN work_orders wo ON s.work_order_id = wo.id
            {date_filter}
            GROUP BY s.name
            ORDER BY usage_count DESC
            LIMIT 10
        '''
        
        services_stats = self.execute_query(services_query, params)
        stats['top_services'] = [dict(row) for row in services_stats]
        
        # Get most active customers
        customers_query = f'''
            SELECT c.name, c.phone, COUNT(wo.id) as order_count, SUM(wo.total_cost) as total_spent
            FROM customers c
            JOIN vehicles v ON c.phone = v.customer_phone
            JOIN work_orders wo ON v.id = wo.vehicle_id
            {date_filter}
            GROUP BY c.name, c.phone
            ORDER BY order_count DESC
            LIMIT 10
        '''
        
        customers_stats = self.execute_query(customers_query, params)
        stats['top_customers'] = [dict(row) for row in customers_stats]
        
        return stats
    
    def get_revenue_by_period(self, period: str = 'monthly') -> List[Dict[str, Any]]:
        """Get revenue statistics by time period"""
        if period == 'daily':
            date_format = '%Y-%m-%d'
            group_by = "DATE(wo.entry_date)"
        elif period == 'monthly':
            date_format = '%Y-%m'
            group_by = "strftime('%Y-%m', wo.entry_date)"
        else:  # yearly
            date_format = '%Y'
            group_by = "strftime('%Y', wo.entry_date)"
        
        query = f'''
            SELECT 
                {group_by} as period,
                COUNT(*) as order_count,
                SUM(total_cost) as revenue,
                AVG(total_cost) as avg_order_value
            FROM work_orders wo
            WHERE status = 'Completed'
            GROUP BY {group_by}
            ORDER BY period DESC
            LIMIT 12
        '''
        
        results = self.execute_query(query)
        return [dict(row) for row in results]
