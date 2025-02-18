"""
Core validation logic for UoM validation.
"""
from typing import Optional, Dict, Any
from units import (
    get_unit_info, get_base_category, get_reference_unit,
    PACKAGE_TYPES, PACKAGE_WORDS
)
from parsers import parse_compound_package, parse_simple_package

def validate_name_only(name: str) -> str:
    """Validate just the unit name and determine its category.
    
    Args:
        name: Name to validate
        
    Returns:
        Validation result message
    """
    # Get base category from unit name
    base_category = get_base_category(name)
    if not base_category:
        return "No se pudo determinar la categoría"
        
    # Check if it's a compound package
    if "/" in name:
        outer_qty, inner_qty, _, inner_part = parse_compound_package(name)
        if not outer_qty or not inner_qty:
            return "No se pudo extraer las cantidades"
            
        # Get unit info
        conversion_factor, unit_name = get_unit_info(inner_part)
        
        # Calculate totals
        total_qty = outer_qty * inner_qty
        total_in_reference = total_qty * conversion_factor
        ref_unit = get_reference_unit(base_category)
        
        return (f"Paquete compuesto ({outer_qty}x{inner_qty} {unit_name}) = {total_qty} {unit_name}. "
                f"Total en unidades de referencia: {total_in_reference:.6f} {ref_unit}. "
                f"Categoría: {base_category}")
                
    # Check if it's a simple package
    for pkg in PACKAGE_TYPES:
        if pkg in name:
            qty, rest_of_name = parse_simple_package(name)
            if not qty:
                return "No se pudo extraer la cantidad"
                
            # Get unit info
            conversion_factor, unit_name = get_unit_info(name)
            total_in_reference = qty * conversion_factor
            ref_unit = get_reference_unit(base_category)
            
            return (f"Paquete simple válido ({qty} {unit_name}). "
                    f"Total en unidades de referencia: {total_in_reference:.6f} {ref_unit}. "
                    f"Categoría: {base_category}")
                    
    # Try simple unit with quantity
    words = name.split()
    try:
        qty = float(words[0])
        conversion_factor, unit_name = get_unit_info(name)
        total_in_reference = qty * conversion_factor
        ref_unit = get_reference_unit(base_category)
        
        return (f"Unidad simple válida ({qty} {unit_name}). "
                f"Total en unidades de referencia: {total_in_reference:.6f} {ref_unit}. "
                f"Categoría: {base_category}")
    except:
        return "Unidad sin cantidad numérica"

def validate_uom(row: Dict[str, Any]) -> str:
    """Validate a UoM row from the CSV file.
    
    Args:
        row: CSV row data
        
    Returns:
        Validation result message
    """
    name = row["Unidad de medida"]
    tipo = row["Tipo"]
    mayor_ratio = float(row["Mayor ratio"])
    ratio = float(row["Ratio"])
    categoria = row["Tipo de categoría de medida"]
    
    # Get base category
    base_category = get_base_category(name)
    if not base_category:
        base_category = categoria
        
    # Verify category matches
    if categoria != base_category:
        return f"Revisar: Tipo de categoría incorrecto, esperado {base_category}."
        
    # Verify reference unit
    if tipo == "Unidad de medida de referencia para esta categoría" and mayor_ratio != 1:
        return "Revisar: La unidad de referencia debe tener Mayor ratio = 1."
        
    # Validate ratios based on package type
    if "/" in name:
        return validate_compound_package(name, tipo, mayor_ratio, ratio)
    else:
        return validate_simple_package(name, tipo, mayor_ratio, ratio)

def validate_compound_package(name: str, tipo: str, mayor_ratio: float, ratio: float) -> str:
    """Validate a compound package UoM.
    
    Args:
        name: Package name
        tipo: UoM type
        mayor_ratio: Mayor ratio value
        ratio: Ratio value
        
    Returns:
        Validation result message
    """
    outer_qty, inner_qty, _, inner_part = parse_compound_package(name)
    if not outer_qty or not inner_qty:
        return "Revisar: No se pudo extraer las cantidades"
        
    # Get conversion factors
    conversion_factor, unit_name = get_unit_info(inner_part)
    
    # Calculate totals
    total_qty = outer_qty * inner_qty
    total_in_reference = total_qty * conversion_factor
    
    if tipo == "Más grande que la unidad de medida de referencia":
        if abs(total_in_reference - mayor_ratio) > 0.01:
            return (f"Revisar: {outer_qty}x{inner_qty}={total_qty} {unit_name}. "
                    f"Total en unidades de referencia: {total_in_reference:.6f}. "
                    f"Mayor ratio esperado: {total_in_reference:.6f}, pero es {mayor_ratio}")
    else:  # "Más pequeña que la unidad de medida de referencia"
        expected_ratio = 1 / total_in_reference if total_in_reference != 0 else 0
        if abs(expected_ratio - ratio) > 0.01:
            return (f"Revisar: {outer_qty}x{inner_qty}={total_qty} {unit_name}. "
                    f"Total en unidades de referencia: {total_in_reference:.6f}. "
                    f"Ratio esperado: {expected_ratio:.6f}, pero es {ratio}")
                    
    return "OK"

def validate_simple_package(name: str, tipo: str, mayor_ratio: float, ratio: float) -> str:
    """Validate a simple package UoM.
    
    Args:
        name: Package name
        tipo: UoM type
        mayor_ratio: Mayor ratio value
        ratio: Ratio value
        
    Returns:
        Validation result message
    """
    qty, rest_of_name = parse_simple_package(name)
    if not qty:
        return "Revisar: No se pudo extraer la cantidad"
        
    # Get conversion factors
    conversion_factor, unit_name = get_unit_info(name)
    total_in_reference = qty * conversion_factor
    
    if tipo == "Más grande que la unidad de medida de referencia":
        if abs(total_in_reference - mayor_ratio) > 0.01:
            return (f"Revisar: El nombre indica {qty} {unit_name}. "
                    f"Total en unidades de referencia: {total_in_reference:.6f}. "
                    f"Mayor ratio esperado: {total_in_reference:.6f}, pero es {mayor_ratio}")
    else:  # "Más pequeña que la unidad de medida de referencia"
        expected_ratio = 1 / total_in_reference if total_in_reference != 0 else 0
        if abs(expected_ratio - ratio) > 0.01:
            return (f"Revisar: El nombre indica {qty} {unit_name}. "
                    f"Total en unidades de referencia: {total_in_reference:.6f}. "
                    f"Ratio esperado: {expected_ratio:.6f}, pero es {ratio}")
                    
    return "OK"
