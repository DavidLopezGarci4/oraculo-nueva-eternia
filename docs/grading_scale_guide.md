# Guía Maestra de la Escala de Conservación y Valoración (Oráculo)

Este documento define la escala de valoración y los coeficientes matemáticos aplicados en la plataforma Oráculo para ajustar el **Valor de Mercado Base** de las reliquias en función de su estado físico y de conservación.

---

## 1. Clasificación del Estado Base (Condition)

El empaque y el desempaque determinan la categoría base del producto en el coleccionismo. El sistema define tres estados fundamentales:

| Estado | Descripción Técnica | Coeficiente Base |
| :--- | :--- | :--- |
| **MOC (Mint on Card)** | La figura está completamente sellada en su blíster original (o caja sellada *Mint in Box - MIB*). Nunca ha sido abierta. | **1.0** (100% del valor base) |
| **NEW (New/Open Box)** | La figura está intacta/nueva (no jugada), pero el blíster ha sido abierto, la burbuja está parcialmente desprendida, o la caja exterior está abierta para inspección. | **0.75** (75% del valor base) |
| **LOOSE (Loose)** | La figura está fuera de su empaque (suelta). No conserva burbuja, cartón ni caja original. | **0.50** (50% del valor base) |

---

## 2. Escala C de Conservación (Grading 1.0 a 10.0)

La escala numérica de **1.0 a 10.0** de Oráculo se basa en la clásica **Escala C (C-1 a C-10)** empleada históricamente por coleccionistas de Star Wars y MOTU para evaluar el estado físico del cartón, la burbuja y la figura.

A continuación, se detalla el significado de cada nota y su equivalencia con las escalas de gradación profesional como **AFA (Action Figure Authority)** o **CAS (Collectible Archive Services)**:

### 10.0 - Gem Mint (C-10 / AFA 95-100)
- **Cartón:** Absolutamente plano, esquinas perfectas y afiladas, colores vivos sin desgaste por luz ni humedad. Sin dobleces ni arrugas de estrés.
- **Burbuja / Blíster:** Cristalina, sin rayones, sin hundimientos y perfectamente adherida al cartón.
- **Valoración:** Pieza perfecta de museo. Sin penalización de valor.

### 9.5 - Mint (C-9.5 / AFA 90)
- **Cartón:** Casi perfecto. Puede presentar un micro-desgaste en una esquina visible solo bajo inspección minuciosa.
- **Burbuja:** Perfecta, cristalina y firme.
- **Valoración:** Pieza de calidad premium muy alta.

### 9.0 - Near Mint / Mint (C-9.0 / AFA 85)
- **Cartón:** Muy limpio. **Se permite un cartón ligeramente doblado (crease leve) o esquinas ligeramente blandas**, siempre que el cartón se mantenga plano en general.
- **Burbuja:** Transparente e intacta, sin abolladuras importantes.
- **Figura:** Intacta en su interior.
- **Nota:** *Aquí es donde pertenece una figura que nunca ha sido sacada de su blíster (MOC) pero cuyo cartón tiene un leve doblez o arruga por almacenamiento.*

### 8.5 - Near Mint (C-8.5 / AFA 80)
- **Cartón:** Desgaste menor por almacenamiento (shelf-wear). Pequeña arruga o doblez en las esquinas, o una marca leve por etiqueta de precio antigua.
- **Burbuja:** Intacta, con micro-rayones superficiales inevitables.
- **Valoración:** El estándar clásico para coleccionistas exigentes.

### 8.0 - Very Good / Near Mint (C-8.0 / AFA 75-80)
- **Cartón:** Arrugas de estrés moderadas alrededor del colgador o esquinas. El cartón puede tener una ligera curvatura.
- **Burbuja:** Adherida firmemente, pero con rayones menores o pequeña deformación en las esquinas del plástico.

### 7.0 - Good (C-7.0 / AFA 70)
- **Cartón:** Dobleces evidentes y marcados, desgaste en bordes con pérdida de color, esquinas abiertas.
- **Burbuja:** Rayada o con abolladuras leves, pero completamente sellada.

