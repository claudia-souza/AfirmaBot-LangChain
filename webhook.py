from flask import Flask, request, jsonify
from app import chain, get_session_history  # importa do app.py
from rag import perguntar_politica_RAG   # importa o RAG

# forma padrão de criar no flask
app = Flask(__name__)


#criando rotas
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    pergunta_usuario = data.get("queryResult", {}).get("queryText", "")
    session_id = data.get("session", "default_session")


    if not pergunta_usuario:
        return jsonify({"fulfillmentText": "Não recebi nenhuma pergunta."})


    history = get_session_history(session_id)


    
    try:
        # consulta RAG.py 
        resultado_rag = perguntar_politica_RAG(pergunta_usuario)

        if resultado_rag["contexto_encontrado"]:
            # Usa resposta do RAG
            resposta = resultado_rag["answer"]
        else:
            # Se não cai no chain normal com histórico
            resposta = chain.invoke({
                "input": pergunta_usuario,
                "history": history.messages
            })

    except Exception as e:
        print(f"Erro ao invocar LangChain: {e}")
        resposta = "Desculpe, houve um erro ao processar sua pergunta."


    history.add_user_message(pergunta_usuario)
    history.add_ai_message(resposta)

    # Retornando minha API
    return jsonify({"fulfillmentText": resposta})


# Para rodar localmente (Windows)
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)



