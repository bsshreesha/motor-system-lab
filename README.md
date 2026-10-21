# Motor System Lab — MATLAB-inspired Python UI

This version keeps M1, M2, and M3 in the same app. Each motor has independent electrical parameters. The System analysis tab shows all three together, with a comparison table, charts, and CSV export.

## Windows PowerShell setup

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

If PowerShell blocks activation, run this and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Open the local URL Streamlit prints, usually http://localhost:8501.

## Engineering caveat
This is an educational steady-state DC motor model. Default motor constants are illustrative, and the time-response plot uses assumed time constants. For validation, use real datasheets, include inertia/inductance/friction/controller dynamics, and compare predictions against measured hardware.


## Mechanical motion visualization
The UI includes an animated SVG/CSS motor–gearbox–drum view for each motor and a three-motor overview. The visible output speed reduction and wobble are illustrative mappings for demonstrating degraded transmission, not a calibrated physical wear model.
