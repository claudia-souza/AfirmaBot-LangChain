from flask import Flask, request, jsonify
from app import chain, get_session_history
import threading
import time

app = Flask(__name__)

resultados = {}  

def processar_em_background(session_id, pergunta_usuario):
    try:
        history = get_session_history(session_id)

        resposta = chain.invoke({
            "input": pergunta_usuario,
            "history": history.messages
        })

        resultados[session_id] = resposta

        # salva no históric
        history.add_user_message(pergunta_usuario)
        history.add_ai_message(resposta)

    except Exception as e:
        resultados[session_id] = f"Erro ao buscar resposta: {str(e)}"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)

    tag = data.get("queryResult", {}).get("intent", {}).get("displayName", "")
    pergunta_usuario = data.get("queryResult", {}).get("queryText", "")
    session_id = data.get("session", "default_session")

    print(f"TAG RECEBIDA: {tag}")

    if tag == "start_processing":
        if not pergunta_usuario:
            return jsonify({"fulfillmentText": "Não recebi nenhuma pergunta."})

        thread = threading.Thread(target=processar_em_background,
                                  args=(session_id, pergunta_usuario))
        thread.start()

        return jsonify({
            "fulfillmentText": (
                "Estou processando sua solicitação. "
                "Pergunte novamente: *resultado*, para ver a resposta."
            )
        })

    if tag == "get_result":
        if session_id in resultados:
            resposta = resultados.pop(session_id)

            return jsonify({
                "fulfillmentText": resposta
            })

        else:
            return jsonify({
                "fulfillmentText": "Ainda estou processando,tente novamente em alguns segundos."
            })

   
    return jsonify({
        "fulfillmentText": "Não reconheci a intenção."
    })


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
