import subprocess

def run_app(name, path):
    """Run a Flask app."""
    print(f"Starting {name}...")
    return subprocess.Popen(["python", path])

if __name__ == "__main__":
    try:
        # Start the web app
        web_app = run_app("Web App", "web-app/app.py")

        # Start the ML app
        ml_app = run_app("ML App", "machine-learning-client/app.py")

        print("Both apps are running. Press Ctrl+C to stop.")

        # Wait for both apps to finish
        web_app.wait()
        ml_app.wait()

    except KeyboardInterrupt:
        print("\nStopping apps...")
        web_app.terminate()
        ml_app.terminate()
