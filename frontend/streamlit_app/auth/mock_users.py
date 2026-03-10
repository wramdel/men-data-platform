"""
Usuarios mock para autenticación en desarrollo.
Reemplazar por LDAP, Azure AD o base de datos en producción.
"""

# username -> { password, nombre, rol, dependencia }
MOCK_USERS = {
    "admin": {
        "password": "admin123",
        "nombre": "Administrador",
        "rol": "Administrador",
        "dependencia": "MEN",
    },
    "analista": {
        "password": "analista123",
        "nombre": "Analista MEN",
        "rol": "Analista",
        "dependencia": "Subdirección",
    },
    "funcionario": {
        "password": "func123",
        "nombre": "Juan Pérez",
        "rol": "Profesional",
        "dependencia": "Subdirección de Aseguramiento de la Calidad",
    },
}
