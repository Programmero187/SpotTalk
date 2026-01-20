

1. Build the Environment:
``` 
cd spotty
python -m venv venv
venv/Scripts/actiavte.ps1
pip install -r requirements
pip installl -e .
```

2. set the environmental variables to the appropriate keys:
```
$env:PICOVOICE_ACCESS_KEY="your_picovoice_access_key"
$env:OPENAI_API_KEY="your_openai_api_key"  
```


3. start the main interface:
```
python main_interface.py --socket --socket-host 127.0.0.1 --socket-port 8765   
```
