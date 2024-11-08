from langchain_chroma import Chroma
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from embed import embeddings
from logger import setup_logging

logger = setup_logging()

MODEL_URL = "http://ollama-service:11434"
VECTORSTORE_PATH = 'data-library/vectorstore'
DEFAULT_ANSWER = "죄송합니다. 질문과 충분히 관련된 정보를 찾지 못했습니다."
SIMILARITY_THRESHOLD = 0.4  # 유사도 임계값

PROMPT_TEMPLATE = (
    "당신은 질문-답변(Question-Answer) Task를 수행하는 AI 어시스턴트입니다.\n"
    "검색된 문맥(context)을 사용하여 질문(question)에 답하세요.\n"
    "답변을 불렛포인트 형식으로 정리하여 알려주세요.\n"
    "한국어로 대답하세요.\n\n"
    "# Question:\n"
    "{question}\n\n"
    "# Context:\n"
    "{context}\n"
)

class DocumentRetriever:
    def __init__(self, vectorstore, k = 3, threshold = SIMILARITY_THRESHOLD):
        self.vectorstore = vectorstore
        self.k = k
        self.threshold = threshold

    def get_relevant_documents(self, query):
        docs_and_scores = self.vectorstore.similarity_search_with_relevance_scores(
            query,
            k=self.k
        )
        return [doc for doc, score in docs_and_scores if score >= self.threshold]

    def invoke(self, question):
        results = self.get_relevant_documents(question)
        for i, doc in enumerate(results):
            logger.info("검색결과%d\n 내용:%s", i+1, doc.page_content)
        return results


class QASystem:
    def __init__(self):
        self.vectorstore = Chroma(
            persist_directory=VECTORSTORE_PATH,
            embedding_function=embeddings
        )

        self.retriever = DocumentRetriever(
            vectorstore=self.vectorstore,
            k=3,
            threshold=SIMILARITY_THRESHOLD
        )

        self.model = ChatOllama(
            base_url=MODEL_URL,
            timeout=6000,
            model="tinyllama",
            temperature=0  # 사실적인 응답을 위해 temperature=0 설정
        )

        self.prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)

        self.rag_chain = (
            self.prompt
            | self.model
            | StrOutputParser()
        )

    def _format_docs(self, docs):
        return '\n\n'.join([d.page_content for d in docs])

    def generate_answer(self, question):
        logger.info("질문: %s", question)

        search_results = self.retriever.invoke(question)

        if not search_results:
            logger.info("유사한 내용이 없습니다.")
            return DEFAULT_ANSWER

        logger.info("유사도: %s", search_results)

        input_data = {
            'context': self._format_docs(search_results),
            'question': question
        }

        answer = self.rag_chain.invoke(input_data)
        logger.info("응답: %s", answer)

        return answer

qa_system = QASystem()

def generate_answer(question):
    return qa_system.generate_answer(question)
