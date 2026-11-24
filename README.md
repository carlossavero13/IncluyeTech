# IncluyeTech 🦻
**Prototipo: Sugerencia de apoyos de comunicación (discapacidad auditiva, colegios públicos de EBR)**  
*Curso: Computación en la Sociedad*

Sistema interactivo de sugerencia y toma de decisiones sobre apoyos de comunicación para estudiantes con discapacidad auditiva en colegios públicos de Educación Básica Regular (EBR).

> **Aviso ético y de alcance:** El sistema **SUGIERE**; la decisión final corresponde al docente y al especialista del SAE. No diagnostica, no evalúa el rendimiento, no graba audio ni almacena datos personales.

---

## 🚀 Requisitos y Ejecución Local

### Requisitos
- Python 3.10 o superior

### Instalación
```bash
pip install -r requirements.txt
```

### Ejecución de la aplicación
```bash
streamlit run streamlit_app.py
```
Abre la interfaz en el navegador (por defecto en `http://localhost:8501`).

### Ejecución de pruebas
```bash
python casos_prueba.py
```
(Ejecuta los 12 casos de prueba ficticios para verificar la lógica de decisión).

---

## 🌐 Despliegue en Vercel (WebAssembly / stlite)

Este proyecto está configurado para desplegarse de manera 100% estática en **Vercel** usando **[stlite](https://github.com/whitphx/stlite)**:
- Ejecuta Streamlit y la lógica de Python directamente en el navegador del usuario a través de WebAssembly (Pyodide).
- No requiere servidores persistentes ni funciones serverless.
- Basta con conectar el repositorio a **Vercel** y se desplegará de forma automática e inmediata a través de `index.html`.

---

## 📁 Estructura del Proyecto

- `index.html`: Entrypoint estático para despliegue en Vercel con `stlite` (WebAssembly).
- `vercel.json` y `.vercelignore`: Configuración para despliegue estático en Vercel.
- `streamlit_app.py`: Interfaz interactiva Streamlit (recorrido de pantallas: Propuesta $\rightarrow$ Diagnóstico $\rightarrow$ Perfil $\rightarrow$ Sugerencia $\rightarrow$ Decisión, más mapa del viaje del usuario y verificación).
- `logica.py`: Constantes, arreglos, funciones y reglas de decisión (sin dependencias de Streamlit).
- `casos_prueba.py`: 12 casos de prueba ficticios y verificación automática.
- `.streamlit/config.toml`: Configuración del tema visual de la interfaz.
- `requirements.txt`: Dependencias del proyecto (`streamlit`) para ejecución local o en Streamlit Community Cloud.
- `LEEME.txt`: Resumen de especificaciones del proyecto.
