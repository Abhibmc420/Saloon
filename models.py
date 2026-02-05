from dotenv import load_dotenv
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
    status = Column(String(20), default='scheduled')  # scheduled, requested, approved, completed, cancelled, no_show
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

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255))
    google_id = Column(String(255), unique=True)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.email} is_admin={self.is_admin}>"

class Invoice(Base):
    __tablename__ = 'invoices'

    id = Column(Integer, primary_key=True)
    invoice_number = Column(String(50), unique=True, nullable=False)
    booking_id = Column(Integer, ForeignKey('bookings.id'), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default='INR')
    status = Column(String(20), default='pending')  # pending, paid, cancelled
    upi_uri = Column(String(1024))
    upi_qr = Column(String(255))  # filename or data-uri
    created_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime)

    # relationship back to booking
    booking = relationship("Booking")

    def __repr__(self):
        return f"<Invoice {self.invoice_number} {self.status} {self.amount}>"

# Database configuration
class DatabaseManager:
    def __init__(self):
        print("Initializing Database Manager");
        load_dotenv()  # loads the environment variables from .env
        # Prefer SQLITE_PATH if explicitly set (useful for tests and dev); otherwise use DATABASE_URL; fallback to local sqlite
        sqlite_path_env = os.getenv('SQLITE_PATH')
        database_url_env = os.getenv('DATABASE_URL')

        if sqlite_path_env:
            self.database_url = f"sqlite:///{sqlite_path_env}"
            print(f"Using SQLITE_PATH env var — SQLite DB at {sqlite_path_env}")
        elif database_url_env:
            self.database_url = database_url_env
        else:
            sqlite_path = 'salon.db'
            self.database_url = f"sqlite:///{sqlite_path}"
            print(f"No DATABASE_URL found — falling back to SQLite database at {sqlite_path}")

        # For SQLite, provide connect_args to avoid thread check issues when used by frameworks
        connect_args = {"check_same_thread": False} if self.database_url.startswith("sqlite") else {}
        self.engine = create_engine(self.database_url, connect_args=connect_args)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get a database session"""
        return self.SessionLocal()
    
    def get_or_create_user(self, email: str, full_name: str = None, google_id: str = None, is_admin: bool = False):
        session = self.get_session()
        try:
            user = session.query(User).filter(User.email == email).first()
            if user:
                # return a plain dict to avoid detached instance problems
                return {
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.full_name,
                    'is_admin': user.is_admin,
                    'google_id': user.google_id
                }
            user = User(email=email, full_name=full_name, google_id=google_id, is_admin=is_admin)
            session.add(user)
            session.commit()
            session.refresh(user)
            return {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'is_admin': user.is_admin,
                'google_id': user.google_id
            }
        except Exception as e:
            session.rollback()
            print(f"Error creating/getting user: {e}")
            return None
        finally:
            session.close()

    def set_user_admin(self, user_id: int, is_admin: bool) -> bool:
        session = self.get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            user.is_admin = is_admin
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error updating user admin status: {e}")
            return False
        finally:
            session.close()

    def list_users(self):
        session = self.get_session()
        try:
            return session.query(User).all()
        finally:
            session.close()

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