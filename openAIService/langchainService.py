from flask import Flask, request
import os

from downloadEmbedding import downloadEmbedding
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.memory import ConversationSummaryBufferMemory
from langchain.prompts import PromptTemplate

app = Flask(__name__)

# Configura tu clave API de OpenAI como una variable de entorno en tu entorno de ejecución
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

@app.route("/getresponsegpt", methods=["GET"])
def get_response_gpt():
    user_prompt = request.args.get("user_prompt")
    
    # Cargar los embeddings y el vector store
    embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
    downloadEmbedding()
    PATH_VECTORSTORE = "vectorStore"
    knowledge_base = FAISS.load_local(PATH_VECTORSTORE + "/faiss_index", embeddings)
    
    # Buscar documentos similares
    docs = knowledge_base.similarity_search(user_prompt)

    # Inicializar el modelo de lenguaje de OpenAI
    llm = OpenAI(model_name="text-davinci-003", api_key=OPENAI_API_KEY) # a partir de enero de 2024 el modelo "text-davinci-003" queda deprecated
    
    # Plantilla para el mensaje del asistente virtual
    template = """Eres un asistente virtual que ayuda a los humanos
    {context} 
    {chat_history} 
    Humano: {human_input} 
    AI Assistant: 
    """
    
    prompt = PromptTemplate(
        input_variables=["context", "chat_history", "human_input"],
        template=template
    )
    
    # Configurar la memoria del chat
    memory = ConversationSummaryBufferMemory(
        llm=llm,
        memory_key="chat_history",
        input_key="human_input",
        max_token_limit=2000
    )
    
    # Configurar la cadena de conversación
    chain = load_qa_chain(
        llm=llm, 
        chain_type="stuff",  # Asegúrate de reemplazar "stuff" por el tipo de cadena que necesitas
        memory=memory,
        prompt=prompt
    )
    
    # Obtener respuesta del modelo
    respuesta = chain(
        {"input_documents": docs, "human_input": user_prompt}, 
        return_only_outputs=True
    )["output_text"]
    
    return respuesta

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8502))
    app.run(host='0.0.0.0', port=port, debug=False)  # Cambia debug a False para producción
