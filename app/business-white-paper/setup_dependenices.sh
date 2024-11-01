source venv/bin/activate
pip install -y huggingface_hub
./model_downloader.sh
pip download -r requirements.txt -d ./packages
