# Codigo_QR

Generador de código QR construido **desde cero en Python**, sin librerías externas.

## Descripción

Proyecto del primer parcial de la materia de Programación en Python. A partir de una URL o un texto, el programa genera un código QR **versión 2 (matriz de 25 × 25 módulos)** implementando a mano cada etapa del proceso:

1. Conversión del texto a ASCII.
2. Armado de la cadena de bits.
3. Corrección de errores con Reed-Solomon.
4. Construcción de la matriz y colocación de los patrones fijos.
5. Inserción de los datos en zigzag.
6. Enmascaramiento (8 máscaras evaluadas con las 4 reglas de penalización).

## Requisitos

- **Python 3.10 o superior** (el código usa `match/case`).
- No requiere instalar nada: solo usa la librería estándar.

## Ejecución

```bash
python codigo_qr.py
```

Al iniciar aparece un menú que se repite hasta que el usuario decide salir:

```
-----CÓDIGO QR------
1. Generar Código QR
2. Validar Reed-Solomon
3. Salir
```

| Opción | Qué hace |
|---|---|
| 1 | Pide una URL o texto y genera el QR, mostrando cada etapa en pantalla |
| 2 | Valida el algoritmo de Reed-Solomon con un ejemplo conocido |
| 3 | Cierra el programa |

## Texto permitido

- Máximo **32 caracteres**.
- Solo caracteres ASCII imprimibles (letras, números y símbolos como `: / . - _ ? = & %`).
- **No se aceptan** espacios, acentos, la letra `ñ` ni emojis.

| Texto | ¿Válido? |
|---|---|
| `https://aulavirtual.uaa.mx` | Sí (26 caracteres) |
| `www.google.com` | Sí |
| `hola mundo` | No: tiene un espacio |
| `canción` | No: tiene un acento |
| `https://github.com/Lorena-Rosales` | No: tiene 33 caracteres |

## Parámetros del QR

| Parámetro | Valor |
|---|---|
| Versión | 2 (25 × 25 módulos) |
| Nivel de corrección de errores | L |
| Modo de codificación | Byte (indicador `0100`, longitud en 8 bits) |
| Palabras de datos | 34 (272 bits) |
| Palabras de corrección (Reed-Solomon) | 10 |
| Palabras totales | 44 (352 bits) |
| Módulos reservados (patrones y formato) | 266 |
| Módulos de datos | 359 (352 bits + 7 de relleno) |

## Etapas y funciones

| Etapa | Qué hace | Funciones |
|---|---|---|
| Entrada | Valida el texto antes de procesarlo | `validar_url` |
| ASCII | Convierte cada carácter a su valor ASCII con un diccionario propio (sin `ord()`) | `generar_diccionario`, `valor_ascii`, `guardar_vector_ascii` |
| Cadena de bits | Modo + longitud + datos + terminador + relleno hasta 272 bits | `iniciar_cadena`, `cadena_bin`, `completar_bin`, `convertir_bytes` |
| Reed-Solomon | Calcula los bytes de corrección en GF(256) | `reed_solomon`, `validar_reed_solomon` |
| Matriz | Crea la matriz y coloca buscadores, temporización, alineamiento y formato | `crear_matriz`, `patron_busqueda`, `patron_temporalizacion`, `patron_alineamiento`, `reservar_formato` |
| Zigzag | Inserta los bits en pares de columnas, alternando subida y bajada | `acomodar_cadena` |
| Máscara | Prueba las 8 máscaras, las califica y elige la de menor penalización | `condicion_mascara`, `aplicar_mascara_matriz`, `calcular_penalizacion`, `seleccionar_mascara` |
| Formato | Calcula y escribe los 15 bits de formato (nivel + máscara) | `generar_bits_formato`, `colocar_bits_formato` |
| Salida | Dibuja la matriz en la terminal | `imprimir_matriz` |

La tabla ASCII funciona porque los códigos son consecutivos: si los caracteres se escriben en orden a partir del 32, la posición de cada uno más 32 es su código.

## Qué muestra el programa al generar un QR

Para cada ejecución se imprimen las evidencias de cada etapa:

