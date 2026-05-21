from app.orchestrator import run_pipeline

prompt = input("Enter engineering problem:\n")

result = run_pipeline(prompt)

print("\nFINAL OUTPUT:\n")

print(result)