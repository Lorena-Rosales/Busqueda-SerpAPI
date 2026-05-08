import tkinter as tk
from tkinter import ttk, messagebox
from serpapi.google_search import GoogleSearch
import csv
from datetime import datetime
import re
import threading
import os
import requests


# ---------- FUNCIONES UI SEGURAS ----------

def ui_set(text):
    root.after(0, lambda: progreso.set(text))


def ui_message(title, text):
    root.after(0, lambda: messagebox.showinfo(title, text))


# ---------- EJECUCIÓN ----------

def ejecutar_busqueda():
    hilo = threading.Thread(target=buscar, daemon=True)
    hilo.start()


def buscar():
    try:
        API_KEY = entry_api.get().strip()
        query = entry_query.get().strip()

        if not API_KEY or not query:
            ui_message("Error", "API Key y Query son obligatorios")
            return

        CITAS_MIN = int(entry_citas.get())
        MAX_PAGINAS = int(entry_paginas.get())
        year_ini = int(entry_year_ini.get())
        year_fin = int(entry_year_fin.get())
        OBJETIVO = int(entry_objetivo.get())

        ui_set("Buscando artículos...")

        RESULTADOS_POR_PAGINA = 20
        todos = []
        contador = 0
        pagina = 0

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        carpeta_pdfs = f"PDFs_{timestamp}"
        os.makedirs(carpeta_pdfs, exist_ok=True)


        while contador < OBJETIVO and pagina < MAX_PAGINAS:

            start = pagina * RESULTADOS_POR_PAGINA

            params = {
                "engine": "google_scholar",
                "q": query,
                "api_key": API_KEY,
                "num": RESULTADOS_POR_PAGINA,
                "start": start,
                "as_ylo": year_ini,
                "as_yhi": year_fin
            }

            search = GoogleSearch(params)
            results = search.get_dict()

            resultados = results.get("organic_results", [])
            if not resultados:
                break

            for r in resultados:

                citas = r.get("inline_links", {}).get("cited_by", {}).get("total", 0)
                if citas < CITAS_MIN:
                    continue

                titulo = r.get("title", "")
                link = r.get("link", "")
                snippet = r.get("snippet", "")

                year = ""
                pub_info = r.get("publication_info", {})
                if "year" in pub_info:
                    year = pub_info["year"]
                elif "summary" in pub_info:
                    match = re.search(r"(20\d{2}|19\d{2})", pub_info["summary"])
                    if match:
                        year = match.group(0)

                pdf_link = ""
                if "resources" in r:
                    for res in r["resources"]:
                        if res.get("file_format") == "PDF":
                            pdf_link = res.get("link", "")
                            break

                leer_completo = "TRUE" if pdf_link else "FALSE"

                nombre_pdf = ""
                if pdf_link:
                    nombre_limpio = limpiar_nombre_archivo(titulo)
                    nombre_pdf = f"{contador+1:03d}_{nombre_limpio}.pdf"
                    ruta_pdf = os.path.join(carpeta_pdfs, nombre_pdf)

                    if descargar_pdf(pdf_link, ruta_pdf):
                        nombre_pdf = nombre_pdf
                    else:
                        nombre_pdf = ""


                leer_completo = "TRUE" if pdf_link else "FALSE"

                plataforma = "Google Scholar"
                if "arxiv.org" in link:
                    plataforma = "arXiv"
                elif "ieee.org" in link:
                    plataforma = "IEEE"
                elif "springer.com" in link:
                    plataforma = "Springer"
                elif "acm.org" in link:
                    plataforma = "ACM"

                todos.append({
                    "Título": titulo,
                    "Plataforma": plataforma,
                    "Fecha de publicación": year if year else "",
                    "Número de citas": citas,
                    "Leer completo": leer_completo,
                    "PDF": nombre_pdf,
                    "Cadena de búsqueda": query,
                    "Link": link,
                    "Dudas": ""
                })


                contador += 1
                ui_set(f"Artículos: {contador}/{OBJETIVO}")

                if contador >= OBJETIVO:
                    break

            pagina += 1

        nombre_archivo = f"resultados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        with open(nombre_archivo, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "Título",
                    "Plataforma",
                    "Fecha de publicación",
                    "Número de citas",
                    "Leer completo",
                    "Cadena de búsqueda",
                    "Link",
                    "Dudas",
                    "PDF"
                ]
            )
            writer.writeheader()
            writer.writerows(todos)

        ui_message("Completado", f"CSV generado:\n{nombre_archivo}\n\nArtículos: {len(todos)}")

        os.startfile(nombre_archivo)

    except Exception as e:
        ui_message("Error", str(e))


