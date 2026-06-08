from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import os
import qrcode
from io import BytesIO

from database import Base, engine, get_db
from models import Product, Batch, ProductionStage, QualityCheck
from schemas import ProductCreate, BatchCreate, StageCreate, QualityCheckCreate
from azure_blob import upload_file_to_blob

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ZIIS-TrustFlow Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173")


@app.get("/")
def home():
    return {"message": "ZIIS-TrustFlow backend is running"}


@app.post("/products")
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    new_product = Product(
        product_name=product.product_name,
        category=product.category,
        description=product.description
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()


@app.post("/batches")
def create_batch(batch: BatchCreate, db: Session = Depends(get_db)):
    existing_batch = db.query(Batch).filter(
        Batch.batch_id == batch.batch_id
    ).first()

    if existing_batch:
        raise HTTPException(status_code=400, detail="Batch already exists")

    qr_url = f"{FRONTEND_BASE_URL}/product/{batch.batch_id}"

    new_batch = Batch(
        batch_id=batch.batch_id,
        product_id=batch.product_id,
        manufacturing_date=batch.manufacturing_date,
        expiry_date=batch.expiry_date,
        qr_url=qr_url
    )

    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)

    return new_batch


@app.post("/stages")
def create_stage(stage: StageCreate, db: Session = Depends(get_db)):
    batch = db.query(Batch).filter(
        Batch.batch_id == stage.batch_id
    ).first()

    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    new_stage = ProductionStage(
        batch_id=stage.batch_id,
        stage_name=stage.stage_name,
        stage_order=stage.stage_order,
        description=stage.description,
        timestamp=stage.timestamp
    )

    db.add(new_stage)
    db.commit()
    db.refresh(new_stage)

    return new_stage


@app.post("/stages/{stage_id}/upload")
def upload_stage_media(
    stage_id: int,
    file: UploadFile = File(...),
    media_type: str = Form(...),
    db: Session = Depends(get_db)
):
    stage = db.query(ProductionStage).filter(
        ProductionStage.stage_id == stage_id
    ).first()

    if not stage:
        raise HTTPException(status_code=404, detail="Stage not found")

    file_url = upload_file_to_blob(file, folder_name=stage.batch_id)

    if media_type == "video":
        stage.video_url = file_url
    elif media_type == "image":
        stage.image_url = file_url
    else:
        raise HTTPException(status_code=400, detail="media_type must be video or image")

    db.commit()
    db.refresh(stage)

    return {
        "message": "File uploaded successfully",
        "file_url": file_url
    }


@app.post("/quality-checks")
def create_quality_check(qc: QualityCheckCreate, db: Session = Depends(get_db)):
    new_qc = QualityCheck(
        batch_id=qc.batch_id,
        checked_by=qc.checked_by,
        result=qc.result,
        remarks=qc.remarks,
        checked_at=qc.checked_at or datetime.utcnow()
    )

    db.add(new_qc)
    db.commit()
    db.refresh(new_qc)

    return new_qc


@app.get("/product/{batch_id}")
def get_product_journey(batch_id: str, db: Session = Depends(get_db)):
    batch = db.query(Batch).filter(
        Batch.batch_id == batch_id
    ).first()

    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    product = db.query(Product).filter(
        Product.product_id == batch.product_id
    ).first()

    stages = db.query(ProductionStage).filter(
        ProductionStage.batch_id == batch_id
    ).order_by(ProductionStage.stage_order).all()

    quality_checks = db.query(QualityCheck).filter(
        QualityCheck.batch_id == batch_id
    ).all()

    return {
        "product": product,
        "batch": batch,
        "stages": stages,
        "quality_checks": quality_checks
    }


@app.get("/batches/{batch_id}/qr")
def generate_qr(batch_id: str, db: Session = Depends(get_db)):
    batch = db.query(Batch).filter(
        Batch.batch_id == batch_id
    ).first()

    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    qr_image = qrcode.make(batch.qr_url)
    buffer = BytesIO()
    qr_image.save(buffer, format="PNG")
    buffer.seek(0)

    class QRFile:
        filename = f"{batch_id}_qr.png"
        content_type = "image/png"
        file = buffer

    qr_url = upload_file_to_blob(QRFile(), folder_name="qr-codes")

    return {
        "batch_id": batch_id,
        "qr_target_url": batch.qr_url,
        "qr_image_url": qr_url
    }