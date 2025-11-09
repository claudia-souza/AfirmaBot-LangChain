from flask import Flask, request, jsonify
from app import chain, get_session_history  # importa do app.py

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    pergunta_usuario = data.get("queryResult", {}).get("queryText", "")
    session_id = data.get("session", "default_session")

    if not pergunta_usuario:
        return jsonify({"fulfillmentText": "Não recebi nenhuma pergunta."})

    history = get_session_history(session_id)


    try:
        resposta = chain.invoke({
            "input": pergunta_usuario,
            "history": history.messages
        })
    except Exception:
            resposta = chain.run(pergunta_usuario)

    history.add_user_message(pergunta_usuario)
    history.add_ai_message(resposta)

    return jsonify({"fulfillmentText": resposta})



#comentando pra ver se é esse o bug
#if __name__ == "__main__":
   # app.run(host="0.0.0.0", port=5000, debug=True)
