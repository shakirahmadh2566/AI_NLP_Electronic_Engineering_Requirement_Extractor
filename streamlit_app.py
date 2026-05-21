import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
from app.orchestrator import run_pipeline, get_pipeline_info
from models.llm_client import get_available_models, get_current_model

st.set_page_config(page_title="Flexible Engineering Assistant - Multi-Model", layout="wide")

st.title("🔧 Flexible Engineering Design Assistant")
st.caption("Choose different AI models for each stage of engineering design")

# =========================
# SIDEBAR - Model Selection
# =========================
with st.sidebar:
    st.header("🤖 Model Selection Per Layer")
    
    available_models = get_available_models()
    
    # Model selection for each layer
    st.markdown("### 📌 Layer 1: Requirements Extraction")
    st.caption("Best for: Understanding requirements, parsing text")
    layer1_model = st.selectbox(
        "Model for Requirements",
        options=list(available_models.keys()),
        format_func=lambda x: f"{x} ({available_models[x]['size']}) - {available_models[x]['best_for']}",
        index=0,
        key="layer1_model"
    )
    
    st.markdown("### 📐 Layer 2: System Decomposition")
    st.caption("Best for: Breaking down systems, technical analysis")
    layer2_model = st.selectbox(
        "Model for Decomposition",
        options=list(available_models.keys()),
        format_func=lambda x: f"{x} ({available_models[x]['size']}) - {available_models[x]['best_for']}",
        index=0,
        key="layer2_model"
    )
    
    st.markdown("### ⚙️ Layer 3: Component Recommendations")
    st.caption("Best for: Hardware selection, specifications")
    layer3_model = st.selectbox(
        "Model for Components",
        options=list(available_models.keys()),
        format_func=lambda x: f"{x} ({available_models[x]['size']}) - {available_models[x]['best_for']}",
        index=0,
        key="layer3_model"
    )
    
    st.divider()
    
    # Optimization tips
    with st.expander("💡 Optimization Tips"):
        st.markdown("""
        **For Speed (same model all layers):**
        - Use `qwen2.5:0.5b` for all layers → Fastest
        - Model loads once, reused for all layers
        
        **For Quality (specialized models):**
        - Layer 1: `lfm2.5-thinking` (good at reasoning)
        - Layer 2: `deepseek-coder:1.3b` (good at code/tech)
        - Layer 3: `phi3:mini` or `electricalengineerv2` (hardware)
        
        **Memory Saving:**
        - Models unload automatically when switching
        - Same model between layers = no reload
        """)
    
    # Show current loaded model status
    current = get_current_model()
    if current:
        st.success(f"📌 Currently loaded: `{current}`")
    else:
        st.info("No model loaded - will load on first request")
    
    # Show pipeline configuration
    with st.expander("📋 Pipeline Categories"):
        config = get_pipeline_info()
        st.markdown("**Layer 1:**")
        for cat in config["layer1"]:
            st.write(f"- {cat}")
        st.markdown("**Layer 2:**")
        for cat in config["layer2"]:
            st.write(f"- {cat}")
        st.markdown("**Layer 3:**")
        for cat in config["layer3"]:
            st.write(f"- {cat}")

# =========================
# MAIN CONTENT
# =========================

# Example prompts
st.subheader("📝 Example Problems (Click to try)")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🌱 Soil Moisture Monitor"):
        st.session_state['example_prompt'] = """Design an ESP32-based soil moisture monitoring system for a green farm. 
        Requirements:
        - Monitor soil moisture at 10 different locations
        - Transmit data via WiFi to central dashboard
        - Battery must last 3 months
        - Budget: $50 per node
        - Temperature range: -10°C to 50°C
        - IP65 waterproof rating needed
        - Send alerts when moisture drops below 30%"""

with col2:
    if st.button("🌡️ Temperature Logger"):
        st.session_state['example_prompt'] = """Create a wireless temperature and humidity monitoring system for a cold storage warehouse.
        Requirements:
        - 20 sensors across 5000 sq ft area
        - LoRaWAN communication (no WiFi available)
        - 1 year battery life
        - Accuracy: ±0.5°C, ±3% humidity
        - Temperature range: -20°C to 40°C
        - Data logging every 15 minutes
        - Alert on temperature deviation > 2°C"""

