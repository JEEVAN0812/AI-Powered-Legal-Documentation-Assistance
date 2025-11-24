from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import CTransformers
from langchain import PromptTemplate
from langchain.chains import RetrievalQA

from IPython.display import display, HTML
import json
import time
import pathlib
from langchain.document_loaders import DirectoryLoader, TextLoader
import warnings

import requests
warnings.filterwarnings("ignore")


loader = DirectoryLoader(
    path="static/pdf/",  
    glob="legal_llama.txt", 
    loader_cls=TextLoader,  
    loader_kwargs={'encoding': 'utf-8'}  
)

documents = loader.load()
splitter = RecursiveCharacterTextSplitter()
texts = splitter.split_documents(documents)
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'})
db = FAISS.from_documents(texts, embeddings)
template = """Use the following pieces of information to answer the user's question.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Context: {context}
Question: {question}
Only return the helpful answer below and nothing else.
Helpful answer:
"""

config = {'max_new_tokens': 256, 'temperature': 0.01}
llm = CTransformers(model='llama-2-7b-chat.ggmlv3.q8_0.bin',
                    model_type='llama', config=config)

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'})

retriever = db.as_retriever(search_kwargs={'k': 2})
prompt = PromptTemplate(
    template=template,
    input_variables=['context', 'question'])
QA_LLM = RetrievalQA.from_chain_type(llm=llm,
                                    chain_type='stuff',
                                    retriever=retriever,
                                    return_source_documents=True,
                                    chain_type_kwargs={'prompt': prompt})

model=QA_LLM
def query(question):
    model_path = model.combine_documents_chain.llm_chain.llm.model
    model_name = pathlib.Path(model_path).name
    time_start = time.time()
    output = model({'query': question})
    response = output["result"]
    time_elapsed = time.time() - time_start
    print(question)
    print(response)
    print(f'Response time: {time_elapsed:.02f} sec')
    return response



# query(QA_LLM, "What is the key difference between a contract and an agreement?")
# query(QA_LLM, "What legal elements must be present for a contract to be valid?")
# query(QA_LLM, "How can ambiguous language in a legal document create disputes?")
# query(QA_LLM, "What are some common pitfalls to avoid when drafting a legal document?")
# query(QA_LLM, "Can a contract be enforceable if one party is a minor?")
# query(QA_LLM, "What are the consequences of signing a legal document without understanding its terms?")
# query(QA_LLM, "How does the statute of frauds impact the enforceability of certain types of contracts?")
# query(QA_LLM, "What role do notaries play in the execution of legal documents?")
# query(QA_LLM, "In what circumstances can a party seek to invalidate a contract based on duress or undue influence?")
# query(QA_LLM, "What are the implications of a force majeure clause in a contract, especially in unforeseen circumstances like a pandemic?")