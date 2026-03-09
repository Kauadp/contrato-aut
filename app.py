import tkinter as tk
from tkinter import scrolledtext, messagebox
import sys
import os
import threading
import queue
import io
from contextlib import redirect_stdout
from main import iniciar_processamento

import sys
import io

if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

class QueueWriter(io.StringIO):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def write(self, text):
        super().write(text)
        # Process each line
        lines = text.split('\n')
        for line in lines:
            if line.strip():
                self.queue.put(('log', line.strip()))
                # Add debugs based on content
                if "INICIANDO" in line:
                    self.queue.put(('info', "🎯 Iniciando geração de contratos..."))
                elif "Gerando contrato para:" in line:
                    self.queue.put(('info', f"📄 {line.strip()}"))
                elif "CNPJ inválido" in line:
                    self.queue.put(('warning', "⚠️ CNPJ inválido detectado!"))
                elif "CONTRATOS GERADOS" in line:
                    self.queue.put(('success', f"✅ {line.strip()}"))
                elif "ERRO" in line.upper():
                    self.queue.put(('error', f"❌ {line.strip()}"))

class ContractGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Automação de Geração de Contratos")
        self.root.geometry("800x600")

        # Título
        self.title_label = tk.Label(root, text="🚀 Automação de Geração de Contratos", font=("Arial", 16, "bold"))
        self.title_label.pack(pady=10)

        # Descrição
        self.desc_label = tk.Label(root, text="Clique no botão abaixo para iniciar a geração de contratos. Os logs serão exibidos em tempo real.")
        self.desc_label.pack(pady=5)

        # Botão
        self.generate_button = tk.Button(root, text="🔄 Gerar Contratos Agora", command=self.start_generation, font=("Arial", 12))
        self.generate_button.pack(pady=10)

        # Área de logs
        self.log_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=20, font=("Courier", 10))
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Configurar tags para cores
        self.log_text.tag_config('info', foreground='blue')
        self.log_text.tag_config('warning', foreground='orange')
        self.log_text.tag_config('error', foreground='red')
        self.log_text.tag_config('success', foreground='green')

        # Frame para resumo
        self.summary_frame = tk.Frame(root)
        self.summary_frame.pack(fill=tk.X, padx=10, pady=5)

        self.invalid_cnpjs_label = tk.Label(self.summary_frame, text="", fg="orange")
        self.not_found_cnpjs_label = tk.Label(self.summary_frame, text="", fg="blue")
        self.invalid_emails_label = tk.Label(self.summary_frame, text="", fg="orange")
        self.success_label = tk.Label(self.summary_frame, text="", fg="green")

        self.queue = queue.Queue()
        self.queue_writer = QueueWriter(self.queue)

    def start_generation(self):
        self.generate_button.config(state=tk.DISABLED)
        self.log_text.delete(1.0, tk.END)
        self.clear_summary()
        threading.Thread(target=self.run_generation, daemon=True).start()
        self.root.after(100, self.check_queue)

    def run_generation(self):
        try:
            with redirect_stdout(self.queue_writer):
                iniciar_processamento()
            logs = self.queue_writer.getvalue()
            self.queue.put(('done', (0, logs)))
        except Exception as e:
            self.queue.put(('error', f"Erro ao executar: {str(e)}"))
            self.queue.put(('done', (1, "")))

    def check_queue(self):
        try:
            while True:
                msg_type, msg = self.queue.get_nowait()
                if msg_type == 'log':
                    self.log_text.insert(tk.END, msg + '\n')
                    self.log_text.see(tk.END)
                elif msg_type == 'info':
                    self.log_text.insert(tk.END, msg + '\n', 'info')
                    self.log_text.see(tk.END)
                elif msg_type == 'warning':
                    self.log_text.insert(tk.END, msg + '\n', 'warning')
                    self.log_text.see(tk.END)
                elif msg_type == 'error':
                    self.log_text.insert(tk.END, msg + '\n', 'error')
                    self.log_text.see(tk.END)
                elif msg_type == 'success':
                    self.log_text.insert(tk.END, msg + '\n', 'success')
                    self.log_text.see(tk.END)
                elif msg_type == 'done':
                    returncode, logs = msg
                    self.handle_completion(returncode, logs)
                    return
        except queue.Empty:
            pass
        self.root.after(100, self.check_queue)

    def handle_completion(self, returncode, logs):
        self.generate_button.config(state=tk.NORMAL)
        if returncode == 0:
            messagebox.showinfo("Sucesso", "🎉 Geração de contratos concluída com sucesso!")
            self.parse_and_display_summary(logs)
        else:
            messagebox.showerror("Erro", "💥 Erro durante a execução. Verifique os logs acima.")

    def parse_and_display_summary(self, logs):
        lines = logs.split('\n')
        summary_start = None
        for i, line in enumerate(lines):
            if line.strip() == "==============================":
                summary_start = i
                break
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

            if invalid_cnpjs:
                self.invalid_cnpjs_label.config(text="CNPJs inválidos na planilha:\n" + '\n'.join(f"- {nome}" for nome in invalid_cnpjs))
                self.invalid_cnpjs_label.pack(anchor='w')
            if not_found_cnpjs:
                self.not_found_cnpjs_label.config(text="CNPJs não encontrados na Receita:\n" + '\n'.join(f"- {nome}" for nome in not_found_cnpjs))
                self.not_found_cnpjs_label.pack(anchor='w')
            if invalid_emails:
                self.invalid_emails_label.config(text="Emails inválidos na planilha:\n" + '\n'.join(f"- {nome}" for nome in invalid_emails))
                self.invalid_emails_label.pack(anchor='w')
            if success_msg:
                self.success_label.config(text=success_msg)
                self.success_label.pack(anchor='w')

    def clear_summary(self):
        self.invalid_cnpjs_label.pack_forget()
        self.not_found_cnpjs_label.pack_forget()
        self.invalid_emails_label.pack_forget()
        self.success_label.pack_forget()

if __name__ == "__main__":
    root = tk.Tk()
    app = ContractGeneratorApp(root)
    root.mainloop()