from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Text, DECIMAL, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel
from typing import List, Optional
import datetime
from datetime import date

# Database configuration - Updated with your MySQL credentials
DATABASE_URL = "mysql+pymysql://root:%40kings635@localhost:3306/inventory_tracking_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# FastAPI app
app = FastAPI(title="Inventory Tracking API by Stephen", version="1.0.0")

# ===============================================
# DATABASE MODELS
# ===============================================

class Category(Base):
    __tablename__ = "categories"
    category_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    products = relationship("Product", back_populates="category")

class Supplier(Base):
    __tablename__ = "suppliers"
    supplier_id = Column(Integer, primary_key=True, index=True)
    supplier_name = Column(String(150), nullable=False)
    contact_person = Column(String(100))
    email = Column(String(100), unique=True)
    phone = Column(String(20))
    address = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    products = relationship("Product", back_populates="supplier")

class Product(Base):
    __tablename__ = "products"
    product_id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(200), nullable=False)
    product_code = Column(String(50), unique=True, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"))
    supplier_id = Column(Integer, ForeignKey("suppliers.supplier_id"))
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    reorder_level = Column(Integer, default=10)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    category = relationship("Category", back_populates="products")
    supplier = relationship("Supplier", back_populates="products")
    inventory = relationship("Inventory", back_populates="product", uselist=False)

class Inventory(Base):
    __tablename__ = "inventory"
    inventory_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.product_id"), unique=True)
    quantity_in_stock = Column(Integer, nullable=False, default=0)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)
    
    product = relationship("Product", back_populates="inventory")

# ===============================================
# PYDANTIC SCHEMAS
# ===============================================

class CategoryBase(BaseModel):
    category_name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    category_id: int
    created_at: datetime.datetime
    
    class Config:
        from_attributes = True

class SupplierBase(BaseModel):
    supplier_name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class SupplierCreate(SupplierBase):
    pass

class SupplierResponse(SupplierBase):
    supplier_id: int
    created_at: datetime.datetime
    
    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    product_name: str
    product_code: str
    category_id: int
    supplier_id: int
    unit_price: float
    reorder_level: Optional[int] = 10
    description: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    product_id: int
    created_at: datetime.datetime
    category: Optional[CategoryResponse] = None
    supplier: Optional[SupplierResponse] = None
    
    class Config:
        from_attributes = True

class InventoryBase(BaseModel):
    product_id: int
    quantity_in_stock: int

class InventoryCreate(InventoryBase):
    pass

class InventoryUpdate(BaseModel):
    quantity_in_stock: int

class InventoryResponse(InventoryBase):
    inventory_id: int
    last_updated: datetime.datetime
    product: Optional[ProductResponse] = None
    
    class Config:
        from_attributes = True

# ===============================================
# DATABASE DEPENDENCY
# ===============================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ===============================================
# API ENDPOINTS
# ===============================================

@app.get("/")
async def root():
    return {"message": "Inventory Tracking API by Stephen", "status": "Running Successfully!"}

# Category endpoints
@app.post("/categories/", response_model=CategoryResponse)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    db_category = Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@app.get("/categories/", response_model=List[CategoryResponse])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categories = db.query(Category).offset(skip).limit(limit).all()
    return categories

@app.get("/categories/{category_id}", response_model=CategoryResponse)
def read_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.category_id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@app.put("/categories/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, category: CategoryCreate, db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(Category.category_id == category_id).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    for key, value in category.dict().items():
        setattr(db_category, key, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category

@app.delete("/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.category_id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db.delete(category)
    db.commit()
    return {"message": "Category deleted successfully"}

# Supplier endpoints
@app.post("/suppliers/", response_model=SupplierResponse)
def create_supplier(supplier: SupplierCreate, db: Session = Depends(get_db)):
    db_supplier = Supplier(**supplier.dict())
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

@app.get("/suppliers/", response_model=List[SupplierResponse])
def read_suppliers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    suppliers = db.query(Supplier).offset(skip).limit(limit).all()
    return suppliers

@app.get("/suppliers/{supplier_id}", response_model=SupplierResponse)
def read_supplier(supplier_id: int, db: Session = Depends(get_db)):
    supplier = db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()
    if supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier

@app.put("/suppliers/{supplier_id}", response_model=SupplierResponse)
def update_supplier(supplier_id: int, supplier: SupplierCreate, db: Session = Depends(get_db)):
    db_supplier = db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()
    if db_supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    for key, value in supplier.dict().items():
        setattr(db_supplier, key, value)
    
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

@app.delete("/suppliers/{supplier_id}")
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    supplier = db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()
    if supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    db.delete(supplier)
    db.commit()
    return {"message": "Supplier deleted successfully"}

# Product endpoints
@app.post("/products/", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    # Create inventory record for new product
    inventory = Inventory(product_id=db_product.product_id, quantity_in_stock=0)
    db.add(inventory)
    db.commit()
    
    return db_product

@app.get("/products/", response_model=List[ProductResponse])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = db.query(Product).offset(skip).limit(limit).all()
    return products

@app.get("/products/{product_id}", response_model=ProductResponse)
def read_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductCreate, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.product_id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    for key, value in product.dict().items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}

# Inventory endpoints
@app.get("/inventory/", response_model=List[InventoryResponse])
def read_inventory(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    inventory = db.query(Inventory).offset(skip).limit(limit).all()
    return inventory

@app.get("/inventory/{product_id}", response_model=InventoryResponse)
def read_product_inventory(product_id: int, db: Session = Depends(get_db)):
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if inventory is None:
        raise HTTPException(status_code=404, detail="Inventory record not found")
    return inventory

@app.put("/inventory/{product_id}", response_model=InventoryResponse)
def update_inventory(product_id: int, inventory_update: InventoryUpdate, db: Session = Depends(get_db)):
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if inventory is None:
        raise HTTPException(status_code=404, detail="Inventory record not found")
    
    inventory.quantity_in_stock = inventory_update.quantity_in_stock
    inventory.last_updated = datetime.datetime.utcnow()
    
    db.commit()
    db.refresh(inventory)
    return inventory

@app.get("/inventory/low-stock/")
def get_low_stock_products(db: Session = Depends(get_db)):
    low_stock = db.query(Product, Inventory).join(Inventory).filter(
        Inventory.quantity_in_stock <= Product.reorder_level
    ).all()
    
    result = []
    for product, inventory in low_stock:
        result.append({
            "product_id": product.product_id,
            "product_name": product.product_name,
            "current_stock": inventory.quantity_in_stock,
            "reorder_level": product.reorder_level,
            "shortage": product.reorder_level - inventory.quantity_in_stock
        })
    
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)