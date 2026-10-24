# Diagnóstico Inicial: Calidad y Catálogo de Code Smells

**Proyecto**: Sistema de Gestión de Solicitudes Académicas  
**Asignatura**: Metodología de Sistemas II — Ciclo Lectivo 2026  
**Integrantes**:
* Rios, Brian Emanuel
* Rivero Albornoz, Juan Pablo
* Riveros Valgañon, Nahuel Nicolás

**Documento Colaborativo en la Nube**: [Google Docs](https://docs.google.com/document/d/15Irlt8jhlZ38hweValE_Yo9zJPmpTaAkLK7_fDfozPQ/edit?usp=sharing)  
**Versión evaluada**: `estado-inicial`  
**Hito del Repositorio**: `etapa-diagnostico`

---

## 1. Resumen Ejecutivo
El presente Trabajo Práctico Integrador aborda el diagnóstico, rediseño y evolución profesional de un Sistema de Gestión de Solicitudes Académicas implementado en Python con persistencia en archivos JSON. A partir de una versión funcional pero con severas deficiencias estructurales, se identifican y catalogan ocho code smells representativos que comprometen la mantenibilidad, cohesión y extensibilidad del software. Mediante la aplicación metódica de principios SOLID, lineamientos de Clean Code y refactorings seguros (Extract Method, Move Method e Introduce Parameter Object), se logra desacoplar la arquitectura en capas bien delimitadas, preservando estrictamente el comportamiento funcional externo mediante pruebas automatizadas y garantizando la trazabilidad del proceso bajo control de versiones en GitHub con seis tags de hito.

---

## 2. Etapa 1: Selección y Descripción del Sistema Base

### 2.1. Dominio y Contexto
En el ámbito universitario, la gestión de trámites y solicitudes estudiantiles (equivalencias, certificados de regularidad, reclamos de examen y pases de carrera) suele iniciarse con formularios dispersos o prototipos monocapa. Se requiere registrar peticiones, categorizarlas por urgencia, asignarlas a áreas pertinentes (Alumnos, Bedelía, Tesorería) y gestionar las transiciones de estado hasta su resolución.

### 2.2. Actores del Sistema
* **Estudiante**: Origina y consulta peticiones académicas asociadas a su legajo y carrera.
* **Responsable de Área**: Agente departamental (Alumnos, Bedelía, Tesorería) asignado para evaluar y resolver el trámite.
* **Administrador / Coordinador**: Supervisa el flujo general, reasigna casos y analiza reportes agregados.

### 2.3. Entidades Principales
1. **Solicitud**: Identificador, legajo y datos de estudiante, tipo de trámite, descripción, fecha de creación, prioridad, estado, responsable asignado y observaciones.
2. **Estudiante**: Legajo, nombre, email institucional y carrera.
3. **Responsable**: Identificador, nombre y departamento asignado.
4. **Estado y Prioridad**: Ciclos de vida (`PENDIENTE`, `EN_CURSO`, `RESUELTA`, `RECHAZADA`) y urgencias (`ALTA`, `MEDIA`, `BAJA`).

### 2.4. Operaciones Funcionales Verificables
1. **Registrar solicitud**: Valida datos, aplica reglas de prioridad, asigna ID correlativo y persiste en estado `PENDIENTE`.
2. **Asignar responsable**: Vincula el área correspondiente y pasa automáticamente a `EN_CURSO`.
3. **Transición controlada de estado**: Permite resolver o rechazar con registro de observaciones exigiendo responsable asignado.
4. **Búsqueda y filtrado**: Permite filtrar por estado, estudiante o responsable.
5. **Reporte analítico**: Totales, distribución por estado y tasa de resolución en tiempo real.

---

## 3. Etapa 2: Calidad Externa vs. Calidad Interna

### 3.1. Calidad Externa (Comportamiento Observable)
Desde la mirada del usuario, el sistema en `estado-inicial` funciona correctamente:
* Permite dar de alta y consultar trámites sin errores de runtime.
* Los datos persisten fielmente en `data/solicitudes.json`.
* La interfaz CLI guía al usuario con claridad.
* El script `test_inicial.py` demuestra que todas las operaciones cumplen el comportamiento esperado con 100% de éxito.

### 3.2. Calidad Interna (Estructura y Deuda Técnica)
A nivel de código fuente, existe una deuda técnica crítica:
* **Monolitismo y Baja Cohesión**: Una única clase `SistemaGestionAcademica` mezcla consola, persistencia en disco, validaciones y lógica de negocio.
* **Alto Acoplamiento**: Dependencia rígida del archivo físico y de llamadas directas a funciones del sistema operativo. Imposible realizar testing unitario aislado.
* **Falta de Encapsulamiento**: Manipulación directa de diccionarios planos y llaves string en lugar de modelos con comportamiento.
* **Fragilidad**: Cadenas condicionales (`if-elif`) y cadenas mágicas ('PENDIENTE', 'Equivalencia de Materia') propensas a errores tipográficos.
* **Supresión de Errores**: Capturas genéricas con `except Exception` y retorno de códigos mágicos (`-1`, `False`).

---

## 4. Etapa 3: Catálogo de los 8 Code Smells Identificados

| # | Code Smell | Ubicación (`app.py`) | Impacto Principal | Riesgo | Prioridad | Refactoring Proyectado |
|---|---|---|---|---|---|---|
| **1** | **God Class / Large Class** | Líneas 23-180 (`SistemaGestionAcademica`) | Viola SRP; concentra persistencia, negocio y CLI. | Alto riesgo de regresiones colaterales. | **ALTA** | *Extract Class* (Repositorio, Servicio, Modelos). |
| **2** | **Long Method** | Líneas 60-135 (`registrar_solicitud`) | 75 líneas continuas con múltiples responsabilidades. | Dificultad para razonar y reutilizar validaciones. | **ALTA** | *Extract Method* (Refactoring obligatorio #1). |
| **3** | **Long Parameter List / Primitive Obsession** | Línea 60 (`registrar_solicitud`) | 8 parámetros primitivos (`str`). | Inversión accidental de argumentos; firma rígida. | **ALTA** | *Introduce Parameter Object* (Refactoring obligatorio #3). |
| **4** | **Feature Envy / Inappropriate Intimacy** | Líneas 95-125 y 145-165 | Gestor manipula directamente atributos de la solicitud. | Lógica de estados dispersa; modelos anémicos. | **MEDIA** | *Move Method / Reubicación de Responsabilidad* (Refactoring #2). |
| **5** | **Switch Statements / Complex Conditionals** | Líneas 80-92 y 150-160 | Cadenas `if-elif` rígidas de trámites y estados. | Viola OCP; difícil incorporar nuevos trámites. | **MEDIA** | *Replace Conditional with Polymorphism / Strategy* (Refactoring #4). |
| **6** | **Magic Strings & Numbers** | Disperso en `app.py` | Cadenas literales quemadas (`"PENDIENTE"`, rutas). | Fallas silenciosas por tipografía; inconsistencias. | **MEDIA** | *Replace Magic Literal with Symbolic Constant / Enum*. |
| **7** | **Duplicate Code** | Líneas 30-58 y 170-185 | Búsquedas manuales y formateo repetido. | Mantenimiento doble y correcciones asimétricas. | **BAJA** | *Extract Method* y abstracciones de repositorio. |
| **8** | **Exception Swallowing / Error Codes** | Líneas 40-45 y retornos `-1` / `False` | Oculta causas de error de archivo e ingreso de datos. | Fallas silenciosas y sobreescritura accidental. | **ALTA** | *Replace Error Code with Exception*. |
