from __future__ import annotations
from models import DatabaseManager, Service, Product, Customer, Staff, Booking, User, Invoice
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any, Optional
import json

class DatabaseServiceManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def get_all_services(self) -> List[Dict[str, Any]]:
        """Get all services"""
        session = self.db_manager.get_session()
        try:
            services = session.query(Service).all()
            return [self._service_to_dict(service) for service in services]
        finally:
            session.close()
    
    def get_service_by_id(self, service_id: int) -> Optional[Dict[str, Any]]:
        """Get service by ID"""
        session = self.db_manager.get_session()
        try:
            service = session.query(Service).filter(Service.id == service_id).first()
            return self._service_to_dict(service) if service else None
        finally:
            session.close()
    
    def add_service(self, service_data: Dict[str, Any]) -> bool:
        """Add new service"""
        session = self.db_manager.get_session()
        try:
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
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error adding service: {e}")
            return False
        finally:
            session.close()
    
    def update_service(self, service_id: int, service_data: Dict[str, Any]) -> bool:
        """Update existing service"""
        session = self.db_manager.get_session()
        try:
            service = session.query(Service).filter(Service.id == service_id).first()
            if not service:
                return False
            
            service.name = service_data['name']
            service.category = service_data['category']
            service.base_price = service_data['base_price']
            service.duration = service_data['duration']
            service.description = service_data.get('description', '')
            service.pricing_tiers = service_data.get('pricing_tiers', [])
            service.add_ons = service_data.get('add_ons', [])
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error updating service: {e}")
            return False
        finally:
            session.close()
    
    def delete_service(self, service_id: int) -> bool:
        """Delete service"""
        session = self.db_manager.get_session()
        try:
            service = session.query(Service).filter(Service.id == service_id).first()
            if not service:
                return False
            
            session.delete(service)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error deleting service: {e}")
            return False
        finally:
            session.close()
    
    def _service_to_dict(self, service: Service) -> Dict[str, Any]:
        """Convert service model to dictionary"""
        return {
            'id': service.id,
            'name': service.name,
            'category': service.category,
            'base_price': service.base_price,
            'duration': service.duration,
            'description': service.description,
            'pricing_tiers': service.pricing_tiers or [],
            'add_ons': service.add_ons or []
        }

class DatabaseProductManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def get_all_products(self) -> List[Dict[str, Any]]:
        """Get all products"""
        session = self.db_manager.get_session()
        try:
            products = session.query(Product).all()
            return [self._product_to_dict(product) for product in products]
        finally:
            session.close()
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Get product by ID"""
        session = self.db_manager.get_session()
        try:
            product = session.query(Product).filter(Product.id == product_id).first()
            return self._product_to_dict(product) if product else None
        finally:
            session.close()
    
    def add_product(self, product_data: Dict[str, Any]) -> bool:
        """Add new product"""
        session = self.db_manager.get_session()
        try:
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
            print(f"Error adding product: {e}")
            return False
        finally:
            session.close()
    
    def update_product(self, product_id: int, product_data: Dict[str, Any]) -> bool:
        """Update existing product"""
        session = self.db_manager.get_session()
        try:
            product = session.query(Product).filter(Product.id == product_id).first()
            if not product:
                return False
            
            product.name = product_data['name']
            product.brand = product_data['brand']
            product.category = product_data['category']
            product.sku = product_data.get('sku', '')
            product.cost_price = product_data['cost_price']
            product.selling_price = product_data['selling_price']
            product.quantity = product_data['quantity']
            product.low_stock_threshold = product_data['low_stock_threshold']
            product.description = product_data.get('description', '')
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error updating product: {e}")
            return False
        finally:
            session.close()
    
    def delete_product(self, product_id: int) -> bool:
        """Delete product"""
        session = self.db_manager.get_session()
        try:
            product = session.query(Product).filter(Product.id == product_id).first()
            if not product:
                return False
            
            session.delete(product)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error deleting product: {e}")
            return False
        finally:
            session.close()
    
    def _product_to_dict(self, product: Product) -> Dict[str, Any]:
        """Convert product model to dictionary"""
        return {
            'id': product.id,
            'name': product.name,
            'brand': product.brand,
            'category': product.category,
            'sku': product.sku,
            'cost_price': product.cost_price,
            'selling_price': product.selling_price,
            'quantity': product.quantity,
            'low_stock_threshold': product.low_stock_threshold,
            'description': product.description
        }

class DatabaseCustomerManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def get_all_customers(self) -> List[Dict[str, Any]]:
        """Get all customers"""
        session = self.db_manager.get_session()
        try:
            customers = session.query(Customer).all()
            return [self._customer_to_dict(customer) for customer in customers]
        finally:
            session.close()

    def get_or_create_customer_by_email(self, email: str, first_name: str = 'Guest', last_name: str = '') -> Dict[str, Any]:
        session = self.db_manager.get_session()
        try:
            customer = session.query(Customer).filter(Customer.email == email).first()
            if customer:
                return self._customer_to_dict(customer)
            # Create a new customer with minimal fields
            customer = Customer(first_name=first_name, last_name=last_name or '', email=email)
            session.add(customer)
            session.commit()
            return self._customer_to_dict(customer)
        except Exception as e:
            session.rollback()
            print(f"Error get_or_create_customer_by_email: {e}")
            return {}
        finally:
            session.close()

    def get_customer_by_email(self, email: str) -> Dict[str, Any]:
        session = self.db_manager.get_session()
        try:
            customer = session.query(Customer).filter(Customer.email == email).first()
            return self._customer_to_dict(customer) if customer else {}
        finally:
            session.close()    
    def get_customer_by_id(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """Get customer by ID"""
        session = self.db_manager.get_session()
        try:
            customer = session.query(Customer).filter(Customer.id == customer_id).first()
            return self._customer_to_dict(customer) if customer else None
        finally:
            session.close()
    
    def add_customer(self, customer_data: Dict[str, Any]) -> bool:
        """Add new customer"""
        session = self.db_manager.get_session()
        try:
            customer = Customer(
                first_name=customer_data['first_name'],
                last_name=customer_data['last_name'],
                email=customer_data.get('email'),
                phone=customer_data.get('phone'),
                address=customer_data.get('address'),
                notes=customer_data.get('notes', '')
            )
            session.add(customer)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error adding customer: {e}")
            return False
        finally:
            session.close()
    
    def update_customer(self, customer_id: int, customer_data: Dict[str, Any]) -> bool:
        """Update existing customer"""
        session = self.db_manager.get_session()
        try:
            customer = session.query(Customer).filter(Customer.id == customer_id).first()
            if not customer:
                return False
            
            customer.first_name = customer_data['first_name']
            customer.last_name = customer_data['last_name']
            customer.email = customer_data.get('email')
            customer.phone = customer_data.get('phone')
            customer.address = customer_data.get('address')
            customer.notes = customer_data.get('notes', '')
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error updating customer: {e}")
            return False
        finally:
            session.close()
    
    def delete_customer(self, customer_id: int) -> bool:
        """Delete customer"""
        session = self.db_manager.get_session()
        try:
            customer = session.query(Customer).filter(Customer.id == customer_id).first()
            if not customer:
                return False
            
            session.delete(customer)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error deleting customer: {e}")
            return False
        finally:
            session.close()
    
    def _customer_to_dict(self, customer: Customer) -> Dict[str, Any]:
        """Convert customer model to dictionary"""
        return {
            'id': customer.id,
            'first_name': customer.first_name,
            'last_name': customer.last_name,
            'full_name': f"{customer.first_name} {customer.last_name}",
            'email': customer.email,
            'phone': customer.phone,
            'address': customer.address,
            'notes': customer.notes
        }

class DatabaseUserManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def get_all_users(self) -> List[Dict[str, Any]]:
        session = self.db_manager.get_session()
        try:
            users = session.query(User).all()
            return [self._user_to_dict(u) for u in users]
        finally:
            session.close()

    def get_user_by_email(self, email: str):
        session = self.db_manager.get_session()
        try:
            return session.query(User).filter(User.email == email).first()
        finally:
            session.close()

    def set_admin(self, user_id: int, is_admin: bool) -> bool:
        return self.db_manager.set_user_admin(user_id, is_admin)

    def _user_to_dict(self, user: User) -> Dict[str, Any]:
        return {
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'is_admin': user.is_admin,
            'is_active': user.is_active
        }


class DatabaseInvoiceManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def create_invoice(self, booking_id: int, amount: float, currency: str = 'INR', upi_uri: str = None, upi_qr: str = None) -> Dict[str, Any]:
        session = self.db_manager.get_session()
        try:
            # simple invoice number pattern
            from datetime import datetime
            invoice_no = f"INV{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{booking_id}"
            invoice = Invoice(invoice_number=invoice_no, booking_id=booking_id, amount=amount, currency=currency, upi_uri=upi_uri, upi_qr=upi_qr)
            session.add(invoice)
            session.commit()
            session.refresh(invoice)
            return {
                'id': invoice.id,
                'invoice_number': invoice.invoice_number,
                'booking_id': invoice.booking_id,
                'amount': invoice.amount,
                'currency': invoice.currency,
                'status': invoice.status,
                'upi_uri': invoice.upi_uri,
                'upi_qr': invoice.upi_qr
            }
        except Exception as e:
            session.rollback()
            print(f"Error creating invoice: {e}")
            return {}
        finally:
            session.close()

    def get_invoice(self, invoice_id: int) -> Dict[str, Any]:
        session = self.db_manager.get_session()
        try:
            inv = session.query(Invoice).filter(Invoice.id == invoice_id).first()
            if not inv:
                return {}
            return {
                'id': inv.id,
                'invoice_number': inv.invoice_number,
                'booking_id': inv.booking_id,
                'amount': inv.amount,
                'currency': inv.currency,
                'status': inv.status,
                'upi_uri': inv.upi_uri,
                'upi_qr': inv.upi_qr,
                'created_at': inv.created_at,
                'paid_at': inv.paid_at
            }
        finally:
            session.close()

    def mark_paid(self, invoice_id: int) -> bool:
        session = self.db_manager.get_session()
        try:
            inv = session.query(Invoice).filter(Invoice.id == invoice_id).first()
            if not inv:
                return False
            inv.status = 'paid'
            inv.paid_at = datetime.utcnow()
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error marking invoice paid: {e}")
            return False
        finally:
            session.close()

class DatabaseStaffManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def get_all_staff(self) -> List[Dict[str, Any]]:
        """Get all staff members"""
        session = self.db_manager.get_session()
        try:
            staff_members = session.query(Staff).all()
            return [self._staff_to_dict(staff) for staff in staff_members]
        finally:
            session.close()
    
    def get_staff_by_id(self, staff_id: int) -> Optional[Dict[str, Any]]:
        """Get staff member by ID"""
        session = self.db_manager.get_session()
        try:
            staff = session.query(Staff).filter(Staff.id == staff_id).first()
            return self._staff_to_dict(staff) if staff else None
        finally:
            session.close()
    
    def add_staff(self, staff_data: Dict[str, Any]) -> bool:
        """Add new staff member"""
        session = self.db_manager.get_session()
        try:
            staff = Staff(
                first_name=staff_data['first_name'],
                last_name=staff_data['last_name'],
                email=staff_data.get('email'),
                phone=staff_data.get('phone'),
                position=staff_data.get('position'),
                hourly_rate=staff_data.get('hourly_rate'),
                is_active=staff_data.get('is_active', True),
                specialties=staff_data.get('specialties', []),
                availability=staff_data.get('availability', {})
            )
            session.add(staff)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error adding staff: {e}")
            return False
        finally:
            session.close()
    
    def update_staff(self, staff_id: int, staff_data: Dict[str, Any]) -> bool:
        """Update existing staff member"""
        session = self.db_manager.get_session()
        try:
            staff = session.query(Staff).filter(Staff.id == staff_id).first()
            if not staff:
                return False
            
            staff.first_name = staff_data['first_name']
            staff.last_name = staff_data['last_name']
            staff.email = staff_data.get('email')
            staff.phone = staff_data.get('phone')
            staff.position = staff_data.get('position')
            staff.hourly_rate = staff_data.get('hourly_rate')
            staff.is_active = staff_data.get('is_active', True)
            staff.specialties = staff_data.get('specialties', [])
            staff.availability = staff_data.get('availability', {})
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error updating staff: {e}")
            return False
        finally:
            session.close()
    
    def delete_staff(self, staff_id: int) -> bool:
        """Delete staff member"""
        session = self.db_manager.get_session()
        try:
            staff = session.query(Staff).filter(Staff.id == staff_id).first()
            if not staff:
                return False
            
            session.delete(staff)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error deleting staff: {e}")
            return False
        finally:
            session.close()
    
    def _staff_to_dict(self, staff: Staff) -> Dict[str, Any]:
        """Convert staff model to dictionary"""
        return {
            'id': staff.id,
            'first_name': staff.first_name,
            'last_name': staff.last_name,
            'full_name': f"{staff.first_name} {staff.last_name}",
            'email': staff.email,
            'phone': staff.phone,
            'position': staff.position,
            'hourly_rate': staff.hourly_rate,
            'is_active': staff.is_active,
            'specialties': staff.specialties or [],
            'availability': staff.availability or {}
        }