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
        if valor >= 0 and valor <= 255:
            binario += format(valor, '08b')
        else:
            print("ERROR Valor invalido")
            return ""
    return(binario)

def completar_bin(binario, capacidadBytes=34):
    capacidadBits = capacidadBytes*8
    faltan = capacidadBits - len(binario)

    if faltan < 0:
        print("ERROR Los datos son mayores a la capacidad")
        return ""
    binario += "0" * min(4, faltan)

    while len(binario) % 8 != 0:
        binario += "0"

    rellenos = ("11101100", "00010001")
    indice = 0

    while len(binario) < capacidadBits:
        binario += rellenos[indice]
        indice = 1 - indice
    return binario

def convertir_bytes(binario):
    datos = []
    for i in range(0, len(binario), 8):
        datos.append(int(binario[i:i + 8], 2))
    return datos

def reed_solomon(datos, cantidadError=10):
    generador = [1]
    raiz = 1

    # Crear el polinomio generador
    for i in range(cantidadError):
        nuevo = [0] * (len(generador) + 1)

        for j in range(len(generador)):
            nuevo[j] ^= generador[j]

            a = generador[j]
            b = raiz
            producto = 0

            while b:
                if b & 1:
                    producto ^= a

                a <<= 1
                if a & 0x100:
                    a ^= 0x11D

                b >>= 1
            nuevo[j + 1] ^= producto

        generador = nuevo
        a = raiz
        b = 2
        producto = 0

        while b:
            if b & 1:
                producto ^= a

            a <<= 1
            if a & 0x100:
                a ^= 0x11D

            b >>= 1
        raiz = producto

    # Calcular los bytes de correccion
    resultado = datos + [0] * cantidadError

    for i in range(len(datos)):
        coeficiente = resultado[i]

        if coeficiente != 0:
            for j in range(len(generador)):
                a = generador[j]
                b = coeficiente
                producto = 0

                while b:
                    if b & 1:
                        producto ^= a

                    a <<= 1
                    if a & 0x100:
                        a ^= 0x11D

                    b >>= 1
                resultado[i + j] ^= producto
    return resultado[len(datos):]

#3 Acomodar la cadena en la matriz 25x25
def crear_matriz(tamano=25):
    matriz = []
    for fila in range(tamano):
        matriz.append([0] * tamano)
    return matriz

def patron_busqueda(matriz, reservada, filaInicial, columnaInicial):
    tam = len(matriz)

    for fila in range(filaInicial - 1, filaInicial + 8):
        for columna in range(columnaInicial - 1, columnaInicial + 8):

            if fila < 0 or fila >= tam or columna < 0 or columna >= tam:
                continue

            filaPatron = fila - filaInicial
            columnaPatron = columna - columnaInicial

            # Separador blanco
            if (filaPatron == -1 or filaPatron == 7 or columnaPatron == -1 or columnaPatron == 7):
                matriz[fila][columna] = 0
            # Borde exterior negro
            elif (filaPatron == 0 or filaPatron == 6 or columnaPatron == 0 or columnaPatron == 6):
                matriz[fila][columna] = 1
            # Cuadrado central negro
            elif (2 <= filaPatron <= 4 and 2 <= columnaPatron <= 4):
                matriz[fila][columna] = 1
            # Anillo interior blanco
            else:
                matriz[fila][columna] = 0

            reservada[fila][columna] = 1
    return matriz, reservada

def patron_temporalizacion(matriz, reservada):
    tam = len(matriz)

    for i in range(8, tam - 8):
        if i % 2 == 0:
            valor = 1
        else:
            valor = 0

        if reservada[6][i] == 0:
            matriz[6][i] = valor
            reservada[6][i] = 1
        if reservada[i][6] == 0:
            matriz[i][6] = valor
            reservada[i][6] = 1

    return matriz, reservada

def patron_alineamiento(matriz, reservada):
    centroFila = 18
    centroColumna = 18

    for f in range(-2, 3):
        for c in range(-2, 3):
            fila = centroFila + f
            columna = centroColumna + c

            if abs(f) == 2 or abs(c) == 2:
                matriz[fila][columna] = 1
            elif f == 0 and c == 0:
                matriz[fila][columna] = 1
            else:
                matriz[fila][columna] = 0
            
            reservada[fila][columna] = 1
    return matriz, reservada

def reservar_formato(matriz, reservada):
    tam = len(matriz)

    # Bits de formato para nivel L y máscara 0
    formato = "111011111000100"

    posiciones1 = [
        (8, 0), (8, 1), (8, 2), (8, 3), (8, 4),
        (8, 5), (8, 7), (8, 8), (7, 8), (5, 8),
        (4, 8), (3, 8), (2, 8), (1, 8), (0, 8)
    ]

    posiciones2 = [
        (24, 8), (23, 8), (22, 8), (21, 8), (20, 8),
        (19, 8), (18, 8), (8, 17), (8, 18), (8, 19),
        (8, 20), (8, 21), (8, 22), (8, 23), (8, 24)
    ]

    for i in range(15):
        fila, columna = posiciones1[i]
        matriz[fila][columna] = int(formato[i])
        reservada[fila][columna] = 1

        fila, columna = posiciones2[i]
        matriz[fila][columna] = int(formato[i])
        reservada[fila][columna] = 1

    matriz[17][8] = 1
    reservada[17][8] = 1

    return matriz, reservada

def acomodar_cadena(matriz, binario, reservada):
    n = len(matriz)
    i = 0
    columna = n - 1
    hacia_arriba = True
    # Se recorre en franjas de 2 columnas, empezando abajo a la derecha.
    # Una franja sube y la siguiente baja (serpiente).
    while columna >= 1 and i < len(binario):
        #la columna 6 esta reservada
        if columna == 6:
            columna = 5
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
                if reservada[fila][c]==0:
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
    binario = completar_bin(binario)
    datos = convertir_bytes(binario)
    correccion = reed_solomon(datos)

    datos_completos = datos + correccion
    binario_completo = ""
    for valor in datos_completos:
        binario_completo+=format(valor, '08b')

    print("Cadena de binario: ", binario_completo)

    matriz = crear_matriz()
    reservada = crear_matriz()

    matriz, reservada = patron_busqueda(matriz, reservada, 0, 0)
    matriz, reservada = patron_busqueda(matriz, reservada, 0, 18)
    matriz, reservada = patron_busqueda(matriz, reservada, 18, 0)

    matriz, reservada = patron_temporalizacion(matriz, reservada)
    matriz, reservada = patron_alineamiento(matriz, reservada)
    matriz, reservada = reservar_formato(matriz, reservada)
    matriz = acomodar_cadena(matriz, binario_completo, reservada)
    print("Matriz 25x25:")
    imprimir_matriz(matriz)

main()