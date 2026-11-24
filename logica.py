"""
logica.py — Lógica del prototipo "Sugerencia de apoyos de comunicación".

Trabajo Final · Computación en la Sociedad · Tema: tecnologías emergentes de apoyo
(IA y accesibilidad digital) para estudiantes con discapacidad auditiva en colegios
públicos de EBR del Perú.

Este módulo NO usa Streamlit: contiene solo constantes, listas (arreglos), funciones y
estructuras de control, de modo que pueda probarse por separado (ver casos_prueba.py).

Principios de diseño (tomados de la "Propuesta de respuesta responsable", informe):
  1. El sistema SUGIERE; la decisión final es del docente y del especialista del SAE.
  2. No diagnostica ni evalúa el rendimiento del estudiante (MINEDU, 2024, num. 5.2.1.5).
  3. La modalidad comunicativa la declara el estudiante / su familia; el sistema no la infiere.
  4. Un apoyo digital (subtítulos, voz a texto) NO reemplaza a la LSP ni al intérprete.
  5. No se guardan datos personales ni audio: solo se procesan condiciones del colegio.
  6. Los tipos de colegio A-D son una propuesta del equipo, no una clasificación oficial.
"""

from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# 1. CONSTANTES
# ---------------------------------------------------------------------------

# Frase que debe acompañar siempre al resultado (Propuesta, "Descripción de la solución").
DECISION_FINAL = (
    "Esta es una SUGERENCIA. La decisión final corresponde al docente y al "
    "especialista del SAE, junto con el estudiante y su familia. El sistema no "
    "diagnostica ni evalúa el rendimiento académico."
)

# --- Modalidad comunicativa DECLARADA por el estudiante / familia -----------------
MOD_LSP = "LSP"
MOD_ORAL = "ORAL_ESCRITA"
MOD_MIXTA = "MIXTA"
MOD_NO_DECLARADA = "NO_DECLARADA"

MODALIDADES = {
    MOD_LSP: "Usa principalmente Lengua de Señas Peruana (LSP)",
    MOD_ORAL: "Usa lengua oral y lectura/escritura (necesita acceso visual al texto)",
    MOD_MIXTA: "Usa LSP y también lengua oral/escrita",
    MOD_NO_DECLARADA: "Aún no se ha consultado o no se ha declarado",
}

# --- Conectividad del local (valores autodeclarados por el docente o director) ---
CONEXION_ESTABLE = "ESTABLE"
CONEXION_LIMITADA = "LIMITADA"
CONEXION_NINGUNA = "NINGUNA"

CONEXIONES = {
    CONEXION_ESTABLE: "Internet estable",
    CONEXION_LIMITADA: "Internet limitado o inestable",
    CONEXION_NINGUNA: "Sin Internet",
}

# --- Tipo de contenido que se necesita hacer accesible ----------------------------
CONT_EN_VIVO = "EN_VIVO"
CONT_GRABADO = "GRABADO"
CONT_AMBOS = "AMBOS"

CONTENIDOS = {
    CONT_EN_VIVO: "Explicación oral del docente en clase (en vivo)",
    CONT_GRABADO: "Videos o audios ya grabados",
    CONT_AMBOS: "Ambos",
}

# --- Tipos de colegio (Tabla 4 del informe; clasificación propuesta por el equipo) ---
TIPO_A, TIPO_B, TIPO_C, TIPO_D = "A", "B", "C", "D"

TIPOS_COLEGIO = {
    TIPO_A: "Tipo A: colegio con conexión estable",
    TIPO_B: "Tipo B: colegio con conexión limitada o inestable",
    TIPO_C: "Tipo C: colegio sin Internet, pero con electricidad",
    TIPO_D: "Tipo D: colegio sin electricidad confiable (o sin dispositivo)",
}

RESPONSABLES_TIPO = {
    TIPO_A: "Dirección del colegio, SAE interno y docentes",
    TIPO_B: "Dirección del colegio, UGEL y equipo técnico",
    TIPO_C: "Equipo técnico, docentes y SAE",
    TIPO_D: "MINEDU, DRE, UGEL y dirección del colegio",
}

