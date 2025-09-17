-- ===============================================
-- INVENTORY TRACKING DATABASE SCHEMA
-- Student: Stephen
-- ===============================================

-- Create the database
CREATE DATABASE inventory_tracking_db;
USE inventory_tracking_db;

-- ===============================================
-- TABLE CREATION WITH RELATIONSHIPS
-- ===============================================

-- Categories table
CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Suppliers table
CREATE TABLE suppliers (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_name VARCHAR(150) NOT NULL,
    contact_person VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products table
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    product_code VARCHAR(50) NOT NULL UNIQUE,
    category_id INT NOT NULL,
    supplier_id INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL CHECK (unit_price >= 0),
    reorder_level INT DEFAULT 10 CHECK (reorder_level >= 0),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE RESTRICT,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE RESTRICT
);

-- Inventory table (current stock levels)
CREATE TABLE inventory (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL UNIQUE,
    quantity_in_stock INT NOT NULL DEFAULT 0 CHECK (quantity_in_stock >= 0),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- Purchase orders table
CREATE TABLE purchase_orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id INT NOT NULL,
    order_date DATE NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    status ENUM('pending', 'received', 'cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE RESTRICT
);

-- Purchase order items table
CREATE TABLE purchase_order_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL CHECK (unit_price >= 0),
    total_price DECIMAL(12,2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
    FOREIGN KEY (order_id) REFERENCES purchase_orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT
);

-- ===============================================
-- SAMPLE DATA INSERTION
-- ===============================================

-- Insert categories
INSERT INTO categories (category_name, description) VALUES
('Electronics', 'Electronic devices and components'),
('Office Supplies', 'Office stationery and supplies'),
('Furniture', 'Office and home furniture'),
('Cleaning Supplies', 'Cleaning and maintenance supplies');

-- Insert suppliers
INSERT INTO suppliers (supplier_name, contact_person, email, phone, address) VALUES
('TechCorp Kenya', 'John Mwangi', 'john@techcorp.ke', '+254-700-123456', 'Nairobi, Kenya'),
('Office Plus Ltd', 'Mary Wanjiku', 'mary@officeplus.ke', '+254-700-234567', 'Mombasa, Kenya'),
('Furniture World', 'Peter Kimani', 'peter@furnitureworld.ke', '+254-700-345678', 'Kisumu, Kenya');

-- Insert products
INSERT INTO products (product_name, product_code, category_id, supplier_id, unit_price, reorder_level, description) VALUES
('Laptop Dell Inspiron', 'DELL-INSP-001', 1, 1, 75000.00, 5, 'Dell Inspiron 15 laptop'),
('Wireless Mouse', 'MOUSE-WRL-001', 1, 1, 2500.00, 20, 'Wireless optical mouse'),
('A4 Paper Ream', 'PAPER-A4-001', 2, 2, 800.00, 50, 'A4 size white paper 500 sheets'),
('Office Chair', 'CHAIR-OFF-001', 3, 3, 15000.00, 10, 'Ergonomic office chair'),
('Desk Sanitizer', 'CLEAN-SAN-001', 4, 2, 500.00, 30, 'Desk cleaning sanitizer spray');

-- Insert initial inventory
INSERT INTO inventory (product_id, quantity_in_stock) VALUES
(1, 15),
(2, 45),
(3, 200),
(4, 25),
(5, 80);

-- Insert sample purchase orders
INSERT INTO purchase_orders (supplier_id, order_date, total_amount, status) VALUES
(1, '2024-01-15', 150000.00, 'received'),
(2, '2024-01-20', 25000.00, 'pending');

-- Insert purchase order items
INSERT INTO purchase_order_items (order_id, product_id, quantity, unit_price) VALUES
(1, 1, 2, 75000.00),
(1, 2, 10, 2500.00),
(2, 3, 30, 800.00),
(2, 5, 10, 500.00);

-- ===============================================
-- USEFUL VIEWS FOR REPORTING
-- ===============================================

-- View: Products with low stock
CREATE VIEW low_stock_products AS
SELECT 
    p.product_id,
    p.product_name,
    p.product_code,
    i.quantity_in_stock,
    p.reorder_level,
    c.category_name,
    s.supplier_name
FROM products p
JOIN inventory i ON p.product_id = i.product_id
JOIN categories c ON p.category_id = c.category_id
JOIN suppliers s ON p.supplier_id = s.supplier_id
WHERE i.quantity_in_stock <= p.reorder_level;

-- View: Product inventory summary
CREATE VIEW inventory_summary AS
SELECT 
    p.product_id,
    p.product_name,
    p.product_code,
    c.category_name,
    s.supplier_name,
    i.quantity_in_stock,
    p.unit_price,
    (i.quantity_in_stock * p.unit_price) AS total_value
FROM products p
JOIN inventory i ON p.product_id = i.product_id
JOIN categories c ON p.category_id = c.category_id
JOIN suppliers s ON p.supplier_id = s.supplier_id;

-- ===============================================
-- DATABASE SCHEMA COMPLETED BY: Stephen
-- ===============================================