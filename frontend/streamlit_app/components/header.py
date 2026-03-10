import base64
import os
import streamlit as st


def render_header(
    *,
    logo_path: str | None = None,
    title: str = "Ministerio de Educación Nacional",
    org_line: str = "Subdirección de Aseguramiento de la Calidad",
    subtitle: str = "Plataforma de Gestión y Analítica de Datos",
) -> None:
    """
    Barra institucional: título, línea institucional y subtítulo.
    (Usuario y Cerrar sesión se muestran en el footer.)
    """
    show_logo = logo_path and os.path.isfile(logo_path)
    logo_data_uri = ""
    if show_logo:
        ext = os.path.splitext(logo_path)[1].lower()
        mime = "image/png" if ext == ".png" else "image/jpeg" if ext in (".jpg", ".jpeg") else "image/svg+xml"
        with open(logo_path, "rb") as f:
            logo_data_uri = f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"

    if show_logo and logo_data_uri:
        st.markdown(
            f"""
            <div class="men-header-bar">
                <div class="men-header-logo-wrap">
                    <img src="{logo_data_uri}" alt="MEN" class="men-logo" />
                </div>
                <div class="men-header-text">
                    <p class="men-header-title">{title}</p>
                    <p class="men-header-org">{org_line}</p>
                    <p class="men-header-subtitle">{subtitle}</p>
                </div>
                <div class="men-header-logo-wrap">
                    <img src="{logo_data_uri}" alt="MEN" class="men-logo" />
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
        f"""
        <div class="men-header-bar">
            <div class="men-header-logo-wrap"></div>
            <div class="men-header-text">
                <p class="men-header-title">{title}</p>
                <p class="men-header-org">{org_line}</p>
                <p class="men-header-subtitle">{subtitle}</p>
            </div>
            <div class="men-header-logo-wrap"></div>
        </div>
        """,
            unsafe_allow_html=True,
        )
