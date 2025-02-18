#!/usr/bin/env python3
"""
UoM Validation Script

This script validates Units of Measure (UoM) definitions in Odoo ERP.
It checks for correct ratios, categories, and naming conventions.
"""

import argparse
import sys
from typing import Optional

import pandas as pd

from validators import validate_name_only, validate_uom

def process_file(input_file: str) -> None:
    """Process a CSV file containing UoM definitions.
    
    Args:
        input_file: Path to input CSV file
    """
    try:
        df = pd.read_csv(input_file)
        df["Correcciones"] = df.apply(validate_uom, axis=1)
        df.to_csv("Correcciones_UoM.csv", index=False)
        print("Archivo procesado. Resultados guardados en 'Correcciones_UoM.csv'")
    except Exception as e:
        print(f"Error procesando archivo: {e}")
        sys.exit(1)

def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Validar nombres de unidades de medida",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-n", "--name", help="Nombre de unidad de medida a validar")
    parser.add_argument("-f", "--file", help="Archivo CSV con unidades de medida")
    
    args = parser.parse_args()
    
    if args.name:
        result = validate_name_only(args.name)
        print(f"Validación de '{args.name}': {result}")
    elif args.file:
        process_file(args.file)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