with col3:
    if st.button("💧 Smart Irrigation"):
        st.session_state['example_prompt'] = """Design a smart irrigation controller using ESP32.
        Requirements:
        - Control 4 water valves
        - Weather-based scheduling
        - Manual override via mobile app
        - Rain sensor input
        - Solar powered with battery backup
        - 6 months battery without sun
        - Report water usage daily via WiFi"""

# Text area for problem input
prompt = st.text_area(
    "Enter Your Engineering Problem", 
    value=st.session_state.get('example_prompt', ''),
    height=150,
    placeholder="Example: Design a smart greenhouse monitoring system that tracks temperature, humidity, and soil moisture..."
)

def safe_join(items):
    """Safely convert items to string for display"""
    if not items:
        return "None"
    if isinstance(items, str):
        return items
    if isinstance(items, dict):
        # Convert dict to readable string
        return ", ".join([f"{k}: {v}" for k, v in items.items()])
    if isinstance(items, list):
        string_items = []
        for item in items:
            if isinstance(item, dict):
                string_items.append(str(item))
            else:
                string_items.append(str(item))
        return ", ".join(string_items) if string_items else "None"
    return str(items)

# Run button
if st.button("🚀 Run Pipeline", type="primary"):
    if not prompt.strip():
        st.warning("⚠️ Please enter an engineering problem")
        st.stop()
    
    # Get selected models from session state
    layer1_model = st.session_state.get('layer1_model', 'phi3:mini')
    layer2_model = st.session_state.get('layer2_model', 'phi3:mini')
    layer3_model = st.session_state.get('layer3_model', 'phi3:mini')
    
    # Show selected configuration
    st.info(f"""
    **📋 Running with configuration:**
    - Layer 1 (Requirements): `{layer1_model}`
    - Layer 2 (Decomposition): `{layer2_model}`
    - Layer 3 (Components): `{layer3_model}`
    """)
    
    # Run pipeline
    with st.spinner("🔄 Running AI pipeline... This may take 2-5 minutes depending on models..."):
        result = run_pipeline(prompt, layer1_model, layer2_model, layer3_model)
    
    # =========================
    # TIMING INFORMATION
    # =========================
    if "timing" in result:
        st.subheader("⏱️ Processing Time")
        timing_data = result["timing"]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            layer1_time = timing_data.get('layer1', 0)
            st.metric("Layer 1", f"{layer1_time} sec" if layer1_time else "N/A")
        with col2:
            layer2_time = timing_data.get('layer2', 0)
            st.metric("Layer 2", f"{layer2_time} sec" if layer2_time else "N/A")
        with col3:
            layer3_time = timing_data.get('layer3', 0)
            st.metric("Layer 3", f"{layer3_time} sec" if layer3_time else "N/A")
        with col4:
            total_time = timing_data.get('total', 0)
            if total_time:
                st.metric("Total", f"{total_time} sec")
            else:
                # Calculate total from individual layers
                calc_total = sum([timing_data.get(k, 0) for k in ['layer1', 'layer2', 'layer3']])
                st.metric("Total", f"{calc_total} sec" if calc_total else "N/A")
    else:
        st.warning("Timing information not available")
    
    # Debug expander
    with st.expander("🔍 Debug - Raw JSON Results"):
        st.json(result)
    
    # =========================
    # LAYER 1 - Requirements Table
    # =========================
    st.subheader("📌 Layer 1: Requirements Extraction")
    
    if "layer1" in result and isinstance(result["layer1"], dict):
        layer1_data = result["layer1"]
        
        if "error" in layer1_data:
            st.error(f"Layer 1 Failed: {layer1_data['error']}")
        else:
            l1_data = []
            for category, items in layer1_data.items():
                if items and not category.endswith("_disabled") and not category.startswith("_"):
                    l1_data.append({
                        "Category": category.replace("_", " ").title(),
                        "Requirements": safe_join(items)
                    })
            if l1_data:
                st.dataframe(pd.DataFrame(l1_data), width="stretch")
            else:
                st.info("No requirements extracted")
    else:
        st.error("Layer 1 data not available")
    
    # =========================
    # LAYER 2 - Decomposition Table
    # =========================
    st.subheader("📐 Layer 2: System Decomposition")
    
    if "layer2" in result and isinstance(result["layer2"], dict):
        layer2_data = result["layer2"]
        
        if "error" in layer2_data:
            st.error(f"Layer 2 Failed: {layer2_data['error']}")
        else:
            l2_data = []
            for category, items in layer2_data.items():
                if items and len(items) > 0:
                    l2_data.append({
                        "Module": category.replace("_", " ").title(),
                        "Requirements": safe_join(items)
                    })
                else:
                    l2_data.append({
                        "Module": category.replace("_", " ").title(),
                        "Requirements": "⚠️ No items extracted"
                    })
            if l2_data:
                st.dataframe(pd.DataFrame(l2_data), width="stretch")
            else:
                st.info("No decomposition data available")
    else:
        st.error("Layer 2 data not available")
    
    # =========================
    # LAYER 3 - Components Table
    # =========================
    st.subheader("⚙️ Layer 3: Component Recommendations")
    
    if "layer3" in result and isinstance(result["layer3"], dict):
        layer3_data = result["layer3"]
        
        if "error" in layer3_data:
            st.error(f"Layer 3 Failed: {layer3_data['error']}")
        else:
            if layer3_data:
                for category, components in layer3_data.items():
                    if components and isinstance(components, list) and len(components) > 0:
                        st.markdown(f"### {category.replace('_', ' ').title()}")
                        
                        table_data = []
                        for comp in components:
                            if isinstance(comp, dict):
                                pros = comp.get("pros", [])
                                if isinstance(pros, str):
                                    pros = [pros]
                                cons = comp.get("cons", [])
                                if isinstance(cons, str):
                                    cons = [cons]
                                
                                table_data.append({
                                    "Component": str(comp.get("name", "N/A")),
                                    "Pros": ", ".join(pros[:3]) if pros else "None listed",
                                    "Cons": ", ".join(cons[:2]) if cons else "None listed",
                                    "Evidence Source": str(comp.get("evidence_source", "LLM Knowledge"))[:100],
                                    "Use Case": str(comp.get("use_case", "General purpose"))[:80]
                                })
                        
                        if table_data:
                            df = pd.DataFrame(table_data)
                            st.dataframe(df, width="stretch", height=min(400, len(table_data) * 35 + 38))
                        else:
                            st.info(f"No valid component data for {category}")
                    else:
                        st.info(f"No components found for {category}")
            else:
                st.warning("Layer 3 returned empty results")
    else:
        st.error("Layer 3 data not available")
    
    # Success message
    if "timing" in result and result["timing"].get('total'):
        st.success(f"✅ Analysis complete! Total time: {result['timing']['total']} seconds")
    elif "timing" in result:
        # Calculate total from individual layers
        layer1_t = result["timing"].get('layer1', 0)
        layer2_t = result["timing"].get('layer2', 0)
        layer3_t = result["timing"].get('layer3', 0)
        calc_total = layer1_t + layer2_t + layer3_t
        if calc_total > 0:
            st.success(f"✅ Analysis complete! Total time: {calc_total} seconds")
        else:
            st.success("✅ Analysis complete!")
    else:
        st.success("✅ Analysis complete!")
    
    # Show which model was used for what
    st.caption(f"""
    📊 **Model Usage Summary:**
    - Layer 1 (Requirements): `{layer1_model}`
    - Layer 2 (Decomposition): `{layer2_model}`
    - Layer 3 (Components): `{layer3_model}`
    """)

# Footer
st.divider()
st.caption("🔧 Flexible Engineering Assistant | Supports multiple AI models | Auto-unloads when switching models | Web search enabled for components")