# --- Prioridades de una sugerencia -------------------------------------------------
PRIORIDAD_PRINCIPAL = "Principal"
PRIORIDAD_COMPLEMENTARIA = "Complementaria"
PRIORIDAD_PROVISIONAL = "Provisional (consultar antes al estudiante y su familia)"

# --- Catálogo de apoyos (arreglo de registros) ------------------------------------
# Cada apoyo declara sus REQUISITOS; una función los contrasta con las condiciones
# del colegio. Así la regla "no sugerir lo que el colegio no puede sostener" queda
# expresada en datos y no repartida en muchos if.
#   conexiones      : conexiones con las que el apoyo puede funcionar
#   electricidad    : requiere electricidad confiable
#   dispositivo     : requiere un dispositivo (del docente o del colegio)
#   dispositivo_apto: requiere un dispositivo con capacidad para procesar localmente
#   consentimiento  : requiere consentimiento escrito de la familia (envía voz a la nube)
#   humano          : es un apoyo humano gestionado por la UGEL
APOYOS = [
    {
        "id": "SUBTITULOS_NUBE",
        "nombre": "Subtítulos en vivo en la nube (p. ej., Live Transcribe)",
        "conexiones": [CONEXION_ESTABLE],
        "electricidad": True, "dispositivo": True, "dispositivo_apto": False,
        "consentimiento": True, "humano": False,
        "nota": "Requiere Internet continuo. La voz viaja a servidores externos: "
                "verificar el tratamiento de datos sensibles de menores.",
    },
    {
        "id": "ASR_LOCAL",
        "nombre": "Transcripción local sin conexión (p. ej., OpenAI Whisper)",
        "conexiones": [CONEXION_ESTABLE, CONEXION_LIMITADA, CONEXION_NINGUNA],
        "electricidad": True, "dispositivo": True, "dispositivo_apto": True,
        "consentimiento": False, "humano": False,
        "nota": "Procesa en el equipo del colegio sin enviar la voz a la nube. "
                "Su rendimiento depende del dispositivo y de pruebas previas en el aula.",
    },
    {
        "id": "TRANSCRIPCION_REVISADA",
        "nombre": "Transcripciones revisadas por el docente",
        "conexiones": [CONEXION_ESTABLE, CONEXION_LIMITADA, CONEXION_NINGUNA],
        "electricidad": True, "dispositivo": True, "dispositivo_apto": False,
        "consentimiento": False, "humano": False,
        "nota": "El docente prepara o corrige el texto antes de compartirlo. "
                "Es el apoyo escrito más confiable porque pasa por revisión humana.",
    },
    {
        "id": "VIDEO_SUBTITULADO",
        "nombre": "Videos con subtítulos descargados previamente",
        "conexiones": [CONEXION_ESTABLE, CONEXION_LIMITADA, CONEXION_NINGUNA],
        "electricidad": True, "dispositivo": True, "dispositivo_apto": False,
        "consentimiento": False, "humano": False,
        "nota": "Se descargan o preparan con anticipación, por lo que no dependen de "
                "la conexión durante la clase. Verificar la licencia del material.",
    },
    {
        "id": "MATERIAL_VISUAL_IMPRESO",
        "nombre": "Materiales visuales impresos (guiones, resúmenes, esquemas)",
        "conexiones": [CONEXION_ESTABLE, CONEXION_LIMITADA, CONEXION_NINGUNA],
        "electricidad": False, "dispositivo": False, "dispositivo_apto": False,
        "consentimiento": False, "humano": False,
        "nota": "No depende de equipos electrónicos; sirve cuando no hay electricidad confiable.",
    },
    {
        "id": "INTERPRETE_LSP",
        "nombre": "Intérprete de LSP (presencial o virtual) gestionado por la UGEL",
        "conexiones": [CONEXION_ESTABLE, CONEXION_LIMITADA, CONEXION_NINGUNA],
        "electricidad": False, "dispositivo": False, "dispositivo_apto": False,
        "consentimiento": False, "humano": True,
        "nota": "Un mismo intérprete suele atender varias instituciones; se organiza por UGEL.",
    },
    {
        "id": "MODELO_LINGUISTICO",
        "nombre": "Modelo lingüístico sordo usuario de LSP",
        "conexiones": [CONEXION_ESTABLE, CONEXION_LIMITADA, CONEXION_NINGUNA],
        "electricidad": False, "dispositivo": False, "dispositivo_apto": False,
        "consentimiento": False, "humano": True,
        "nota": "Facilita el aprendizaje de la LSP y el acercamiento a la cultura sorda.",
    },
    {
        "id": "GESTION_INFRAESTRUCTURA",
        "nombre": "Gestión de mejoras de energía y equipos ante MINEDU, DRE y UGEL",
        "conexiones": [CONEXION_ESTABLE, CONEXION_LIMITADA, CONEXION_NINGUNA],
        "electricidad": False, "dispositivo": False, "dispositivo_apto": False,
        "consentimiento": False, "humano": True,
        "nota": "Antes de incorporar herramientas de IA hay que resolver la infraestructura.",
    },
]

