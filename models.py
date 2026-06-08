from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from database import Base


class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_name = Column(String(255), nullable=False)
    category = Column(String(100))
    description = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Batch(Base):
    __tablename__ = "batches"

    batch_id = Column(String(100), primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    manufacturing_date = Column(Date)
    expiry_date = Column(Date)
    status = Column(String(50), default="active")
    qr_url = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())


class ProductionStage(Base):
    __tablename__ = "production_stages"

    stage_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    batch_id = Column(String(100), ForeignKey("batches.batch_id"), nullable=False)
    stage_name = Column(String(255), nullable=False)
    stage_order = Column(Integer)
    description = Column(Text)
    video_url = Column(Text)
    image_url = Column(Text)
    timestamp = Column(DateTime)
    created_at = Column(TIMESTAMP, server_default=func.now())


class QualityCheck(Base):
    __tablename__ = "quality_checks"

    check_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    batch_id = Column(String(100), ForeignKey("batches.batch_id"), nullable=False)
    checked_by = Column(String(255))
    result = Column(String(100))
    remarks = Column(Text)
    checked_at = Column(DateTime)