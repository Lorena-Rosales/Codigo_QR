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


def main():
    url = input("Introduce la URL: ")
    vector_ascii = guardar_vector_ascii(url)
    print("Vector ASCII:", vector_ascii)
    binario = iniciar_cadena(vector_ascii)
    binario = cadena_bin(binario, vector_ascii)
    print("Cadena de binario: ", binario)

main()