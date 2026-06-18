from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, DECIMAL
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    phone = Column(String(50))
    city = Column(String(50))
    state = Column(String(2))
    industry = Column(String(50))
    customer_segment = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(50), unique=True)
    profit_margin = Column(DECIMAL(5,2))

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(100))
    category_id = Column(Integer, ForeignKey("categories.id"))
    price = Column(DECIMAL(10,2))
    cost = Column(DECIMAL(10,2))
    sku = Column(String(20), unique=True)
    
    category = relationship("Category")

class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100))
    email = Column(String(100), unique=True)
    department = Column(String(50))
    hire_date = Column(Date)
    salary = Column(DECIMAL(10,2))
    performance_score = Column(Integer)

class Sale(Base):
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    employee_id = Column(Integer, ForeignKey("employees.id"))
    sale_date = Column(Date)
    quantity = Column(Integer)
    unit_price = Column(DECIMAL(10,2))
    discount = Column(DECIMAL(5,2), default=0)
    total_amount = Column(DECIMAL(10,2))
    payment_method = Column(String(20))
    
    customer = relationship("Customer")
    product = relationship("Product")
    employee = relationship("Employee")