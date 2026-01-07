## Project Structure

asana-simulation/
│
├── logs/
│   └── generation.log
│
├── output/
│   └── asana_simulation.sqlite
│
├── src/
│   │
│   ├── __pycache__/           # Python bytecode cache
│   │
│   ├── generators/            # Data generation modules
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   ├── comments.py
│   │   ├── custom_fields.py
│   │   ├── projects.py
│   │   ├── tags.py
│   │   ├── tasks.py
│   │   ├── teams.py
│   │   └── users.py
│   │
│   ├── models/                # Data models
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   └── base.py
│   │
│   ├── scrapers/              # Web scraping utilities
│   │   ├── __init__.py
│   │   └── github_scraper.py
│   │
│   ├── utils/                 # Helper utilities
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   ├── helpers.py
│   │   ├── llm_client.py
│   │   ├── text_generator.py
│   │   └── validators.py
│   │
│   ├── __init__.py
│   └── main.py                # Main entry point
│
├── .env.example               # Example environment variables
├── README.md                  # Project documentation (this file)
├── requirements.txt           # Python dependencies
└── schema.sql                 # Database schema

##  Getting Started

### Installation
1. Clone the repository:
   ```
   git clone https://github.com/yashghadale/Asana_Simulation.git
   cd asana-simulation
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Configure environment variables:
   ```
   cp .env.example .env
   # Edit .env with your API keys and settings
   ```

### Usage
Run the full simulation:
```
python src/main.py
```

This will generate the complete dataset in `output/asana_simulation.sqlite`.

### Checking Results
View the database structure:
```
sqlite3 output/asana_simulation.sqlite ".schema"
```

