import sqlite3
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()

# Connect to SQLite
conn = sqlite3.connect('oracle_orange.db')
cur = conn.cursor()

# Check if tables exist and have data
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sales'")
if cur.fetchone():
    cur.execute("SELECT COUNT(*) FROM sales")
    count = cur.fetchone()[0]
    if count > 0:
        print(f"✅ Database already has {count} sales records. Skipping generation.")
        conn.close()
        exit()

print("📦 Generating sample data...")

# Insert Categories
categories = [
    ('Electronics', 0.35), ('Clothing', 0.50), ('Books', 0.30),
    ('Home & Garden', 0.40), ('Sports', 0.45), ('Toys', 0.55),
    ('Automotive', 0.25), ('Food & Beverage', 0.20), ('Health', 0.60),
    ('Office Supplies', 0.30)
]

for cat_name, margin in categories:
    cur.execute("INSERT INTO categories (category_name, profit_margin) VALUES (?, ?)", (cat_name, margin))
print(f"✅ Inserted {len(categories)} categories")

# Insert Customers
customers = []
used_emails = set()

print("👤 Generating 500 customers...")
for i in range(500):
    # Generate unique email
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
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, email, phone, city, state, industry, segment))
    customers.append(cur.lastrowid)
    
    if (i + 1) % 100 == 0:
        print(f"  Inserted {i + 1}/500 customers")
print(f"✅ Inserted {len(customers)} customers")

# Insert Products
products = []
used_skus = set()
category_ids = list(range(1, 11))

print("📦 Generating 200 products...")
for i in range(200):
    category_id = random.choice(category_ids)
    cur.execute("SELECT profit_margin FROM categories WHERE id = ?", (category_id,))
    margin = cur.fetchone()[0]
    
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
        VALUES (?, ?, ?, ?, ?)
    """, (product_name, category_id, price, cost, sku))
    products.append(cur.lastrowid)
print(f"✅ Inserted {len(products)} products")

# Insert Employees
employees = []
departments = ['Sales', 'Support', 'Engineering', 'Marketing', 'Finance']
used_employee_emails = set()

print("👔 Generating 50 employees...")
for i in range(50):
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
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, email, dept, hire_date, salary, performance))
    employees.append(cur.lastrowid)
print(f"✅ Inserted {len(employees)} employees")

# Insert Sales
print("💰 Generating 30,000 sales transactions... (this will take ~30 seconds)")
sales_count = 30000
for i in range(sales_count):
    customer_id = random.choice(customers)
    product_id = random.choice(products)
    employee_id = random.choice(employees)
    sale_date = fake.date_between(start_date='-2y', end_date='today')
    quantity = random.randint(1, 10)
    
    cur.execute("SELECT price FROM products WHERE id = ?", (product_id,))
    unit_price = cur.fetchone()[0]
    
    discount = random.choices([0, 0.05, 0.10, 0.15], weights=[60, 20, 15, 5])[0]
    total_amount = round((unit_price * quantity) * (1 - discount), 2)
    payment = random.choice(['Credit Card', 'PayPal', 'Bank Transfer'])
    
    cur.execute("""
        INSERT INTO sales (customer_id, product_id, employee_id, sale_date, quantity, unit_price, discount, total_amount, payment_method)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (customer_id, product_id, employee_id, sale_date, quantity, unit_price, discount, total_amount, payment))
    
    if (i + 1) % 5000 == 0:
        print(f"  Inserted {i + 1}/{sales_count} sales")

conn.commit()
print(f"✅ Inserted {sales_count} sales transactions!")
print("🎉 DATA GENERATION COMPLETE!")

# Create indexes for speed
print("📊 Creating indexes...")
cur.execute("CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date)")
cur.execute("CREATE INDEX IF NOT EXISTS idx_sales_customer ON sales(customer_id)")
cur.execute("CREATE INDEX IF NOT EXISTS idx_sales_product ON sales(product_id)")
cur.execute("CREATE INDEX IF NOT EXISTS idx_customers_segment ON customers(customer_segment)")
cur.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id)")
conn.commit()
print("✅ Indexes created!")

# Verify data
cur.execute("SELECT COUNT(*) FROM sales")
count = cur.fetchone()[0]
print(f"✅ Total sales records: {count}")

cur.close()
conn.close()
print("🎉 All done!")