### 5.0 - Fair (C-5.0 / AFA 50)
- **Cartón:** Muy desgastado, doblado, con roturas por humedad, residuos de pegamento o rasgaduras grandes al retirar etiquetas.
- **Burbuja:** Amarilleada, abollada o parcialmente despegada en los bordes.

### 3.0 a 1.0 - Poor (C-3.0 a C-1.0 / AFA <40)
- **Empaque:** Blíster roto, burbuja sujeta con cinta adhesiva, o cartón mutilado. La figura sigue dentro pero el conjunto está severamente dañado.

---

## 3. Algoritmo de Ajuste de Valoración (Fórmula Matemática)

Para calcular el **Valor Real Ajustado** de una pieza, el sistema utiliza la siguiente fórmula:

$$\text{Valor Ajustado} = \text{Valor de Mercado Base} \times \text{Multiplicador de Estado (Base)} \times \text{Factor de Conservación (Grading)}$$

Donde el **Factor de Conservación** se calcula de la siguiente manera:

$$\text{Factor de Conservación} = 1.0 - ((10.0 - \text{Grade}) \times 0.04)$$
*Nota: El factor de conservación tiene un suelo mínimo de 0.10 (10%) para evitar que el valor caiga a cero.*

### Tabla de Descuentos por Conservación:
Cada 0.5 puntos que se reduce en la nota de conservación (Grading) resta un **2%** de valor sobre el estado base:

- **10.0:** Factor = **1.0** (0% de descuento)
- **9.5:** Factor = **0.98** (2% de descuento)
- **9.0:** Factor = **0.96** (4% de descuento)  <-- *Caso del cartón ligeramente doblado*
- **8.5:** Factor = **0.94** (6% de descuento)  <-- *Caso del cartón doblado con desgaste leve*
- **8.0:** Factor = **0.92** (8% de descuento)
- **7.0:** Factor = **0.88** (12% de descuento)
- **5.0:** Factor = **0.80** (20% de descuento)
- **1.0:** Factor = **0.64** (36% de descuento)

---

## 4. Ejemplo Práctico: Beast Man (Cartoon Collection)

Comparemos dos situaciones de la misma figura (Valor de Mercado Base = `81.55€`, Precio de Compra = `45.00€`):

### Escenario A (Tu configuración actual en la foto)
- **Tú la clasificaste como:** `NEW` (Estado Abierto / Caja abierta) y nota `10.0`.
- **Cálculo:**
  - Multiplicador Base: `0.75` (NEW)
  - Factor de Grado: `1.0` (Grading 10)
  - Multiplicador Final: `0.75 * 1.0 = 0.75`
  - **Valor Real Ajustado:** `81.55€ * 0.75 = 61.16€`
  - **Ganancia / Revalorización:** `+16.16€` (`35.9%` de ROI)

### Escenario B (Blíster sin abrir, pero cartón ligeramente doblado)
- **Clasificación correcta:** `MOC` (Sellada en blíster) y nota `9.0` (debido al doblez leve del cartón).
- **Cálculo:**
  - Multiplicador Base: `1.0` (MOC - conserva el empaque intacto de fábrica)
  - Factor de Grado: `1.0 - ((10.0 - 9.0) * 0.04) = 0.96` (96% de valor de conservación)
  - Multiplicador Final: `1.0 * 0.96 = 0.96`
  - **Valor Real Ajustado:** `81.55€ * 0.96 = 78.29€`
  - **Ganancia / Revalorización:** `78.29€ - 45.00€ = +33.29€`
  - **ROI Real Personalizado:** `(33.29€ / 45.00€) * 100 = +74.0%`

> [!TIP]
> Al mantener la figura en su blíster original sin abrir, la pieza retiene significativamente más valor de mercado (un 96% frente a un 75% de si se abre el blíster), a pesar de que el cartón presente pequeñas imperfecciones como dobleces leves.
