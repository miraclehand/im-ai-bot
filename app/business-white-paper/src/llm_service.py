import logging
from langchain_community.chat_models import ChatOllama
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from embed import embeddings

logger = logging.getLogger(__name__)

DIRECTORY_PATH = 'data-library/plainfiles'
VECTORSTORE_PATH = 'data-library/vectorstore'

model = ChatOllama(base_url='http://ollama-service:11434', timeout=6000, model="tinyllama", temperature=0)
vectorstore = Chroma(persist_directory=VECTORSTORE_PATH, embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={'k': 3})

def generate_answer(question):
    search_results = retriever.invoke(question)

    if not search_results:
        yield "죄송합니다. 해당 질문에 대한 답변을 찾을 수 없습니다."
        return

    logger.info("Search results: %s", search_results)

    template = (
        "당신은 질문-답변(Question-Answer) Task 를 수행하는 AI 어시스턴트 입니다.\n"
        "검색된 문맥(context)를 사용하여 질문(question)에 답하세요.\n"
        "답변을 불렛포인트 형식으로 정리하여 알려주세요.\n"
        "한국어로 대답하세요.\n\n"
        "#Question:\n"
        "{question}\n\n"
        "#Context:\n"
        "{context}\n"
    )

    prompt = PromptTemplate.from_template(template)

    def format_docs(docs):
        return '\n\n'.join([d.page_content for d in docs])

    input_data = {'context': format_docs(search_results), 'question': question}
    rag_chain = (
        prompt
        | model
        | StrOutputParser()
    )

    yield from rag_chain.invoke(input_data)

    #return rag_chain.invoke(input_data)
