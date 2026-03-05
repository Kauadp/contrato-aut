import streamlit as st
import subprocess
import sys
import os

st.title("🚀 Automação de Geração de Contratos")

st.write("Clique no botão abaixo para iniciar a geração de contratos. Os logs serão exibidos em tempo real.")

if st.button("🔄 Gerar Contratos Agora"):
    log_area = st.empty()
    logs = ""
    
    process = subprocess.Popen(
        [sys.executable, "main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=os.getcwd()
    )
    
    for line in process.stdout:
        logs += line
        log_area.write(logs)
        
        # Adicionar debugs bonitinhos baseados no conteúdo
        if "INICIANDO" in line:
            st.info("🎯 Iniciando geração de contratos...")
        elif "Gerando contrato para:" in line:
            st.info(f"📄 {line.strip()}")
        elif "CNPJ inválido" in line:
            st.warning("⚠️ CNPJ inválido detectado!")
        elif "CONTRATOS GERADOS" in line:
            st.success(f"✅ {line.strip()}")
        elif "ERRO" in line.upper():
            st.error(f"❌ {line.strip()}")
    
    process.wait()
    
    if process.returncode == 0:
        st.success("🎉 Geração de contratos concluída com sucesso!")
    else:
        st.error("💥 Erro durante a execução. Verifique os logs acima.")