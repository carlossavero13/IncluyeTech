"""
app.py — Interfaz Streamlit del prototipo, organizada como un recorrido de pantallas.

Ejecutar con:  streamlit run app.py
La interfaz solo recoge datos y muestra resultados; toda la lógica está en logica.py.

Recorrido del usuario (docente o especialista del SAE):
    1 Propuesta -> 2 Diagnóstico del colegio -> 3 Perfil declarado -> 4 Sugerencia -> 5 Decisión
Pantallas de apoyo: "Viaje del usuario" (mapa del proceso) y "Verificación" (casos de prueba).
"""

import streamlit as st

from logica import (
    Entrada, sugerir_apoyos, clasificar_colegio, resumen_en_texto,
    MODALIDADES, CONEXIONES, CONTENIDOS, TIPOS_COLEGIO, RESPONSABLES_TIPO,
    SALVAGUARDAS, FASES, DECISION_FINAL,
    PRIORIDAD_PRINCIPAL, PRIORIDAD_COMPLEMENTARIA,
    CONEXION_ESTABLE, CONT_EN_VIVO, MOD_NO_DECLARADA,
    TIPO_A, TIPO_B, TIPO_C, TIPO_D,
)
from casos_prueba import ejecutar_casos

st.set_page_config(page_title="Apoyos de comunicación", page_icon="🦻", layout="wide")

# ---------------------------------------------------------------------------
# CONSTANTES DE INTERFAZ
# ---------------------------------------------------------------------------
# Pantallas del recorrido principal (arreglo) y pantallas de apoyo.
RECORRIDO = ["Propuesta", "Diagnóstico", "Perfil", "Sugerencia", "Decisión"]
APOYO = ["Viaje del usuario", "Verificación"]
PANTALLAS = RECORRIDO + APOYO

OPCIONES_DECISION = [
    "Pendiente",
    "Se adopta la sugerencia",
    "Se adopta con modificaciones",
    "Se descarta la sugerencia",
]

# Color por tipo de colegio (progresión de menor a mayor restricción)
COLOR_TIPO = {TIPO_A: "#0f766e", TIPO_B: "#3b82a0", TIPO_C: "#b7791f", TIPO_D: "#b4413c"}
BREVE_TIPO = {
    TIPO_A: "Internet estable, electricidad y equipos",
    TIPO_B: "Hay Internet, pero se cae o es lento",
    TIPO_C: "Sin Internet, con electricidad y equipo",
    TIPO_D: "Sin electricidad confiable o sin equipo",
}
COLOR_PRIORIDAD = {PRIORIDAD_PRINCIPAL: "#0f766e", PRIORIDAD_COMPLEMENTARIA: "#3b82a0"}

# Cifras del análisis (informe: MINEDU, 2026; MINEDU, 2021b)
CIFRAS = [
    ("27,3 %", "de los locales públicos tiene Internet"),
    ("18,9 %", "en el área rural"),
    ("10 %", "de los locales no tiene electricidad"),
    ("57", "intérpretes de LSP en 2021, para todo el sector"),
]

# Mapa del viaje del usuario: fase (Tabla 5) -> qué hace el usuario, pantalla, alcance del sistema
VIAJE = [
    ("Diagnóstico de necesidades", "Dirección, docentes y SAE",
     "Describen las condiciones del colegio y la forma de comunicación que declara el estudiante.",
     "Pantallas 2 y 3", "Sí: recoge los datos"),
    ("Selección de herramientas", "Equipo técnico, SAE y UGEL",
     "Revisan los apoyos sugeridos, sus requisitos y sus alertas.",
     "Pantalla 4", "Sí: sugiere y explica"),
    ("Pruebas de funcionamiento", "Desarrolladores, docentes y SAE",
     "Prueban la herramienta en el aula real: precisión, ruido, tiempo de respuesta.",
     "Fuera del sistema", "No: lo hacen las personas"),
    ("Implementación progresiva", "Dirección, SAE y UGEL",
     "Deciden, capacitan a los docentes y establecen la supervisión humana.",
     "Pantalla 5", "Parcial: registra la decisión"),
    ("Seguimiento y mejora", "Docentes, SAE, estudiantes",
     "Recogen observaciones, revisan incidencias y ajustan el apoyo.",
     "Fuera del sistema", "No: lo hacen las personas"),
]

