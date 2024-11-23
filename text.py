import streamlit as st
import re
import pandas as pd

def split_text_into_parts(text, num_parts=3):
    """
    Split text into approximately equal parts while maintaining sentence coherence.
    """
    # Clean and normalize the text
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Split into sentences
    sentences = []
    temp_sentence = ""
    
    for char in text:
        temp_sentence += char
        if char == '.' and not (
            re.search(r'\b[A-Z]\.$', temp_sentence) or
            re.search(r'\b[A-Z][a-z]+\.$', temp_sentence) or
            re.search(r'\d+\.$', temp_sentence)
        ):
            sentences.append(temp_sentence.strip())
            temp_sentence = ""
    
    if temp_sentence.strip():
        sentences.append(temp_sentence.strip())
    
    # Ensure we have enough sentences to distribute
    if len(sentences) < num_parts:
        return [" ".join(sentences)] + [""] * (num_parts - 1)
    
    # Calculate approximate number of sentences per part
    total_sentences = len(sentences)
    sentences_per_part = total_sentences // num_parts
    
    # Distribute sentences into parts
    parts = []
    start_idx = 0
    
    for i in range(num_parts):
        if i == num_parts - 1:
            # Last part gets all remaining sentences
            part_sentences = sentences[start_idx:]
        else:
            # Calculate end index for current part
            end_idx = start_idx + sentences_per_part
            # Adjust for the last part to ensure all sentences are used
            if i == num_parts - 2:
                remaining_sentences = total_sentences - end_idx - sentences_per_part
                if remaining_sentences < sentences_per_part // 2:
                    end_idx += remaining_sentences
            part_sentences = sentences[start_idx:end_idx]
            start_idx = end_idx
        
        parts.append(" ".join(part_sentences))
    
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
