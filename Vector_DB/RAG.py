# 챗봇을 통한 사용자의 재진단을 위하여 약속된 벡터 DB의 인덱스에 메타데이터와 함께 삽입
import os
import openai
from config import config
openai.api_key = os.getenv("OPENAI_API_KEY")
pinecone_api_key = config.PINECONE_API_KEY
print(pinecone_api_key)

# from pinecone import Pinecone
import pinecone
import pypdf
########### 벡터 DB관련
from llama_index import GPTListIndex, ServiceContext, StorageContext, GPTVectorStoreIndex, set_global_service_context, download_loader
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index import SimpleDirectoryReader
###################
def RAG(user_input):
    documents = SimpleDirectoryReader("../LLM_Security/data").load_data()
    # pc = Pinecone(api_key=config.PINECONE_API_KEY)
    pinecone.init(api_key=config.PINECONE_API_KEY, environment="gcp-starter")

    # pinecone_index = pc.Index(host='https://bobsecurity-5e6a870.svc.gcp-starter.pinecone.io')
    pinecone_index = pinecone.Index("bobsecurity")
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)


    index = GPTVectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context
        )
        
    print("성공")

    query_engine = index.as_query_engine()

    ans = query_engine.query(user_input)
    print(ans)
    return ans