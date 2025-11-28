from pathlib import Path
from typing import Dict
from langchain_community.document_loaders import PyMuPDFLoader 
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    openai_api_key=OPENAI_API_KEY
)

docs = []

# data ( pasta com pdf )
folder = Path("data/")

for n in folder.glob("*.pdf"):
    try:
        loader = PyMuPDFLoader(str(n))
        docs.extend(loader.load())
        print(f"Carregado com sucesso: {n.name}")
    except Exception as e:
        print(f"Erro ao carregar arquivo {n.name}: {e}")

print(f"Total de documentos carregados: {len(docs)}")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=30
)

chunks = splitter.split_documents(docs)

for i, chunk in enumerate(chunks[:3]):
    print(f"Chunk {i+1}")
    print(chunk.page_content)
    print("\n")

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",
    api_key=OPENAI_API_KEY
)


vectorstore = FAISS.from_documents(chunks, embeddings)

retriever = vectorstore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"score_threshold": 0.3, "k": 4}
)

prompt_rag = ChatPromptTemplate.from_messages([
    (
        "system",
        "Você é o Afirma Bot 👩🏾‍🦱👨🏾‍🦱, uma assistente virtual especializada na Lei de Cotas (Lei nº 12.711/2012) "
        "e no processo de heteroidentificação.\n"
        "Responder SOMENTE com base no contexto fornecido.\n"
        "Se não houver base suficiente, responda 'Não sei.'"
    ),
    ("human", "Pergunta: {input}\n\nContexto: \n{context}")
])

document_chain = create_stuff_documents_chain(llm, prompt_rag)

def perguntar_politica_RAG(pergunta: str) -> Dict:
    # Pega documentos relacionados
    docs_relacionados = retriever.get_relevant_documents(pergunta)

    if not docs_relacionados:
        return {
            "answer": "Não sei.",
            "citacoes": [],
            "contexto_encontrado": False
        }

    # Gera resposta
    answer = document_chain.invoke({
        "input": pergunta,
        "context": docs_relacionados
    })

    txt = (answer or "").strip()

     # Quando não tiver contexto suficiente ,responder com n sei 
    if txt.rstrip(".!?") == "Não sei":
        return {
            "answer": "Não sei.",
            "citacoes": [],
            "contexto_encontrado": False
        }

    # Caminho feliz
    return {
        "answer": txt,
        "citacoes": docs_relacionados,
        "contexto_encontrado": True
    }


# testando os Embeddings pelo terminal 

if __name__ == "__main__":
    print("Digite sua pergunta ou digite 'sair' para encerrar):")
    while True:
        pergunta = input("> ")
        if pergunta.lower() in ["sair", "exit", "quit"]:
            break
        resultado = perguntar_politica_RAG(pergunta)
        print("\nResposta:")
        print(resultado["answer"])
        if resultado["contexto_encontrado"]:
            print(f"(Base de {len(resultado['citacoes'])} chunks de contexto)\n")
        else:
            print("(Sem contexto relevante)\n")
