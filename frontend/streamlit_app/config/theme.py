"""
Identidad visual del aplicativo inspirada en el MEN.
No clona el portal; define paleta y estilos para la plataforma.
"""

# Paleta institucional (referencia MEN: azul, gris, acento)
MEN_PRIMARY = "#003366"      # Azul institucional
MEN_NAV_BG = "#2c3e50"      # Barra superior
MEN_ACCENT = "#c41230"      # Acento (rojo institucional)
MEN_TEXT_LIGHT = "#6c757d"
MEN_CARD_BORDER = "rgba(0, 51, 102, 0.25)"
MEN_CARD_HOVER = "rgba(0, 51, 102, 0.08)"
MEN_FOOTER_BG = "rgba(44, 62, 80, 0.6)"

# CSS global para la app (compatible con tema claro/oscuro de Streamlit)
def get_global_css() -> str:
    return f"""
    <style>
    :root {{
        --men-primary: {MEN_PRIMARY};
        --men-nav-bg: {MEN_NAV_BG};
        --men-accent: {MEN_ACCENT};
        --men-card-border: {MEN_CARD_BORDER};
        --men-card-hover: {MEN_CARD_HOVER};
        --men-footer-bg: {MEN_FOOTER_BG};
        --men-text-muted: {MEN_TEXT_LIGHT};
    }}
    .block-container {{
        padding-top: 2.5rem;
        padding-bottom: 4.5rem;
        padding-left: 3rem;
        padding-right: 3rem;
        max-width: 1350px;
    }}
    /* Header minimalista: logo izq | título centrado | logo der */
    .men-header-bar {{
        margin: 0 -3rem 2rem -3rem;
        padding: 1.25rem 3rem 1.5rem 3rem;
        border-bottom: 1px solid rgba(0,0,0,0.08);
        display: flex;
        align-items: center;
        justify-content: space-between;
        min-height: 140px;
    }}
    .men-header-logo-wrap {{
        flex: 0 0 auto;
        display: flex;
        align-items: center;
    }}
    .men-header-bar img.men-logo {{
        height: 88px;
        width: auto;
        object-fit: contain;
    }}
    .men-header-text {{
        flex: 1;
        text-align: center;
        padding: 0 1.5rem;
    }}
    .men-header-title {{
        font-size: 3.5rem;
        font-weight: 800;
        color: inherit;
        margin: 0;
        line-height: 1.15;
        letter-spacing: -0.02em;
    }}
    .men-header-org {{
        font-size: 2rem;
        font-weight: 600;
        color: var(--men-primary);
        margin: 0.45rem 0 0 0;
        line-height: 1.3;
    }}
    .men-header-subtitle {{
        font-size: 1.75rem;
        color: var(--men-text-muted);
        margin: 0.3rem 0 0 0;
        font-weight: 500;
    }}
    /* Espaciado entre grupos de módulos */
    .men-module-group {{
        margin-bottom: 2.5rem;
    }}
    .men-module-group .men-section-title {{
        margin-bottom: 1rem;
    }}
    /* Cards con acento institucional y espacio entre filas */
    .men-module-card {{
        border: 1px solid var(--men-card-border);
        border-left: 4px solid var(--men-primary);
        border-radius: 10px;
        padding: 0.8rem 1rem;
        min-height: 88px;
        margin-bottom: 1.25rem;
        display: flex;
        flex-direction: column;
        justify-content: center;
        background: rgba(255,255,255,0.02);
        cursor: pointer;
        transition: background 0.2s ease, border-color 0.2s ease, transform 0.2s ease;
    }}
    .men-module-card:hover {{
        background: var(--men-card-hover);
        border-left-color: var(--men-accent);
        transform: translateY(-2px);
    }}
    .men-module-card .men-card-icon {{
        font-size: 1.75rem;
        margin-bottom: 0.35rem;
    }}
    .men-module-card .men-card-title {{
        font-size: 1.1rem;
        font-weight: 700;
        line-height: 1.25;
        color: inherit;
    }}
    /* Footer fijo al fondo de la pantalla para que siempre sea visible al hacer scroll */
    .men-footer {{
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        margin: 0;
        padding: 0.75rem 1rem;
        border-top: 1px solid var(--men-card-border);
        background: rgba(255,255,255,0.97);
        text-align: center;
        font-size: 0.85rem;
        color: var(--men-text-muted);
        z-index: 999;
    }}
    .men-footer a {{
        color: var(--men-primary);
        text-decoration: none;
    }}
    .men-footer a:hover {{
        text-decoration: underline;
    }}
    </style>
    """


def get_module_submenu_css() -> str:
    """
    Estilo de submenú tipo menú (radio): sin bordes, ítems compactos, alineado a la izquierda.
    Reutilizable en otros módulos.
    """
    return f"""
    <style>
    /* Quitar cuadro/borde del expander del submenú */
    [data-testid="stSidebar"] [data-testid="stExpander"]:has(.men-module-submenu-marker),
    [data-testid="stSidebar"] [data-testid="stExpander"]:has(.men-module-submenu-marker) > div,
    [data-testid="stSidebar"] [data-testid="stExpander"]:has(.men-module-submenu-marker) details,
    [data-testid="stSidebar"] [data-testid="stExpander"]:has(.men-module-submenu-marker) summary,
    [data-testid="stSidebar"] section:has([data-testid="stExpander"]:has(.men-module-submenu-marker)) {{
        border: none !important;
        border-radius: 0 !important;
        box-shadow: none !important;
    }}
    [data-testid="stSidebar"] [data-testid="stExpander"]:has(.men-module-submenu-marker),
    [data-testid="stSidebar"] [data-testid="stExpander"]:has(.men-module-submenu-marker) > div,
    [data-testid="stSidebar"] [data-testid="stExpander"]:has(.men-module-submenu-marker) details {{
        border: none !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        background: transparent !important;
    }}
    [data-testid="stSidebar"] [data-testid="stExpander"]:has(.men-module-submenu-marker) details > div {{
        padding-left: 0 !important;
        padding-right: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        gap: 0 !important;
    }}
    /* Menú (st.radio): compacto, alineado a la izquierda, sin espacio entre ítems */
    [data-testid="stSidebar"] [data-testid="stExpander"]:has(.men-module-submenu-marker) [data-testid="stRadio"] {{
        margin: 0 !important;
        padding: 0 !important;
    }}
    [data-testid="stSidebar"] [data-testid="stExpander"]:has(.men-module-submenu-marker) [data-testid="stRadio"] > div {{
        margin: 0 !important;
        padding: 0.2rem 0 !important;
        gap: 0 !important;
    }}
    [data-testid="stSidebar"] [data-testid="stExpander"]:has(.men-module-submenu-marker) [data-testid="stRadio"] label {{
        margin: 0 !important;
        padding: 0 !important;
        justify-content: flex-start !important;
        text-align: left !important;
    }}
    [data-testid="stSidebar"] [data-testid="stExpander"]:has(.men-module-submenu-marker) [data-testid="stRadio"] p {{
        margin: 0 !important;
        margin-block-start: 0 !important;
        margin-block-end: 0 !important;
    }}
    </style>
    """
