import os
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image, ImageOps
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_drawable_canvas import st_canvas

Expert = " "
profile_imgenh = " "
    
def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."

# Streamlit 
st.set_page_config(page_title='Fábrica de Monstruos - Tablero Inteligente')
st.title('🎨 Fábrica de Monstruos')

with st.sidebar:
    st.subheader("Acerca de:")
    st.subheader("¡Da vida a tu imaginación! En esta aplicación, una inteligencia artificial analizará el boceto de tu monstruo único para darle una identidad completa.")

st.subheader("¡Libera tu creatividad! Dibuja tu propio monstruo en el tablero de abajo y presiona el botón para descubrir quién es.")

# Add canvas component
drawing_mode = "freedraw"
stroke_width = st.sidebar.slider('Selecciona el ancho de línea', 1, 30, 5)
stroke_color = "#000000" 
bg_color = '#FFFFFF'

# Create a canvas component
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=300,
    width=400,
    drawing_mode=drawing_mode,
    key="canvas",
)

ke = st.text_input('Ingresa tu Clave de OpenAI (API Key)')
os.environ['OPENAI_API_KEY'] = ke

# Retrieve the OpenAI API Key from secrets
api_key = os.environ['OPENAI_API_KEY']

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=api_key)

analyze_button = st.button("¡Crear Monstruo!", type="secondary")

# Check if an image has been uploaded, if the API key is available, and if the button has been pressed
if canvas_result.image_data is not None and api_key and analyze_button:

    with st.spinner("Dando vida a tu criatura... Analizando trazos..."):
        # Encode the image
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8'), 'RGBA')
        input_image.save('img.png')
        
        # Codificar la imagen en base64
        base64_image = encode_image_to_base64("img.png")
            
        # Prompt actualizado para la creación e interpretación completa del personaje monstruoso en español
        prompt_text = (
            "Analiza detalladamente este dibujo de un monstruo hecho por un usuario. "
            "A partir de su forma, estilo y aspecto visual, realiza una interpretación completa de creación de personaje en español que incluya: "
            "1. Nombre épico o divertido para el monstruo. "
            "2. Edad (o tiempo de existencia). "
            "3. Habilidades o poderes especiales únicos basados en sus rasgos visuales. "
            "4. Una posible historia corta (lore) sobre de dónde viene, qué le gusta hacer o cuál es su misión en el mundo. "
            "Dale un tono creativo, amigable y narrativo."
        )
    
        # Create the payload for the completion request
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": f"data:image/png;base64,{base64_image}",
                    },
                ],
            }
        ]
    
        # Make the request to the OpenAI API
        try:
            full_response = ""
            message_placeholder = st.empty()
            response = openai.chat.completions.create(
              model="gpt-4o-mini",
              messages=[
                {
                   "role": "user",
                   "content": [
                     {"type": "text", "text": prompt_text},
                     {
                       "type": "image_url",
                       "image_url": {
                         "url": f"data:image/png;base64,{base64_image}",
                       },
                     },
                   ],
                 }
                ],
              max_tokens=600,
              )
              
            if response.choices[0].message.content is not None:
                full_response += response.choices[0].message.content
                message_placeholder.markdown(full_response + "▌")
                
            # Final update to placeholder after the stream ends
            message_placeholder.markdown(full_response)
            
            if Expert == profile_imgenh:
                st.session_state.mi_respuesta = response.choices[0].message.content 
    
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
else:
    if not api_key:
        st.warning("Por favor ingresa tu API key para comenzar la creación.")