1. Vector ASCII, polinomio generador, palabras de datos, palabras de corrección y secuencia final.
2. **Matriz de módulos reservados** (patrones fijos y formato).
3. **Matriz con datos antes de Reed-Solomon**.
4. **Matriz con datos y Reed-Solomon antes del enmascaramiento**.
5. Tabla de penalización de las 8 máscaras y la máscara elegida.
6. **Matriz QR final enmascarada**.

Ejemplo de salida con `https://aulavirtual.uaa.mx`:

```
Vector ASCII: [104, 116, 116, 112, 115, 58, 47, 47, 97, 117, 108, 97, 118, 105, 114, 116, 117, 97, 108, 46, 117, 97, 97, 46, 109, 120]
Polinomio generador: [1, 216, 194, 159, 111, 199, 94, 95, 113, 157, 193]
Palabras de correccion ( 10 ): [72, 149, 29, 134, 184, 148, 197, 146, 4, 177]
Penalización: [598, 595, 564, 631, 466, 559, 545, 715]
Máscara seleccionada: 4
Modulos funcionales alterados por la mascara: 0
Modulos de datos invertidos por la mascara: 177
```

## Enmascaramiento

La máscara invierte (0 ↔ 1) ciertos módulos **de datos** según una fórmula de su fila y su columna. Evita zonas grandes del mismo color y figuras que se parezcan a los buscadores de las esquinas. No altera los módulos funcionales (buscadores, temporización, alineamiento y formato).

| Máscara | Se invierte el módulo si... | Cómo se ve |
|---|---|---|
| 0 | `(fila + col) % 2 == 0` | Tablero de ajedrez |
| 1 | `fila % 2 == 0` | Franjas horizontales |
| 2 | `col % 3 == 0` | Franjas verticales |
| 3 | `(fila + col) % 3 == 0` | Diagonales |
| 4 | `(fila // 2 + col // 3) % 2 == 0` | Bloques de 2 × 3 |
| 5 | `(fila * col) % 2 + (fila * col) % 3 == 0` | Rejilla de puntos y cruces |
| 6 | `((fila * col) % 2 + (fila * col) % 3) % 2 == 0` | Rejilla rellena |
| 7 | `((fila + col) % 2 + (fila * col) % 3) % 2 == 0` | Mezcla de diagonales y bloques |

Cada máscara se califica con las 4 reglas de penalización de la norma; gana la de menor puntaje:

| Regla | Castiga | Puntos |
|---|---|---|
| 1 | 5 o más módulos del mismo color seguidos | 3 + los que sobren de 5 |
| 2 | Bloques de 2 × 2 del mismo color | 3 por bloque |
| 3 | Patrón `1011101` con 4 módulos blancos al lado | 40 por patrón |
| 4 | Desbalance entre módulos negros y blancos | 10 por cada 5 % de diferencia con el 50 % |

## Validación de Reed-Solomon

La opción 2 del menú comprueba la función `reed_solomon` con el ejemplo **"HELLO WORLD" (versión 1, nivel M)**: con las 16 palabras de datos del ejemplo, el programa debe obtener las mismas 10 palabras de corrección que publica el tutorial.

- Esperado: `[196, 35, 39, 119, 235, 215, 231, 226, 93, 23]`
- El polinomio generador calculado coincide con el del tutorial (expresado en enteros en lugar de potencias de α).

## Limitaciones

- Solo genera la **versión 2** con **nivel de corrección L**.
- Máximo de 32 caracteres por código.
- Siempre usa modo byte.
- La salida es en la terminal. Para escanearlo con el celular conviene una terminal con fondo claro, o capturar la imagen y verla con fondo blanco y un margen alrededor.

## Estructura del repositorio

```
Codigo_QR/
├── codigo_qr.py    Programa principal
├── README.md
└── .gitignore
```

## Referencias

- ISO/IEC 18004: norma de los códigos QR.
- [QR Mask Patterns Explained](https://www.thonky.com/qr-code-tutorial/mask-patterns): fórmulas de las 8 máscaras.
- [Data Masking](https://www.thonky.com/qr-code-tutorial/data-masking): reglas de penalización.
- [Error Correction Coding](https://www.thonky.com/qr-code-tutorial/error-correction-coding): ejemplo "HELLO WORLD" de Reed-Solomon.
