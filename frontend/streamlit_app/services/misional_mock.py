"""
Datos mock para módulos misionales.
Alineado con los tres ejes: información rápida, consolidación y seguimiento a funcionarios.
"""


def get_dashboard_kpis(module_id: str) -> list[dict]:
    """KPIs ejecutivos: volumen de casos, estados generales, alertas rápidas."""
    return [
        {"label": "Casos / trámites activos", "value": "24", "icon": "📋"},
        {"label": "Completados (mes)", "value": "156", "icon": "✅"},
        {"label": "En revisión", "value": "12", "icon": "🔄"},
        {"label": "Alertas (vencimientos)", "value": "3", "icon": "⚠️"},
    ]


def get_consultas_results_placeholder() -> list[dict]:
    """Resultados de consulta: búsqueda por institución, programa, trámite, expediente."""
    return [
        {
            "Expediente": "EXP-2025-001",
            "Institución": "Institución A",
            "Programa / Trámite": "Registro calificado",
            "Estado": "En trámite",
            "Responsable": "Área 1",
            "Fecha ingreso": "2025-03-01",
        },
        {
            "Expediente": "EXP-2025-002",
            "Institución": "Institución B",
            "Programa / Trámite": "Acreditación",
            "Estado": "Completado",
            "Responsable": "Área 2",
            "Fecha ingreso": "2025-03-02",
        },
        {
            "Expediente": "EXP-2025-003",
            "Institución": "Institución C",
            "Programa / Trámite": "Convalidación",
            "Estado": "En revisión",
            "Responsable": "Área 1",
            "Fecha ingreso": "2025-03-03",
        },
    ]


def get_actividades_placeholder() -> list[dict]:
    """Lista operativa: tareas con responsable, fecha límite, estado y prioridad."""
    return [
        {
            "responsable": "María Pérez",
            "actividad": "Revisión de documentación",
            "fecha_limite": "2025-03-15",
            "estado": "En curso",
            "prioridad": "Alta",
        },
        {
            "responsable": "Juan García",
            "actividad": "Validación de requisitos",
            "fecha_limite": "2025-03-20",
            "estado": "Pendiente",
            "prioridad": "Media",
        },
        {
            "responsable": "María Pérez",
            "actividad": "Emisión de concepto técnico",
            "fecha_limite": "2025-03-10",
            "estado": "Completado",
            "prioridad": "Alta",
        },
        {
            "responsable": "Ana López",
            "actividad": "Seguimiento a observaciones",
            "fecha_limite": "2025-03-08",
            "estado": "Vencida",
            "prioridad": "Alta",
        },
    ]


def get_reportes_placeholder() -> list[dict]:
    """Reportes formales: listados, históricos, por responsable o por estado."""
    return [
        {
            "Reporte": "Reporte mensual de trámites",
            "Periodo": "Mensual",
            "Última actualización": "2025-03-01",
        },
        {
            "Reporte": "Reporte por responsable / equipo",
            "Periodo": "Semanal",
            "Última actualización": "2025-03-07",
        },
        {
            "Reporte": "Histórico de expedientes por estado",
            "Periodo": "Trimestral",
            "Última actualización": "2025-02-28",
        },
        {
            "Reporte": "Resumen ejecutivo del módulo",
            "Periodo": "Semanal",
            "Última actualización": "2025-03-07",
        },
    ]


def get_indicadores_seguimiento_kpis(module_id: str) -> list[dict]:
    """Indicadores de seguimiento a funcionarios: carga, tareas, tiempos."""
    return [
        {"label": "Funcionarios con tareas asignadas", "value": "8", "icon": "👥"},
        {"label": "Total tareas activas", "value": "42", "icon": "📋"},
        {"label": "Tareas vencidas", "value": "5", "icon": "⚠️"},
        {"label": "Tareas cerradas (mes)", "value": "128", "icon": "✅"},
        {"label": "Tiempo promedio de gestión (días)", "value": "7,2", "icon": "⏱"},
        {"label": "Carga promedio por funcionario", "value": "5,3", "icon": "📊"},
    ]


def get_indicadores_avance_por_responsable() -> list[dict]:
    """Tabla placeholder: avance del proceso por responsable."""
    return [
        {"Responsable": "María Pérez", "Tareas asignadas": "12", "Completadas": "9", "Pendientes": "2", "Vencidas": "1", "Avance %": "75"},
        {"Responsable": "Juan García", "Tareas asignadas": "8", "Completadas": "6", "Pendientes": "2", "Vencidas": "0", "Avance %": "75"},
        {"Responsable": "Ana López", "Tareas asignadas": "10", "Completadas": "7", "Pendientes": "1", "Vencidas": "2", "Avance %": "70"},
    ]


def get_indicadores_distribucion_estado() -> list[dict]:
    """Tabla placeholder: distribución de actividades por estado."""
    return [
        {"Estado": "En curso", "Cantidad": "18", "Porcentaje": "43%"},
        {"Estado": "Pendiente", "Cantidad": "19", "Porcentaje": "45%"},
        {"Estado": "Vencida", "Cantidad": "5", "Porcentaje": "12%"},
    ]