# Apoyos que el sistema NO sugiere nunca, con su razón (lista constante).
APOYOS_EXCLUIDOS_SIEMPRE = [
    {
        "nombre": "Avatares o traducción automática a LSP como reemplazo del intérprete",
        "razon": "La WFD y la WASLI (2018) advierten contra sustituir intérpretes por avatares, "
                 "y no se halló una herramienta validada para la LSP.",
    },
    {
        "nombre": "Voz a texto como vía para que el estudiante sordo se exprese",
        "razon": "El reconocimiento de voz falla mucho con voz sorda (≈78 % de error en un "
                 "estudio pequeño; Glasser et al., 2017). Úsese solo para que el estudiante "
                 "reciba lo que dice el docente.",
    },
]

# Salvaguardas que acompañan SIEMPRE cualquier sugerencia (lista constante).
SALVAGUARDAS = [
    "Revisión humana: el docente revisa y corrige lo que produzca cualquier herramienta "
    "antes de usarlo como única fuente de información importante.",
    "No grabar ni almacenar audio de la clase; procesar en el dispositivo cuando sea posible.",
    "Probar la herramienta en el aula real antes de adoptarla (precisión, tiempo de respuesta, ruido).",
    "Verificar la licencia de los videos, textos e imágenes antes de subirlos a un servicio.",
    "Consultar al estudiante y a su familia; la elección del apoyo debe ser de ellos, no impuesta.",
    "Los subtítulos y la LSP atienden necesidades distintas: ninguno sustituye automáticamente al otro.",
]

# Pasos de verificación según las fases de implementación (Tabla 5 del informe).
FASES = [
    "1. Diagnóstico de necesidades",
    "2. Selección de herramientas",
    "3. Pruebas de funcionamiento",
    "4. Implementación progresiva",
    "5. Seguimiento y mejora continua",
]


# ---------------------------------------------------------------------------
# 2. ESTRUCTURAS DE DATOS
# ---------------------------------------------------------------------------

@dataclass
class Entrada:
    """Datos que ingresa el docente o el SAE. No contiene datos personales."""
    modalidad: str = MOD_NO_DECLARADA
    conexion: str = CONEXION_NINGUNA
    electricidad_confiable: bool = True
    hay_dispositivo: bool = True
    dispositivo_apto_local: bool = False
    apoyo_humano_lsp_disponible: bool = False
    consentimiento_familia: bool = False
    aula_ruidosa: bool = False
    contenido: str = CONT_EN_VIVO


@dataclass
class Sugerencia:
    id_apoyo: str
    nombre: str
    prioridad: str
    motivo: str
    nota: str
    regla: str


@dataclass
class Resultado:
    tipo_colegio: str = ""
    sugerencias: list = field(default_factory=list)
    no_sugeridos: list = field(default_factory=list)   # (nombre, razón)
    alertas: list = field(default_factory=list)
    reglas_aplicadas: list = field(default_factory=list)
    errores: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# 3. FUNCIONES
# ---------------------------------------------------------------------------

def validar_entrada(e: Entrada) -> list:
    """Devuelve la lista de errores de validación (vacía si todo es válido)."""
    errores = []
    if e.modalidad not in MODALIDADES:
        errores.append("Modalidad comunicativa no válida.")
    if e.conexion not in CONEXIONES:
        errores.append("Tipo de conexión no válido.")
    if e.contenido not in CONTENIDOS:
        errores.append("Tipo de contenido no válido.")
    # Coherencia: no puede haber dispositivo apto si no hay dispositivo.
    if e.dispositivo_apto_local and not e.hay_dispositivo:
        errores.append("Se indicó dispositivo apto para procesamiento local, pero no hay dispositivo.")
    return errores


