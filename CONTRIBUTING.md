# Contributing to Advanced Index Analyzer / Beiträge zum Advanced Index Analyzer

[English](#english) | [Deutsch](#deutsch)

---

<a name="english"></a>
## 🤝 Contributing Guidelines (English)

Thank you for your interest in contributing to the Advanced Index Analyzer! We welcome contributions from the community and are grateful for any help you can provide.

### 📋 Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Process](#development-process)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)

### 📜 Code of Conduct

We are committed to providing a welcoming and inspiring community for all. Please read and follow our Code of Conduct:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Accept feedback gracefully
- Put the project's best interests first

### 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/index-analyzer.git
   cd index-analyzer
   ```
3. **Set up development environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```
4. **Run tests** to ensure everything works:
   ```bash
   python test_analyzer.py
   ```

### 💡 How to Contribute

#### Reporting Bugs
- Check if the bug has already been reported in [Issues](https://github.com/project/issues)
- Create a detailed bug report with:
  - Clear description of the problem
  - Steps to reproduce
  - Expected vs actual behavior
  - System information (OS, Python version, etc.)
  - Error messages and logs

#### Suggesting Features
- Check existing feature requests first
- Open a new issue with:
  - Clear feature description
  - Use cases and benefits
  - Possible implementation approach
  - Mockups or examples (if applicable)

#### Code Contributions
1. **Find an issue** to work on or create a new one
2. **Comment on the issue** to let others know you're working on it
3. **Create a feature branch**:
   ```bash
   git checkout -b feature/amazing-feature
   ```
4. **Make your changes** following our coding standards
5. **Write/update tests** for your changes
6. **Update documentation** if needed
7. **Commit your changes**:
   ```bash
   git commit -m "Add amazing feature"
   ```
8. **Push to your fork**:
   ```bash
   git push origin feature/amazing-feature
   ```
9. **Open a Pull Request**

### 🔄 Development Process

#### Branch Naming Convention
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions or fixes

#### Commit Message Format
```
<type>: <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build process or auxiliary tool changes

Example:
```
feat: add Elliott Wave pattern detection

Implemented automatic detection of Elliott Wave patterns
in price data using signal processing techniques.

Closes #123
```

### 🔍 Pull Request Process

1. **Ensure your PR**:
   - Passes all tests
   - Includes tests for new functionality
   - Updates relevant documentation
   - Follows coding standards
   - Has a clear description

2. **PR Description Template**:
   ```markdown
   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update

   ## Testing
   - [ ] Tests pass locally
   - [ ] New tests added
   - [ ] Manual testing completed

   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Documentation updated
   - [ ] No new warnings
   ```

3. **Review Process**:
   - At least one maintainer review required
   - Address all feedback
   - Keep PR focused and small when possible

### 💻 Coding Standards

#### Python Style Guide
- Follow [PEP 8](https://pep8.org/)
- Use type hints where appropriate
- Maximum line length: 120 characters
- Use descriptive variable names

#### Code Organization
```python
# Good example
class TechnicalIndicator:
    """
    Calculate technical indicators for market analysis.
    
    Attributes:
        data: OHLCV price data
        period: Calculation period
    """
    
    def __init__(self, data: pd.DataFrame, period: int = 14):
        """Initialize indicator with data and period."""
        self.data = data
        self.period = period
    
    def calculate(self) -> pd.Series:
        """Calculate indicator values."""
        # Implementation
        pass
```

#### Documentation
- All public functions/classes need docstrings
- Use Google-style docstrings
- Include type hints
- Add inline comments for complex logic

### 🧪 Testing

#### Running Tests
```bash
# Run all tests
python test_analyzer.py

# Run specific test
python -m pytest tests/test_patterns.py

# Run with coverage
python -m pytest --cov=.
```

#### Writing Tests
```python
def test_candlestick_pattern_detection():
    """Test that candlestick patterns are correctly detected."""
    # Arrange
    data = create_test_data()
    detector = CandlestickPatterns(data)
    
    # Act
    patterns = detector.detect_all_patterns()
    
    # Assert
    assert len(patterns) > 0
    assert patterns[0]['pattern'] == 'Expected Pattern'
```

### 📚 Documentation

#### Code Documentation
- Update docstrings for any modified functions
- Keep README.md up to date
- Update configuration examples

#### User Documentation
- Update user guide for new features
- Add examples for new functionality
- Update FAQ if needed

### 🎁 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Given credit in documentation

### 📞 Getting Help

- Join our [Discord server](https://discord.gg/example)
- Ask questions in [Discussions](https://github.com/project/discussions)
- Contact maintainers: maintainers@example.com

---

<a name="deutsch"></a>
## 🤝 Beitragsrichtlinien (Deutsch)

Vielen Dank für Ihr Interesse, zum Advanced Index Analyzer beizutragen! Wir begrüßen Beiträge aus der Community und sind dankbar für jede Hilfe.

### 📋 Inhaltsverzeichnis
- [Verhaltenskodex](#verhaltenskodex)
- [Erste Schritte](#erste-schritte)
- [Wie man beiträgt](#wie-man-beiträgt)
- [Entwicklungsprozess](#entwicklungsprozess)
- [Pull-Request-Prozess](#pull-request-prozess)
- [Coding-Standards](#coding-standards-de)
- [Testen](#testen)
- [Dokumentation](#dokumentation-de)

### 📜 Verhaltenskodex

Wir verpflichten uns, eine einladende und inspirierende Gemeinschaft für alle zu schaffen:

- Seien Sie respektvoll und inklusiv
- Begrüßen Sie Neulinge und helfen Sie ihnen
- Konzentrieren Sie sich auf konstruktive Kritik
- Nehmen Sie Feedback dankbar an
- Stellen Sie die Interessen des Projekts in den Vordergrund

### 🚀 Erste Schritte

1. **Forken Sie das Repository** auf GitHub
2. **Klonen Sie Ihren Fork** lokal:
   ```bash
   git clone https://github.com/ihrbenutzername/index-analyzer.git
   cd index-analyzer
   ```
3. **Entwicklungsumgebung einrichten**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Auf macOS/Linux: source venv/bin/activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Entwicklungsabhängigkeiten
   ```
4. **Tests ausführen** um sicherzustellen, dass alles funktioniert:
   ```bash
   python test_analyzer.py
   ```

### 💡 Wie man beiträgt

#### Fehler melden
- Prüfen Sie, ob der Fehler bereits in [Issues](https://github.com/project/issues) gemeldet wurde
- Erstellen Sie einen detaillierten Fehlerbericht mit:
  - Klarer Problembeschreibung
  - Schritten zur Reproduktion
  - Erwartetem vs. tatsächlichem Verhalten
  - Systeminformationen (OS, Python-Version, etc.)
  - Fehlermeldungen und Logs

#### Features vorschlagen
- Prüfen Sie zuerst bestehende Feature-Anfragen
- Öffnen Sie ein neues Issue mit:
  - Klarer Feature-Beschreibung
  - Anwendungsfällen und Vorteilen
  - Möglichem Implementierungsansatz
  - Mockups oder Beispielen (falls zutreffend)

#### Code-Beiträge
1. **Finden Sie ein Issue** zum Bearbeiten oder erstellen Sie ein neues
2. **Kommentieren Sie das Issue** um andere zu informieren
3. **Erstellen Sie einen Feature-Branch**:
   ```bash
   git checkout -b feature/tolles-feature
   ```
4. **Nehmen Sie Ihre Änderungen vor** gemäß unseren Coding-Standards
5. **Schreiben/aktualisieren Sie Tests** für Ihre Änderungen
6. **Aktualisieren Sie die Dokumentation** falls nötig
7. **Committen Sie Ihre Änderungen**:
   ```bash
   git commit -m "Füge tolles Feature hinzu"
   ```
8. **Pushen Sie zu Ihrem Fork**:
   ```bash
   git push origin feature/tolles-feature
   ```
9. **Öffnen Sie einen Pull Request**

### 🔄 Entwicklungsprozess

#### Branch-Namenskonvention
- `feature/` - Neue Features
- `fix/` - Fehlerbehebungen
- `docs/` - Dokumentationsaktualisierungen
- `refactor/` - Code-Refactoring
- `test/` - Test-Ergänzungen oder -Korrekturen

#### Commit-Nachrichtenformat
```
<typ>: <betreff>

<body>

<footer>
```

Typen:
- `feat`: Neues Feature
- `fix`: Fehlerbehebung
- `docs`: Dokumentationsänderungen
- `style`: Code-Stil-Änderungen
- `refactor`: Code-Refactoring
- `test`: Test-Änderungen
- `chore`: Build-Prozess oder Hilfswerkzeug-Änderungen

### 🔍 Pull-Request-Prozess

1. **Stellen Sie sicher, dass Ihr PR**:
   - Alle Tests besteht
   - Tests für neue Funktionalität enthält
   - Relevante Dokumentation aktualisiert
   - Coding-Standards folgt
   - Eine klare Beschreibung hat

2. **Review-Prozess**:
   - Mindestens ein Maintainer-Review erforderlich
   - Adressieren Sie alles Feedback
   - Halten Sie PRs fokussiert und klein

### 💻 Coding-Standards <a name="coding-standards-de"></a>

- Befolgen Sie [PEP 8](https://pep8.org/)
- Verwenden Sie Type Hints wo angemessen
- Maximale Zeilenlänge: 120 Zeichen
- Verwenden Sie beschreibende Variablennamen
- Alle öffentlichen Funktionen/Klassen benötigen Docstrings

### 🧪 Testen

```bash
# Alle Tests ausführen
python test_analyzer.py

# Mit Coverage
python -m pytest --cov=.
```

### 📚 Dokumentation <a name="dokumentation-de"></a>

- Aktualisieren Sie Docstrings für modifizierte Funktionen
- Halten Sie README.md aktuell
- Aktualisieren Sie Konfigurationsbeispiele
- Fügen Sie Beispiele für neue Funktionalität hinzu

### 📞 Hilfe erhalten

- Treten Sie unserem [Discord-Server](https://discord.gg/example) bei
- Stellen Sie Fragen in [Discussions](https://github.com/project/discussions)
- Kontaktieren Sie die Maintainer: maintainers@example.com

---

## Thank You! / Vielen Dank! 🙏

Your contributions make this project better for everyone!
Ihre Beiträge machen dieses Projekt für alle besser!