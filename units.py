"""
Unit definitions and conversion factors for the UoM validation system.
"""
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

@dataclass
class UnitDefinition:
    """Definition of a unit of measure."""
    name: str
    reference_unit: str
    conversion_factor: float
    category: str
    patterns: List[str]

# Volume units (reference: litros)
VOLUME_UNITS = [
    UnitDefinition("ml", "litros", 0.001, "volume", ["ml"]),
    UnitDefinition("Fl Oz", "litros", 0.0295735, "volume", ["fl oz"]),
    UnitDefinition("galones", "litros", 3.78541, "volume", ["galon", "galón", "galones"]),
    UnitDefinition("cuartos de galón", "litros", 0.946353, "volume", ["cuarto de galon", "cuarto de galón", "cuartos de galon", "cuartos de galón"]),
    UnitDefinition("litros", "litros", 1.0, "volume", ["litro", "litros"]),
]

# Weight units (reference: libras)
WEIGHT_UNITS = [
    UnitDefinition("kg", "libras", 2.20462, "weight", ["kg", "KG", "Kg", "kgs", "Kgs"]),  # Check kg before g
    UnitDefinition("gr", "libras", 0.00220462, "weight", ["gr", "g", " g"]),
    UnitDefinition("Oz", "libras", 0.0625, "weight", ["oz", "onza", "onzas"]),
    UnitDefinition("Libras", "libras", 1.0, "weight", ["libra", "libras", "lb"]),
]

# Length units (reference: metros)
LENGTH_UNITS = [
    UnitDefinition("pulgadas", "metros", 0.0254, "length", ["pulgada", "pulgadas"]),
]

# Unit types (reference: unidades)
UNIT_TYPES = [
    UnitDefinition("unidades", "unidades", 1.0, "unit", ["uds", "unidades", "unidad", "servicios", "servicio", "porciones", "porcion"]),
]

# Package types and words
PACKAGE_TYPES = [
    "Caja de", "Paquete de", "Fardo de", "Empaque de", "Envase de",
    "Botella de", "Lata de", "Frasco de", "Sobre de", "Saco de"
]

PACKAGE_WORDS = [
    "Huacales", "Huacal", "Cajas", "Paquetes", "Fardos", "Empaques",
    "Envases", "Botellas", "Latas", "Frascos", "Sobres", "Sacos"
]

# All units
ALL_UNITS = VOLUME_UNITS + WEIGHT_UNITS + LENGTH_UNITS + UNIT_TYPES

def get_unit_info(unit_text: str) -> Tuple[float, str]:
    """Get conversion factor and standardized name for a unit.
    
    Args:
        unit_text: The text containing the unit name
        
    Returns:
        Tuple of (conversion_factor, standardized_name)
    """
    unit_text = unit_text.lower()
    
    # First check specific patterns
    for unit in ALL_UNITS:
        if any(pattern in unit_text and len(pattern) > 2 for pattern in unit.patterns):
            return unit.conversion_factor, unit.name
    
    # Then check shorter patterns
    for unit in ALL_UNITS:
        if any(pattern in unit_text for pattern in unit.patterns):
            return unit.conversion_factor, unit.name
            
    # Default to unit type if no match
    return 1.0, ""

def get_base_category(unit_text: str) -> Optional[str]:
    """Get the base category for a unit text.
    
    Args:
        unit_text: The text containing the unit name
        
    Returns:
        Category name or None if no match
    """
    unit_text = unit_text.lower()
    
    # Find matching unit definition
    for unit in ALL_UNITS:
        if any(pattern in unit_text for pattern in unit.patterns):
            return unit.category
            
    return None

def get_reference_unit(category: str) -> str:
    """Get the reference unit name for a category.
    
    Args:
        category: The unit category
        
    Returns:
        Reference unit name
    """
    reference_units = {
        "volume": "litros",
        "weight": "libras", 
        "length": "metros",
        "unit": "unidades"
    }
    return reference_units.get(category, "unidades")
