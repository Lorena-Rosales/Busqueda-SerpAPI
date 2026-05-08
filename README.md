# Documentación de la Aplicación de Búsqueda Académica
Esta documentación describe el funcionamiento, configuración y uso de la aplicación de búsqueda de artículos académicos desarrollada en Python con una interfaz gráfica (GUI) en Tkinter.

## 1. Descripción General
La aplicación permite buscar artículos académicos y documentos científicos utilizando la API de Google Scholar proporcionada por el servicio de SerpApi. Integra funcionalidades para filtrar resultados, exportar metadatos a un archivo CSV y descargar automáticamente los archivos PDF disponibles en los resultados de búsqueda.

##2. Requisitos y Configuración

### 2.1 Dependencias del Código
`tkinter` (Para la interfaz gráfica de usuario, incluida por defecto en Python)
`google-search-results` (El cliente oficial de SerpApi para Python)
`requests` (Para gestionar la descarga de los archivos PDF)

### 2.2 El Servicio: SerpApi (Google Scholar API)
El código utiliza SerpApi. Dado que hacer peticiones directas y masivas a Google Scholar suele resultar en bloqueos, SerpApi actúa como un intermediario que resuelve las búsquedas y devuelve los datos estructurados en formato JSON para ser procesados por la aplicación.

### 2.3 Guía: Creación de cuenta en SerpApi y obtención de API Key
Para que la aplicación funcione, es necesario insertar una "API Key" válida en la interfaz. A continuación, se detallan los pasos para obtenerla:
Dirigirse a la página web oficial: https://serpapi.com/.

Hacer clic en el botón "Register" o "Sign Up".
Crear una cuenta ingresando un correo electrónico y contraseña, o utilizando integraciones (Sign in with Google o GitHub).
Una vez completado el registro y verificado el correo, se dirigirá al Dashboard (Panel de Control Principal).

En la página de inicio del Dashboard, se encontrará un recuadro titulado "Your Private API Key".
Copiar esa clave y pegarla en el campo "API Key" de la aplicación.
Nota de facturación: SerpApi ofrece un plan gratuito para desarrolladores que incluye 100 búsquedas al mes. Si se requiere extraer más documentos, se debe adquirir un plan de pago.

## 3. Manual de Usuario (Interfaz Gráfica)
La interfaz de la aplicación está dividida en varias secciones que se deben configurar antes de iniciar la búsqueda:
| Campo / Input | Descripción y Uso |
|---------------|------------------|
| **API Key** | El campo obligatorio donde se pega la clave privada obtenida en SerpApi. |
| **Query** | El término, concepto o frase de búsqueda. Funciona igual que la barra de búsqueda de Google Scholar. |
| **Citas ≥** | Filtro mínimo de impacto. La aplicación solo descargará y guardará en el CSV aquellos artículos que tengan un número de citas igual o superior al establecido. |
| **Páginas** | Establece cuántas páginas de resultados de SerpApi explorará el script. |
| **Desde / Hasta** | Filtros temporales. Define el rango de años para restringir la fecha de publicación de los artículos recuperados. |
| **Objetivo** | Cantidad límite de artículos a recopilar. Si la aplicación alcanza este número de artículos que cumplan los filtros, la búsqueda se detiene. |
## 4. Arquitectura y Lógica Interna del Código
Ejecución Asíncrona (Multihilo): Al presionar el botón de búsqueda, la aplicación ejecuta la función `ejecutar_busqueda()` la cual inicializa un hilo secundario (`threading.Thread(target=buscar, daemon=True)`). Esto asegura que la interfaz gráfica no se "congele" durante la descarga de archivos.
Gestión de la UI: Las actualizaciones de estado se envían al hilo principal de Tkinter utilizando el método `root.after(0, ...)`.
Procesamiento y Normalización: El sistema crea archivos CSV para volcar los metadatos de la búsqueda. Además, limpia los títulos de los artículos utilizando expresiones regulares (`re.sub`) para usarlos como nombres de archivo válidos al descargar el PDF.
Manejo de Errores: Si no se introduce la Query o la API Key, el sistema bloquea la búsqueda y alerta mediante `messagebox.showinfo`.
