# EASYSQL: A Smart SQL Query Suggestion Tool

EASYSQL is a terminal-based tool designed to help beginners write correct SQL queries by offering real-time, schema-based suggestions and corrections. It simplifies learning SQL by guiding users through syntax, structure, and query construction using dynamic, context-aware suggestions.

---

## 🔍 Features

- 🧠 **Real-time SQL Suggestions**: Offers context-aware recommendations based on live schema and user input.
- 🛠 **Automatic Query Correction**: Fixes syntax errors like missing semicolons, unmatched parentheses, and misused keywords.
- 📊 **Live Database Validation**: Suggests actual table and field names by connecting to a MySQL database.
- 🎓 **Beginner-Friendly**: Built for students and learners to understand and improve SQL writing.
- ⚙️ **Terminal-Based**: Lightweight and cross-platform, works on Windows CMD, Bash, and ZSH terminals.

---

## 📸 Screenshots

> 📌 **Suggestion Prompting**  
Real-time keyword and clause suggestions as the user types.  
![Suggestion Prompting](Documentation/Screen_shot/detect_exack_words.png)

> 📌 **Schema-Aware Completion**  
Displays relevant table/column names pulled from the connected database.  
![Schema Completion](Documentation/Screen_shot/fifth.png)

> 📌 **Automatic Corrections**  
Corrects syntax issues like missing semicolons or unmatched parentheses.  
![Auto Correction](Documentation/Screen_shot/correction.png)

---

## 📚 Dataset

- 1400+ pre-constructed queries based on SQL operations.
  - `SELECT`: 300+  
  - `INSERT`: 150+  
  - `UPDATE`: 110+  
  - `DELETE`: 120+  
- Query ontology and knowledge graph built manually.
- Tools used: Protégé, ChatGPT for refinement and structure.

---

## 🧪 Technical Specifications

- **Languages**: Python 3.6+
- **Libraries**:
  - `prompt_toolkit`
  - `rich`
  - `os`, `re`, `pytest-shutil`
- **Supported OS**:
  - Windows 10/11
  - Ubuntu 20.04+, Manjaro Linux 25.0.0
- **Databases**:
  - MySQL
  - MariaDB 11.7.2
- **Minimum Requirements**:
  - 2 GB RAM
  - Python 3.6 or later

---

## 🏗 Architecture Overview

High-level architecture showing user interaction, suggestion engine, and database connection.  
![Architecture](Documentation/Diagrma/use_case.png)

---

## 🧩 Methodology

Includes use case diagrams, suggestion process logic, and backend workflow.  
![Workflow](Documentation/Diagram/overal_steps..png)

---

## 🧱 Limitations

- Only supports **MySQL/MariaDB**.
- Dependent on pre-defined ontology.
- Does not currently support **GUI** or **natural language input**.

---

## 🚀 Future Scope

- PostgreSQL and Oracle DB support
- Natural language to SQL conversion
- Machine learning–based suggestion engine
- GUI version for non-terminal users

---

## 🙏 Acknowledgements

Developed under the guidance of **Dr. Sayani Mondal**, Assistant Professor, Department of Computer Science, Sister Nivedita University.

Special thanks to our families, peers, and academic mentors for their support and encouragement throughout this project.

---

## 📄 License

Copyright (c) 2025 Team EASYSQL (Sister Nivedita University)

This project is made available for **academic demonstration purposes only**.  
Redistribution, modification, or commercial use is **strictly prohibited** without prior written permission.

For licensing inquiries, please contact the authors.


---

## 📫 Contact

For questions, suggestions, or collaboration, please open an [Issue](https://github.com/yourusername/EASYSQL/issues) or contact any team member via GitHub.

