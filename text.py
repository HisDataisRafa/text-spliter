
import streamlit as st
import re
import pandas as pd

def get_sentences(text):
    """Extract sentences from text."""
    # Normalize spaces and clean text
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Split text into sentences
    sentences = []
    current = ""
    
    for char in text:
        current += char
        if char == '.' and not (
            re.search(r'\b[A-Z]\.$', current) or  # Single letter abbreviation
            re.search(r'\b[A-Z][a-z]+\.$', current) or  # Common abbreviation
            re.search(r'\d+\.$', current)  # Number with period
        ):
            sentences.append(current.strip())
            current = ""
            
    if current.strip():
        sentences.append(current.strip())
        
    return sentences

def split_text_into_parts(text, num_parts=3):
    """
    Split text into equal parts while maintaining sentence coherence.
    """
    # Get sentences
    sentences = get_sentences(text)
    
    if not sentences:
        return [""] * num_parts
        
    # Calculate total length
    total_length = sum(len(s) for s in sentences)
    target_length_per_part = total_length / num_parts
    
    # Initialize parts
    parts = [""] * num_parts
    current_part = 0
    current_length = 0
    
    # Distribute sentences
    for sentence in sentences:
        # If we've filled all but the last part, put everything else in the last part
        if current_part == num_parts - 1:
            parts[current_part] += sentence
            continue
            
        # Add sentence to current part
        if not parts[current_part]:
            parts[current_part] = sentence
        else:
            parts[current_part] += " " + sentence
            
        current_length += len(sentence)
        
        # Check if we should move to next part
        if current_length >= target_length_per_part:
            current_part += 1
            current_length = 0
    
    return parts

def main():
    st.set_page_config(
        page_title="Divisor de Texto",
        page_icon="📑",
        layout="wide"
    )
    
    st.title("📑 Divisor de Texto en Partes")
    st.write("Esta aplicación divide tu texto en partes iguales manteniendo la coherencia de las oraciones.")
    
    # Input methods
    input_method = st.radio(
        "Selecciona el método de entrada:",
        ["Subir archivo de texto", "Pegar texto directamente"]
    )
    
    text_input = ""
    
    if input_method == "Subir archivo de texto":
        uploaded_file = st.file_uploader("Sube tu archivo de texto", type=['txt'])
        if uploaded_file is not None:
            text_input = uploaded_file.getvalue().decode('utf-8')
    else:
        text_input = st.text_area("Pega tu texto aquí:", height=200)
    
    num_parts = st.slider("Número de partes:", min_value=2, max_value=5, value=3)
    
    if st.button("Dividir Texto") and text_input:
        with st.spinner('Dividiendo el texto...'):
            # Split the text
            parts = split_text_into_parts(text_input, num_parts)
            
            # Calculate statistics
            total_chars = sum(len(part) for part in parts)
            stats_data = []
            
            # Show results in tabs
            tabs = st.tabs([f"Parte {i+1}" for i in range(num_parts)])
            
            for i, (tab, part) in enumerate(zip(tabs, parts), 1):
                with tab:
                    percentage = (len(part) / total_chars) * 100 if total_chars > 0 else 0
                    st.markdown(f"### Parte {i}")
                    st.text_area(
                        f"Contenido de la parte {i}:",
                        part,
                        height=200,
                        key=f"part_{i}"
                    )
                    stats_data.append({
                        'Parte': f'Parte {i}',
                        'Caracteres': len(part),
                        'Porcentaje': f'{percentage:.1f}%'
                    })
            
            # Show statistics
            st.markdown("### Estadísticas")
            stats_df = pd.DataFrame(stats_data)
            st.dataframe(stats_df, hide_index=True)
            
            # Download buttons for each part
            st.markdown("### Descargar Partes")
            cols = st.columns(num_parts)
            
            for i, (col, part) in enumerate(zip(cols, parts), 1):
                with col:
                    st.download_button(
                        f"Descargar Parte {i}",
                        part,
                        f"parte_{i}.txt",
                        "text/plain",
                        key=f"download_{i}"
                    )

if __name__ == "__main__":
    main()
