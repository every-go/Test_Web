#!/usr/bin/env python3
"""
Script semplificato per compilare i file .tex in .pdf
Input: file .tex nella cartella 'src'
Output: file .pdf nella cartella 'output'
"""

import os
import shutil
import subprocess

def compile_tex_to_pdf():
    # Crea la cartella output se non esiste
    if not os.path.exists("output"):
        os.makedirs("output")
    
    # Cerca tutti i file .tex nella cartella src e sottocartelle
    tex_files = []
    for root, dirs, files in os.walk("src"):
        for file in files:
            if file.endswith(".tex"):
                tex_files.append(os.path.join(root, file))
    
    if not tex_files:
        print("Nessun file .tex trovato nella cartella 'src'")
        return
    
    print(f"Trovati {len(tex_files)} file .tex da compilare:")
    
    # Compila ogni file .tex
    success_count = 0
    for tex_file in tex_files:
        try:
            print(f"Compilando: {tex_file}")
            
            # Directory del file .tex
            tex_dir = os.path.dirname(tex_file)
            tex_name = os.path.basename(tex_file)
            
            # Compila con latexmk
            result = subprocess.run(
                ["latexmk", "-pdf", "-interaction=nonstopmode", tex_name],
                cwd=tex_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Trova il file PDF generato
                pdf_name = os.path.splitext(tex_name)[0] + ".pdf"
                pdf_path = os.path.join(tex_dir, pdf_name)
                
                if os.path.exists(pdf_path):
                    # Crea struttura cartelle corrispondente in output
                    relative_path = os.path.relpath(tex_dir, "src")
                    output_dir = os.path.join("output", relative_path)
                    os.makedirs(output_dir, exist_ok=True)
                    
                    # Copia il PDF nella cartella output
                    output_pdf_path = os.path.join(output_dir, pdf_name)
                    shutil.copy2(pdf_path, output_pdf_path)
                    
                    # Pulisci i file temporanei
                    subprocess.run(["latexmk", "-c"], cwd=tex_dir, capture_output=True)
                    
                    print(f"✓ Creato: {output_pdf_path}")
                    success_count += 1
                else:
                    print(f"✗ PDF non generato per: {tex_file}")
            else:
                print(f"✗ Errore compilazione: {tex_file}")
                print(f"  Log: {result.stderr}")
                
        except Exception as e:
            print(f"✗ Errore durante la compilazione di {tex_file}: {e}")
    
    print(f"\nCompilazione completata: {success_count}/{len(tex_files)} file compilati con successo")

if __name__ == "__main__":
    compile_tex_to_pdf()
