"""
Datos mock para el módulo Gobierno de Datos.
Fuente única de datos del módulo; en el futuro se reemplazará por llamadas al backend.
"""

FUENTES = ["Todas", "SNIES", "SACES"]
FUENTE_KEY_TODAS = "Todas"
FUENTE_KEY_SNIES = "SNIES"
FUENTE_KEY_SACES = "SACES"


def get_hub_metrics(fuente: str) -> list[dict]:
    """KPIs del hub según la fuente seleccionada (mock)."""
    base = [
        {"label": "Fuentes registradas", "value": "2", "icon": "📁"},
        {"label": "Datasets catalogados", "value": "12", "icon": "📊"},
        {"label": "Reglas de calidad activas", "value": "28", "icon": "✓"},
        {"label": "Procesos trazados", "value": "6", "icon": "🔄"},
    ]
    if fuente == FUENTE_KEY_SNIES:
        return [
            {"label": "Fuentes registradas", "value": "1", "icon": "📁"},
            {"label": "Datasets catalogados", "value": "6", "icon": "📊"},
            {"label": "Reglas de calidad activas", "value": "14", "icon": "✓"},
            {"label": "Procesos trazados", "value": "3", "icon": "🔄"},
        ]
    if fuente == FUENTE_KEY_SACES:
        return [
            {"label": "Fuentes registradas", "value": "1", "icon": "📁"},
            {"label": "Datasets catalogados", "value": "6", "icon": "📊"},
            {"label": "Reglas de calidad activas", "value": "14", "icon": "✓"},
            {"label": "Procesos trazados", "value": "3", "icon": "🔄"},
        ]
    return base


def get_catalogo(fuente: str) -> list[dict]:
    """Inventario mock de datasets. Columnas: Fuente, Dataset, Descripción, Responsable, Frecuencia, Estado."""
    rows = [
        {"Fuente": "SNIES", "Dataset": "instituciones", "Descripción": "Instituciones de educación superior", "Responsable": "Área SNIES", "Frecuencia": "Mensual", "Estado": "Activo"},
        {"Fuente": "SNIES", "Dataset": "programas", "Descripción": "Programas académicos ofertados", "Responsable": "Área SNIES", "Frecuencia": "Mensual", "Estado": "Activo"},
        {"Fuente": "SNIES", "Dataset": "acreditaciones", "Descripción": "Estado de acreditación de programas", "Responsable": "Área SNIES", "Frecuencia": "Trimestral", "Estado": "Activo"},
        {"Fuente": "SACES", "Dataset": "solicitudes", "Descripción": "Solicitudes de registro calificado", "Responsable": "Área SACES", "Frecuencia": "Diaria", "Estado": "Activo"},
        {"Fuente": "SACES", "Dataset": "evaluaciones", "Descripción": "Evaluaciones de pares académicos", "Responsable": "Área SACES", "Frecuencia": "Semanal", "Estado": "Activo"},
        {"Fuente": "SACES", "Dataset": "resoluciones", "Descripción": "Resoluciones de registro calificado", "Responsable": "Área SACES", "Frecuencia": "Diaria", "Estado": "Activo"},
    ]
    if fuente == FUENTE_KEY_TODAS:
        return rows
    return [r for r in rows if r["Fuente"] == fuente]


def get_calidad(fuente: str) -> list[dict]:
    """Reglas de calidad mock. Columnas: Fuente, Regla, Estado, Cumplimiento, Última ejecución."""
    rows = [
        {"Fuente": "SNIES", "Regla": "Completitud instituciones", "Estado": "Activa", "Cumplimiento": "98%", "Última ejecución": "2025-03-07"},
        {"Fuente": "SNIES", "Regla": "Sin duplicados programas", "Estado": "Activa", "Cumplimiento": "100%", "Última ejecución": "2025-03-07"},
        {"Fuente": "SNIES", "Regla": "Consistencia códigos", "Estado": "Activa", "Cumplimiento": "95%", "Última ejecución": "2025-03-06"},
        {"Fuente": "SACES", "Regla": "Completitud solicitudes", "Estado": "Activa", "Cumplimiento": "99%", "Última ejecución": "2025-03-07"},
        {"Fuente": "SACES", "Regla": "Validación fechas", "Estado": "Activa", "Cumplimiento": "100%", "Última ejecución": "2025-03-07"},
    ]
    if fuente == FUENTE_KEY_TODAS:
        return rows
    return [r for r in rows if r["Fuente"] == fuente]