def clasificar_colegio(e: Entrada) -> str:
    """Clasifica el colegio en A, B, C o D (Tabla 4 del informe).

    Se evalúa en orden de restricción: primero energía/dispositivo, luego conectividad.
    """
    if (not e.electricidad_confiable) or (not e.hay_dispositivo):
        return TIPO_D
    if e.conexion == CONEXION_NINGUNA:
        return TIPO_C
    if e.conexion == CONEXION_LIMITADA:
        return TIPO_B
    return TIPO_A


def buscar_apoyo(id_apoyo: str) -> dict:
    """Busca un apoyo en el catálogo recorriendo la lista."""
    for apoyo in APOYOS:
        if apoyo["id"] == id_apoyo:
            return apoyo
    raise KeyError(f"Apoyo no registrado: {id_apoyo}")


def evaluar_viabilidad(apoyo: dict, e: Entrada) -> tuple:
    """Contrasta los requisitos de un apoyo con las condiciones del colegio.

    Devuelve (es_viable, razón). Si no es viable, la razón explica por qué.
    """
    if e.conexion not in apoyo["conexiones"]:
        return False, "requiere una conexión a Internet que el colegio no tiene en este momento"
    if apoyo["electricidad"] and not e.electricidad_confiable:
        return False, "requiere electricidad confiable"
    if apoyo["dispositivo"] and not e.hay_dispositivo:
        return False, "requiere un dispositivo (del docente o del colegio)"
    if apoyo["dispositivo_apto"] and not e.dispositivo_apto_local:
        return False, "requiere un dispositivo con capacidad para procesar localmente"
    if apoyo["consentimiento"] and not e.consentimiento_familia:
        return False, "requiere consentimiento escrito de la familia (la voz se envía a la nube)"
    if apoyo["humano"] and apoyo["id"] in ("INTERPRETE_LSP", "MODELO_LINGUISTICO") \
            and not e.apoyo_humano_lsp_disponible:
        return False, "no hay apoyo humano de LSP disponible; debe gestionarse con la UGEL"
    return True, ""


def candidatos_por_tipo(tipo: str) -> list:
    """Devuelve la lista de candidatos (id, prioridad base, motivo, regla) según el tipo de colegio."""
    if tipo == TIPO_A:
        return [
            ("SUBTITULOS_NUBE", PRIORIDAD_PRINCIPAL,
             "El colegio tiene Internet estable y dispositivos.", "R-A1"),
            ("ASR_LOCAL", PRIORIDAD_COMPLEMENTARIA,
             "Alternativa que no envía la voz a la nube.", "R-A2"),
            ("VIDEO_SUBTITULADO", PRIORIDAD_COMPLEMENTARIA,
             "Para materiales audiovisuales grabados.", "R-A3"),
            ("TRANSCRIPCION_REVISADA", PRIORIDAD_COMPLEMENTARIA,
             "Respaldo revisado por una persona.", "R-A4"),
        ]
    if tipo == TIPO_B:
        return [
            ("VIDEO_SUBTITULADO", PRIORIDAD_PRINCIPAL,
             "La conexión es inestable: conviene preparar los materiales con anticipación.", "R-B1"),
            ("TRANSCRIPCION_REVISADA", PRIORIDAD_PRINCIPAL,
             "No depende de la conexión durante la clase.", "R-B2"),
            ("ASR_LOCAL", PRIORIDAD_COMPLEMENTARIA,
             "Funciona sin conexión si el equipo es compatible.", "R-B3"),
        ]
    if tipo == TIPO_C:
        return [
            ("ASR_LOCAL", PRIORIDAD_PRINCIPAL,
             "No hay Internet, pero hay electricidad y dispositivo.", "R-C1"),
            ("TRANSCRIPCION_REVISADA", PRIORIDAD_PRINCIPAL,
             "Material revisado y preparado sin conexión.", "R-C2"),
            ("VIDEO_SUBTITULADO", PRIORIDAD_COMPLEMENTARIA,
             "Videos con subtítulos cargados con anticipación en el equipo.", "R-C3"),
        ]
    # Tipo D
    return [
        ("MATERIAL_VISUAL_IMPRESO", PRIORIDAD_PRINCIPAL,
         "No hay electricidad confiable o dispositivo: priorizar materiales sin equipos.", "R-D1"),
        ("GESTION_INFRAESTRUCTURA", PRIORIDAD_PRINCIPAL,
         "Antes de usar herramientas de IA se deben evaluar mejoras de infraestructura.", "R-D2"),
    ]


