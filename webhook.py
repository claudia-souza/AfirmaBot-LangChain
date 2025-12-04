from flask import Flask, request, jsonify
from app import chain, get_session_history  # importa do app.py

# tentativa do uso do negrito 
import re


# forma padrão de criar no flask 
app = Flask(__name__)



# --- Conversor simples de Markdown para HTML ---
def md_to_html(text):
    # Negrito **texto**
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    # Itálico *texto*
    text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", text)
    return text

# ---------------------------------------------------------



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
        resposta = chain.invoke({
            "input": pergunta_usuario,
            "history": history.messages
        })
    except Exception as e:
        print(f"Erro ao invocar LangChain: {e}")
        resposta = "Desculpe, houve um erro ao processar sua pergunta."


    history.add_user_message(pergunta_usuario)
    history.add_ai_message(resposta)



    # ---------------------------
    resposta_html = md_to_html(resposta)
    
    return jsonify({"fulfillmentText": resposta_html})
    #-----------------------------


    # Retornando minha API 
    #return jsonify({"fulfillmentText": resposta})


# Para rodar localmente (Windows)
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
