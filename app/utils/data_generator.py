import psycopg2
from faker import Faker
import random

fake = Faker()

# Connection to your PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="oracle_orange",
    user="postgres",
    password="admin123"  # Change this to your actual PostgreSQL password
)
cur = conn.cursor()

# DROP TABLES IF THEY EXIST (start fresh)
cur.execute("""
    DROP TABLE IF EXISTS sales CASCADE;
    DROP TABLE IF EXISTS products CASCADE;
    DROP TABLE IF EXISTS customers CASCADE;
    DROP TABLE IF EXISTS employees CASCADE;
    DROP TABLE IF EXISTS categories CASCADE;
""")

# CREATE TABLES WITH FIXED COLUMN SIZES
cur.execute("""
    CREATE TABLE customers (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(100),
        email VARCHAR(100) UNIQUE,
        phone VARCHAR(50),
        city VARCHAR(50),
        state VARCHAR(2),
        industry VARCHAR(50),
        customer_segment VARCHAR(20),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE categories (
        id SERIAL PRIMARY KEY,
        category_name VARCHAR(50) UNIQUE,
        profit_margin DECIMAL(5,2)
    );
    
    CREATE TABLE products (
        id SERIAL PRIMARY KEY,
        product_name VARCHAR(100),
        category_id INTEGER REFERENCES categories(id),
        price DECIMAL(10,2),
        cost DECIMAL(10,2),
        sku VARCHAR(20) UNIQUE
    );
    
    CREATE TABLE employees (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(100),
        email VARCHAR(100) UNIQUE,
        department VARCHAR(50),
        hire_date DATE,
        salary DECIMAL(10,2),
        performance_score INTEGER
    );
    
    CREATE TABLE sales (
        id SERIAL PRIMARY KEY,
        customer_id INTEGER REFERENCES customers(id),
        product_id INTEGER REFERENCES products(id),
        employee_id INTEGER REFERENCES employees(id),
        sale_date DATE,
        quantity INTEGER,
        unit_price DECIMAL(10,2),
        discount DECIMAL(5,2) DEFAULT 0,
        total_amount DECIMAL(10,2),
        payment_method VARCHAR(20)
    );
""")

print("✅ Tables created!")

# 1. INSERT CATEGORIES
categories = [
    ('Electronics', 0.35), ('Clothing', 0.50), ('Books', 0.30),
    ('Home & Garden', 0.40), ('Sports', 0.45), ('Toys', 0.55),
    ('Automotive', 0.25), ('Food & Beverage', 0.20), ('Health', 0.60),
    ('Office Supplies', 0.30)
]
for cat_name, margin in categories:
    cur.execute("INSERT INTO categories (category_name, profit_margin) VALUES (%s, %s)", (cat_name, margin))
print(f"✅ Inserted {len(categories)} categories")

# 2. INSERT CUSTOMERS (with guaranteed unique emails)
customer_ids = []
used_emails = set()  # Keep track of used emails

for _ in range(500):
    # Generate a unique email
    while True:
        first_name = fake.first_name()
        last_name = fake.last_name()
        domain = random.choice(['gmail.com', 'yahoo.com', 'outlook.com', 'company.com', 'example.com'])
        email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@{domain}"
        if email not in used_emails:
            used_emails.add(email)
            break
    
    name = f"{first_name} {last_name}"
    phone = fake.phone_number()[:20]
    city = fake.city()
    state = fake.state_abbr()
    industry = random.choice(['Tech', 'Retail', 'Healthcare', 'Finance', 'Education', 'Manufacturing'])
    segment = random.choices(['Premium', 'Standard', 'Basic'], weights=[20, 50, 30])[0]
    
    cur.execute("""
        INSERT INTO customers (full_name, email, phone, city, state, industry, customer_segment)
        VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
    """, (name, email, phone, city, state, industry, segment))
    customer_ids.append(cur.fetchone()[0])
    
    if _ % 100 == 0:
        print(f"Inserted {_}/500 customers")