def candidatos_por_modalidad(modalidad: str) -> list:
    """Apoyos humanos que dependen de la modalidad declarada (LSP o mixta)."""
    if modalidad in (MOD_LSP, MOD_MIXTA):
        return [
            ("INTERPRETE_LSP", PRIORIDAD_PRINCIPAL,
             "El estudiante usa LSP: el apoyo humano en LSP es el principal.", "R-M1"),
            ("MODELO_LINGUISTICO", PRIORIDAD_PRINCIPAL,
             "Facilita el aprendizaje de la LSP y el acercamiento a la cultura sorda.", "R-M2"),
        ]
    return []


def ajustar_prioridad_por_modalidad(prioridad: str, modalidad: str, es_humano: bool) -> str:
    """Ajusta la prioridad de un apoyo digital según la modalidad declarada."""
    if es_humano:
        return prioridad
    if modalidad == MOD_NO_DECLARADA:
        return PRIORIDAD_PROVISIONAL
    if modalidad == MOD_LSP and prioridad == PRIORIDAD_PRINCIPAL:
        # Para quien usa LSP, el texto es un complemento y no un reemplazo.
        return PRIORIDAD_COMPLEMENTARIA
    return prioridad


def construir_alertas(e: Entrada, tipo: str, sugerencias: list) -> list:
    """Genera las alertas que el docente / SAE debe leer antes de decidir."""
    alertas = []
    ids = [s.id_apoyo for s in sugerencias]

    if e.modalidad == MOD_NO_DECLARADA:
        alertas.append("Perfil incompleto: todavía no se consultó la modalidad comunicativa del "
                       "estudiante. Las sugerencias son provisionales; consulte primero al "
                       "estudiante y a su familia.")

    if e.modalidad in (MOD_LSP, MOD_MIXTA) and not e.apoyo_humano_lsp_disponible:
        alertas.append("Brecha de apoyo humano: el estudiante usa LSP y no hay intérprete ni modelo "
                       "lingüístico disponible. Gestione el apoyo con la UGEL; el texto automático "
                       "no es un reemplazo.")

    if e.modalidad == MOD_LSP:
        alertas.append("Para quien usa LSP principalmente, los subtítulos son un complemento y "
                       "no equivalen a la interpretación (WCAG 2.2: criterios 1.2.2/1.2.4 y 1.2.6 son distintos).")

    usa_asr = any(i in ids for i in ("SUBTITULOS_NUBE", "ASR_LOCAL"))
    if usa_asr and e.aula_ruidosa:
        alertas.append("Aula ruidosa: la tasa de error de los reconocedores de voz sube mucho en aulas "
                       "reales (Southwell et al., 2022). Use un micrófono cercano al docente y trate "
                       "la transcripción como apoyo revisable, no como registro fiel.")

    if "SUBTITULOS_NUBE" in ids:
        alertas.append("Herramienta en la nube: confirme el consentimiento escrito de la familia y "
                       "las condiciones del servicio (datos sensibles de menores).")

    if "ASR_LOCAL" in ids and tipo in (TIPO_B, TIPO_C):
        alertas.append("Procesamiento local: valide en el equipo real la velocidad y la precisión "
                       "antes de usarlo en clase.")

    if e.contenido in (CONT_EN_VIVO, CONT_AMBOS) and tipo == TIPO_D:
        alertas.append("Contenido en vivo sin electricidad confiable: se requiere apoyo humano "
                       "coordinado, porque no hay una solución digital viable por ahora.")

    return alertas


