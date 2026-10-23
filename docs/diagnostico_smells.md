# Diagnóstico Inicial: Calidad y Catálogo de Code Smells

**Proyecto**: Sistema de Gestión de Solicitudes Académicas  
**Asignatura**: Metodología de Sistemas II  
**Versión evaluada**: `estado-inicial`  

---

## 1. Calidad Externa vs. Calidad Interna

* **Calidad Externa (Lo que ve el usuario)**:  
  El sistema cumple con el 100% de los requerimientos operativos funcionales: permite dar de alta solicitudes, cambiar estados de trámite, asignar responsables de departamentos, filtrar registros y calcular métricas en tiempo de ejecución. Los datos persisten correctamente en `solicitudes.json`. Desde el punto de vista del usuario o cliente, el software "funciona".

* **Calidad Interna (Lo que sufre el desarrollador)**:  
  La arquitectura interna es monolítica y frágil. Toda la lógica (presentación por consola, persistencia en disco, validaciones y cálculos) se concentra en una única clase `SistemaGestionAcademica`. No existe encapsulamiento de entidades (se manejan diccionarios primitivos mutables sin control), las reglas de transición de estado son cadenas de `if-elif` rígidas y no hay abstracciones. Cualquier cambio en la estructura de almacenamiento romperá la interfaz de usuario y la lógica de negocio (alto acoplamiento y baja cohesión).

---

## 2. Catálogo de los 8 Code Smells Identificados

