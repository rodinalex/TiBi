The project follows the MVC (Model-View-Controller) approach. In addition, it makes use of the Command pattern for Undo/Redo functionality, as well as Workers for multi-thread processes. 

# Project Structure

```
TiBi/
├── assets/                 # Documentation/Demo assets
├── docs/                   # Documentation 
├── TiBi/                   # Main package
│   ├── app.py              # Entry point
│   ├── assets/             # Styling resources (e.g., icons)
│   ├── controllers/        # Application controllers
│   ├── core/               # Physics functions
│   ├── logic/              # App commands and data serialization
│   │   ├── commands/       # Commands for Undo/Redo actions
│   │   ├── serialization/  # Data serialization
│   │   └── workers/        # Workers for parallel threads
│   ├── models/             # Data models
│   ├── ui/                 # UI resources (styles, etc.)
│   │   ├── actions/        # Action manager
│   │   ├── styles/         # UI styling
│   │   └── ...             # Constants and Utility *.py files
│   └── views/              # UI views
│       ├── panels/         # View components
│       ├── widgets/        # View widgets
│       └── ...             # Principal View *.py files
├── app_mac.spec            # macOS build config
├── app_win.spec            # Windows build config
├── app_linux.spec          # Linux build config
├── environment.yml         # Conda dependencies
├── requirements.txt        # pip dependencies
├── mkdocs.yml              # MkDocs settings
└── README.md
```

---