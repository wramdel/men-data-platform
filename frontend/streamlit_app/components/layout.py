import streamlit as st
from components.cards import render_module_card


def render_module_group(group_name: str, modules: list[dict], columns_count: int = 3) -> None:
    st.markdown(
        f"""
        <div class="men-module-group">
            <div class="men-section-title" style="font-size: 1.2rem; font-weight: 700;">{group_name}</div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(columns_count)
    for idx, module in enumerate(modules):
        with cols[idx % columns_count]:
            render_module_card(
                title=module["title"],
                icon=module["icon"],
            )
    st.markdown("</div>", unsafe_allow_html=True)