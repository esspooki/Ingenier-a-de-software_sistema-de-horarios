import json

# cargar los datos desde el json
with open('ofertaEjemplo.json', 'r', encoding='utf-8') as f:
    classes = json.load(f)
#busqueda de ejemplo, al usar ".lower()"" se ignora mayusculas y minusculas
def buscar_materia(materia):
    return [c for c in classes if c['Materia'].lower() == materia.lower()]

def buscar_nrc(nrc):
    return next((c for c in classes if c['NRC'] == nrc), None)

def buscar_maestro(maestro):
    return [c for c in classes if maestro.lower() in c['Maestro'].lower()]

# Ejemplo:
if __name__ == "__main__":
    print("\n Resultado por materia:\n")

    result = buscar_materia("PROGRAMACION ESTRUCTURADA")
    for r in result:
        print(r)

    print("\n Resultado por NRC:\n")

    nrc_resultado = buscar_nrc("193703")
    print(nrc_resultado)

    print("\n Resultado por maestro (busqueda parcial):\n")
    maestro_resultado = buscar_maestro("JORGE ERNESTO")
    print(maestro_resultado)