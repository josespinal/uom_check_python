import pandas as pd
import argparse
import sys
import re

def validate_name_only(name):
    """Valida solo el nombre de la unidad de medida y determina su categoría.
    
    El ratio en Odoo representa la conversión a la unidad de referencia:
    - Para volumen: ratio = cantidad en la unidad / cantidad en galones US
    - Para peso: ratio = cantidad en la unidad / cantidad en libras
    - Para unidades: ratio = cantidad en la unidad / cantidad en unidad base
    
    Por ejemplo:
    - 1 litro = 0.264172 galones -> ratio = 1/0.264172 = 3.78541
    - 1 kg = 2.20462 libras -> ratio = 1/2.20462 = 0.453592
    """
    # Detectar tipo de unidad y cantidad
    name = name.strip()
    
    # Obtener categoría base
    base_category = get_base_category(name)
    if not base_category:
        return "No se pudo determinar la categoría"
        
    # Extraer cantidad y unidad
    package_types = ["Caja de", "Paquete de", "Fardo de", "Empaque de", "Envase de", 
                    "Botella de", "Lata de", "Frasco de", "Sobre de", "Saco de"]
    package_words = ["Huacales", "Huacal", "Cajas", "Paquetes", "Fardos", "Empaques", 
                    "Envases", "Botellas", "Latas", "Frascos", "Sobres", "Sacos"]
    unit_words = ["Porciones", "Porcion", "Servicios", "Servicio", "Unidades", "Unidad"]
    
    # Verificar si es un paquete compuesto (ej: "Caja de 12 / Botella de 750 ml")
    if "/" in name:
        parts = name.split("/")
        if len(parts) != 2:
            return f"Formato inválido para paquete compuesto. Categoría esperada: {base_category}"
            
        outer_part, inner_part = parts[0].strip(), parts[1].strip()
        try:
            # Extraer cantidades
            outer_qty = None
            # Primero intentar con package_types
            for pkg in package_types:
                if pkg in outer_part:
                    try:
                        outer_qty = float(outer_part.split(pkg)[1].strip().split(" ")[0])
                        break
                    except:
                        continue
            # Si no se encontró, intentar con package_words
            if not outer_qty:
                for word in package_words:
                    if word in outer_part:
                        numbers = re.findall(r'\d+(?:\.\d+)?', outer_part)
                        if numbers:
                            try:
                                outer_qty = float(numbers[0])
                                break
                            except:
                                continue
            
            # Extraer cantidad interna
            inner_qty = None
            # Primero intentar con package_types
            for pkg in package_types:
                if pkg in inner_part:
                    try:
                        inner_qty = float(inner_part.split(pkg)[1].strip().split(" ")[0])
                        break
                    except:
                        continue
            
            # Si no se encontró, intentar con unit_words
            if not inner_qty:
                for word in unit_words:
                    if word in inner_part:
                        numbers = re.findall(r'\d+(?:\.\d+)?', inner_part)
                        if numbers:
                            try:
                                inner_qty = float(numbers[0])
                                break
                            except:
                                continue
            
            if not outer_qty or not inner_qty:
                return f"No se pudo extraer las cantidades. Categoría esperada: {base_category}"
            
            # Obtener el factor de conversión de la unidad
            unit_ratio, unit_name = get_unit_info(inner_part)
            
            # Cantidad total en la unidad original
            total_qty = outer_qty * inner_qty
            
            # Cantidad en unidades de referencia
            total_in_reference = total_qty * unit_ratio
            
            # Obtener el nombre de la unidad de referencia
            ref_unit = "litros" if base_category == "volume" else "libras" if base_category == "weight" else "unidades"
            
            return (f"Paquete compuesto ({outer_qty}x{inner_qty} {unit_name}) = {total_qty} {unit_name}. "
                    f"Total en unidades de referencia: {total_in_reference:.6f} {ref_unit}. "
                    f"Categoría: {base_category}")
        except:
            return f"No se pudo extraer las cantidades. Categoría esperada: {base_category}"
    
    # Para paquetes simples
    for pkg in package_types:
        if pkg in name:
            try:
                qty = float(name.split(pkg)[1].strip().split(" ")[0])
                # Obtener el factor de conversión y nombre de la unidad
                unit_ratio, unit_name = get_unit_info(name)
                # Calcular la cantidad en unidades de referencia
                total_in_reference = qty * unit_ratio
                # Obtener el nombre de la unidad de referencia
                ref_unit = "litros" if base_category == "volume" else "libras" if base_category == "weight" else "unidades"
                # Determinar la unidad de referencia basado en la categoría
                if base_category == "volume":
                    ref_unit = "litros"
                elif base_category == "weight":
                    ref_unit = "libras"
                elif base_category == "length":
                    ref_unit = "metros"
                else:
                    ref_unit = "unidades"
                
                return (f"Paquete simple válido ({qty} {unit_name}). "
                        f"Total en unidades de referencia: {total_in_reference:.6f} {ref_unit}. "
                        f"Categoría: {base_category}")
            except:
                return f"No se pudo extraer la cantidad. Categoría esperada: {base_category}"
    
    # Si no es un paquete, verificar si tiene número y unidad
    words = name.split()
    try:
        qty = float(words[0])
        # Obtener el factor de conversión y nombre de la unidad
        unit_ratio, unit_name = get_unit_info(name)
        # Calcular la cantidad en unidades de referencia
        total_in_reference = qty * unit_ratio
        # Obtener el nombre de la unidad de referencia
        ref_unit = "litros" if base_category == "volume" else "libras" if base_category == "weight" else "unidades"
        return (f"Unidad simple válida ({qty} {unit_name}). "
                f"Total en unidades de referencia: {total_in_reference:.6f} {ref_unit}. "
                f"Categoría: {base_category}")
    except:
        return f"Unidad sin cantidad numérica. Categoría esperada: {base_category}"