def sugerir_apoyos(e: Entrada) -> Resultado:
    """Función principal: recibe las condiciones y devuelve las sugerencias.

    Flujo (secuencial):
      1) validar -> 2) clasificar colegio -> 3) reunir candidatos -> 4) filtrar por
      viabilidad -> 5) ajustar prioridad por modalidad -> 6) alertas.
    """
    r = Resultado()

    # 1) Validación
    r.errores = validar_entrada(e)
    if r.errores:
        return r

    # 2) Clasificación del colegio
    r.tipo_colegio = clasificar_colegio(e)
    r.reglas_aplicadas.append(f"Clasificación: {TIPOS_COLEGIO[r.tipo_colegio]}")

    # 3) Candidatos (por tipo de colegio y por modalidad declarada)
    candidatos = candidatos_por_modalidad(e.modalidad) + candidatos_por_tipo(r.tipo_colegio)

    # 4) Filtrado por viabilidad + 5) ajuste de prioridad
    vistos = []
    for id_apoyo, prioridad, motivo, regla in candidatos:
        if id_apoyo in vistos:
            continue
        vistos.append(id_apoyo)
        apoyo = buscar_apoyo(id_apoyo)
        viable, razon = evaluar_viabilidad(apoyo, e)
        if not viable:
            r.no_sugeridos.append((apoyo["nombre"], razon))
            r.reglas_aplicadas.append(f"{regla}: descartado ({razon})")
            continue
        prioridad_final = ajustar_prioridad_por_modalidad(prioridad, e.modalidad, apoyo["humano"])
        r.sugerencias.append(Sugerencia(id_apoyo, apoyo["nombre"], prioridad_final,
                                        motivo, apoyo["nota"], regla))
        r.reglas_aplicadas.append(f"{regla}: sugerido como «{prioridad_final}»")

    # Ordenar: principal, complementaria, provisional
    orden = {PRIORIDAD_PRINCIPAL: 0, PRIORIDAD_COMPLEMENTARIA: 1, PRIORIDAD_PROVISIONAL: 2}
    r.sugerencias.sort(key=lambda s: orden.get(s.prioridad, 9))

    # Apoyos excluidos siempre (constantes)
    for excluido in APOYOS_EXCLUIDOS_SIEMPRE:
        r.no_sugeridos.append((excluido["nombre"], excluido["razon"]))

    # 6) Alertas
    r.alertas = construir_alertas(e, r.tipo_colegio, r.sugerencias)
    return r


def resumen_en_texto(e: Entrada, r: Resultado, decision: str = "", justificacion: str = "") -> str:
    """Genera un resumen descargable. No incluye nombres ni datos personales."""
    lineas = ["SUGERENCIA DE APOYOS DE COMUNICACIÓN (prototipo académico)", "=" * 60]
    lineas.append(f"Modalidad declarada: {MODALIDADES.get(e.modalidad, e.modalidad)}")
    lineas.append(f"Conexión: {CONEXIONES.get(e.conexion, e.conexion)}")
    lineas.append(f"Tipo de colegio: {TIPOS_COLEGIO.get(r.tipo_colegio, '-')}")
    lineas.append(f"Responsables sugeridos: {RESPONSABLES_TIPO.get(r.tipo_colegio, '-')}")
    lineas.append("")
    lineas.append("APOYOS SUGERIDOS")
    for i, s in enumerate(r.sugerencias, start=1):
        lineas.append(f"  {i}. [{s.prioridad}] {s.nombre}")
        lineas.append(f"     Motivo: {s.motivo}")
    lineas.append("")
    lineas.append("NO SUGERIDOS")
    for nombre, razon in r.no_sugeridos:
        lineas.append(f"  - {nombre}: {razon}")
    lineas.append("")
    lineas.append("ALERTAS")
    for a in r.alertas:
        lineas.append(f"  ! {a}")
    lineas.append("")
    lineas.append("SALVAGUARDAS")
    for s in SALVAGUARDAS:
        lineas.append(f"  * {s}")
    lineas.append("")
    lineas.append("DECISIÓN DEL DOCENTE / SAE")
    lineas.append(f"  Decisión: {decision or '(pendiente)'}")
    lineas.append(f"  Justificación: {justificacion or '(pendiente)'}")
    lineas.append("")
    lineas.append(DECISION_FINAL)
    return "\n".join(lineas)
