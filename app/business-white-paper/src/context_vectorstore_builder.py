import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_chroma import Chroma
from embed import embeddings

DIRECTORY_PATH = 'data-library/plainfiles'
VECTORSTORE_PATH = 'data-library/vectorstore'

def load_and_persist_documents(directory_path=DIRECTORY_PATH, vectorstore_path=VECTORSTORE_PATH):
    loaders = []

    for filename in os.listdir(directory_path):
        filepath = os.path.join(directory_path, filename)
        if filename.endswith('.txt'):
            loaders.append(TextLoader(filepath))
        else:
            print("지원하지 않는 파일 형식: %s", filename)

    documents = []
    for loader in loaders:
        documents.extend(loader.load())

    # 문서를 청크로 분리
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )
    chunked_docs = text_splitter.split_documents(documents)

    os.makedirs(vectorstore_path, exist_ok=True)

    Chroma.from_documents(chunked_docs, embeddings, persist_directory=vectorstore_path)
    print("Vectorstore created and persisted")

if __name__ == '__main__':
    load_and_persist_documents()
