import sqlglot
from sqlalchemy import text
from ..core.database import SessionLocal
from .sql_validator import SQLValidator
import pandas as pd
import re

class NL2SQLService:
    def __init__(self):
        self.schema_context = """
        DATABASE SCHEMA FOR ORACLE ORANGE (SQLite):
        
        Tables and their columns:
        
        1. customers: 
           - id (integer, primary key)
           - full_name (text, customer's full name)
           - email (text, unique)
           - phone (text)
           - city (text)
           - state (text, 2-letter code)
           - industry (text: 'Tech', 'Retail', 'Healthcare', 'Finance', 'Education', 'Manufacturing')
           - customer_segment (text: 'Premium', 'Standard', 'Basic')
           - created_at (timestamp)
        
        2. categories:
           - id (integer, primary key)
           - category_name (text: 'Electronics', 'Clothing', 'Books', 'Home & Garden', 'Sports', 'Toys', 'Automotive', 'Food & Beverage', 'Health', 'Office Supplies')
           - profit_margin (decimal, 0.00 to 1.00)
        
        3. products:
           - id (integer, primary key)
           - product_name (text)
           - category_id (integer, foreign key to categories.id)
           - price (decimal, current selling price)
           - cost (decimal, cost of goods)
           - sku (text, unique product code)
        
        4. employees:
           - id (integer, primary key)
           - full_name (text)
           - email (text, unique)
           - department (text: 'Sales', 'Support', 'Engineering', 'Marketing', 'Finance')
           - hire_date (date)
           - salary (decimal)
           - performance_score (integer, 1-100)
        
        5. sales:
           - id (integer, primary key)
           - customer_id (integer, foreign key to customers.id)
           - product_id (integer, foreign key to products.id)
           - employee_id (integer, foreign key to employees.id)
           - sale_date (date)
           - quantity (integer)
           - unit_price (decimal, price at time of sale)
           - discount (decimal, 0.00 to 0.99)
           - total_amount (decimal, quantity * unit_price * (1 - discount))
           - payment_method (text: 'Credit Card', 'PayPal', 'Bank Transfer')
        
        IMPORTANT SQLITE RULES:
        1. Use SQLite syntax (NOT PostgreSQL!)
        2. For dates: use strftime('%Y-%m', sale_date) for month grouping
        3. For last 6 months: sale_date >= date('now', '-6 months')
        4. Use COALESCE for null values
        5. Never use DATE_TRUNC, INTERVAL, or PostgreSQL-specific functions
        6. Use || for string concatenation
        7. Use CASE statements for conditional logic
        8. For LIMIT, put at the end of the query
        """
    
    def generate_sql(self, user_question: str) -> dict:
        sql_query = self._generate_sql_from_pattern(user_question)
        
        if sql_query is None:
            return {
                "success": False, 
                "error": "Could not understand your question. Try rephrasing."
            }
        
        if not SQLValidator.validate_sql(sql_query):
            return {"success": False, "error": "SQL validation failed - potentially dangerous query", "sql": sql_query}
        
        return {"success": True, "sql": sql_query}
    
    def _generate_sql_from_pattern(self, question: str) -> str:
        """Generate SQL using pattern matching for SQLite"""
        
        question_lower = question.lower()
        
        # Pattern 1: Revenue by month/year
        if "revenue" in question_lower and ("month" in question_lower or "year" in question_lower):
            if "2024" in question_lower:
                return """
                    SELECT 
                        strftime('%Y-%m', sale_date) as month,
                        COALESCE(SUM(total_amount), 0) as revenue
                    FROM sales
                    WHERE sale_date >= '2024-01-01' AND sale_date < '2025-01-01'
                    GROUP BY strftime('%Y-%m', sale_date)
                    ORDER BY month ASC
                """
            else:
                return """
                    SELECT 
                        strftime('%Y-%m', sale_date) as month,
                        COALESCE(SUM(total_amount), 0) as revenue
                    FROM sales
                    WHERE sale_date >= date('now', '-6 months')
                    GROUP BY strftime('%Y-%m', sale_date)
                    ORDER BY month ASC
                """
        
        # Pattern 2: Top products
        if "top" in question_lower and "product" in question_lower:
            if "selling" in question_lower:
                return """
                    SELECT 
                        p.product_name,
                        COUNT(s.id) as number_of_sales,
                        COALESCE(SUM(s.total_amount), 0) as revenue
                    FROM sales s
                    JOIN products p ON s.product_id = p.id
                    GROUP BY p.product_name
                    ORDER BY revenue DESC
                    LIMIT 5
                """
            else:
                return """
                    SELECT 
                        p.product_name,
                        COALESCE(SUM(s.total_amount), 0) as revenue
                    FROM sales s
                    JOIN products p ON s.product_id = p.id
                    GROUP BY p.product_name
                    ORDER BY revenue DESC
                    LIMIT 5
                """
        
        # Pattern 3: Top customers
        if "top" in question_lower and "customer" in question_lower:
            return """
                SELECT 
                    c.full_name,
                    c.customer_segment,
                    COUNT(s.id) as orders,
                    COALESCE(SUM(s.total_amount), 0) as total_spent
                FROM sales s
                JOIN customers c ON s.customer_id = c.id
                GROUP BY c.full_name, c.customer_segment
                ORDER BY total_spent DESC
                LIMIT 5
            """
        
        # Pattern 4: Sales by category
        if "category" in question_lower and ("revenue" in question_lower or "sales" in question_lower):
            return """
                SELECT 
                    cat.category_name,
                    COUNT(s.id) as sales_count,
                    COALESCE(SUM(s.total_amount), 0) as revenue
                FROM sales s
                JOIN products p ON s.product_id = p.id
                JOIN categories cat ON p.category_id = cat.id
                GROUP BY cat.category_name
                ORDER BY revenue DESC
            """
        
        # Pattern 5: Revenue by state
        if "state" in question_lower or "region" in question_lower:
            return """
                SELECT 
                    c.state,
                    COUNT(s.id) as sales_count,
                    COALESCE(SUM(s.total_amount), 0) as revenue
                FROM sales s
                JOIN customers c ON s.customer_id = c.id
                GROUP BY c.state
                ORDER BY revenue DESC
                LIMIT 10
            """
        
        # Pattern 6: Employee performance
        if "employee" in question_lower and ("performance" in question_lower or "top" in question_lower):
            return """
                SELECT 
                    e.full_name,
                    e.department,
                    e.performance_score,
                    COUNT(s.id) as deals_closed,
                    COALESCE(SUM(s.total_amount), 0) as revenue_generated
                FROM employees e
                LEFT JOIN sales s ON e.id = s.employee_id
                GROUP BY e.full_name, e.department, e.performance_score
                ORDER BY e.performance_score DESC
                LIMIT 10
            """
        
        # Pattern 7: Average order value
        if "average" in question_lower and "order" in question_lower:
            return """
                SELECT 
                    strftime('%Y-%m', sale_date) as month,
                    COALESCE(AVG(total_amount), 0) as avg_order_value,
                    COUNT(id) as orders
                FROM sales
                WHERE sale_date >= date('now', '-6 months')
                GROUP BY strftime('%Y-%m', sale_date)
                ORDER BY month ASC
            """
        
        # Pattern 8: Customer segments
        if "segment" in question_lower or "premium" in question_lower:
            return """
                SELECT 
                    c.customer_segment,
                    COUNT(DISTINCT c.id) as customer_count,
                    COALESCE(SUM(s.total_amount), 0) as revenue,
                    COALESCE(AVG(s.total_amount), 0) as avg_order_value
                FROM customers c
                LEFT JOIN sales s ON c.id = s.customer_id
                GROUP BY c.customer_segment
                ORDER BY revenue DESC
            """
        
        # Pattern 9: Payment methods
        if "payment" in question_lower:
            return """
                SELECT 
                    payment_method,
                    COUNT(id) as transaction_count,
                    COALESCE(SUM(total_amount), 0) as total_revenue
                FROM sales
                GROUP BY payment_method
                ORDER BY total_revenue DESC
            """
        
        # Pattern 10: Total revenue
        if "total" in question_lower and "revenue" in question_lower:
            return """
                SELECT 
                    COALESCE(SUM(total_amount), 0) as total_revenue,
                    COUNT(id) as total_transactions,
                    COALESCE(AVG(total_amount), 0) as avg_transaction
                FROM sales
            """
        
        # Pattern 11: General question - return help message
        if "what" in question_lower or "who" in question_lower or "how" in question_lower:
            return None
        
        # Default: Simple sales overview
        return """
            SELECT 
                strftime('%Y-%m', sale_date) as month,
                COUNT(id) as orders,
                COALESCE(SUM(total_amount), 0) as revenue
            FROM sales
            WHERE sale_date >= date('now', '-6 months')
            GROUP BY strftime('%Y-%m', sale_date)
            ORDER BY month DESC
        """
    
    def execute_sql(self, sql: str) -> dict:
        """Run SQL query safely"""
        try:
            db = SessionLocal()
            result = db.execute(text(sql))
            
            columns = result.keys()
            rows = result.fetchall()
            
            data = [dict(zip(columns, row)) for row in rows]
            
            db.close()
            
            return {
                "success": True, 
                "data": data, 
                "columns": list(columns), 
                "row_count": len(data)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def generate_insight(self, question: str, sql: str, data: list) -> str:
        """Generate insight from data"""
        
        if not data:
            return "No data found for your query. Try rephrasing your question."
        
        if data and len(data) > 0:
            first_row = data[0]
            if "revenue" in first_row:
                total = sum(float(row.get('revenue', 0)) for row in data[:10])
                return f"Found {len(data)} results. Total revenue shown: ${total:,.2f}"
            
            if "customer_segment" in first_row:
                premium = sum(1 for row in data if row.get('customer_segment') == 'Premium')
                standard = sum(1 for row in data if row.get('customer_segment') == 'Standard')
                basic = sum(1 for row in data if row.get('customer_segment') == 'Basic')
                return f"Customer breakdown: {premium} Premium, {standard} Standard, {basic} Basic customers."
            
            return f"Query returned {len(data)} results. Use the data above for insights."
        
        return "No insights available."