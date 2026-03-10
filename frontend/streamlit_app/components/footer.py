import streamlit as st

PORTAL_MEN_URL = "https://www.mineducacion.gov.co/portal/"


def render_footer() -> None:
    """Pie institucional en una línea. Si hay usuario: Subdirección... MEN | 👤 Usuario · Rol — Dependencia | Cerrar sesión."""
    try:
        from auth.auth_service import get_current_user

        user = get_current_user()
    except Exception:
        user = None

    if user:
        user_line = (
            f'👤 <strong>{user.get("nombre", "")}</strong> · {user.get("rol", "")} — {user.get("dependencia", "")}'
            ' | <a href="?logout=1" style="margin-left: 0.5rem;">Cerrar sesión</a>'
        )
        st.markdown(
            f"""
            <div class="men-footer" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
                <span>
                    Subdirección de Aseguramiento de la Calidad — 
                    <a href="{PORTAL_MEN_URL}" target="_blank" rel="noopener"><strong>Ministerio de Educación Nacional</strong></a>
                </span>
                <span>{user_line}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="men-footer">
                Subdirección de Aseguramiento de la Calidad — 
                <a href="{PORTAL_MEN_URL}" target="_blank" rel="noopener"><strong>Ministerio de Educación Nacional</strong></a>
            </div>
            """,
            unsafe_allow_html=True,
        )
