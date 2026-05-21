import time
from layers.layer1_requirements.extractor import extract_requirements
from layers.layer2_decomposition.decomposer import decompose
from layers.layer3_components.recommender import recommend_components
from layers.layer1_requirements.config import get_enabled_categories as get_l1_categories
from layers.layer2_decomposition.config import get_enabled_categories as get_l2_categories
from layers.layer3_components.config import get_enabled_categories as get_l3_categories
from models.llm_client import get_current_model, reset_model
import gc

def run_pipeline(prompt, layer1_model, layer2_model, layer3_model):
    """Run pipeline with smart model management - only unload if switching"""
    
    results = {}
    timing = {}
    
    # Reset at start of pipeline
    reset_model()
    
    # =========================
    # LAYER 1 - Requirements
    # =========================
    print(f"\n{'='*60}")
    print(f"📌 LAYER 1: Requirements Extraction")
    print(f"   Model: {layer1_model}")
    print(f"{'='*60}")
    
    start_time = time.time()
    try:
        results["layer1"] = extract_requirements(prompt, layer1_model)
        layer1_time = time.time() - start_time
        timing["layer1"] = round(layer1_time, 2)
        print(f"✅ Layer 1 complete in {layer1_time:.2f}s")
        gc.collect()
    except Exception as e:
        results["layer1"] = {"error": f"Layer 1 failed: {str(e)}"}
        timing["layer1"] = round(time.time() - start_time, 2)
        # Calculate total even on error
        timing["total"] = timing["layer1"]
        results["timing"] = timing
        return results
    
    # =========================
    # LAYER 2 - Decomposition
    # =========================
    print(f"\n{'='*60}")
    if layer2_model == layer1_model:
        print(f"📐 LAYER 2: System Decomposition")
        print(f"   Model: {layer2_model} (♻️ REUSED from Layer 1)")
    else:
        print(f"📐 LAYER 2: System Decomposition")
        print(f"   Model: {layer2_model} (🔄 NEW - will unload previous)")
    print(f"{'='*60}")
    
    start_time = time.time()
    try:
        results["layer2"] = decompose(results["layer1"], layer2_model)
        layer2_time = time.time() - start_time
        timing["layer2"] = round(layer2_time, 2)
        print(f"✅ Layer 2 complete in {layer2_time:.2f}s")
        gc.collect()
    except Exception as e:
        results["layer2"] = {"error": f"Layer 2 failed: {str(e)}"}
        timing["layer2"] = round(time.time() - start_time, 2)
        # Calculate total with available times
        timing["total"] = round(sum([timing.get('layer1', 0), timing.get('layer2', 0)]), 2)
        results["timing"] = timing
        return results
    
    # =========================
    # LAYER 3 - Components
    # =========================
    print(f"\n{'='*60}")
    if layer3_model == layer2_model:
        print(f"⚙️ LAYER 3: Component Recommendations")
        print(f"   Model: {layer3_model} (♻️ REUSED from Layer 2)")
    elif layer3_model == layer1_model and layer2_model != layer1_model:
        print(f"⚙️ LAYER 3: Component Recommendations")
        print(f"   Model: {layer3_model} (🔄 RELOADING from Layer 1)")
    else:
        print(f"⚙️ LAYER 3: Component Recommendations")
        print(f"   Model: {layer3_model} (🔄 NEW model)")
    print(f"{'='*60}")
    
    start_time = time.time()
    try:
        results["layer3"] = recommend_components(results["layer2"], layer3_model)
        layer3_time = time.time() - start_time
        timing["layer3"] = round(layer3_time, 2)
        print(f"✅ Layer 3 complete in {layer3_time:.2f}s")
        gc.collect()
    except Exception as e:
        results["layer3"] = {"error": f"Layer 3 failed: {str(e)}"}
        timing["layer3"] = round(time.time() - start_time, 2)
    
    # =========================
    # CALCULATE TOTAL TIME
    # =========================
    # Ensure all timing values exist
    timing["layer1"] = timing.get("layer1", 0)
    timing["layer2"] = timing.get("layer2", 0)
    timing["layer3"] = timing.get("layer3", 0)
    timing["total"] = round(timing["layer1"] + timing["layer2"] + timing["layer3"], 2)
    
    results["timing"] = timing
    
    # =========================
    # PRINT SUMMARY
    # =========================
    print(f"\n{'='*60}")
    print(f"📊 PIPELINE COMPLETE - SUMMARY")
    print(f"{'='*60}")
    print(f"   Layer 1: {layer1_model} - {timing['layer1']}s")
    if layer2_model == layer1_model:
        print(f"   Layer 2: {layer2_model} - {timing['layer2']}s (♻️ reused)")
    else:
        print(f"   Layer 2: {layer2_model} - {timing['layer2']}s (🔄 loaded fresh)")
    if layer3_model == layer2_model:
        print(f"   Layer 3: {layer3_model} - {timing['layer3']}s (♻️ reused)")
    elif layer3_model == layer1_model and layer2_model != layer1_model:
        print(f"   Layer 3: {layer3_model} - {timing['layer3']}s (🔄 reloaded)")
    else:
        print(f"   Layer 3: {layer3_model} - {timing['layer3']}s (🔄 loaded fresh)")
    print(f"{'='*60}")
    print(f"   ✅ TOTAL TIME: {timing['total']} seconds")
    print(f"{'='*60}")
    
    # Show current loaded model
    current_model = get_current_model()
    if current_model:
        print(f"\n💡 Model '{current_model}' remains loaded for next run")
    else:
        print(f"\n💡 No model currently loaded")
    
    return results


def get_pipeline_info():
    """Get current pipeline configuration"""
    return {
        "layer1": list(get_l1_categories().keys()),
        "layer2": list(get_l2_categories().keys()),
        "layer3": list(get_l3_categories().keys())
    }