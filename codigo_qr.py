# 1. Convertir texto a ASCII y guardarlo en un vector
CARACTERES_ASCII = (
    " !\"#$%&'()*+,-./0123456789:;<=>?@"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`"
    "abcdefghijklmnopqrstuvwxyz{|}~"
)

def generar_diccionario():
    diccionario = {}
    posicion = 32
    for c in CARACTERES_ASCII:
        diccionario[c] = posicion
        posicion = posicion + 1
    return diccionario

DICCIONARIO = generar_diccionario()   

def valor_ascii(c):
    if c in DICCIONARIO:
        return DICCIONARIO[c]
    else:
        return -1                                 

def guardar_vector_ascii(url):
    vector_ascii = []
    for c in url:
        vector_ascii.append(valor_ascii(c))
    return vector_ascii

#2 Convertir ascii a binario y guardar en una cadena
def iniciar_cadena(vector_ascii):
    binario = '0100'
    binario += format(len(vector_ascii), '08b')
    return binario

def cadena_bin(binario, vector_ascii):
    for valor in vector_ascii:
        binario += format(valor, '08b')
    return(binario)

#3 Acomodar la cadena en la matriz 25x25
def crear_matriz(tamano=25):
    matriz = []
    for fila in range(tamano):
        matriz.append([0] * tamano)
    return matriz

def acomodar_cadena(matriz, binario):
    n = len(matriz)
    i = 0
    columna = n - 1
    hacia_arriba = True
    # Se recorre en franjas de 2 columnas, empezando abajo a la derecha.
    # Una franja sube y la siguiente baja (serpiente).
    while columna >= 0 and i < len(binario):
        if hacia_arriba:
            #empieza en 24(n-1), hasta antes de 0 (-1) y baja de 1 en 1 (-1)
            filas = range(n - 1, -1, -1)
        else:
            filas = range(0, n)
        for fila in filas:
            # Primero la columna derecha, luego la izquierda
            for c in (columna, columna - 1):
                # para la ultima columna
                if c < 0:
                    continue
                if i < len(binario):
                    matriz[fila][c] = int(binario[i])
                    i += 1
        columna -= 2
        hacia_arriba = not hacia_arriba
    return matriz

def imprimir_matriz(matriz):
    for fila in matriz:
        linea = ''
        for celda in fila:
            if celda == 1:
                linea += '██'
            else:
                linea += '  '
        print(linea)


def main():
    url = input("Introduce la URL: ")
    vector_ascii = guardar_vector_ascii(url)
    print("Vector ASCII:", vector_ascii)
    binario = iniciar_cadena(vector_ascii)
    binario = cadena_bin(binario, vector_ascii)
    print("Cadena de binario: ", binario)
    matriz = crear_matriz()
    matriz = acomodar_cadena(matriz, binario)
    print("Matriz 25x25:")
    imprimir_matriz(matriz)

main()