def process_file(input_file):
    """Procesa el archivo completo de UoM y guarda los resultados."""
    # Cargar el archivo original con UTF-8
    df = pd.read_csv(input_file, encoding='utf-8')
    df["Correcciones"] = "OK"
    
    # Aplicar la validación a cada fila
    df["Correcciones"] = df.apply(validate_uom, axis=1)
    
    # Guardar el archivo corregido con UTF-8 y BOM para Excel
    output_file = "Correcciones_UoM.csv"
    df.to_csv(output_file, index=False, encoding='utf-8-sig')

# Definir reglas de nomenclatura
def get_unit_info(unit_text):
    """Obtiene el ratio y nombre de la unidad respecto a la unidad de referencia.
    
    Las unidades de referencia son:
    - Peso: Libra (1 libra = 1)
    - Volumen: Litro (1 litro = 1)
    - Unidades: Unidad (1 unidad = 1)
    
    Para unidades más grandes que la referencia:
    - factor = cuántas unidades de referencia hay en esta unidad
    Ejemplo: 1 galón = 3.78541 litros -> factor = 3.78541
    
    Para unidades más pequeñas que la referencia:
    - factor = cuántas unidades hay en una unidad de referencia
    Ejemplo: 1 litro = 1000 ml -> factor = 1000
    """
    unit_text = unit_text.lower()
    
    # Conversiones de volumen (respecto al litro)
    # Primero intentar patrones más específicos
    if "cuarto de galon" in unit_text.lower() or "cuarto de galón" in unit_text.lower():
        return (0.946353, "cuartos de galón")  # 1 cuarto de galón = 0.946353 litros
    elif "fl oz" in unit_text:
        return (0.0295735, "Fl Oz")  # 1 fl oz = 0.0295735 litros
    # Luego patrones más generales
    elif "ml" in unit_text:
        return (0.001, "ml")  # 1 ml = 0.001 litros
    elif any(u in unit_text.lower() for u in ["galon", "galón", "galones"]):
        return (3.78541, "galones")  # 1 galón = 3.78541 litros
    elif ("cuarto" in unit_text.lower() or "cuartos" in unit_text.lower()) and "galon" not in unit_text.lower() and "galón" not in unit_text.lower():
        return (0.946353, "cuartos")  # 1 cuarto = 0.946353 litros
    elif "litro" in unit_text:
        return (1.0, "litros")  # Unidad de referencia
    
    # Conversiones de peso (respecto a la libra)
    elif any(u in unit_text for u in ["kg", "KG", "Kg"]):
        return (2.20462, "kg")  # 1 kg = 2.20462 libras
    elif any(u in unit_text for u in ["gr", "g", " g"]) and not any(u in unit_text for u in ["kg", "KG", "Kg"]):
        return (0.00220462, "gr")  # 1 gramo = 0.00220462 libras
    elif any(u in unit_text.lower() for u in ["oz", "onza", "onzas"]) and "fl" not in unit_text.lower():
        return (0.0625, "Oz")  # 1 onza = 0.0625 libras
    elif "libra" in unit_text or "lb" in unit_text:
        return (1.0, "Libras")  # Unidad de referencia
    elif any(u in unit_text.lower() for u in ["pulgada", "pulgadas"]):
        return (0.0254, "pulgadas")  # 1 pulgada = 0.0254 metros
    
    # Para unidades simples
    elif any(u in unit_text for u in ["uds", "unidades", "unidad", "servicios", "servicio", "porciones", "porcion"]):
        return (1.0, "")  # Unidad de referencia
    
    return (1.0, "")

