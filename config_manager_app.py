"""
Configuration Manager for Engineering Assistant
Run this separately to manage categories: streamlit run config_manager_app.py
"""

import streamlit as st
import config_manager as cm
import os

st.set_page_config(page_title="Config Manager - All 3 Layers", layout="wide")

st.title("🔧 Engineering Assistant - Configuration Manager")
st.caption("Add, remove, or modify categories in ALL 3 layers - Changes apply immediately")

# Load current config
config = cm.load_config()

# =========================
# SIDEBAR - Info
# =========================
with st.sidebar:
    st.header("📋 Instructions")
    st.markdown("""
    1. **Add Category**: Fill form and click Add
    2. **Toggle Enabled/Disabled**: Use switches below
    3. **Changes auto-save** to config files
    4. **Main app** will use new config on next run
    
    **Layer Purposes:**
    - **Layer 1**: Requirements extraction
    - **Layer 2**: System decomposition  
    - **Layer 3**: Component recommendations
    """)
    
    st.divider()
    
    if st.button("🔄 Regenerate All Config Files"):
        cm.regenerate_config_files()
        st.success("✅ Config files regenerated!")
    
    st.divider()
    
    # Show config file location
    st.info(f"💾 Config file: `{os.path.abspath('dynamic_config.json')}`")
    
    if st.button("🗑️ Reset to Default Configuration"):
        if st.checkbox("Confirm reset"):
            os.remove("dynamic_config.json")
            st.success("Config deleted! Restart app to recreate.")
            st.rerun()

# =========================
# ADD NEW CATEGORY - ALL 3 LAYERS
# =========================
st.header("➕ Add New Category")

tab1, tab2, tab3 = st.tabs(["Layer 1 (Requirements)", "Layer 2 (Decomposition)", "Layer 3 (Components)"])

# ========== LAYER 1 ADD ==========
with tab1:
    st.subheader("Add to Requirements Extraction")
    
    col1, col2 = st.columns(2)
    with col1:
        new_l1_name = st.text_input(
            "Category Name", 
            key="new_l1_name",
            placeholder="e.g., 'cost_analysis' or 'regulatory_compliance'",
            help="Use snake_case: no spaces, use underscores"
        )
    with col2:
        new_l1_desc = st.text_input(
            "Description", 
            key="new_l1_desc",
            placeholder="What this category represents",
            help="Example: 'Budget constraints and cost optimization'"
        )
    
    new_l1_hint = st.text_input(
        "Prompt Hint", 
        key="new_l1_hint",
        placeholder="What to extract",
        help="Example: 'List cost constraints, budget limits, and ROI requirements'"
    )
    
    if st.button("➕ Add to Layer 1", key="add_l1"):
        if new_l1_name and new_l1_desc:
            try:
                cm.add_layer1_category(new_l1_name, new_l1_desc, new_l1_hint)
                st.success(f"✅ Added '{new_l1_name}' to Layer 1!")
                st.balloons()
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please fill at least Name and Description")

# ========== LAYER 2 ADD ==========
with tab2:
    st.subheader("Add to System Decomposition")
    st.caption("Note: Adding to Layer 2 automatically creates Layer 3 category")
    
    col1, col2 = st.columns(2)
    with col1:
        new_l2_name = st.text_input(
            "Category Name", 
            key="new_l2_name",
            placeholder="e.g., 'thermal_management' or 'mechanical_structure'",
            help="Use snake_case: no spaces, use underscores"
        )
    with col2:
        new_l2_desc = st.text_input(
            "Description", 
            key="new_l2_desc",
            placeholder="What this category represents",
            help="Example: 'Heat dissipation, cooling requirements'"
        )
    
    new_l2_example = st.text_input(
        "Example Items", 
        key="new_l2_example",
        placeholder="Comma separated examples",
        help="Example: 'Heatsinks, fans, thermal paste, ventilation'"
    )
    
    if st.button("➕ Add to Layer 2", key="add_l2"):
        if new_l2_name and new_l2_desc:
            try:
                cm.add_layer2_category(new_l2_name, new_l2_desc, new_l2_example)
                st.success(f"✅ Added '{new_l2_name}' to Layer 2!")
                st.info(f"📌 Layer 3 category '{new_l2_name}_components' auto-created!")
                st.balloons()
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please fill at least Name and Description")

# ========== LAYER 3 ADD ==========
with tab3:
    st.subheader("Add Directly to Component Recommendations")
    st.caption("Add standalone Layer 3 category (not linked to Layer 2)")
    
    col1, col2 = st.columns(2)
    with col1:
        new_l3_name = st.text_input(
            "Category Name", 
            key="new_l3_name",
            placeholder="e.g., 'wiring_harness' or 'mounting_hardware'",
            help="Use snake_case: no spaces, use underscores"
        )
    with col2:
        new_l3_desc = st.text_input(
            "Description", 
            key="new_l3_desc",
            placeholder="What components this covers",
            help="Example: 'Cables, connectors, wiring accessories'"
        )
    
    if st.button("➕ Add to Layer 3", key="add_l3"):
        if new_l3_name and new_l3_desc:
            try:
                cm.add_layer3_category(new_l3_name, new_l3_desc)
                st.success(f"✅ Added '{new_l3_name}' to Layer 3!")
                st.balloons()
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please fill Name and Description")

