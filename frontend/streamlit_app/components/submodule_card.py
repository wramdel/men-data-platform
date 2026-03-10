"""
Tarjeta de submódulo con título, descripción y navegación (Gobierno de Datos).
Soporta navegación interna (view_id + estado) o enlace a página (page).
"""
import streamlit as st


def render_submodule_card(
    title: str,
    description: str,
    icon: str,
    *,
    page: str | None = None,
    view_id: str | None = None,
    session_state_key: str = "governance_view",
    key: str | None = None,
) -> None:
    """
    Muestra una tarjeta con título, descripción y botón "Acceder".
    - Si view_id está definido: botón que actualiza session_state y rerun (navegación interna).
    - Si page está definido: st.page_link a esa página.
    """
    with st.container():
        st.markdown(
            f"""
            <div class="men-module-card" style="min-height: 100px;">
                <div class="men-card-icon">{icon}</div>
                <div class="men-card-title">{title}</div>
                <p style="margin: 0.4rem 0 0 0; font-size: 0.85rem; color: var(--men-text-muted); line-height: 1.35;">
                    {description}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if view_id is not None:
            if st.button("Acceder", key=key or f"card_{view_id}"):
                st.session_state[session_state_key] = view_id
                st.session_state["gov_nav_radio"] = view_id  # mantiene el menú radio en sync
                st.rerun()
        elif page is not None:
            st.page_link(page, label="Acceder")
