"""
Functions for parsing unit names and quantities.
"""
import re
from typing import Tuple, Optional
from units import PACKAGE_TYPES, PACKAGE_WORDS

def extract_quantity(text: str, split_on: str = "de") -> Optional[float]:
    """Extract a quantity from text.
    
    Args:
        text: Text containing a quantity
        split_on: Word to split on before looking for quantity
        
    Returns:
        Extracted quantity or None if not found
    """
    # Try splitting on word first
    if split_on in text:
        try:
            return float(text.split(split_on)[-1].strip().split(" ")[0])
        except:
            pass
    
    # Try finding any number
    numbers = re.findall(r'\d+(?:\.\d+)?', text)
    if numbers:
        try:
            return float(numbers[0])
        except:
            pass
            
    return None

def parse_compound_package(name: str) -> Tuple[Optional[float], Optional[float], str, str]:
    """Parse a compound package name like "Caja de 12 / Botella de 750 ml".
    
    Args:
        name: Package name to parse
        
    Returns:
        Tuple of (outer_qty, inner_qty, outer_part, inner_part)
    """
    parts = name.split("/")
    if len(parts) != 2:
        return None, None, "", ""
        
    outer_part, inner_part = parts[0].strip(), parts[1].strip()
    
    # Extract outer quantity
    outer_qty = None
    # First try package types
    for pkg in PACKAGE_TYPES:
        if pkg in outer_part:
            try:
                outer_qty = float(outer_part.split(pkg)[1].strip().split(" ")[0])
                break
            except:
                continue
                
    # If not found, try package words
    if not outer_qty:
        for word in PACKAGE_WORDS:
            if word in outer_part:
                outer_qty = extract_quantity(outer_part)
                if outer_qty:
                    break
                    
    # Extract inner quantity
    inner_qty = extract_quantity(inner_part)
    
    return outer_qty, inner_qty, outer_part, inner_part

def parse_simple_package(name: str) -> Tuple[Optional[float], str]:
    """Parse a simple package name like "Envase de 750 ml".
    
    Args:
        name: Package name to parse
        
    Returns:
        Tuple of (quantity, rest_of_name)
    """
    for pkg in PACKAGE_TYPES:
        if pkg in name:
            split_name = name.split(pkg)[-1].strip().split(" ")[0]
            try:
                qty = float(split_name)
                rest_of_name = name.split(split_name, 1)[1].strip()
                return qty, rest_of_name
            except:
                continue
                
    return None, name
