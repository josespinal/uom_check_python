# UoM Validation Script

This script validates Units of Measure (UoM) definitions in Odoo ERP. It checks for correct ratios, categories, and naming conventions.

## Features

- Validates compound package names (e.g., "Caja de 12 / Botella de 750 ml")
- Validates simple package names (e.g., "Envase de 750 ml")
- Supports multiple unit types:
  - Volume (ml, litros, fl oz, galones, cuartos de galón)
  - Weight (gr, oz, libras, kg)
  - Length (pulgadas)
  - Units (unidades, servicios, porciones)
- Validates conversion ratios against Odoo's reference units
- Handles both larger and smaller units relative to reference units

## Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Unix/macOS
   # or
   venv\Scripts\activate  # On Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Validate a single UoM name:
```bash
python check_uom.py -n "Envase de 1 cuarto de galón"
```

### Process a CSV file of UoMs:
```bash
python check_uom.py -f uom.uom.csv
```

The CSV file should have the following columns:
- `Unidad de medida`: UoM name
- `Tipo`: UoM type (e.g., "Más grande que la unidad de medida de referencia")
- `Mayor ratio`: Ratio for larger units
- `Ratio`: Ratio for smaller units
- `Tipo de categoría de medida`: Category (weight, volume, unit, length)

## Code Structure

- `check_uom.py`: Main script with CLI handling
- `units.py`: Unit definitions and conversion factors
- `validators.py`: Core validation logic
- `parsers.py`: Functions for parsing unit names and quantities

## Reference Units

- Volume: litros
- Weight: libras
- Length: metros
- Units: unidades
