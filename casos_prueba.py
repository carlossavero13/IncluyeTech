"""
casos_prueba.py — Casos de prueba FICTICIOS para verificar la lógica (Objetivo específico 6).

No usa datos reales de estudiantes ni de colegios. Se ejecuta de dos formas:
    python casos_prueba.py        -> imprime una tabla de resultados
    pytest casos_prueba.py        -> cada caso es un test
"""

from logica import (
    Entrada, sugerir_apoyos,
    MOD_LSP, MOD_ORAL, MOD_MIXTA, MOD_NO_DECLARADA,
    CONEXION_ESTABLE, CONEXION_LIMITADA, CONEXION_NINGUNA,
    CONT_EN_VIVO, CONT_GRABADO, CONT_AMBOS,
    PRIORIDAD_PRINCIPAL, PRIORIDAD_COMPLEMENTARIA, PRIORIDAD_PROVISIONAL,
)

# Cada caso: nombre, entrada, tipo esperado, ids que DEBEN aparecer, ids que NO deben aparecer,
# y fragmentos de texto que deben aparecer en alguna alerta.
CASOS = [
    {
        "nombre": "C1 · Urbano conectado, estudiante oral, con consentimiento",
        "entrada": Entrada(MOD_ORAL, CONEXION_ESTABLE, True, True, True, False, True, False, CONT_EN_VIVO),
        "tipo": "A",
        "debe": ["SUBTITULOS_NUBE", "ASR_LOCAL"],
        "no_debe": ["INTERPRETE_LSP", "MATERIAL_VISUAL_IMPRESO"],
        "alertas": ["consentimiento"],
        "principal": "SUBTITULOS_NUBE",
    },
    {
        "nombre": "C2 · Conexión estable pero SIN consentimiento: no se sugiere la nube",
        "entrada": Entrada(MOD_ORAL, CONEXION_ESTABLE, True, True, True, False, False, False, CONT_EN_VIVO),
        "tipo": "A",
        "debe": ["ASR_LOCAL"],
        "no_debe": ["SUBTITULOS_NUBE"],
        "alertas": [],
    },
    {
        "nombre": "C3 · Conexión inestable: se priorizan materiales preparados",
        "entrada": Entrada(MOD_ORAL, CONEXION_LIMITADA, True, True, False, False, False, False, CONT_GRABADO),
        "tipo": "B",
        "debe": ["VIDEO_SUBTITULADO", "TRANSCRIPCION_REVISADA"],
        "no_debe": ["SUBTITULOS_NUBE", "ASR_LOCAL"],
        "alertas": [],
    },
    {
        "nombre": "C4 · Rural sin Internet, con electricidad y equipo apto",
        "entrada": Entrada(MOD_ORAL, CONEXION_NINGUNA, True, True, True, False, False, False, CONT_EN_VIVO),
        "tipo": "C",
        "debe": ["ASR_LOCAL", "TRANSCRIPCION_REVISADA"],
        "no_debe": ["SUBTITULOS_NUBE"],
        "alertas": ["Procesamiento local"],
        "principal": "ASR_LOCAL",
    },
    {
        "nombre": "C5 · Rural sin Internet y equipo NO apto: sin ASR local",
        "entrada": Entrada(MOD_ORAL, CONEXION_NINGUNA, True, True, False, False, False, False, CONT_EN_VIVO),
        "tipo": "C",
        "debe": ["TRANSCRIPCION_REVISADA"],
        "no_debe": ["ASR_LOCAL", "SUBTITULOS_NUBE"],
        "alertas": [],
    },
    {
        "nombre": "C6 · Sin electricidad confiable: nada de IA, material impreso y gestión",
        "entrada": Entrada(MOD_ORAL, CONEXION_NINGUNA, False, True, False, False, False, False, CONT_EN_VIVO),
        "tipo": "D",
        "debe": ["MATERIAL_VISUAL_IMPRESO", "GESTION_INFRAESTRUCTURA"],
        "no_debe": ["ASR_LOCAL", "SUBTITULOS_NUBE", "VIDEO_SUBTITULADO"],
        "alertas": ["apoyo humano coordinado"],
    },
    {
        "nombre": "C7 · Usa LSP con intérprete: el apoyo humano es el principal",
        "entrada": Entrada(MOD_LSP, CONEXION_ESTABLE, True, True, True, True, True, False, CONT_EN_VIVO),
        "tipo": "A",
        "debe": ["INTERPRETE_LSP", "MODELO_LINGUISTICO", "SUBTITULOS_NUBE"],
        "no_debe": [],
        "alertas": ["no equivalen a la interpretación"],
        "principal": "INTERPRETE_LSP",
        "complementaria": "SUBTITULOS_NUBE",
    },
    {
        "nombre": "C8 · Usa LSP y NO hay intérprete: alerta de brecha, sin avatar",
        "entrada": Entrada(MOD_LSP, CONEXION_NINGUNA, True, True, True, False, False, False, CONT_EN_VIVO),
        "tipo": "C",
        "debe": ["ASR_LOCAL"],
        "no_debe": ["INTERPRETE_LSP", "MODELO_LINGUISTICO"],
        "alertas": ["Brecha de apoyo humano"],
        "complementaria": "ASR_LOCAL",
    },
    {
        "nombre": "C9 · Modalidad no declarada: todo es provisional",
        "entrada": Entrada(MOD_NO_DECLARADA, CONEXION_ESTABLE, True, True, True, False, True, False, CONT_EN_VIVO),
        "tipo": "A",
        "debe": ["SUBTITULOS_NUBE"],
        "no_debe": [],
        "alertas": ["Perfil incompleto"],
        "provisional": "SUBTITULOS_NUBE",
    },
    {
        "nombre": "C10 · Aula ruidosa con ASR: alerta de micrófono y revisión",
        "entrada": Entrada(MOD_ORAL, CONEXION_NINGUNA, True, True, True, False, False, True, CONT_EN_VIVO),
        "tipo": "C",
        "debe": ["ASR_LOCAL"],
        "no_debe": [],
        "alertas": ["Aula ruidosa"],
    },
    {
        "nombre": "C11 · Modalidad mixta: apoyo humano y texto, ambos principales",
        "entrada": Entrada(MOD_MIXTA, CONEXION_ESTABLE, True, True, True, True, True, False, CONT_AMBOS),
        "tipo": "A",
        "debe": ["INTERPRETE_LSP", "SUBTITULOS_NUBE"],
        "no_debe": [],
        "alertas": [],
        "principal": "SUBTITULOS_NUBE",
    },
    {
        "nombre": "C12 · Entrada incoherente: dispositivo apto sin dispositivo",
        "entrada": Entrada(MOD_ORAL, CONEXION_NINGUNA, True, False, True, False, False, False, CONT_EN_VIVO),
        "tipo": "",
        "debe": [],
        "no_debe": [],
        "alertas": [],
        "con_error": True,
    },
]