def get_linaje(fuente: str) -> list[dict]:
    """Nodos de linaje mock: origen → etapas → destino."""
    if fuente == FUENTE_KEY_SNIES:
        return [
            {"etapa": "Origen", "nombre": "SNIES", "descripcion": "Sistema Nacional de Información"},
            {"etapa": "Staging", "nombre": "staging_snies", "descripcion": "Área de preparación"},
            {"etapa": "Modelo", "nombre": "modelo_analitico", "descripcion": "Modelo analítico unificado"},
            {"etapa": "Consumo", "nombre": "dashboard_snies", "descripcion": "Dashboard ejecutivo"},
        ]
    if fuente == FUENTE_KEY_SACES:
        return [
            {"etapa": "Origen", "nombre": "SACES", "descripcion": "Sistema de Aseguramiento"},
            {"etapa": "Staging", "nombre": "staging_saces", "descripcion": "Área de preparación"},
            {"etapa": "Consolidado", "nombre": "dataset_consolidado", "descripcion": "Dataset unificado"},
            {"etapa": "Consumo", "nombre": "reporte_saces", "descripcion": "Reportes de gestión"},
        ]
    # Todas: mostrar ambos flujos
    return [
        {"etapa": "Origen", "nombre": "SNIES / SACES", "descripcion": "Fuentes de datos"},
        {"etapa": "Staging", "nombre": "Staging", "descripcion": "Preparación y validación"},
        {"etapa": "Modelo / Consolidado", "nombre": "Capa analítica", "descripcion": "Modelos y conjuntos consolidados"},
        {"etapa": "Consumo", "nombre": "Dashboards y reportes", "descripcion": "Visualización y reportes"},
    ]


def get_metadatos(fuente: str) -> list[dict]:
    """Metadatos mock. Columnas: Fuente, Nombre técnico, Descripción, Tipo, Responsable, Actualización."""
    rows = [
        {"Fuente": "SNIES", "Nombre técnico": "dim_institucion", "Descripción": "Dimensión de instituciones", "Tipo": "Tabla", "Responsable": "Área SNIES", "Actualización": "2025-03-01"},
        {"Fuente": "SNIES", "Nombre técnico": "dim_programa", "Descripción": "Dimensión de programas", "Tipo": "Tabla", "Responsable": "Área SNIES", "Actualización": "2025-03-01"},
        {"Fuente": "SNIES", "Nombre técnico": "hecho_matricula", "Descripción": "Hecho de matrícula", "Tipo": "Tabla", "Responsable": "Área SNIES", "Actualización": "2025-02-28"},
        {"Fuente": "SACES", "Nombre técnico": "solicitudes", "Descripción": "Entidad de solicitudes", "Tipo": "Tabla", "Responsable": "Área SACES", "Actualización": "2025-03-05"},
        {"Fuente": "SACES", "Nombre técnico": "resoluciones", "Descripción": "Entidad de resoluciones", "Tipo": "Tabla", "Responsable": "Área SACES", "Actualización": "2025-03-05"},
    ]
    if fuente == FUENTE_KEY_TODAS:
        return rows
    return [r for r in rows if r["Fuente"] == fuente]


def get_submodulos_hub() -> list[dict]:
    """Definición de las 4 capacidades del hub (título, descripción, icono, view_id para navegación interna)."""
    return [
        {
            "title": "Catálogo de Datos",
            "description": "Inventario de datasets disponibles, su origen y su uso.",
            "icon": "📋",
            "view_id": "catalogo",
        },
        {
            "title": "Calidad de Datos",
            "description": "Monitoreo de consistencia, completitud y confiabilidad.",
            "icon": "✅",
            "view_id": "calidad",
        },
        {
            "title": "Linaje",
            "description": "Seguimiento del recorrido de los datos desde el origen hasta reportes o dashboards.",
            "icon": "🔄",
            "view_id": "linaje",
        },
        {
            "title": "Metadatos",
            "description": "Definiciones técnicas y de contexto de los activos de información.",
            "icon": "📐",
            "view_id": "metadatos",
        },
    ]
