import os
import torch
from huggingface_hub import snapshot_download
from langchain_huggingface import HuggingFaceEmbeddings
from logger import setup_logging

logger = setup_logging()

MODEL_PATH = os.getenv("MODEL_PATH", "/app/models/bge-m3")

if not os.path.exists(MODEL_PATH):
    logger.info('path not exists')
    snapshot_download(repo_id="BAAI/bge-m3", local_dir=MODEL_PATH)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
embeddings = HuggingFaceEmbeddings(
    model_name=MODEL_PATH,
    model_kwargs={"device":DEVICE},
    encode_kwargs={"normalize_embeddings":True},
)
