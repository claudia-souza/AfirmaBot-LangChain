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



# Cria o modelo passando a chave lida do .env
# Chave do GPT 
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,
    max_tokens=400,
    frequency_penalty=0.2,
    presence_penalty=0.1,
    openai_api_key="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"
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

Responda sempre em português do Brasil 🇧🇷.
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

def iniciar_afirma_bot():
    print("Olá! 👩🏾‍🦱👨🏾‍🦱 Sou sua assistente virtual Afirma Bot!")
    print("Podemos conversar sobre a Lei de Cotas e o processo de heteroidentificação.")
    print("Digite 'sair' para encerrar a conversa.\n")

    session_id = "user123" # meio que um ID ficticio
    history = get_session_history(session_id)

    while True:
        pergunta_usuario = input("Você: ").strip()

        if pergunta_usuario.lower() in ["sair", "exit"]:
            print("Afirma Bot: Foi ótimo conversar com você! Espero ter te ajudado,até mais!")
            break

        if not pergunta_usuario:
            print("Afirma Bot: Por favor, digite uma pergunta sobre cotas ou heteroidentificação.")
            continue

        resposta = chain.invoke({
            "input": pergunta_usuario,
            "history": history.messages
        })

    
        history.add_user_message(pergunta_usuario)
        history.add_ai_message(resposta)

       
        print(f"Afirma Bot: {resposta}\n")
        
# Inicia o afirma bot
#if __name__ == "__main__":
   # iniciar_afirma_bot()