# =========================
# VIEW AND EDIT CATEGORIES - ALL 3 LAYERS
# =========================
st.header("📋 Current Categories")

# ========== LAYER 1 ==========
with st.expander("Layer 1: Requirements Categories", expanded=True):
    st.markdown("Toggle switches to enable/disable categories")
    st.caption("These categories appear in the requirements extraction phase")
    
    for cat, info in config["layer1"].items():
        col1, col2, col3 = st.columns([2, 3, 1])
        with col1:
            st.markdown(f"**{cat}**")
        with col2:
            st.caption(info['description'])
        with col3:
            new_state = st.toggle("Enabled", value=info['enabled'], key=f"l1_{cat}")
            if new_state != info['enabled']:
                cm.enable_category("layer1", cat, new_state)
                st.rerun()

# ========== LAYER 2 ==========
with st.expander("Layer 2: Decomposition Categories", expanded=True):
    st.markdown("Toggle switches to enable/disable categories")
    st.caption("These categories appear in the system decomposition phase")
    
    for cat, info in config["layer2"].items():
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
        with col1:
            st.markdown(f"**{cat}**")
        with col2:
            st.caption(info['description'])
        with col3:
            if info.get('example'):
                st.caption(f"📌 {info['example'][:40]}...")
        with col4:
            new_state = st.toggle("Enabled", value=info['enabled'], key=f"l2_{cat}")
            if new_state != info['enabled']:
                cm.enable_category("layer2", cat, new_state)
                st.rerun()

# ========== LAYER 3 ==========
with st.expander("Layer 3: Component Categories", expanded=True):
    st.markdown("Toggle switches to enable/disable categories")
    st.caption("These categories appear in the component recommendation phase")
    
    # Show mapping first
    st.markdown("**Layer 2 → Layer 3 Mapping:**")
    for l2, l3 in config["layer3_mapping"].items():
        if l2 in config["layer2"] and config["layer2"][l2]["enabled"]:
            st.caption(f"`{l2}` → `{l3}`")
    
    st.divider()
    
    # Layer 3 categories
    for cat, info in config["layer3"].items():
        col1, col2, col3 = st.columns([2, 3, 1])
        with col1:
            st.markdown(f"**{cat}**")
        with col2:
            st.caption(info['description'])
        with col3:
            new_state = st.toggle("Enabled", value=info['enabled'], key=f"l3_{cat}")
            if new_state != info['enabled']:
                cm.enable_category("layer3", cat, new_state)
                st.rerun()

# =========================
# DELETE/DISABLE CATEGORY SECTION
# =========================
st.header("🗑️ Disable Categories")
st.caption("Use toggles above to enable/disable. Disabled categories won't appear in pipeline.")

# =========================
# RAW CONFIG VIEW
# =========================
with st.expander("📄 View Raw Configuration (JSON)"):
    st.json(config)

# =========================
# STATISTICS
# =========================
st.header("📊 Statistics")

col1, col2, col3 = st.columns(3)
with col1:
    enabled_l1 = sum(1 for v in config["layer1"].values() if v["enabled"])
    st.metric("Layer 1 Categories", f"{enabled_l1}/{len(config['layer1'])}")
with col2:
    enabled_l2 = sum(1 for v in config["layer2"].values() if v["enabled"])
    st.metric("Layer 2 Categories", f"{enabled_l2}/{len(config['layer2'])}")
with col3:
    enabled_l3 = sum(1 for v in config["layer3"].values() if v["enabled"])
    st.metric("Layer 3 Categories", f"{enabled_l3}/{len(config['layer3'])}")

# =========================
# QUICK ACTIONS
# =========================
st.divider()
st.subheader("⚡ Quick Actions")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("✅ Enable All Categories"):
        for cat in config["layer1"]:
            cm.enable_category("layer1", cat, True)
        for cat in config["layer2"]:
            cm.enable_category("layer2", cat, True)
        for cat in config["layer3"]:
            cm.enable_category("layer3", cat, True)
        st.success("All categories enabled!")
        st.rerun()

with col2:
    if st.button("❌ Disable All Categories"):
        for cat in config["layer1"]:
            cm.enable_category("layer1", cat, False)
        for cat in config["layer2"]:
            cm.enable_category("layer2", cat, False)
        for cat in config["layer3"]:
            cm.enable_category("layer3", cat, False)
        st.warning("All categories disabled!")
        st.rerun()

with col3:
    if st.button("📋 Show Config Path"):
        st.code(f"Config file: {os.path.abspath('dynamic_config.json')}")

st.caption("⚠️ Note: Changes take effect immediately. Main app will use new config on next run.")