### 1. God Class / Large Class
* **Ubicación**: [app.py](file:///d:/Mis%20documentos/Estudio/Tec.%20en%20Programacion%20en%20sistemas/Anio%202/2C/Metodologia%20de%20sistemas%202/TPI/sistema-solicitudes-academicas/app.py) (Clase `SistemaGestionAcademica`).
* **Evidencia**: Acumula E/S de archivos JSON, validación de cadenas, lógica de transición de estados y generación de reportes.
* **Impacto**: Viola el Principio de Responsabilidad Única (SRP).
* **Riesgo**: Imposible testear la lógica de negocio sin depender de archivos físicos en disco.
* **Prioridad**: **Alta**.
* **Solución**: *Extract Class* en Repositorio, Servicio de Negocio y Modelos.

---

### 2. Long Method
* **Ubicación**: [app.py](file:///d:/Mis%20documentos/Estudio/Tec.%20en%20Programacion%20en%20sistemas/Anio%202/2C/Metodologia%20de%20sistemas%202/TPI/sistema-solicitudes-academicas/app.py#L60-L135) (Método `registrar_solicitud`).
* **Evidencia**: Supera las 70 líneas haciendo validación de campos, formateo de fechas, asignación de prioridades, búsqueda de alumnos y persistencia.
* **Impacto**: Dificultad para leer, razonar y reutilizar validaciones.
* **Riesgo**: Alto riesgo de introducir regresiones ante cualquier ajuste en las reglas de alta.
* **Prioridad**: **Alta**.
* **Solución**: *Extract Method* (Refactoring obligatorio #1).

---

### 3. Long Parameter List / Primitive Obsession
* **Ubicación**: [app.py](file:///d:/Mis%20documentos/Estudio/Tec.%20en%20Programacion%20en%20sistemas/Anio%202/2C/Metodologia%20de%20sistemas%202/TPI/sistema-solicitudes-academicas/app.py#L60) (`registrar_solicitud(self, legajo, nombre, email, carrera, tipo, prioridad, descripcion, observaciones)`).
* **Evidencia**: Recibe 8 parámetros primitivos (todos `str`).
* **Impacto**: Lista propensa a errores por inversión de argumentos, difícil de extender si se agregan campos como teléfono o turno.
* **Riesgo**: Código frágil y poco expresivo.
* **Prioridad**: **Alta**.
* **Solución**: *Introduce Parameter Object* (Refactoring obligatorio #3) creando la clase `DatosSolicitud` o modelo `Estudiante`.

---

### 4. Feature Envy / Inappropriate Intimacy
* **Ubicación**: [app.py](file:///d:/Mis%20documentos/Estudio/Tec.%20en%20Programacion%20en%20sistemas/Anio%202/2C/Metodologia%20de%20sistemas%202/TPI/sistema-solicitudes-academicas/app.py#L90-L105) (`registrar_solicitud` y `cambiar_estado`).
* **Evidencia**: La clase gestora inspecciona y manipula directamente las llaves del diccionario de la solicitud (`solicitud["estado"]`, `solicitud["responsable_id"]`) para evaluar si puede cambiar de estado o si está cerrada.
* **Impacto**: Las reglas de si una solicitud puede o no resolverse no están en la entidad `Solicitud`, sino desperdigadas en el gestor.
* **Riesgo**: Si cambia la estructura interna de una solicitud, hay que modificar todos los métodos del gestor.
* **Prioridad**: **Media**.
* **Solución**: *Move Method* (Refactoring obligatorio #2) trasladando las transiciones y validaciones a la entidad `Solicitud`.

---

### 5. Conditional Complexity / Switch Statements
* **Ubicación**: [app.py](file:///d:/Mis%20documentos/Estudio/Tec.%20en%20Programacion%20en%20sistemas/Anio%202/2C/Metodologia%20de%20sistemas%202/TPI/sistema-solicitudes-academicas/app.py#L80-L95) (Cadenas `if tipo == "Equivalencia de Materia" ... elif ...`).
* **Evidencia**: Múltiples bifurcaciones para deducir prioridades o reglas según el tipo de trámite académico.
* **Impacto**: Viola el Principio Open/Closed (OCP). Agregar un nuevo trámite exige tocar el método principal.
* **Riesgo**: Crecimiento descontrolado de sentencias condicionales anidadas.
* **Prioridad**: **Media**.
* **Solución**: *Replace Conditional with Polymorphism / Strategy* (4to Refactoring Justificado).

---

### 6. Magic Strings & Magic Numbers
* **Ubicación**: [app.py](file:///d:/Mis%20documentos/Estudio/Tec.%20en%20Programacion%20en%20sistemas/Anio%202/2C/Metodologia%20de%20sistemas%202/TPI/sistema-solicitudes-academicas/app.py#L145-L165).
* **Evidencia**: Cadenas literales `"PENDIENTE"`, `"EN_CURSO"`, `"RESUELTA"`, `"RECHAZADA"`, `"data/solicitudes.json"` esparcidas por el código.
* **Impacto**: Vulnerable a errores tipográficos invisibles para el intérprete en tiempo de compilación.
* **Riesgo**: Un error en un caracter (`"PENDINTE"`) corrompe la persistencia y la consistencia del estado.
* **Prioridad**: **Media**.
* **Solución**: Reemplazar por `Enum` (`EstadoSolicitud`, `Prioridad`).

---

### 7. Duplicate Code
* **Ubicación**: [app.py](file:///d:/Mis%20documentos/Estudio/Tec.%20en%20Programacion%20en%20sistemas/Anio%202/2C/Metodologia%20de%20sistemas%202/TPI/sistema-solicitudes-academicas/app.py#L30-L58).
* **Evidencia**: Patrones repetidos para búsqueda de elementos por ID en listas de diccionarios y formateos de cadenas.
* **Impacto**: Incremento innecesario de líneas de código y esfuerzo duplicado ante modificaciones.
* **Riesgo**: Inconsistencia si se actualiza un método de búsqueda pero se olvida otro.
* **Prioridad**: **Baja**.
* **Solución**: Abstraer métodos auxiliares genéricos o métodos de repositorio.

---

### 8. Exception Swallowing / Manejo Deficiente de Errores
* **Ubicación**: [app.py](file:///d:/Mis%20documentos/Estudio/Tec.%20en%20Programacion%20en%20sistemas/Anio%202/2C/Metodologia%20de%20sistemas%202/TPI/sistema-solicitudes-academicas/app.py#L40-L45) y retornos de `-1` o `False`.
* **Evidencia**: Capturas genéricas con `except Exception as e:` que solo imprimen en consola y enmascaran fallos críticos de archivo o validación, retornando códigos de error mágicos (`-1`, `False`).
* **Impacto**: Oculta la causa raíz de las excepciones a los llamadores y confunde la capa de presentación.
* **Riesgo**: Fallos silenciosos que pueden corromper la persistencia sin alertar al usuario.
* **Prioridad**: **Alta**.
* **Solución**: *Replace Error Code with Exception*, creando excepciones de dominio personalizadas (`SolicitudInvalidaError`, `TransicionEstadoError`).
