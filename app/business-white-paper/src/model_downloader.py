from huggingface_hub import snapshot_download

MODEL_PATH = "models/bge-m3"
MODEL_REPO_ID = "BAAI/bge-m3"
def download_huggingface_model():
    snapshot_download(repo_id=MODEL_REPO_ID, local_dir=MODEL_PATH)

if __name__ == '__main__':
    download_huggingface_model()
