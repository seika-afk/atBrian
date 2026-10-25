from jev_call import call
import time


TEXT = input("> ")
start = time.perf_counter()
print(call(TEXT))
end= time.perf_counter()
print(f"Time taken: {end - start:.4f} seconds")
