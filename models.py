from flask.cli import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()

class Service(Base):
    __tablename__ = 'services'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    base_price = Column(Float, nullable=False)
    duration = Column(Integer, nullable=False)  # in minutes
    description = Column(Text)
    pricing_tiers = Column(JSON)  # Store pricing tiers as JSON
    add_ons = Column(JSON)  # Store add-ons as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bookings = relationship("Booking", back_populates="service")

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    brand = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)
    sku = Column(String(50))
    cost_price = Column(Float, nullable=False)
    selling_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    low_stock_threshold = Column(Integer, nullable=False, default=5)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Customer(Base):
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True)
    phone = Column(String(20))
    address = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bookings = relationship("Booking", back_populates="customer")

class Staff(Base):
    __tablename__ = 'staff'
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True)
    phone = Column(String(20))
    position = Column(String(100))
    hourly_rate = Column(Float)
    is_active = Column(Boolean, default=True)
    specialties = Column(JSON)  # Services they can perform
    availability = Column(JSON)  # Working hours by day
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bookings = relationship("Booking", back_populates="staff_member")

class Booking(Base):
    __tablename__ = 'bookings'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False)
    staff_id = Column(Integer, ForeignKey('staff.id'))
    appointment_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    status = Column(String(20), default='scheduled')  # scheduled, completed, cancelled, no_show
    total_price = Column(Float, nullable=False)
    payment_status = Column(String(20), default='pending')  # pending, paid, refunded
    payment_method = Column(String(50))
    notes = Column(Text)
    add_ons = Column(JSON)  # Selected add-ons
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="bookings")
    service = relationship("Service", back_populates="bookings")
    staff_member = relationship("Staff", back_populates="bookings")

# Database configuration
class DatabaseManager:
    def __init__(self):
        print("Initializing Database Manager");
        load_dotenv()  # loads the environment variables from .env BMC
        #print("URL: " + str(os.getenv('DATABASE_URL')))
        self.database_url = os.getenv('DATABASE_URL');
       # self.database_url = "postgresql://postgres:Admin123@localhost:5432/Saloon";
        #print(f"Initializing Database Manager successful" +str(self.database_url));
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")
        
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get a database session"""
        return self.SessionLocal()
    
    def migrate_json_data(self, services_data, products_data):
        """Migrate existing JSON data to database"""
        session = self.get_session()
        try:
            # Migrate services
            for service_data in services_data:
                service = Service(
                    name=service_data['name'],
                    category=service_data['category'],
                    base_price=service_data['base_price'],
                    duration=service_data['duration'],
                    description=service_data.get('description', ''),
                    pricing_tiers=service_data.get('pricing_tiers', []),
                    add_ons=service_data.get('add_ons', [])
                )
                session.add(service)
            
            # Migrate products
            for product_data in products_data:
                product = Product(
                    name=product_data['name'],
                    brand=product_data['brand'],
                    category=product_data['category'],
                    sku=product_data.get('sku', ''),
                    cost_price=product_data['cost_price'],
                    selling_price=product_data['selling_price'],
                    quantity=product_data['quantity'],
                    low_stock_threshold=product_data['low_stock_threshold'],
                    description=product_data.get('description', '')
                )
                session.add(product)
            
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            print(f"Migration error: {e}")
            return False
        finally:
            session.close()