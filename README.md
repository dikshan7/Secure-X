# Python Web App

A minimal Flask front end with one clearly marked spot to plug in your
own Python program.

## Run it

```
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000, enter an IP address or range, and select **Scan Target**.
The generated report opens at `/report` and is also saved as `vulnerability_report.html`.

## Where to integrate your program

Open `app.py` and find `run_my_program()` near the top — that's the
only function you need to touch. Replace its body with a call into
your actual code. It takes the text from the input box and whatever
string it returns is shown on the page.

```python
def run_my_program(user_input: str) -> str:
    return f"Python processed your input: '{user_input.upper()}'"
```

A couple of common patterns:

**Calling a function from your own module:**
```python
from my_module import analyze

def run_my_program(user_input: str) -> str:
    return analyze(user_input)
```

**Calling an external script:**
```python
import subprocess

def run_my_program(user_input: str) -> str:
    proc = subprocess.run(
        ["python3", "my_script.py", user_input],
        capture_output=True, text=True
    )
    return proc.stdout
```

If your program takes more than a second or two to run, let me know —
a blocking call like the above will hang the page, and it's better
handled with a background thread and a "processing..." status instead.

## Files

- `app.py` — routes + the integration point
- `templates/index.html` — the page (form + result)
- `static/style.css` — basic styling
- `requirements.txt` — dependencies