def verificar_caso(caso: dict) -> tuple:
    """Ejecuta un caso y devuelve (aprobado, lista_de_fallas)."""
    r = sugerir_apoyos(caso["entrada"])
    fallas = []

    if caso.get("con_error"):
        if not r.errores:
            fallas.append("Se esperaba un error de validación y no ocurrió")
        return (len(fallas) == 0), fallas

    ids = [s.id_apoyo for s in r.sugerencias]
    if r.tipo_colegio != caso["tipo"]:
        fallas.append(f"Tipo esperado {caso['tipo']}, obtenido {r.tipo_colegio}")
    for i in caso["debe"]:
        if i not in ids:
            fallas.append(f"Debía sugerir {i}")
    for i in caso["no_debe"]:
        if i in ids:
            fallas.append(f"No debía sugerir {i}")
    for fragmento in caso["alertas"]:
        if not any(fragmento in a for a in r.alertas):
            fallas.append(f"Falta alerta con «{fragmento}»")

    esperadas = [("principal", PRIORIDAD_PRINCIPAL),
                 ("complementaria", PRIORIDAD_COMPLEMENTARIA),
                 ("provisional", PRIORIDAD_PROVISIONAL)]
    for clave, prioridad in esperadas:
        if clave in caso:
            encontrada = [s.prioridad for s in r.sugerencias if s.id_apoyo == caso[clave]]
            if encontrada != [prioridad]:
                fallas.append(f"{caso[clave]} debía ser «{prioridad}», fue {encontrada}")

    # Invariantes que se cumplen en TODOS los casos válidos
    if any("avatar" in s.nombre.lower() for s in r.sugerencias):
        fallas.append("Nunca se debe sugerir un avatar")
    if not any("avatar" in n.lower() for n, _ in r.no_sugeridos):
        fallas.append("Los avatares deben figurar como no sugeridos")

    return (len(fallas) == 0), fallas


def ejecutar_casos() -> list:
    """Ejecuta todos los casos y devuelve filas (nombre, aprobado, detalle)."""
    filas = []
    for caso in CASOS:
        ok, fallas = verificar_caso(caso)
        filas.append((caso["nombre"], ok, "; ".join(fallas) if fallas else "—"))
    return filas


# --- Compatibilidad con pytest ----------------------------------------------------
def test_todos_los_casos():
    for nombre, ok, detalle in ejecutar_casos():
        assert ok, f"{nombre}: {detalle}"


if __name__ == "__main__":
    total_ok = 0
    for nombre, ok, detalle in ejecutar_casos():
        print(("OK   " if ok else "FALLA"), nombre, "" if ok else f"-> {detalle}")
        total_ok += ok
    print(f"\n{total_ok}/{len(CASOS)} casos aprobados")