print(f"✅ Inserted {len(customer_ids)} customers")

# 3. INSERT PRODUCTS
product_ids = []
category_ids = list(range(1, 11))
used_skus = set()

for _ in range(200):
    category_id = random.choice(category_ids)
    cur.execute("SELECT profit_margin FROM categories WHERE id = %s", (category_id,))
    margin = float(cur.fetchone()[0])  # Convert Decimal to float
    
    price = round(random.uniform(9.99, 299.99), 2)
    cost = round(price * (1 - margin), 2)
    product_name = fake.catch_phrase()[:50]
    
    # Generate unique SKU
    while True:
        sku = f"SKU-{fake.unique.bothify('???-#####')}"
        if sku not in used_skus:
            used_skus.add(sku)
            break
    
    cur.execute("""
        INSERT INTO products (product_name, category_id, price, cost, sku)
        VALUES (%s, %s, %s, %s, %s) RETURNING id
    """, (product_name, category_id, price, cost, sku))
    product_ids.append(cur.fetchone()[0])
print(f"✅ Inserted {len(product_ids)} products")

# 4. INSERT EMPLOYEES (with guaranteed unique emails)
employee_ids = []
departments = ['Sales', 'Support', 'Engineering', 'Marketing', 'Finance']
used_employee_emails = set()

for _ in range(50):
    # Generate unique email for employee
    while True:
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 99)}@company.com"
        if email not in used_employee_emails:
            used_employee_emails.add(email)
            break
    
    name = f"{first_name} {last_name}"
    dept = random.choice(departments)
    hire_date = fake.date_between(start_date='-5y', end_date='today')
    salary = round(random.uniform(45000, 120000), 2)
    performance = random.randint(40, 100)
    
    cur.execute("""
        INSERT INTO employees (full_name, email, department, hire_date, salary, performance_score)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
    """, (name, email, dept, hire_date, salary, performance))
    employee_ids.append(cur.fetchone()[0])
print(f"✅ Inserted {len(employee_ids)} employees")

# 5. INSERT SALES (30,000 transactions)
print("Inserting 30,000 sales transactions... (this will take about 30 seconds)")
for i in range(30000):
    customer_id = random.choice(customer_ids)
    product_id = random.choice(product_ids)
    employee_id = random.choice(employee_ids)
    sale_date = fake.date_between(start_date='-2y', end_date='today')
    quantity = random.randint(1, 10)
    
    cur.execute("SELECT price FROM products WHERE id = %s", (product_id,))
    unit_price = float(cur.fetchone()[0])  # Convert Decimal to float
    
    discount = random.choices([0, 0.05, 0.10, 0.15], weights=[60, 20, 15, 5])[0]
    total_amount = round((unit_price * quantity) * (1 - discount), 2)
    payment = random.choice(['Credit Card', 'PayPal', 'Bank Transfer'])
    
    cur.execute("""
        INSERT INTO sales (customer_id, product_id, employee_id, sale_date, quantity, unit_price, discount, total_amount, payment_method)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (customer_id, product_id, employee_id, sale_date, quantity, unit_price, discount, total_amount, payment))
    
    if i % 5000 == 0:
        print(f"Progress: {i}/30000 sales inserted")

conn.commit()
print("✅ Inserted 30,000 sales transactions!")
print("🎉 DATA GENERATION COMPLETE! Your fake e-commerce empire is ready.")

# CREATE INDEXES FOR SPEED
print("Creating indexes for fast queries...")
cur.execute("""
    CREATE INDEX idx_sales_date ON sales(sale_date);
    CREATE INDEX idx_sales_customer ON sales(customer_id);
    CREATE INDEX idx_sales_product ON sales(product_id);
    CREATE INDEX idx_customers_segment ON customers(customer_segment);
    CREATE INDEX idx_products_category ON products(category_id);
""")
conn.commit()
print("✅ Indexes created for lightning-fast queries!")

cur.close()
conn.close()
print("🎉 All done! Your database is ready for Oracle Orange!")