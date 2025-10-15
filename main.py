# pip install requests beautifulsoup4
import requests
from bs4 import BeautifulSoup
import json

URL_FORM = "https://siiauescolar.siiau.udg.mx/wal/sspseca.forma_consulta"
URL_POST = "https://siiauescolar.siiau.udg.mx/wal/sspseca.consulta_oferta"


#emula un navegador para acceder a la pagina y solicitar las clases,
#dandole un diccionario "payload", donde estan los requerimientos con el
#formato que pide, y regresa la pagina con puro html en texto

def consulta_oferta_session(payload):
    with requests.Session() as s:
        s.get(URL_FORM)

        headers = {
            "Referer": URL_FORM,
            "Origin": "https://siiauescolar.siiau.udg.mx",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        r = s.post(URL_POST, data=payload, headers=headers)
        r.encoding = "ISO-8859-1"
        r.raise_for_status()
        return r.text

#funcion quee construye el diccionario donde cada dato tiene el formato requerido
#para modificarlos abajo dejé un ejemplo y al final los formatos que acepta para 
# el ciclo y el centro universitario
def build_payload(
    ciclop="",# abajo estan todos pero por ejemplo "200480"
    cup="", # igual abajo estan todos pero por ejemplo "D"
    majrp="", # aqui va la clave de la carrera de 4 digitos y en mayuscula por ejemplo "ICOM"
    majrdescp="", # aqui va la descripcion de la carrera que ni idea que sea XD pero por lo general esta vacio
    crsep="", # clave del a materia por ejemplo "IL360"
    materiap="", # el nombre de la materia "REDES DE COMPUTADORAS"
    horaip="", #hora de inicio en 24hr
    horafp="", #hora de fin en 24hr
    dias=None, #aqui es para buscar por un dia, acepta "M-T-W-R-F-S"
    edifp="", # aqui see filtra por edificio
    aulap="", # aqui por aula
    dispp=False, # este para indicar si se quiere omitir las secciones sin cupos
    ordenp="0", # es el orden de como se muestra, 0 por materia, 1 por clave, y 2 por nrc
    mostrarp="500" # este de cuantos va mostrar, solo acepta 100, 200 y 500, pero en codigo se puede casi cualquier numero
):
    payload = {
        "ciclop": ciclop,
        "cup": cup,
        "majrp": majrp,
        "majrdescp": majrdescp,
        "crsep": crsep,
        "materiap": materiap,
        "horaip": horaip,
        "horafp": horafp,
        "edifp": edifp,
        "aulap": aulap,
        "ordenp": ordenp,
        "mostrarp": mostrarp,
    }
#esto solo ayuda a transformar el formato que necesita la pagina para los dias
    dias = dias or []
    dia_campos = {"M": "lup", "T": "map", "W": "mip", "R": "jup", "F": "vip", "S": "sap"}
    for d in dias:
        if d in dia_campos:
            payload[dia_campos[d]] = d
#esto solo ayuda a generar clases con cupos disponibles,omite los que no en caso de ser TRUE
    if dispp:
        payload["dispp"] = "D"

    return payload

#esta funcion solo parsea los resultados del html para no verlo en formato de codigo
#si no como en formato de texto en corchetes []
def parse_result(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    table = soup.find("table")
    if not table:
        return []

    rows = []
    for tr in table.find_all("tr")[1:]:  # saltar encabezado
        cols = [td.get_text(strip=True) for td in tr.find_all("td")]
        if cols:
            rows.append(cols)
    return rows

#aqui procesa la lista que se parseó para separar los datos que necesitamos
#esto es porque el formato que genera por cada clase es bastante raro:
'''
['194919', 
 'IL349', 
 'ADMINISTRACION', 
 'D01', 
 '8', 
 '35', 
 '2', 
 '011500-1655. M . J . .DEDTA01511/08/25 - 16/12/25', 
 '01', 
 '1500-1655', 
 '. M . J . .', 
 'DEDT', 
 'A015', 
 '11/08/25 - 16/12/25', 
 '01VENTURA MUÑOZ, MINERVA GUADALUPE', 
 '01', 
 'VENTURA MUÑOZ, MINERVA GUADALUPE'],
 ['01', '1500-1655', '. M . J . .', 'DEDT', 'A015', '11/08/25 - 16/12/25'], 
 ['01', 'VENTURA MUÑOZ, MINERVA GUADALUPE'],
'''
def procesar_clases(rows):
    clases = []
    i = 0
    while i < len(rows):
        fila = rows[i]

        if len(fila) >= 8 and fila[0].isdigit():
            clase = {
                "NRC": fila[0],
                "Clave": fila[1],
                "Materia": fila[2],
                "Seccion": fila[3],
                "Creditos": fila[4],
                "CupoTotal": fila[5],
                "CupoDisponible": fila[6],
                "Horario": "",
                "Dias": "",
                "Aula": "",
                "Maestro": ""
            }

            if i + 1 < len(rows) and len(rows[i + 1]) >= 6:
                detalle = rows[i + 1]
                clase["Horario"] = detalle[1]
                clase["Dias"] = detalle[2].replace(".", "").strip()
                clase["Aula"] = detalle[4]
                i += 1

            if i + 1 < len(rows) and len(rows[i + 1]) >= 2:
                posible_maestro = rows[i + 1]
                if len(posible_maestro) == 2:
                    clase["Maestro"] = posible_maestro[1]
                    i += 1

            clases.append(clase)

        i += 1

    return clases

#ya aqui solo genera un ejemplo con los datos que puse y
#convierte la salida en un archivo json
if __name__ == "__main__":
    payload = build_payload(
        ciclop="202520",
        cup="D",
        majrp="ICOM",
        dispp=True,
        ordenp="0",
        mostrarp="500"
    )
    html = consulta_oferta_session(payload)
    rows = parse_result(html)
    clases = procesar_clases(rows)

    with open("ofertaEjemplo.json", "w", encoding="utf-8") as f:
        json.dump(clases, f, ensure_ascii=False, indent=4)

    print(f"Se guardaron {len(clases)} clases en 'ofertaEjemplo.json'")


#-----------------------------------------------------------------------------------------------------------------------
#FORMATO PARA "ciclop" (ciclo que se cursa)
    """
    198010 - Calendario 80 A
    198210 - Calendario 82 A
    198810 - Calendario 88 A
    199010 - Calendario 90 A
    199030 - Calendario 90 C
    199110 - Calendario 91 A
    199220 - Calendario 92 B
    199310 - Calendario 93 A
    199320 - Calendario 93 B
    199410 - Calendario 94 A
    199420 - Calendario 94 B
    199510 - Calendario 95 A
    199520 - Calendario 95 B
    199610 - Calendario 96 A
    199611 - Calendario 1996 Extra
    199620 - Calendario 96 B
    199710 - Calendario 97 A
    199720 - Calendario 97 B
    199810 - Calendario 98 A
    199820 - Calendario 98 B
    199830 - Calendario 98 C
    199840 - Calendario 98 D
    199850 - Calendario 98 E
    199860 - Calendario 98 A anualidades
    199870 - Calendario 98 B anualidades
    199910 - Calendario 99 A
    199911 - Calendario 99 A bis
    199920 - Calendario 99 B
    199921 - Calendario 99 B
    199950 - Calendario 99 E cuatrimestre
    199960 - Calendario 99 A anualidades
    199990 - Calendario de Prueba
    200010 - Calendario 00 A
    200020 - Calendario 00 B
    200030 - Calendario 2000 C
    200050 - Calendario 2000 E
    200060 - Calendario 2000 B anualidades
    200099 - Calendario de prueba
    200110 - Calendario 01 A
    200120 - Calendario 01 B
    200130 - Calendario 01 C cuatrimestres
    200160 - Calendario 01 A Anualidades
    200210 - Calendario 02 A
    200220 - Calendario 02 B
    200280 - Cursos de Verano 2002
    200310 - Calendario 03 A
    200320 - Calendario 03 B
    200380 - Cursos de Verano 2003
    200410 - Calendario 04 A
    200420 - Calendario 04 B
    200480 - Cursos de Verano 2004
    200510 - Calendario 05 A
    200520 - Calendario 05 B
    200580 - Cursos de Verano 2005
    200610 - Calendario 06 A
    200620 - Calendario 06 B
    200680 - Cursos de Verano 2006
    200690 - Calendario 06 U
    200710 - Calendario 07 A
    200720 - Calendario 07 B
    200780 - Cursos de Verano 2007
    200790 - Calendario 07 U
    200810 - Calendario 08 A
    200820 - Calendario 08 B
    200880 - Cursos de Verano 2008
    200890 - Calendario 08 U
    200910 - Calendario 09 A
    200920 - Calendario 09 B
    200980 - Cursos de Verano 2009
    200990 - Calendario 09 U
    201010 - Calendario 10 A
    201020 - Calendario 10 B
    201080 - Cursos de Verano 2010
    201090 - Calendario 10 U
    201110 - Calendario 11 A
    201120 - Calendario 11 B
    201180 - Cursos de Verano 2011
    2011H - Promocion 2011H
    2011S - Promocion 2011S
    2011T - Promocion 2011T
    2011Z - Promocion 2011Z
    201210 - Calendario 12 A
    201220 - Calendario 12 B
    201280 - Cursos de Verano 2012
    2012P - Promocion 2012P
    2012S - Promocion 2012S
    2012T - Promocion 2012T
    201310 - Calendario 13 A
    201320 - Calendario 13 B
    201380 - Cursos de Verano 2013
    2013R - Promocion 2013R
    2013S - Promocion 2013S
    201410 - Calendario 14 A
    201420 - Calendario 14 B
    201480 - Cursos de Verano 2014
    2014D - Promocion 2014D
    2014R - Promocion 2014R
    2014S - Promocion 2014S
    2014T - Promocion 2014T
    201510 - Calendario 15 A
    201520 - Calendario 15 B
    201580 - Ciclo de Verano 2015
    2015E - Promocion 2015E
    2015G - Promocion 2015G
    2015S - Promocion 2015S
    2015T - Promocion 2015T
    201610 - Calendario 16 A
    201620 - Calendario 16 B
    201680 - Ciclo de Verano 2016
    2016E - Promocion 2016E
    2016R - Promocion 2016R
    2016S - Promocion 2016S
    2016T - Promocion 2016T
    201710 - Calendario 17 A
    201720 - Calendario 17 B
    201780 - Ciclo de Verano 2017
    2017D - Promocion 2017D
    2017E - Promocion 2017E
    2017F - Promocion 2017F
    2017I - Promocion 2017I
    201810 - Calendario 18 A
    201820 - Calendario 18 B
    201880 - Ciclo de Verano 2018
    2018D - Promocion 2018D
    2018E - Promocion 2018E
    2018F - Promocion 2018F
    2018G - Promocion 2018G
    201910 - Calendario 19 A
    201920 - Calendario 19 B
    201980 - Ciclo de Verano 2019
    2019C - Promocion 2019C
    2019D - Promocion 2019D
    2019E - Promocion 2019E
    202010 - Calendario 20 A
    202020 - Calendario 20 B
    202080 - Ciclo de Verano 2020
    2020D - Promocion 2020D
    2020G - Promocion 2020G
    2020Z - Calendario 20Z Cuatrimestre
    202110 - Calendario 21 A
    202120 - Calendario 21 B
    2021C - Promocion 2021C
    2021D - Promocion 2021D
    2021F - Promocion 2021F
    2021G - Promocion 2021G
    2021I - Promocion 2021I
    2021X - Calendario 21X Cuatrimestre
    2021Y - Calendario 21Y Cuatrimestre
    2021Z - Calendario 21Z Cuatrimestre
    202210 - Calendario 22 A
    202220 - Calendario 22 B
    2022C - Promocion 2022C
    2022E - Promocion 2022E
    2022F - Promocion 2022F
    2022H - Promocion 2022H
    2022X - Calendario 22X Cuatrimestre
    2022Y - Calendario 22Y Cuatrimestre
    2022Z - Calendario 22Z Cuatrimestre
    202310 - Calendario 23 A
    202320 - Calendario 23 B
    202380 - Ciclo de Verano 2023
    2023C - Promocion 2023C
    2023E - Promocion 2023E
    2023F - Promocion 2023F
    2023I - Promocion 2023I
    2023J - Calendario 23 J
    2023X - Calendario 23X Cuatrimestre
    2023Y - Calendario 23Y Cuatrimestre
    2023Z - Calendario 23Z Cuatrimestre
    202410 - Calendario 24 A
    202420 - Calendario 24 B
    202480 - Ciclo de Verano 2024
    2024C - Promocion 2024C
    2024D - Promocion 2024 D
    2024E - Promocion 2024E
    2024X - Calendario 24X Cuatrimestre
    2024Y - Calendario 24Y Cuatrimestre
    2024Z - Calendario 24Z Cuatrimestre
    202510 - Calendario 25 A
    202520 - Calendario 25 B
    202580 - Ciclo de Verano 2025
    2025C - Promocion 2025C
    2025D - Promocion 2025D
    2025E - Promocion 2025E
    202610 - Calendario 26 A 
    """

#FORMATO PARA "cup" (centro universitario)
    """
    3 - C. U. DE TLAJOMULCO
    4 - C. U. DE GUADALAJARA
    5 - C.U. DE TLAQUEPAQUE
    6 - C.U. DE CHAPALA
    A - C.U. DE ARTE, ARQ. Y DISEÑO
    B - C.U. DE CS. BIOLOGICO Y AGR.
    C - C.U. DE CS. ECONOMICO-ADMVAS.
    D - C.U. DE CS. EXACTAS E ING.
    E - C.U. DE CS. DE LA SALUD
    F - C.U. DE CS. SOCIALES Y HUM.
    G - C.U. DE LOS ALTOS
    H - C.U. DE LA CIENEGA
    I - C.U. DE LA COSTA
    J - C.U. DE LA COSTA SUR
    K - C.U. DEL SUR
    M - C. U. DE LOS VALLES
    N - C.U. DEL NORTE
    O - CUCEI SEDE VALLES
    P - CUCSUR SEDE VALLES
    Q - CUCEI SEDE NORTE
    R - CUALTOS SEDE NORTE
    S - CUCOSTA SEDE NORTE
    T - SEDE TLAJOMULCO
    U - C. U. DE LOS LAGOS
    V - CICLO DE VERANO
    W - CUCEA SEDE VALLE
    X - SIST. DE UNIVERSIDAD VIRTUAL
    Y - ESCUELAS INCORPORADAS
    Z - C. U. DE TONALA
    """
