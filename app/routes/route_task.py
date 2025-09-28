from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile

import os

router = APIRouter(prefix="/tasks", tags=["tasks"])

UPLOAD_DIR = "public/filesTask"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.