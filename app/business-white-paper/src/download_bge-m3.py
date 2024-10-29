from huggingface_hub import snapshot_download

def download_model():
    MODEL_PATH = "models/bge-m3"
    snapshot_download(repo_id="BAAI/bge-m3", local_dir=MODEL_PATH)

if __name__ == '__main__':
    download_model()

