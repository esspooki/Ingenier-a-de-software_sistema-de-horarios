import json

# cargar los datos desde el json
with open('ofertaEjemplo.json', 'r', encoding='utf-8') as f:
    classes = json.load(f)
#busqueda de ejemplo, al usar ".lower()"" se ignora mayusculas y minusculas
def buscar_materia(materia):
    return [c for c in classes if c['Materia'].lower() == materia.lower()]

def buscar_nrc(nrc):
    return next((c for c in classes if c['NRC'] == nrc), None)

# Ejemplo:
if __name__ == "__main__":
    result = buscar_materia("PROGRAMACION ESTRUCTURADA")
    for r in result:
        print(r)

    nrc_resultado = buscar_nrc("193703")
    print(nrc_resultado)