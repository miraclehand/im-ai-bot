import requests
from bs4 import BeautifulSoup
import re
import json
from transformers import AutoTokenizer, GPT2LMHeadModel, GPT2Config, TextDataset, DataCollatorForLanguageModeling
from transformers import Trainer, TrainingArguments
import torch

# 1. 데이터 수집
def get_wikipedia_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    paragraphs = soup.find_all('p')
    content = ' '.join([p.text for p in paragraphs])
    return content

# 위키피디아 한국어 페이지 URL 목록 (예시)
urls = [
    "https://ko.wikipedia.org/wiki/대한민국",
    "https://ko.wikipedia.org/wiki/서울특별시",
    # 더 많은 URL 추가
]

corpus = []
for url in urls:
    corpus.append(get_wikipedia_content(url))

# 2. 데이터 전처리
def preprocess_text(text):
    # 특수 문자 제거, 공백 정리 등
    text = re.sub(r'\[.*?\]|\(.*?\)|\{.*?\}', '', text)
    text = re.sub(r'\s+', ' ', text)
    #text = re.sub(r'\n{2}', '\n', text)  # 2개의 엔터는 1개로
    #text = re.sub(r'\n{3,}', '\n\n', text)  # 3개 이상의 엔터는 2개로
    return text.strip()

processed_corpus = [preprocess_text(text) for text in corpus]

# 3. 토크나이저 구현 (GPT-2 토크나이저 사용)
tokenizer = AutoTokenizer.from_pretrained("skt/kogpt2-base-v2")

# 4. 모델 아키텍처 설계 (GPT-2 기반)
config = GPT2Config(
    vocab_size=tokenizer.vocab_size,
    n_positions=512,
    n_ctx=512,
    n_embd=768,
    n_layer=6,
    n_head=12
)
model = GPT2LMHeadModel(config)

# 5. 모델 학습
# 데이터셋 준비
with open('train.txt', 'w', encoding='utf-8') as f:
    for text in processed_corpus:
        f.write(text + '\n')

train_dataset = TextDataset(
    tokenizer=tokenizer,
    file_path="train.txt",
    block_size=128
)

data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False
)

training_args = TrainingArguments(
    output_dir="./results",
    overwrite_output_dir=True,
    num_train_epochs=3,
    per_device_train_batch_size=4,
    save_steps=10_000,
    save_total_limit=2,
)

trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=train_dataset,
)

trainer.train()

# 6. 모델 평가 (간단한 예시)
eval_text = "대한민국의 수도는"
input_ids = tokenizer.encode(eval_text, return_tensors='pt')
output = model.generate(input_ids, max_length=50, num_return_sequences=1)
generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
print(generated_text)

# 7. Ollama 형식으로 변환
model.save_pretrained("./korean_gpt2")
tokenizer.save_pretrained("./korean_gpt2")

# Modelfile 생성
#modelfile_content = """
#FROM ./korean_gpt2
#TEMPLATE """{{.Prompt}}
#Human: {{.Input}}
#AI: """
#
#PARAMETER stop "Human:"
#PARAMETER stop "AI:"
#"""
#
#with open("Modelfile", "w") as f:
#    f.write(modelfile_content)
#
#print("모델과 Modelfile이 생성되었습니다. Ollama에 추가하려면 'ollama create korean_gpt2 -f Modelfile' 명령을 실행하세요.")
