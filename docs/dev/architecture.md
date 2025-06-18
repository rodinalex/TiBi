# Architecture


### Project Structure
```
TiBi/
├── TiBi/                 # Main package
│   ├── app.py            # Entry point
│   ├── assets/           # Styling resources
│   ├── controllers/      # Application controllers
│   ├── core/             # Physics functions
│   ├── logic/            # App commands and data serialization
│   ├── models/           # Data models
│   ├── ui/               # UI resources (styles, etc.)
│   └── views/            # UI views
├── app_mac.spec          # macOS build config
├── app_win.spec          # Windows build config
├── app_linux.spec        # Linux build config
├── environment.yml       # Conda dependencies
├── requirements.txt      # pip dependencies
└── README.md
```

---