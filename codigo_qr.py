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

# Validación de la cadena para que tenga formato de URL (no acepta, españos, acentos ni letra ñ)
def validar_url(cadena, limite_caracteres=32):
    if len(cadena) == 0:
        return False, "El texto no puede estar vacio."
    if len(cadena) > limite_caracteres:
        return False, "Maximo " + str(limite_caracteres) + " caracteres (escribiste " + str(len(cadena)) + ")."
    for c in cadena:
        if c == " ":
            return False, "No se permiten espacios."
        if c not in DICCIONARIO:
            return False, "Caracter no permitido: '" + c + "'"
    return True, ""

# 8 máscaras
def condicion_mascara(mascara, fila, col):
    match mascara:
        case 0:
            return (fila + col) % 2 == 0
        case 1:
            return fila % 2 == 0
        case 2:
            return col % 3 == 0
        case 3:
            return (fila + col) % 3 == 0
        case 4:
            return (fila // 2 + col // 3) % 2 == 0
        case 5:
            return (fila * col) % 2 + (fila * col) % 3 == 0
        case 6:
            return ((fila * col) % 2 + (fila * col) % 3) % 2 == 0
        case _:
            return ((fila + col) % 2 + (fila * col) % 3) % 2 == 0

def aplicar_mascara_matriz(matriz, reservada, mascara):
    tam = len(matriz)
    matriz_con_mascara = []
    for f in range(tam):
        matriz_con_mascara.append(matriz[f][:])
    for f in range(tam):
        for c in range(tam):
            if reservada[f][c] == 0 and condicion_mascara(mascara, f, c):
                matriz_con_mascara[f][c] = 1 - matriz_con_mascara[f][c]
    return matriz_con_mascara

# Generación de bits que le dicen al lector qué nivel de corrección y qué máscara se usó
def generar_bits_formato(nivel_bits, mascara):
    datos = (nivel_bits << 3) | mascara
    residuo = datos << 10
    for i in range(14, 9, -1):
        if (residuo >> i) & 1:
            residuo ^= 0x537 << (i - 10)
    bits = ((datos << 10) | residuo) ^ 0x5412
    return format(bits, '015b')

def colocar_bits_formato(matriz, formato):
    posiciones1 = [(8,0),(8,1),(8,2),(8,3),(8,4),(8,5),(8,7),(8,8),(7,8),(5,8),(4,8),(3,8),(2,8),(1,8),(0,8)]
    posiciones2 = [(24,8),(23,8),(22,8),(21,8),(20,8),(19,8),(18,8),(8,17),(8,18),(8,19),(8,20),(8,21),(8,22),(8,23),(8,24)]
    for i in range(15):
        fila, col = posiciones1[i]
        matriz[fila][col] = int(formato[i])
        fila, col = posiciones2[i]
        matriz[fila][col] = int(formato[i])
    return matriz

# Coloca una calificación a una matriz con las 4 reglas de la norma
def calcular_penalizacion(matriz):
    n = len(matriz)
    puntos = 0
    # Regla 1: Busca 5 o más módulos del mismo color seguidos en una fila o en una columna
    for num_linea in range(n):
        for linea in ([matriz[num_linea][col] for col in range(n)], [matriz[fila][num_linea] for fila in range(n)]):
            racha = 1
            for i in range(1, n):
                if linea[i] == linea[i - 1]:
                    racha += 1
                else:
                    if racha >= 5:
                        puntos += 3 + (racha - 5)
                    racha = 1
            if racha >= 5:
                puntos += 3 + (racha - 5)
    # Regla 2: Busca bloques de 2x2 del mismo color
    for fila in range(n - 1):
        for col in range(n - 1):
            if matriz[fila][col] == matriz[fila][col+1] == matriz[fila+1][col] == matriz[fila+1][col+1]:
                puntos += 3
    # Regla 3: Busca una figura parecido al patrón de posición (1011101 con 4 módulos blancos al lado)
    patron_buscador = [1, 0, 1, 1, 1, 0, 1]
    for num_linea in range(n):
        for linea in ([matriz[num_linea][col] for col in range(n)], [matriz[fila][num_linea] for fila in range(n)]):
            for i in range(n - 6):
                if linea[i:i+7] == patron_buscador:
                    if (i >= 4 and linea[i-4:i] == [0,0,0,0]) or (i + 11 <= n and linea[i+7:i+11] == [0,0,0,0]):
                        puntos += 40
    # Regla 4: Busca qué porcentaje del QR es negro
    modulos_negros = sum(sum(fila) for fila in matriz)
    porcentaje = modulos_negros * 100 / (n * n)
    puntos += int(abs(porcentaje - 50) // 5) * 10
    return puntos

# Prueba las 8 máscaras, al calcular la penalziación se queda con la de menos puntos.
def seleccionar_mascara(matriz, reservada, nivel_bits):
    mejor_mascara, mejor_penalizacion, mejor_matriz, tabla = 0, None, None, []
    for mascara in range(8):
        matriz_candidata = aplicar_mascara_matriz(matriz, reservada, mascara)
        matriz_candidata = colocar_bits_formato(matriz_candidata, generar_bits_formato(nivel_bits, mascara))
        penalizacion = calcular_penalizacion(matriz_candidata)
        tabla.append(penalizacion)
        if mejor_penalizacion is None or penalizacion < mejor_penalizacion:
            mejor_mascara, mejor_penalizacion, mejor_matriz = mascara, penalizacion, matriz_candidata
    return mejor_mascara, mejor_matriz, tabla

def imprimir_matriz(matriz):
    for fila in matriz:
        linea = ''
        for celda in fila:
            if celda == 1:
                linea += '██'
            else:
                linea += '  '
        print(linea)


def generar_qr():
    while True:
        url = input("\nIntroduce la URL: ")
        valido, motivo = validar_url(url)
        if valido:
            break
        print ("Error: ", motivo)

    vector_ascii = guardar_vector_ascii(url)
    print("\nVector ASCII:", vector_ascii)

    binario = iniciar_cadena(vector_ascii)
    binario = cadena_bin(binario, vector_ascii)
    binario = completar_bin(binario)
    datos = convertir_bytes(binario)
    correccion = reed_solomon(datos)

    datos_completos = datos + correccion
    binario_completo = ""
    for valor in datos_completos:
        binario_completo+=format(valor, '08b')

    print("\nCadena de binario: ", binario_completo)

    matriz = crear_matriz()
    reservada = crear_matriz()

    matriz, reservada = patron_busqueda(matriz, reservada, 0, 0)
    matriz, reservada = patron_busqueda(matriz, reservada, 0, 18)
    matriz, reservada = patron_busqueda(matriz, reservada, 18, 0)

    matriz, reservada = patron_temporalizacion(matriz, reservada)
    matriz, reservada = patron_alineamiento(matriz, reservada)
    matriz, reservada = reservar_formato(matriz, reservada)
    matriz = acomodar_cadena(matriz, binario_completo, reservada)

    mejor, matriz_final, tabla = seleccionar_mascara(matriz, reservada, 1)
    print("\nPenalización:", tabla)
    print("\nMáscara seleccionada:", mejor)

    print("\nMatriz 25x25:\n")
    imprimir_matriz(matriz_final)

def mostrar_menu():
    print()
    print("-----CÓDIGO QR------")
    print("1. Generar Código QR")
    print("2. Salir")

def main():
    while True:
        mostrar_menu()
        opcion = input("Selecciona una opción: ").strip()

        if opcion == "1":
            generar_qr()
        elif opcion == "2":
            break
        else:
            print("Opcion no válida")

main()
