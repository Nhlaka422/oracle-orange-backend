# Use Python 3.12
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create directory for database
RUN mkdir -p /app/data

# Initialize database (create tables)
RUN python -c "from app.core.database import engine; from app.models.user import User; from app.models.schemas import Customer, Category, Product, Employee, Sale; User.__table__.create(engine, checkfirst=True); Customer.__table__.create(engine, checkfirst=True); Category.__table__.create(engine, checkfirst=True); Product.__table__.create(engine, checkfirst=True); Employee.__table__.create(engine, checkfirst=True); Sale.__table__.create(engine, checkfirst=True); print('✅ Tables created!')"

# Create admin user
RUN python -c "from app.core.database import SessionLocal; from app.services.auth_service import AuthService; db=SessionLocal(); user=AuthService.create_user(db=db, full_name='Admin User', email='admin@oracle.com', password='admin123', role='admin'); print(f'✅ Admin user created: {user.email if user else \"User already exists\"}'); db.close()"

# Generate sample data (30,000 sales records)
RUN python generate_data.py

# Expose the port
EXPOSE 8001

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]