CSS = """
<style>
.block-container {max-width: 1080px; padding-top: 4rem;}
h1, h2, h3 {letter-spacing: -0.01em;}
.stepper {display:flex; gap:6px; margin: 0 0 1.4rem 0; flex-wrap:wrap;}
.step {flex:1; min-width:120px; padding:8px 10px; border-radius:8px; background:#f1f5f4;
       color:#5b6b7a; font-size:0.85rem; border-bottom:3px solid #d6dfdd;}
.step b {display:block; font-size:0.72rem; letter-spacing:.06em; text-transform:uppercase;}
.step.on {background:#e2f1ee; color:#0b4f49; border-bottom-color:#0f766e;}
.step.done {color:#0b4f49; border-bottom-color:#7fb8b1;}
.hero {padding: 1.6rem 1.8rem; border-radius:14px; background:#0f3d3a; color:#f3faf9; margin-bottom:1.2rem;}
.hero h1 {color:#ffffff; margin:0 0 .4rem 0; font-size:2rem;}
.hero p {margin:0; font-size:1.05rem; color:#cfe6e3;}
.cifra {padding:12px 14px; border-radius:10px; background:#f1f5f4; min-height:118px;}
.cifra b {font-size:1.7rem; color:#0f766e; display:block; line-height:1.1;}
.cifra span {font-size:.85rem; color:#44556a;}
.tipo {padding:14px 16px; border-radius:10px; background:#fff; border:1px solid #dfe6e4;
       border-top:5px solid var(--c); min-height:96px;}
.tipo.sel {background:#f6fbfa; box-shadow:0 0 0 2px var(--c);}
.tipo b {font-size:1.05rem; color:var(--c);}
.tipo p {margin:.3rem 0 0 0; font-size:.88rem; color:#44556a;}
.apoyo {padding:14px 16px; border-radius:10px; background:#fff; border:1px solid #dfe6e4;
        border-left:6px solid var(--c); margin-bottom:10px;}
.apoyo .tag {font-size:.72rem; text-transform:uppercase; letter-spacing:.06em; color:var(--c); font-weight:700;}
.apoyo h4 {margin:.1rem 0 .3rem 0; font-size:1.02rem;}
.apoyo p {margin:.15rem 0; font-size:.9rem; color:#33445a;}
.aviso {padding:10px 14px; border-radius:8px; background:#fff7e6; border:1px solid #f0d9a4;
        font-size:.9rem; margin-bottom:8px;}
.decide {padding:12px 16px; border-radius:10px; background:#eef4ff; border:1px solid #c9d8f5;
         color:#1f3a6b; font-size:.95rem; margin-bottom:1rem;}
.fila {display:grid; grid-template-columns: 1.1fr 1.2fr 2fr .9fr 1.1fr; gap:10px; padding:10px 12px;
       border-bottom:1px solid #e3e9e7; font-size:.86rem; align-items:start;}
.fila.cab {font-weight:700; color:#0b4f49; background:#f1f5f4; border-radius:8px 8px 0 0;
           font-size:.75rem; text-transform:uppercase; letter-spacing:.05em;}
.si {color:#0f766e; font-weight:600;} .no {color:#b4413c; font-weight:600;} .par {color:#b7791f; font-weight:600;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# ESTADO: valores del formulario que persisten entre pantallas
# ---------------------------------------------------------------------------
def iniciar_estado():
    if "pantalla" not in st.session_state:
        st.session_state["pantalla"] = PANTALLAS[0]
    if "datos" not in st.session_state:
        st.session_state["datos"] = {
            "modalidad": MOD_NO_DECLARADA, "conexion": CONEXION_ESTABLE,
            "electricidad": True, "dispositivo": True, "apto": False,
            "humano": False, "consentimiento": False, "ruidosa": False,
            "contenido": CONT_EN_VIVO,
        }


def ir_a(nombre: str):
    """Callback de navegación."""
    st.session_state["pantalla"] = nombre


def construir_entrada() -> Entrada:
    d = st.session_state["datos"]
    return Entrada(
        modalidad=d["modalidad"], conexion=d["conexion"],
        electricidad_confiable=d["electricidad"], hay_dispositivo=d["dispositivo"],
        dispositivo_apto_local=d["apto"], apoyo_humano_lsp_disponible=d["humano"],
        consentimiento_familia=d["consentimiento"], aula_ruidosa=d["ruidosa"],
        contenido=d["contenido"],
    )


def selector(etiqueta, clave, opciones: dict, ayuda=None):
    """Selectbox que lee y escribe en st.session_state['datos']."""
    llaves = list(opciones.keys())
    actual = st.session_state["datos"][clave]
    elegido = st.selectbox(etiqueta, llaves, index=llaves.index(actual),
                           format_func=lambda k: opciones[k], help=ayuda, key=f"w_{clave}")
    st.session_state["datos"][clave] = elegido


def casilla(etiqueta, clave, ayuda=None):
    """Checkbox que lee y escribe en st.session_state['datos']."""
    valor = st.checkbox(etiqueta, value=st.session_state["datos"][clave], help=ayuda, key=f"w_{clave}")
    st.session_state["datos"][clave] = valor


def barra_pasos():
    """Dibuja el indicador de pasos del recorrido principal."""
    actual = st.session_state["pantalla"]
    idx = RECORRIDO.index(actual) if actual in RECORRIDO else -1
    piezas = []
    for i, nombre in enumerate(RECORRIDO):
        clase = "on" if i == idx else ("done" if 0 <= idx and i < idx else "")
        piezas.append(f'<div class="step {clase}"><b>Paso {i + 1}</b>{nombre}</div>')
    st.markdown(f'<div class="stepper">{"".join(piezas)}</div>', unsafe_allow_html=True)


def navegacion(anterior=None, siguiente=None, texto_sig="Continuar"):
    col_a, _, col_b = st.columns([1, 3, 1])
    if anterior:
        col_a.button("← Volver", on_click=ir_a, args=(anterior,), key=f"ant_{anterior}")
    if siguiente:
        col_b.button(f"{texto_sig} →", on_click=ir_a, args=(siguiente,), type="primary", key=f"sig_{siguiente}")


def tarjeta_tipo(tipo: str, seleccionado=False) -> str:
    clase = "tipo sel" if seleccionado else "tipo"
    return (f'<div class="{clase}" style="--c:{COLOR_TIPO[tipo]}"><b>Tipo {tipo}</b>'
            f'<p>{BREVE_TIPO[tipo]}</p></div>')


# ---------------------------------------------------------------------------
# PANTALLAS
# ---------------------------------------------------------------------------
def pantalla_propuesta():
    st.markdown(
        '<div class="hero"><h1>Apoyos de comunicación para estudiantes con discapacidad auditiva</h1>'
        '<p>Un prototipo que ayuda al docente y al especialista del SAE a considerar qué apoyo digital '
        'o humano es viable en su colegio público. Sugiere; no decide.</p></div>',
        unsafe_allow_html=True)

    st.markdown("#### El problema: una misma solución no sirve para todos los colegios")
    cols = st.columns(len(CIFRAS))
    for col, (cifra, texto) in zip(cols, CIFRAS):
        col.markdown(f'<div class="cifra"><b>{cifra}</b><span>{texto}</span></div>', unsafe_allow_html=True)
    st.caption("Fuentes: Censo Educativo 2025 (MINEDU, 2026); MINEDU (2021b). Datos de conectividad autodeclarados.")

    st.markdown("#### La propuesta: cuatro tipos de colegio, cuatro caminos")
    cols = st.columns(4)
    for col, tipo in zip(cols, TIPOS_COLEGIO):
        col.markdown(tarjeta_tipo(tipo), unsafe_allow_html=True)
    st.caption("Clasificación propuesta por el equipo; no es una clasificación oficial del MINEDU.")

    st.markdown(f'<div class="decide"><b>Quién decide:</b> {DECISION_FINAL}</div>', unsafe_allow_html=True)
    st.write("**El prototipo no pide nombres ni datos personales, no graba audio y no diagnostica.**")
    navegacion(siguiente="Diagnóstico", texto_sig="Comenzar el recorrido")


def pantalla_diagnostico():
    st.header("Diagnóstico del colegio")
    st.write("Indique las condiciones actuales del local. No se necesita identificar el colegio.")
    col1, col2 = st.columns(2)
    with col1:
        selector("Conectividad del local", "conexion", CONEXIONES)
        casilla("Hay electricidad confiable en el local", "electricidad")
        casilla("Hay un dispositivo disponible (del docente o del colegio)", "dispositivo")
    with col2:
        casilla("El dispositivo puede procesar voz localmente (equipo compatible)", "apto",
                "Si no está seguro, déjelo sin marcar: es la opción prudente.")
        casilla("El aula suele ser ruidosa", "ruidosa")
        selector("Contenido que se necesita hacer accesible", "contenido", CONTENIDOS)

    entrada = construir_entrada()
    tipo = clasificar_colegio(entrada)
    st.markdown("##### Clasificación resultante")
    cols = st.columns(4)
    for col, t in zip(cols, TIPOS_COLEGIO):
        col.markdown(tarjeta_tipo(t, seleccionado=(t == tipo)), unsafe_allow_html=True)
    st.write(f"**{TIPOS_COLEGIO[tipo]}.** Responsables sugeridos: {RESPONSABLES_TIPO[tipo]}.")
    navegacion("Propuesta", "Perfil")


def pantalla_perfil():
    st.header("Perfil comunicativo declarado")
    st.markdown('<div class="aviso">La forma de comunicación la declara el estudiante y su familia. '
                'El sistema no la infiere ni la evalúa.</div>', unsafe_allow_html=True)
    selector("¿Cómo se comunica el estudiante, según lo declarado por él y su familia?",
             "modalidad", MODALIDADES)
    col1, col2 = st.columns(2)
    with col1:
        casilla("Hay intérprete de LSP o modelo lingüístico disponible (vía UGEL)", "humano")
    with col2:
        casilla("La familia dio consentimiento escrito para usar herramientas en la nube", "consentimiento",
                "Obligatorio para herramientas que envían la voz a servidores externos.")
    if st.session_state["datos"]["modalidad"] == MOD_NO_DECLARADA:
        st.warning("Si aún no se consultó al estudiante y su familia, las sugerencias saldrán como provisionales.")
    navegacion("Diagnóstico", "Sugerencia", "Ver sugerencia")


def tarjeta_apoyo(s) -> str:
    color = COLOR_PRIORIDAD.get(s.prioridad, "#b7791f")
    etiqueta = s.prioridad.split(" (")[0]
    return (f'<div class="apoyo" style="--c:{color}"><span class="tag">{etiqueta}</span>'
            f'<h4>{s.nombre}</h4><p><b>Por qué:</b> {s.motivo}</p>'
            f'<p><b>Tenga en cuenta:</b> {s.nota}</p></div>')


def pantalla_sugerencia():
    entrada = construir_entrada()
    r = sugerir_apoyos(entrada)
    st.session_state["resultado"] = r
    st.header("Sugerencia de apoyos")
    if r.errores:
        for err in r.errores:
            st.error(err)
        navegacion("Perfil", None)
        return

    st.markdown(f'<div class="decide"><b>Recuerde:</b> {DECISION_FINAL}</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    for col, t in zip(cols, TIPOS_COLEGIO):
        col.markdown(tarjeta_tipo(t, seleccionado=(t == r.tipo_colegio)), unsafe_allow_html=True)

    if r.alertas:
        st.markdown("##### Alertas antes de decidir")
        for a in r.alertas:
            st.markdown(f'<div class="aviso">⚠️ {a}</div>', unsafe_allow_html=True)

    st.markdown("##### Apoyos sugeridos")
    if not r.sugerencias:
        st.write("No hay apoyos viables con las condiciones indicadas.")
    for s in r.sugerencias:
        st.markdown(tarjeta_apoyo(s), unsafe_allow_html=True)

    with st.expander(f"No sugeridos ({len(r.no_sugeridos)})"):
        for nombre, razon in r.no_sugeridos:
            st.write(f"- **{nombre}:** {razon}")
    with st.expander("Salvaguardas obligatorias"):
        for s in SALVAGUARDAS:
            st.write(f"- {s}")
    with st.expander("Cómo se llegó a esta sugerencia (trazabilidad)"):
        for regla in r.reglas_aplicadas:
            st.write(f"- {regla}")
    navegacion("Perfil", "Decisión", "Registrar decisión")


def pantalla_decision():
    st.header("Decisión del docente y del SAE")
    st.markdown('<div class="decide">El sistema no decide. Aquí se registra lo que resuelvan el docente y el '
                'especialista del SAE, con el estudiante y su familia.</div>', unsafe_allow_html=True)
    entrada = construir_entrada()
    r = sugerir_apoyos(entrada)
    if r.errores:
        st.error("Revise los datos de las pantallas anteriores.")
        navegacion("Sugerencia", None)
        return
    decision = st.radio("Decisión", OPCIONES_DECISION, horizontal=True)
    justificacion = st.text_area("Justificación (sin nombres ni datos personales)")
    st.download_button(
        "Descargar resumen (.txt)",
        data=resumen_en_texto(entrada, r, decision if decision != "Pendiente" else "", justificacion),
        file_name="resumen_sugerencia.txt", mime="text/plain", type="primary")
    st.markdown("##### Después de decidir")
    st.write("El sistema termina aquí. Las **pruebas en el aula** y el **seguimiento** (fases 3 y 5 de la "
             "propuesta) las realizan las personas: probar la herramienta, capacitar a los docentes y "
             "recoger las observaciones del estudiante.")
    navegacion("Sugerencia", "Viaje del usuario", "Ver el viaje")


def pantalla_viaje():
    st.header("Viaje del usuario")
    st.write("Recorrido de un docente o especialista del SAE a lo largo de las cinco fases de implementación "
             "propuestas, y qué parte cubre el prototipo.")
    cabecera = ("Fase", "Quién participa", "Qué hace", "Dónde", "¿Lo cubre el sistema?")
    filas = ['<div class="fila cab">' + "".join(f"<div>{c}</div>" for c in cabecera) + "</div>"]
    for i, (fase, quien, que, donde, alcance) in enumerate(VIAJE, start=1):
        clase = "si" if alcance.startswith("Sí") else ("par" if alcance.startswith("Parcial") else "no")
        filas.append(f'<div class="fila"><div><b>{i}. {fase}</b></div><div>{quien}</div><div>{que}</div>'
                     f'<div>{donde}</div><div class="{clase}">{alcance}</div></div>')
    st.markdown("".join(filas), unsafe_allow_html=True)
    st.caption("Fases tomadas de la Tabla 5 del informe. Las fases 3 y 5 requieren personas: el sistema no las sustituye.")
    st.button("Volver a la propuesta", on_click=ir_a, args=("Propuesta",))


def pantalla_verificacion():
    st.header("Verificación con casos de prueba")
    st.write("Doce casos ficticios contrastan la lógica con el resultado esperado. No usan datos reales.")
    filas = ejecutar_casos()
    aprobados = sum(1 for _, ok, _ in filas if ok)
    st.metric("Casos aprobados", f"{aprobados} / {len(filas)}")
    st.dataframe(
        [{"Caso": n, "Resultado": "✅ Aprobado" if ok else "❌ Falla", "Detalle": d} for n, ok, d in filas],
        width="stretch", hide_index=True)


PANTALLA_FUNCION = {
    "Propuesta": pantalla_propuesta, "Diagnóstico": pantalla_diagnostico, "Perfil": pantalla_perfil,
    "Sugerencia": pantalla_sugerencia, "Decisión": pantalla_decision,
    "Viaje del usuario": pantalla_viaje, "Verificación": pantalla_verificacion,
}

# ---------------------------------------------------------------------------
# PROGRAMA PRINCIPAL
# ---------------------------------------------------------------------------
iniciar_estado()

with st.sidebar:
    st.markdown("### 🦻 Apoyos de comunicación")
    st.caption("Prototipo académico · Computación en la Sociedad")
    st.radio("Pantalla", PANTALLAS, key="pantalla")
    st.divider()
    st.caption("Sugiere, no decide. Sin datos personales.")

barra_pasos()
PANTALLA_FUNCION[st.session_state["pantalla"]]()
