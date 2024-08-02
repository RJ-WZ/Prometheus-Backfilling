# Prometheus-Backfilling Executable Program

1. Download PyInstaller
```pip install pyinstaller```

2. Change directory to the Python script directory
```cd <path>```

3. Compile Python script to .exe (--name = output name; --onefile = single executable file)
```pyinstaller --name "Prometheus Backfilling" --onefile prometheus_backfill.py```

5. Go to the /dist directory to find the .exe file 
