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
streamlit run app.py
```
Abre la interfaz en el navegador (por defecto en `http://localhost:8501`).

### Ejecución de pruebas
```bash
python casos_prueba.py
```
(Ejecuta los 12 casos de prueba ficticios para verificar la lógica de decisión).

---

## 📁 Estructura del Proyecto

- `app.py`: Interfaz interactiva Streamlit (recorrido de pantallas: Propuesta $\rightarrow$ Diagnóstico $\rightarrow$ Perfil $\rightarrow$ Sugerencia $\rightarrow$ Decisión, más mapa del viaje del usuario y verificación).
- `logica.py`: Constantes, arreglos, funciones y reglas de decisión (sin dependencias de Streamlit).
- `casos_prueba.py`: 12 casos de prueba ficticios y verificación automática.
- `.streamlit/config.toml`: Configuración del tema visual de la interfaz.
- `requirements.txt`: Dependencias del proyecto (`streamlit`).
- `LEEME.txt`: Resumen de especificaciones del proyecto.