def limpiar_nombre_archivo(texto):
    texto = re.sub(r'[\\/*?:"<>|]', "", texto)
    texto = texto.replace("\n", " ").strip()
    texto = re.sub(r"\s+", " ", texto)
    return texto[:120]

def descargar_pdf(url, ruta):
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        with open(ruta, "wb") as f:
            f.write(r.content)
        return True
    except:
        return False


# ---------- INTERFAZ ----------

root = tk.Tk()
root.title("Buscador de citas")
root.geometry("820x460")
root.resizable(False, False)

style = ttk.Style(root)
style.theme_use("clam")

main = ttk.Frame(root, padding=20)
main.pack(fill="both", expand=True)

titulo = ttk.Label(
    main,
    text="Buscador de citas",
    font=("Segoe UI", 16, "bold")
)
titulo.pack(pady=(0, 15))

# -------- Búsqueda --------

frame_busqueda = ttk.LabelFrame(main, text="Búsqueda", padding=15)
frame_busqueda.pack(fill="x")

ttk.Label(frame_busqueda, text="API Key:").grid(row=0, column=0, sticky="w")
entry_api = ttk.Entry(frame_busqueda)
entry_api.grid(row=0, column=1, sticky="ew", padx=8, pady=6)

ttk.Label(frame_busqueda, text="Query:").grid(row=1, column=0, sticky="w")
entry_query = ttk.Entry(frame_busqueda)
entry_query.grid(row=1, column=1, sticky="ew", padx=8, pady=6)

frame_busqueda.columnconfigure(1, weight=1)

# -------- Filtros --------

frame_filtros = ttk.LabelFrame(main, text="Filtros", padding=15)
frame_filtros.pack(fill="x", pady=10)

ttk.Label(frame_filtros, text="Citas ≥").grid(row=0, column=0)
entry_citas = ttk.Entry(frame_filtros, width=8)
entry_citas.insert(0, "50")
entry_citas.grid(row=0, column=1, padx=6)

ttk.Label(frame_filtros, text="Páginas").grid(row=0, column=2)
entry_paginas = ttk.Entry(frame_filtros, width=8)
entry_paginas.insert(0, "1")
entry_paginas.grid(row=0, column=3, padx=6)

ttk.Label(frame_filtros, text="Desde").grid(row=1, column=0, pady=6)
entry_year_ini = ttk.Entry(frame_filtros, width=8)
entry_year_ini.insert(0, "2020")
entry_year_ini.grid(row=1, column=1)

ttk.Label(frame_filtros, text="Hasta").grid(row=1, column=2)
entry_year_fin = ttk.Entry(frame_filtros, width=8)
entry_year_fin.insert(0, "2025")
entry_year_fin.grid(row=1, column=3)

ttk.Label(frame_filtros, text="Objetivo artículos").grid(row=2, column=0, pady=6)
entry_objetivo = ttk.Entry(frame_filtros, width=8)
entry_objetivo.insert(0, "50")
entry_objetivo.grid(row=2, column=1)

# -------- Botón --------

btn = ttk.Button(
    main,
    text="Buscar y generar CSV",
    command=ejecutar_busqueda
)
btn.pack(pady=10, ipadx=10, ipady=6)

# -------- Estado --------

progreso = tk.StringVar(value="Listo")
status = ttk.Label(main, textvariable=progreso, foreground="#0a5")
status.pack()

root.mainloop()
