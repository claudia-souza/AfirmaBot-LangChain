from flask import Flask, request, jsonify
from threading import Thread
from app import chain, get_session_history

app = Flask(__name__)

pending_responses = {}


def process_in_background(session_id, pergunta):
    """Processa usando LangChain sem travar o Dialogflow"""
    
    history = get_session_history(session_id)
    pending_responses[session_id] = "PROCESSING"

    try:
        resposta = chain.invoke({
            "input": pergunta,
            "history": history.messages
        })

        # salva no histórico
        history.add_user_message(pergunta)
        history.add_ai_message(resposta)

        pending_responses[session_id] = resposta

    except Exception as e:
        pending_responses[session_id] = f"Erro ao processar: {e}"


@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.get_json(force=True)
    intent = body["queryResult"]["intent"]["displayName"]
    pergunta = body["queryResult"]["queryText"]
    session_id = body["session"]

    if intent == "start_processing":

        Thread(target=process_in_background, args=(session_id, pergunta)).start()

        return jsonify({
            "fulfillmentText": (
                "Certo! Estou processando sua solicitação. "
                "Quando quiser ver o resultado, digite **resultado**."
            )
        })
    
    if intent == "get_result":

        resultado = pending_responses.get(session_id, None)

        if resultado is None:
            return jsonify({"fulfillmentText": "Nenhum processamento foi iniciado ainda."})

        if resultado == "PROCESSING":
            return jsonify({"fulfillmentText": "Ainda estou processando! Tente novamente em alguns segundos."})

    
        return jsonify({"fulfillmentText": resultado})


    return jsonify({"fulfillmentText": "Não reconheci a intenção."})


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
