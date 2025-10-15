#!/usr/bin/env python3
"""
Script semplificato per compilare i file .tex in .pdf
"""

import os
import shutil
import subprocess
import sys

def cleanup_source_pdf():
    """
    Rimuove tutti i file PDF dalla cartella src e sottocartelle
    """
    print("\n=== CLEANING SOURCE DIRECTORY ===")
    pdf_files_removed = 0
    
    for root, dirs, files in os.walk("src"):
        for file in files:
            if file.endswith(".pdf"):
                pdf_path = os.path.join(root, file)
                try:
                    os.remove(pdf_path)
                    print(f"✓ Removed PDF from source: {pdf_path}")
                    pdf_files_removed += 1
                except Exception as e:
                    print(f"✗ Error removing {pdf_path}: {e}")
    
    print(f"Removed {pdf_files_removed} PDF files from source directory")

def compile_tex_to_pdf():
    print("=== STARTING COMPILATION ===")
    print("Current working directory:", os.getcwd())
    print("Directory contents:", os.listdir('.'))
    
    # Crea la cartella output se non esiste
    if not os.path.exists("output"):
        os.makedirs("output")
        print("Created output directory")
    
    # Cerca tutti i file .tex nella cartella src e sottocartelle
    tex_files = []
    if os.path.exists("src"):
        print("Found src directory")
        for root, dirs, files in os.walk("src"):
            print(f"Scanning: {root}")
            for file in files:
                if file.endswith(".tex"):
                    tex_path = os.path.join(root, file)
                    tex_files.append(tex_path)
                    print(f"Found .tex file: {tex_path}")
    else:
        print("ERROR: 'src' directory not found!")
        return
    
    if not tex_files:
        print("No .tex files found in src directory!")
        return
    
    print(f"Found {len(tex_files)} .tex files to compile")
    
    # Compila ogni file .tex
    success_count = 0
    for tex_file in tex_files:
        try:
            print(f"\n=== COMPILING: {tex_file} ===")
            
            # Directory del file .tex
            tex_dir = os.path.dirname(tex_file)
            tex_name = os.path.basename(tex_file)
            
            print(f"Changing to directory: {tex_dir}")
            print(f"Compiling file: {tex_name}")
            
            # Compila con latexmk
            result = subprocess.run(
                ["latexmk", "-pdf", "-interaction=nonstopmode", tex_name],
                cwd=tex_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            print(f"Compilation return code: {result.returncode}")
            if result.stdout:
                print("STDOUT:", result.stdout[-1000:])
            if result.stderr:
                print("STDERR:", result.stderr[-1000:])
            
            if result.returncode == 0:
                # Trova il file PDF generato
                pdf_name = os.path.splitext(tex_name)[0] + ".pdf"
                pdf_path = os.path.join(tex_dir, pdf_name)
                
                print(f"Looking for PDF at: {pdf_path}")
                if os.path.exists(pdf_path):
                    print(f"PDF successfully created: {pdf_path}")
                    
                    # Crea struttura cartelle corrispondente in output
                    relative_path = os.path.relpath(tex_dir, "src")
                    output_dir = os.path.join("output", relative_path)
                    os.makedirs(output_dir, exist_ok=True)
                    
                    # Copia il PDF nella cartella output
                    output_pdf_path = os.path.join(output_dir, pdf_name)
                    shutil.copy2(pdf_path, output_pdf_path)
                    
                    print(f"✓ PDF copied to: {output_pdf_path}")
                    success_count += 1
                else:
                    print(f"✗ PDF not found at: {pdf_path}")
                    print(f"Files in {tex_dir}:")
                    for f in os.listdir(tex_dir):
                        print(f"  - {f}")
            else:
                print(f"✗ Compilation failed for: {tex_file}")
                
        except Exception as e:
            print(f"✗ Error compiling {tex_file}: {e}")
    
    print(f"\n=== COMPILATION SUMMARY ===")
    print(f"Successfully compiled: {success_count}/{len(tex_files)} files")
    
    # PULISCI SOLO DOPO AVER COPIATO TUTTI I PDF
    cleanup_source_pdf()

if __name__ == "__main__":
    compile_tex_to_pdf()