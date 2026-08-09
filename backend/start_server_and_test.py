import asyncio
import os
import signal
import subprocess
import time
import httpx

def kill_port_8000():
    try:
        # Find process listening on 8000
        output = subprocess.check_output("netstat -ano | findstr :8000", shell=True).decode()
        pids = set()
        for line in output.strip().split("\n"):
            parts = line.split()
            if len(parts) >= 5 and "LISTENING" in parts[3]:
                pids.add(parts[4])
        for pid in pids:
            print(f"Killing process PID {pid} on port 8000...")
            subprocess.call(f"taskkill /F /PID {pid}", shell=True)
    except Exception as e:
        print("No process on port 8000 to kill:", e)

def main():
    kill_port_8000()
    time.sleep(1)

    print("Starting fresh uvicorn server on port 8000...")
    log_file = open("uvicorn_test.log", "w", encoding="utf-8")
    proc = subprocess.Popen(
        [r".\venv\Scripts\python.exe", "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--log-level", "debug"],
        cwd=r"C:\Users\MSi\.gemini\antigravity\scratch\aimos\backend",
        stdout=log_file,
        stderr=subprocess.STDOUT
    )

    # Wait for server to start
    time.sleep(3)

    try:
        print("Sending POST request to http://127.0.0.1:8000/api/v1/agents/research ...")
        res = httpx.post(
            "http://127.0.0.1:8000/api/v1/agents/research",
            json={"product_name": "Bánh Trung Thu", "target_market": "Vietnam", "provider": "mock"},
            timeout=10.0
        )
        print("HTTP STATUS CODE:", res.status_code)
        print("HTTP RESPONSE HEADERS:", dict(res.headers))
        print("HTTP RESPONSE BODY:", res.text)
    finally:
        proc.terminate()
        log_file.close()
        time.sleep(1)
        if os.path.exists("uvicorn_test.log"):
            with open("uvicorn_test.log", "r", encoding="utf-8", errors="ignore") as f:
                print("--- SERVER LOGS ---")
                print(f.read())

if __name__ == "__main__":
    main()
