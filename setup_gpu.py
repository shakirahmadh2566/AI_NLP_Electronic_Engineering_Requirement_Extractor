#!/usr/bin/env python3
"""
GPU Configuration for phi3:mini
Run this once to verify GPU is working
"""

import ollama
import subprocess
import sys

def check_gpu():
    """Check if GPU is available"""
    print("="*60)
    print("GPU CONFIGURATION CHECK")
    print("="*60)
    
    # Check NVIDIA GPU
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total,memory.free', '--format=csv'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("\n✓ NVIDIA GPU Detected:")
            lines = result.stdout.strip().split('\n')
            for line in lines[1:]:  # Skip header
                print(f"  {line}")
        else:
            print("\n✗ NVIDIA GPU not found")
    except FileNotFoundError:
        print("\n✗ nvidia-smi not found - NVIDIA drivers not installed")
    
    # Test Ollama with GPU
    print("\n" + "="*60)
    print("TESTING OLLAMA GPU MODE")
    print("="*60)
    
    test_prompt = "Say 'GPU is working' in one word"
    
    try:
        response = ollama.generate(
            model="phi3:mini",
            prompt=test_prompt,
            options={
                "num_gpu": 1,
                "main_gpu": 0,
                "num_predict": 10
            }
        )
        print(f"\n✓ Ollama GPU test successful!")
        print(f"  Response: {response['response']}")
        print(f"  Model: phi3:mini")
        
        # Show process info
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        if result.returncode == 0:
            print("\n  Current GPU Status:")
            # Show only relevant lines
            for line in result.stdout.split('\n')[5:10]:
                if 'ollama' in line or 'python' in line or 'MiB' in line:
                    print(f"    {line}")
                    
    except Exception as e:
        print(f"\n✗ GPU test failed: {e}")
        print("  Make sure Ollama is running: 'ollama serve'")
    
    print("\n" + "="*60)
    print("RECOMMENDATIONS")
    print("="*60)
    print("1. Run: ollama serve (in separate terminal)")
    print("2. Set environment variable: export OLLAMA_NUM_GPU=1")
    print("3. For more GPU memory: export OLLAMA_GPU_OVERHEAD=0")
    print("4. Verify with: nvidia-smi (should show ollama process)")

if __name__ == "__main__":
    check_gpu()