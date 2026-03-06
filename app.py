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
        
        # Parse and display the summary nicely
        lines = logs.split('\n')
        summary_start = None
        for i, line in enumerate(lines):
            if line.strip() == "==============================":
                summary_start = i
        if summary_start is not None:
            summary_lines = lines[summary_start:]
            invalid_cnpjs = []
            not_found_cnpjs = []
            invalid_emails = []
            i = 1
            if i < len(summary_lines) and "CNPJs inválidos na planilha:" in summary_lines[i]:
                i += 1
                while i < len(summary_lines) and summary_lines[i].startswith('- '):
                    invalid_cnpjs.append(summary_lines[i][2:])
                    i += 1
            if i < len(summary_lines) and "CNPJs não encontrados na Receita:" in summary_lines[i]:
                i += 1
                while i < len(summary_lines) and summary_lines[i].startswith('- '):
                    not_found_cnpjs.append(summary_lines[i][2:])
                    i += 1
            if i < len(summary_lines) and summary_lines[i].strip() == "==============================":
                i += 1
                if i < len(summary_lines) and "Emails inválidos na planilha:" in summary_lines[i]:
                    i += 1
                    while i < len(summary_lines) and summary_lines[i].startswith('- '):
                        invalid_emails.append(summary_lines[i][2:])
                        i += 1
            success_lines = summary_lines[i:]
            success_msg = '\n'.join(success_lines).strip()
            
            st.info("📊 Resumo da Geração de Contratos")
            if invalid_cnpjs:
                st.warning("CNPJs inválidos na planilha:")
                for nome in invalid_cnpjs:
                    st.write(f"- {nome}")
            if not_found_cnpjs:
                st.info("CNPJs não encontrados na Receita:")
                for nome in not_found_cnpjs:
                    st.write(f"- {nome}")
            if invalid_emails:
                st.warning("Emails inválidos na planilha:")
                for nome in invalid_emails:
                    st.write(f"- {nome}")
            if success_msg:
                st.success(success_msg)
    else:
        st.error("💥 Erro durante a execução. Verifique os logs acima.")