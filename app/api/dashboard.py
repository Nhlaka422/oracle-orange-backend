from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..core.database import get_db

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get key metrics for dashboard"""
    
    try:
        # Total revenue
        revenue_result = db.execute(text("SELECT COALESCE(SUM(total_amount), 0) FROM sales"))
        total_revenue = float(revenue_result.scalar() or 0)
        
        # Total customers
        customers_result = db.execute(text("SELECT COUNT(*) FROM customers"))
        total_customers = customers_result.scalar() or 0
        
        # Total sales
        sales_result = db.execute(text("SELECT COUNT(*) FROM sales"))
        total_sales = sales_result.scalar() or 0
        
        # Average order value
        avg_result = db.execute(text("SELECT COALESCE(AVG(total_amount), 0) FROM sales"))
        avg_order_value = float(avg_result.scalar() or 0)
        
        # Top 5 products
        top_products_result = db.execute(text("""
            SELECT p.product_name, COALESCE(SUM(s.total_amount), 0) as revenue
            FROM sales s
            JOIN products p ON s.product_id = p.id
            GROUP BY p.product_name
            ORDER BY revenue DESC
            LIMIT 5
        """))
        top_products = top_products_result.fetchall()
        
        # Revenue by month (last 6 months)
        monthly_revenue_result = db.execute(text("""
            SELECT 
                TO_CHAR(DATE_TRUNC('month', sale_date), 'YYYY-MM') as month,
                COALESCE(SUM(total_amount), 0) as revenue
            FROM sales
            WHERE sale_date >= CURRENT_DATE - INTERVAL '6 months'
            GROUP BY DATE_TRUNC('month', sale_date)
            ORDER BY month ASC
        """))
        monthly_revenue = monthly_revenue_result.fetchall()
        
        return {
            "total_revenue": total_revenue,
            "total_customers": total_customers,
            "total_sales": total_sales,
            "avg_order_value": avg_order_value,
            "top_products": [{"name": p[0], "revenue": float(p[1])} for p in top_products],
            "monthly_revenue": [{"month": m[0], "revenue": float(m[1])} for m in monthly_revenue]
        }
    except Exception as e:
        return {
            "error": str(e),
            "total_revenue": 0,
            "total_customers": 0,
            "total_sales": 0,
            "avg_order_value": 0,
            "top_products": [],
            "monthly_revenue": []
        }