# 🧠 Circuito del Triage Numérico

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Este repositorio contiene las bases teóricas, las reglas y el código fuente (Python/LaTeX) para generar el **"Circuito de Cálculos Mentales"**. Se trata de un ejercicio de simulación de alta presión diseñado para estudiantes de ingeniería, cuyo objetivo principal es combatir la "ceguera de datos" y forjar resiliencia cognitiva frente a los fallos de herramientas digitales.

---

## 📖 Resumen del Marco Teórico

La dependencia absoluta de calculadoras y software ha generado una vulnerabilidad crítica en la ingeniería moderna: la **ceguera de datos**. Los profesionales corren el riesgo de perder la intuición numérica, aceptando resultados físicamente incoherentes sin cuestionarlos. 

Este proyecto se fundamenta en tres pilares neuro-cognitivos y técnicos:
1. **Optimización de la Carga Mental:** Automatizar operaciones aritméticas simples libera la memoria de trabajo del cerebro, permitiendo concentrar la energía en el pensamiento sistémico y creativo.
2. **Estimación de Magnitudes:** En lugar de buscar el cálculo exacto, el ingeniero debe desarrollar rutas de *descomposición mental* para predecir el orden de magnitud de un resultado. Detectar una coma decimal desplazada es, a menudo, la única barrera antes de un fallo estructural.
3. **Resiliencia y Auditoría Interna:** Un profesional blindado es aquel capaz de validar los datos arrojados por un "sensor" (caja negra). El ejercicio fomenta una mentalidad de auditoría constante, entrenando al estudiante para descartar resultados imposibles incluso cuando la tecnología falla.

---

## 🏃 Dinámica del Ejercicio (Reglas de Juego)

El **Circuito de Cálculos Mentales** es un ejercicio físico y mental de relevos, evaluado por tiempo y precisión. 

### Configuración
El aula se divide en dos extremos:
* **Punto A (Origen y Punto de Salida):** Contiene tarjetas del **Lote A** (solo operaciones matemáticas). Tiene dos cajas de descarte: "Respuesta Correcta" y "Respeusta Incorrecta".
* **Punto B (Clasificación y Retiro de otra tarjeta):** Contiene tres contenedores de magnitudes (Exponentes de la notación científica, por ejemplo: -9,-6,-3,0,3,6,9 ; 8,5,2,-1,-2,-7,-10; 10,7,4,1,-2,-5,-8 ) y las tarjetas del **Lote B** (operación + lectura de un sensor, donde el 30% tiene errores).

### Flujo del Circuito
1. **Ida:** Un estudiante toma una tarjeta del Lote A y corre hacia el Punto B. En el trayecto, realiza cálculo mental/estimación sin usar lápiz ni papel.
2. **Clasificación:** En el Punto B, deposita la tarjeta A en el contenedor de la magnitud correcta de forma inmediata.
3. **Retorno:** Toma una tarjeta del Lote B y corre de regreso al Punto A. Durante el trayecto, audita si el número del "sensor" impreso es real o tiene un error de magnitud.
4. **Triage y Relevo:** Al llegar al Punto A, deposita la tarjeta B en "Respuesta Correcta" o "Respuesta Incorrecta" y da el relevo al siguiente compañero.

### Evaluación
Se tiene en cuenta el tiempo que se tarda en realizar el ejercicio y por otro lado la cantidad de respuestas incorrectas sobre el total. 
---

## 🛠️ Generación de Tarjetas

El material de juego es dinámico y se genera aleatoriamente mediante un script de Python que exporta un documento en LaTeX listo para ser impreso y recortado en formato de tarjetas. 

Las operaciones incluyen notación científica, fracciones decimales, conversiones de unidades del SI y reglas de tres, utilizando valores reales de ingeniería (ej. voltajes, serie E12 de componentes, constantes físicas).

### Requisitos

* **Python 3.x**
* Una distribución de **LaTeX** instalada en el sistema que incluya `pdflatex` (por ejemplo, [TeX Live](https://tug.org/texlive/), [MiKTeX](https://miktex.org/) o [MacTeX](https://tug.org/mactex/)). Las dependencias de paquetes LaTeX son estándar (`amsmath`, `tikz`, `tcolorbox`, `geometry`).

### Instrucciones de uso

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/seba-san/calculos_mentales.git
   cd calculos_mentales
   ```

2. **Generar el código fuente de las tarjetas (.tex):**
   Ejecuta el script de Python para generar un lote nuevo de problemas y errores aleatorios.
   ```bash
   python generar_circuito.py
   ```
   *Esto creará en tu directorio un archivo llamado `circuito_triage.tex`.*

3. **Compilar el archivo PDF:**
   Utiliza `pdflatex` para renderizar el documento (puedes usar tu editor LaTeX de preferencia o hacerlo desde la terminal).
   ```bash
   pdflatex circuito_triage.tex
   ```
   *Esto generará el archivo `circuito_triage.pdf` con la grilla de tarjetas listas para imprimir (8 tarjetas por página).*

---
## 👤 Autor
* **Sebastian Sansoni** - (Seba-san) - *Idea original, desarrollo y teoría.*

---

## 📄 Licencia

Este proyecto se distribuye bajo la licencia **Apache License, Version 2.0**. 

**Copyright 2024 Sebastian Sansoni**

Puedes usar, modificar y distribuir este contenido libremente, siempre que mantengas el aviso de copyright. Para más detalles, consulta el archivo [LICENSE](LICENSE) o visita [apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0).

***



