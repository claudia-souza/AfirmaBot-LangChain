from pathlib import Path
from langchain_community.document_loaders import PyMuPDFLoader 
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
# Quebrar textos grandes em pedaços menores (chunks)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

#pegar documentos
#salvar em uma lista vazia
docs = []

# Caminho da pasta data/
folder = Path("data/")

# Buscar todos PDFs ( no meu caso1) 
for n in folder.glob("*.pdf"):
    try:
        loader = PyMuPDFLoader(str(n))
        docs.extend(loader.load())
        print(f"Carregado com sucesso: {n.name}")
    except Exception as e:
        print(f"Erro ao carregar arquivo {n.name}: {e}")

print(f"Total de documentos carregados: {len(docs)}")

# (chunks)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,    
    chunk_overlap=30
)

chunks = splitter.split_documents(docs)

# iMPRIMINDO OS Chunk
for i, chunk in enumerate(chunks[:3]):
    print(f"Chunk {i+1}")
    print(chunk.page_content)
    print("\n")


# embeddings 
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",  
    api_key=OPENAI_API_KEY
)

#vetor
vectorstore = FAISS.from_documents(chunks,embeddings)

#busca no vector
#definindo os padrões de busca 
retriever = vectorstore.as_retriever(search_type="similarity_score_threshold",search_kwargs={"score_threshold": 0.3,"k":4})

#definindo os prompts 
prompt_rag = ChatPromptTemplate.from_messages([
(
"system",
"Você é o Afirma Bot 👩🏾‍🦱👨🏾‍🦱, uma assistente virtual especializada na Lei de Cotas (Lei nº 12.711/2012) e no processo de heteroidentificação."
"Responder SOMENTE com base no contexto fornecido"
"Se não houver base suficiente,responda 'Não sei.'"),
("human","Pergunta : {input}\n\nContexto: \n{context}")
])

document_chain = create_stuff_documents_chain(llm,prompt_rag)


#criando as funções 
def perguntar_politica_RAG(pergunta : str) -> Dict:
    docs_relacionados = retriever.invoke(pergunta)

    if not docs_relacionados:
        return {"answer": "Não sei.",
                "citacoes": [],
                "contexto_encontrado": False
                
                
                }
    answer = document_chain