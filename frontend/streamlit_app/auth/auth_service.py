"""
Servicio de autenticación. Usa session_state para la sesión actual.
Preparado para sustituir por LDAP, Azure AD o backend real.
"""
import streamlit as st

from auth.mock_users import MOCK_USERS

SESSION_KEY_USER = "authenticated_user"


def login(username: str, password: str) -> bool:
    """
    Valida credenciales contra usuarios mock y, si son correctas, guarda el usuario en sesión.
    Devuelve True si el login fue exitoso.
    """
    username = (username or "").strip().lower()
    password = (password or "").strip()
    if not username or not password:
        return False
    user_data = MOCK_USERS.get(username)
    if not user_data or user_data["password"] != password:
        return False
    st.session_state[SESSION_KEY_USER] = {
        "username": username,
        "nombre": user_data["nombre"],
        "rol": user_data["rol"],
        "dependencia": user_data["dependencia"],
    }
    return True


def logout() -> None:
    """Cierra la sesión eliminando el usuario de session_state."""
    if SESSION_KEY_USER in st.session_state:
        del st.session_state[SESSION_KEY_USER]


def is_authenticated() -> bool:
    """Indica si hay un usuario autenticado en la sesión."""
    return SESSION_KEY_USER in st.session_state and st.session_state[SESSION_KEY_USER] is not None


def get_current_user() -> dict | None:
    """
    Devuelve el usuario actual { username, nombre, rol, dependencia } o None.
    """
    return st.session_state.get(SESSION_KEY_USER)
