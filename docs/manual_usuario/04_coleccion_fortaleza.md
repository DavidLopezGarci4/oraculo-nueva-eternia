# Manual del Usuario: 04. Gestión de Colecciones (Fortaleza)

El módulo de **Colección** es el santuario donde registras y gestionas las figuras que posees físicamente en tu inventario. Al igual que el resto del sistema, está dividido en dos fortalezas independientes para aislar el valor del coleccionismo moderno del retro:
*   **Mi Fortaleza**: Para figuras modernas de la línea *Origins* o *Nueva Eternia*.
*   **Mi Fortaleza Vintage**: Para figuras clásicas de los años 80 (*Eternia Vintage*).

---

## Interfaz de la Fortaleza

Al entrar en cualquiera de las fortalezas, verás un listado en forma de cuadrícula de las figuras de tu inventario. Cada tarjeta de figura presenta:
*   La foto de la figura.
*   El nombre y la oleada/Wave.
*   El **Estado Físico** (`MOC`, `NEW` o `LOOSE`) con una etiqueta coloreada.
*   La **Calificación de Conservación (Nota de 1.0 a 10.0)**.
*   El **Precio Pagado** y el **Valor de Mercado Ajustado**.
*   El **ROI Real (Retorno de Inversión)** obtenido, calculado a partir de la diferencia entre lo que pagaste y el valor actual de mercado ajustado. El porcentaje se resalta en verde para indicar plusvalía o en rojo para depreciaciones.

---

## El Formulario de Edición (Modal de Detalle)

Al hacer clic en cualquier figura de tu colección se abre un modal de edición. Aquí puedes ajustar de manera precisa los parámetros que determinan el valor real de tu pieza en el mercado:

### Parámetros de la Figura:
1.  **Estado Físico (Condición)**:
    *   `MOC (Mint on Card)`: La figura está sellada en su blíster original o caja cerrada. Nunca ha sido abierta.
    *   `NEW (New / Open Box)`: La figura está nueva y completa, pero el blíster o caja ha sido abierto.
    *   `LOOSE (Loose)`: La figura está suelta, fuera de su empaque original. No conserva caja ni cartón.
2.  **Calificación de Conservación (Grading)**:
    *   Un valor del **1.0 al 10.0** que representa la calidad física de los elementos (cartón, burbuja, pintura de la figura).
3.  **Precio de Compra / Coste Real**:
    *   Cuánto pagaste por ella (se recomienda incluir envíos y aranceles prorrateados).
4.  **Precio Recomendado de Tienda (MSRP / Retail)**:
    *   El precio oficial de venta en tiendas físicas que sirve como referencia secundaria de salida al mercado.
5.  **Notas del Guardián**:
    *   Un espacio libre para apuntar si la figura tiene shelf wear, firma del diseñador, variaciones de color en el plástico, etc.

---

## Escala de Conservación y Valoración (Guía Rápida)

En la parte inferior de la ventana de edición, encontrarás un botón desplegable interactivo titulado **"Escala de Valoración (Detalles de la nota)"**. Al desplegarlo, se detalla la escala que sigue el Oráculo:

*   **10.0 - Gem Mint**: Cartón plano impecable, esquinas afiladas, burbuja cristalina y sin marcas. Calidad de museo.
*   **9.5 - Mint**: Casi perfecto. Se tolera un microdesgaste casi imperceptible visible solo a inspección de lupa.
*   **9.0 - Near Mint / Mint**: Cartón plano en general, pero **se permite un cartón ligeramente doblado (crease leve) o esquinas ligeramente blandas**. Burbuja intacta.
    > *Nota: Una figura MOC (en blíster sellado) con un cartón un poco doblado o arrugado por almacenamiento se califica aquí. Al no haber sido abierta, retiene un gran valor.*
*   **8.5 - Near Mint**: Desgaste de almacenamiento menor (shelf-wear). Pequeñas marcas de etiquetas viejas, roces o esquinas ligeramente dobladas.
*   **8.0 - Very Good / Near Mint**: Arrugas de estrés moderadas alrededor del colgador. La burbuja está firme pero tiene micro-rayones o un leve hundimiento.
*   **7.0 - Good**: Cartón con dobleces claros y desgaste visible en bordes (pérdida de color), esquinas desgastadas.
*   **5.0 - Fair**: Cartón muy fatigado con roturas menores, arrugas profundas, pegamento, o burbuja amarilleada/abollada.
*   **3.0 a 1.0 - Poor**: Burbuja rota o sujeta con cinta adhesiva, cartón dañado o mutilado. El empaque está destruido pero la figura sigue dentro.

---

## Algoritmo de Ajuste Financiero (ROI e Inversión)

El Oráculo calcula automáticamente el **Valor de Mercado Ajustado** usando una fórmula que aplica deducciones según el desgaste físico:

$$\text{Valor Ajustado} = \text{Valor de Mercado Base} \times \text{Multiplicador de Estado} \times \text{Factor de Conservación}$$

### Coeficientes de Estado:
*   `MOC`: **1.0** (100% del valor base del mercado).
*   `NEW`: **0.75** (Aplica una penalización del 25% por empaque abierto).
*   `LOOSE`: **0.50** (Aplica una penalización del 50% por figura suelta sin caja).

### Factor de Conservación:
El factor numérico de conservación se rige por la siguiente lógica:
$$\text{Factor de Conservación} = 1.0 - ((10.0 - \text{Nota}) \times 0.04)$$
*(Suelo mínimo del factor: 0.10 para evitar valoraciones nulas).*

**Ejemplo de Descuentos**:
*   Nota **10.0**: 0% de penalización (Factor 1.0)
*   Nota **9.0** (Cartón doblado leve): 4% de penalización (Factor 0.96)
*   Nota **8.0**: 8% de penalización (Factor 0.92)
*   Nota **5.0**: 20% de penalización (Factor 0.80)

Una vez obtenido el Valor Ajustado, el sistema calcula el **ROI Real**:
$$\text{ROI Real} = \left( \frac{\text{Valor Ajustado} - \text{Precio Pagado}}{\text{Precio Pagado}} \right) \times 100$$
Esto te permite saber con precisión matemática si tus decisiones de compra te están dando un retorno positivo o si has pagado de más por una pieza según su estado real de conservación.
