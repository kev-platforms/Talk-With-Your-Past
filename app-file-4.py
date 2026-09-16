import streamlit as st
import requests

# 1. Configuración visual de la interfaz
st.set_page_config(page_title="Talk-With-Your-Past", page_icon="⏳", layout="wide")
st.title("⏳ Talk-With-Your-Past (Simulador Espacio-Temporal)")
st.write("Habla con tus coordenadas de forma fluida y totalmente inteligente.")

# 2. Barra lateral con configuraciones sencillas
st.sidebar.header("📝 Configura tus Datos Base")
nombre = st.sidebar.text_input("Tu Nombre:", "Carlos")
gustos = st.sidebar.text_area("Tus gustos en el pasado:", "Me gustaba jugar videojuegos, escuchar música y salir con amigos.")
año_destino = st.sidebar.slider("Año al que quieres viajar:", 2010, 2045, 2014)

es_pasado = año_destino <= 2026

# 3. Gestión Segura de Claves (Evita errores de GitHub)
# Si ejecutas local o en la nube, buscará en el cofre secreto de Streamlit.
# Si no encuentra la clave, usará un texto vacío para evitar que el código falle de golpe.
hf_token = st.secrets.get("HF_TOKEN", "")

# 4. FUNCIÓN CON IA INTELIGENTE MEJORADA
def consultar_ia_gratis(historial_mensajes, año, es_pasado):
    if es_pasado:
        prompt_sistema = f"Eres el 'Yo' del pasado de {nombre} en el año {año}. Tus gustos en esta época son: {gustos}. No sabes NADA de lo que ocurrió después del año {año}. Habla de forma muy casual, juvenil, alegre y responde de forma corta, como si realmente fueras él en el pasado."
    else:
        prompt_sistema = f"Eres el 'Yo' del futuro de {nombre} en el año {año}. Eres sabio, maduro, conoces sus decisiones del 2026 y le hablas con cariño, dándole consejos realistas y motivándolo desde el futuro."

    # Formateamos la conversación de forma limpia para Llama 3
    conversacion_completa = f"<|system|>\n{prompt_sistema}\n"
    for msg in historial_mensajes:
        if msg["role"] == "user":
            conversacion_completa += f"<|user|>\n{msg['content']}\n"
        else:
            conversacion_completa += f"<|assistant|>\n{msg['content']}\n"
    
    conversacion_completa += "<|assistant|>\n"

    # API oficial de inferencia directa para Meta-Llama
    API_URL = "https://huggingface.co"
    headers = {"Authorization": f"Bearer {hf_token}"} if hf_token else {}
    
    payload = {
        "inputs": conversacion_completa,
        "parameters": {"max_new_tokens": 120, "temperature": 0.7, "stop": ["<|user|>", "<|system|>"]}
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
        resultado = response.json()
        
        # Extracción segura del bloque de texto generado
        if isinstance(resultado, list) and 'generated_text' in resultado[0]:
            texto_generado = resultado[0]['generated_text']
        elif isinstance(resultado, dict) and 'generated_text' in resultado:
            texto_generado = resultado['generated_text']
        else:
            texto_generado = resultado
            
        respuesta_limpia = texto_generado.split("<|assistant|>\n")[-1].strip()
        return respuesta_limpia
    except:
        # Mensajes de respaldo optimizados por si la API pública está saturada
        if es_pasado:
            return f"¡Qué loco! Me dejas pensando con lo que dices en este {año}. ¡Espero que sigamos dándole con todo a los juegos y a los estudios!"
        else:
            return f"Todo lo que estás viviendo ahora mismo en tu presente del 2026 está construyendo el lugar donde estoy yo hoy en el año {año}."

# 5. Diseño de dos columnas corregido
col_izquierda, col_derecha = st.columns(2)

with col_derecha:
    st.subheader(f"🖼️ Tu Avatar en {año_destino}")
    
    # URL oficial de la API de DiceBear corregida para mostrar avatares válidos de pixeles y robots
    if es_pasado:
        url_avatar = f"https://dicebear.com{nombre}Pasado"
    else:
        url_avatar = f"https://dicebear.com{nombre}Futuro"
        
    st.image(url_avatar, width=250)
    st.caption("Avatar interactivo adaptado a tu coordenada temporal.")

with col_izquierda:
    st.subheader(f"💬 Chat con tu 'Yo' de {año_destino}")

    # Botón para limpiar la caché y reiniciar la conversación de forma interactiva
    if st.button("Reiniciar Línea Temporal"):
        st.session_state.messages = []
        st.rerun()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar mensajes en pantalla
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrada de mensajes del usuario
    if prompt_usuario := st.chat_input("Escribe un mensaje..."):
        with st.chat_message("user"):
            st.markdown(prompt_usuario)
        st.session_state.messages.append({"role": "user", "content": prompt_usuario})

        with st.chat_message("assistant"):
            with st.spinner("Pensando respuesta temporal..."):
                respuesta_ia = consultar_ia_gratis(st.session_state.messages, año_destino, es_pasado)
                st.markdown(respuesta_ia)
        st.session_state.messages.append({"role": "assistant", "content": respuesta_ia})
