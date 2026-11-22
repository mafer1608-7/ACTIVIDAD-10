# Chasis del robot móvil – diseño propio (Guía 5)

Chasis híbrido: **2 placas de acrílico de 3 mm (corte láser)** + **piezas impresas en 3D**.
Tracción diferencial: 2 motores TT + rueda loca trasera. Diámetro 180 mm, altura total ~150 mm.

## Archivos

| Carpeta | Contenido | Uso |
|---|---|---|
| `STEP/ensamble_robot.step` | Ensamble completo con colores (incluye motores, ruedas, batería, ESP32, etc. como referencia) | Abrir en SolidWorks |
| `STEP/*.step` | Cada pieza por separado | Abrir en SolidWorks y guardar como `.SLDPRT` |
| `DXF/placa_inferior.dxf`, `DXF/placa_superior.dxf` | Contorno 2D a escala 1:1 en mm | Llevar al local de corte láser |
| `STL/*.stl` | Piezas para imprimir | Abrir en Cura/PrusaSlicer |
| `robot_chasis.py` | Modelo paramétrico (CadQuery) | Cambiar medidas y regenerar todo |
| `vista_ensamble.png`, `vista_placas_dxf.png` | Vistas de verificación | Informe |

## Abrir en SolidWorks

1. **Archivo → Abrir**, tipo de archivo *STEP (\*.step;\*.stp)*, elegir `ensamble_robot.step`.
2. SolidWorks lo importa como **ensamble** (`.SLDASM`) con una pieza por componente. Guardarlo con *Guardar como*.
3. Si quieren modificar una pieza con operaciones propias, ábranla y usen **FeatureWorks → Reconocer operaciones**
   (Herramientas → Complementos → FeatureWorks). Así el STEP pasa a tener croquis y extrusiones editables.
4. Para los planos del informe: *Archivo → Crear dibujo desde pieza*, vistas superior/frontal/isométrica, acotar.

> Recomendación para el informe: rehagan en SolidWorks al menos las piezas impresas (son sencillas: extrusiones y cortes)
> usando estas medidas. Así el árbol de operaciones demuestra que el diseño es de ustedes.

## Piezas a fabricar

| Pieza | Cant. | Proceso | Notas |
|---|---|---|---|
| Placa inferior | 1 | Láser, acrílico 3 mm | ranuras de ruedas, agujeros M3 |
| Placa superior | 1 | Láser, acrílico 3 mm | rejilla M3 cada 10 mm para montar electrónica |
| Soporte motor izq. / der. | 1 + 1 | Impresión 3D | son espejo uno del otro, imprimir apoyados en la base |
| Soporte ultrasónico | 1 | Impresión 3D | HC-SR04 (agujeros Ø16,6); tiene 2 agujeros M2 para VL53L0X |
| Mástil magnetómetro | 1 | Impresión 3D | 80 mm de alto, cables por dentro, flecha = frente |
| Separador rueda loca | 1 | Impresión 3D | solo si la rueda loca mide menos de 15 mm de alto |

Impresión sugerida: PETG o PLA, 0,2 mm de capa, 3 perímetros, 30 % de relleno.

## Tornillería

- 4 separadores **de latón** M3 × 40 mm (hembra-hembra) + 8 tornillos M3 × 6
- 8 tornillos M3 × 10 + tuercas (soportes de motor)
- 4 tornillos M3 × 30 + tuercas (sujetan cada motor TT a su soporte)
- 2 M3 × 10 (soporte ultrasónico), 2 M3 × 20 (rueda loca + separador), 4 M3 × 10 (mástil)
- **Tornillos de nylon o latón en el mástil y cerca del magnetómetro** (el acero desvía la brújula)
- Bridas plásticas para el portapilas

## Medidas clave

- Altura del eje: 32,5 mm (= radio de rueda de 65 mm)
- Distancia entre ruedas (centro a centro): 150 mm, valor de `L` para la cinemática diferencial
- Despeje al suelo de la placa inferior: 15,25 mm
- El eje de las ruedas pasa por el centro del robot: gira sobre sí mismo sin desplazarse
- Sensor IMU/magnetómetro a ~150 mm del suelo y ~115 mm por encima de los motores

## ⚠️ Antes de mandar a cortar e imprimir

Las medidas de los componentes son **valores típicos**. Cuando compren las piezas, midan con calibrador y ajusten
la sección `PARAMETROS` de `robot_chasis.py`:

- `M_AGUJEROS_X`: posición de los 2 agujeros pasantes del motor TT respecto al eje (las ranuras dan ±1 mm de holgura)
- `D_RUEDA`, `W_RUEDA`: rueda comprada
- `H_RUEDA_LOCA`, `SEP_AGUJEROS_LOCA`: rueda loca comprada
- Agujeros de montaje del ESP32 y del driver: usan la rejilla de 10 mm de la placa superior (o separadores de nylon)

Regenerar:

```bash
pip install cadquery
python robot_chasis.py
```