def get_base_category(unit_text):
    unit_text = unit_text.lower()
    # Primero buscar patrones específicos de volumen
    if any(u in unit_text for u in ["cuarto de galon", "cuarto de galón", "cuartos de galon", "cuartos de galón"]):
        return "volume"
    # Luego patrones generales
    elif any(u in unit_text for u in ["ml", "litro", "fl oz", "galon", "galón", "galones"]):
        return "volume"
    elif any(u in unit_text for u in ["gr", "g", "oz", "onza", "onzas", "libra", "lb", "kg", "KG", "Kg"]):
        return "weight"
    elif any(u in unit_text for u in ["pulgada", "pulgadas"]):
        return "length"
    elif any(u in unit_text for u in ["uds", "unidades", "unidad", "servicios", "servicio", "porciones", "porcion"]):
        return "unit"
    return None

def convert_to_base_unit(qty, unit_text):
    conversion_factor, _ = get_unit_info(unit_text)
    return qty * conversion_factor

def validate_uom(row):
    name = row["Unidad de medida"]
    tipo = row["Tipo"]
    mayor_ratio = row["Mayor ratio"]
    categoria = row["Tipo de categoría de medida"]

    # Determinar si el nombre contiene unidades de peso/volumen
    has_volume = any(unit in name.lower() for unit in ["ml", "litro", "fl oz", "galon", "galón", "galones", "cuarto de galon", "cuarto de galón", "cuartos de galon", "cuartos de galón"])
    has_weight = any(unit in name.lower() for unit in ["oz", "libras", "gr", "kg", "lb", "g", "onza", "onzas", "pulgada", "pulgadas"])
    
    # Detectar unidades de conteo
    unit_indicators = ["Uds", "Unidades", "Unidad", "servicios", "servicio", "porciones", "porcion"]
    has_units = any(unit in name for unit in unit_indicators)
    
    # Detectar tipos de empaque
    package_types = ["Caja de", "Paquete de", "Fardo de", "Empaque de", "Envase de", "Botella de", "Lata de", "Frasco de", "Sobre de", "Saco de"]
    package_words = ["Huacales", "Huacal", "Cajas", "Paquetes", "Fardos", "Empaques", "Envases", "Botellas", "Latas", "Frascos", "Sobres", "Sacos"]
    is_package = any(pkg in name for pkg in package_types) or any(word in name for word in package_words)
    
    # Determinar la categoría base por el nombre
    base_category = get_base_category(name)
    if base_category:
        expected_category = base_category
    else:
        expected_category = categoria # Keep existing category if no clear match

    # Validación de categoría
    if has_volume:
        expected_category = "volume"
    elif has_weight:
        expected_category = "weight"
    elif has_units and not (has_volume or has_weight):
        expected_category = "unit"
    else:
        expected_category = categoria # Keep existing category if no clear match

    # Verificar si la categoría es la esperada
    if categoria != expected_category:
        return f"Revisar: Tipo de categoría incorrecto, esperado {expected_category}."

    # Verificar referencia de unidad
    if tipo == "Unidad de medida de referencia para esta categoría" and mayor_ratio != 1:
        return "Revisar: La unidad de referencia debe tener Mayor ratio = 1."

    # Validar formato de cantidad en el nombre
    if "/" in name:
        # Para paquetes compuestos (ej: "Caja de 12 / Botella de 200 ml")
        parts = name.split("/")
        outer_part, inner_part = parts[0].strip(), parts[1].strip()
        
        try:
            # Extraer cantidad del paquete externo
            outer_qty = None
            # Primero intentar con package_types
            for pkg in package_types:
                if pkg in outer_part:
                    try:
                        outer_qty = float(outer_part.split(pkg)[1].strip().split(" ")[0])
                        break
                    except:
                        continue
            # Si no se encontró, intentar con package_words
            if not outer_qty:
                for word in package_words:
                    if word in outer_part:
                        numbers = re.findall(r'\d+(?:\.\d+)?', outer_part)
                        if numbers:
                            try:
                                outer_qty = float(numbers[0])
                                break
                            except:
                                continue
            
            # Extraer cantidad interna
            inner_qty = None
            # Primero buscar después de "de"
            if "de" in inner_part:
                try:
                    inner_qty = float(inner_part.split("de")[-1].strip().split(" ")[0])
                except:
                    pass
            # Si no se encontró, buscar números en cualquier parte
            if not inner_qty:
                numbers = re.findall(r'\d+(?:\.\d+)?', inner_part)
                if numbers:
                    try:
                        inner_qty = float(numbers[0])
                    except:
                        pass
            
            if not inner_qty:
                return "Revisar: No se pudo extraer la cantidad interna"
            
            total_qty = outer_qty * inner_qty  # Cantidad total en la unidad original
            
            # Obtener el factor de conversión para el paquete interno
            inner_conversion, unit_name = get_unit_info(inner_part)
            
            # Obtener los factores del CSV
            ratio = float(row["Ratio"])
            
            # Calcular la cantidad total en la unidad original y en unidades de referencia
            total_qty = outer_qty * inner_qty
            total_in_reference = total_qty * inner_conversion
            
            if tipo == "Unidad de medida de referencia para esta categoría":
                # Unidad de referencia debe tener factor = 1 y factor_inv = 1
                if abs(1.0 - ratio) > 0.01 or abs(1.0 - mayor_ratio) > 0.01:
                    return (f"Revisar: Unidad de referencia debe tener Ratio = 1 y Mayor ratio = 1. "
                            f"Actuales: Ratio = {ratio}, Mayor ratio = {mayor_ratio}")
            
            elif tipo == "Más grande que la unidad de medida de referencia":
                # Para unidades más grandes, validar el Mayor ratio
                # Mayor ratio = cuántas unidades de referencia hay en esta unidad
                # Ejemplo: 1 galón = 3.78541 litros -> Mayor ratio = 3.78541
                expected_mayor_ratio = total_in_reference
                if abs(expected_mayor_ratio - mayor_ratio) > 0.01:
                    return (f"Revisar: {outer_qty}x{inner_qty}={total_qty} {unit_name}. "
                            f"Total en unidades de referencia: {total_in_reference:.6f}. "
                            f"Mayor ratio esperado: {expected_mayor_ratio:.6f}, pero es {mayor_ratio}")
            
            else:  # "Más pequeña que la unidad de medida de referencia"
                # Para unidades más pequeñas, validar el Ratio
                # Ratio = factor = 1/factor_inv
                # Ejemplo: 1 litro = 33.814 onzas -> factor = 1/33.814
                expected_ratio = 1 / total_in_reference if total_in_reference != 0 else 0
                if abs(expected_ratio - ratio) > 0.01:
                    return (f"Revisar: {outer_qty}x{inner_qty}={total_qty} {unit_name}. "
                            f"Total en unidades de referencia: {total_in_reference:.6f}. "
                            f"Para unidad más pequeña, Ratio esperado: {expected_ratio:.6f}, pero es {ratio}")
        except ValueError:
            return "Revisar: No se pudo validar la cantidad en el nombre compuesto."
    elif any(pkg in name for pkg in package_types):
        # Para paquetes simples
        for pkg in package_types:
            if pkg in name:
                split_name = name.split(pkg)[-1].strip().split(" ")[0]
                try:
                    qty = float(split_name)
                    # Convertir a unidad base si es necesario
                    rest_of_name = name.split(split_name, 1)[1].strip()
                    conversion_factor, unit = get_unit_info(rest_of_name)
                    if unit:
                        # Cantidad en unidades de referencia
                        total_in_reference = qty * conversion_factor
                        ratio = float(row["Ratio"])
                        
                        if tipo == "Más grande que la unidad de medida de referencia":
                            # Mayor ratio debe ser igual a la cantidad en unidades de referencia
                            if abs(total_in_reference - mayor_ratio) > 0.01:
                                return (f"Revisar: El nombre indica {qty} {unit}. "
                                        f"Total en unidades de referencia: {total_in_reference:.6f}. "
                                        f"Mayor ratio esperado: {total_in_reference:.6f}, pero es {mayor_ratio}")
                        else:  # "Más pequeña que la unidad de medida de referencia"
                            # Ratio debe ser el inverso de la cantidad en unidades de referencia
                            expected_ratio = 1 / total_in_reference if total_in_reference != 0 else 0
                            if abs(expected_ratio - ratio) > 0.01:
                                return (f"Revisar: El nombre indica {qty} {unit}. "
                                        f"Total en unidades de referencia: {total_in_reference:.6f}. "
                                        f"Ratio esperado: {expected_ratio:.6f}, pero es {ratio}")
                    else:
                        expected_ratio = qty
                        if abs(expected_ratio - mayor_ratio) > 0.01:
                            return f"Revisar: El nombre indica {qty}, pero el Mayor ratio es {mayor_ratio}."
                    break
                except ValueError:
                    # Intentar extraer número si está seguido por una unidad
                    for unit in unit_indicators:
                        if unit in split_name:
                            try:
                                num = split_name.split(unit)[0].strip()
                                expected_ratio = float(num)
                                if abs(expected_ratio - mayor_ratio) > 0.01:
                                    return f"Revisar: El nombre indica {expected_ratio}, pero el Mayor ratio es {mayor_ratio}."
                                break
                            except ValueError:
                                continue
                    return "Revisar: No se pudo validar la cantidad en el nombre."

    return "OK"

def main():
    parser = argparse.ArgumentParser(description='Validador de Unidades de Medida')
    parser.add_argument('--name', '-n', help='Nombre de la unidad de medida a validar')
    parser.add_argument('--file', '-f', help='Archivo CSV con unidades de medida a validar')
    args = parser.parse_args()

    if args.name:
        # Validar solo el nombre
        result = validate_name_only(args.name)
        print(f"Validación de '{args.name}': {result}")
    elif args.file:
        # Procesar archivo completo
        process_file(args.file)
        print(f"Archivo procesado. Resultados guardados en 'Correcciones_UoM.csv'")
    else:
        # Si no hay argumentos, procesar el archivo por defecto
        process_file("uom.uom.csv")
        print(f"Archivo procesado. Resultados guardados en 'Correcciones_UoM.csv'")

if __name__ == "__main__":
    main()
