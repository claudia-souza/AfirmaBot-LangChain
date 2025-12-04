from flask import Flask, request, jsonify
from app import chain, get_session_history 
# importa do app.py

# forma padrão de criar no flask 
app = Flask(__name__)

# Função auxiliar para formatar a resposta do LLM em Rich Content do Dialogflow
def create_dialogflow_rich_response(text_response):
    """
    Cria a estrutura de Custom Payload (richContent) para o Dialogflow Messenger.
    O texto deve ser pré-formatado com HTML (tags <b> para negrito) se necessário.
    
    Como o LLM geralmente retorna um parágrafo único, colocamos todo o texto
    em uma única string dentro do array 'text'. Se o texto for multi-parágrafo,
    o LangChain/LLM deve formatar as quebras de linha com <br>.
    """
    
    # Substitui a sintaxe Markdown **negrito** por <b>negrito</b>.
   
    formatted_text = text_response.replace('**', '<b>', 1).replace('**', '</b>', 1)
    

    return {
        "fulfillmentMessages": [
            {
                "payload": {
                    "richContent": [
                        [
                            {
                                "type": "description",
                                "title": "Resposta do Chatbot", # Título opcional
                                "text": [
                                    formatted_text 
                                ]
                            }
                        ]
                    ]
                }
            }
        ]
    }


# Criando rotas 
@app.route("/webhook", methods=["POST"])
def webhook():
    # 1. Obter dados da requisição
    data = request.get_json(force=True)
    pergunta_usuario = data.get("queryResult", {}).get("queryText", "")
    session_id = data.get("session", "default_session")

    if not pergunta_usuario:
        return jsonify({"fulfillmentText": "Não recebi nenhuma pergunta."})

    history = get_session_history(session_id)

    # Invocar o LangChain
    try:
        resposta_bruta = chain.invoke({
            "input": pergunta_usuario,
            "history": history.messages
        })
    except Exception as e:
        print(f"Erro ao invocar LangChain: {e}")
        return jsonify({"fulfillmentText": "Desculpe, houve um erro ao processar sua pergunta."})


    history.add_user_message(pergunta_usuario)
    history.add_ai_message(resposta_bruta)

    #Formatar a resposta para Rich Content do Dialogflow

    resposta_formatada_json = create_dialogflow_rich_response(resposta_bruta)

    #Retornar o JSON de Rich Content
    return jsonify(resposta_formatada_json)


# Para rodar localmente (Windows)
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)