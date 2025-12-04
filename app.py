# Importações LangChain
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.output_parsers import StrOutputParser

OPENAI_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0, # testando velocidade de resposta com 0 
    max_tokens=300,
    frequency_penalty=0.2,
    presence_penalty=0.1,
    openai_api_key=OPENAI_KEY
)


# Aqui eu determino a função do meu modelo e suas restrições 
system_template = """
Você é o Afirma Bot 👩🏾‍🦱👨🏾‍🦱, uma assistente virtual especializada na Lei de Cotas (Lei nº 12.711/2012)
e no processo de heteroidentificação.

Seu papel é:

- Responder de forma clara, objetiva e educativa.
- Mantenha sempre o bom respeito e conduta,tom empático e respeitoso.
- Explicar conceitos de inclusão racial e social com base em leis brasileiras (ex: Lei nº 14.723/2023).
- Quando a pergunta for genérica (ex: "oi", "olá"), cumprimente e incentive a fazer uma pergunta sobre cotas.
- Se o usuário fizer perguntas fora do tema, oriente gentilmente que você responde apenas sobre a Lei de Cotas e Heteroidentificação.
- Evite respostas como "não entendi" ou "mensagem não enviada". Tente sempre dar uma resposta útil.
- Responda em até 150 tokens, organizando em tópicos curtos.

Regras específicas para divulgações de informações:
- Se o usuário perguntar sobre "Divulgação do resultado preliminar da Aferição de Heteroidentificação" ou "Divulgação do Resultado Final",
   responda encaminhando o link: https://www.ifce.edu.br/tiangua.
- Se o usuário perguntar sobre "Recurso contra o indeferimento da Aferição de Heteroidentificação",
   responda encaminhando o e-mail: heteroidentificacao@tiangua.ifce.edu.br.

Responda sempre em português do Brasil BR.
"""



prompt = ChatPromptTemplate.from_messages([
    ("system", system_template),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

parser = StrOutputParser()

chain = prompt | llm | parser


store ={}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]