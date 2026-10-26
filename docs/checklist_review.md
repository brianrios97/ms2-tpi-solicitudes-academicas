# Checklist y Registro de Code Review Profesional (Etapa 7)

**Proyecto**: Sistema de Gestión de Solicitudes Académicas  
**Asignatura**: Metodología de Sistemas II — Ciclo Lectivo 2026  
**Integrantes**:
* Rios, Brian Emanuel (@brianrios97)
* Rivero Albornoz, Juan Pablo (@juanpiRiv)
* Riveros Valgañon, Nahuel Nicolás (@nahunicoR)

---

## 1. Checklist Técnico Estándar de Revisión

Este checklist fue diseñado por el equipo y aplicado de forma obligatoria sobre cada Pull Request antes de su incorporación a la rama principal (`main`):

| # | Dimensión / Criterio | Pregunta de Control | Estado |
|---|---|---|:---:|
| **C1** | **Preservación del Comportamiento** | ¿Se mantienen idénticos los mensajes de salida, orden de validación y estructura del archivo JSON sin introducir regresiones? | ✅ |
| **C2** | **Refactorings Documentados** | ¿Cada refactor responde a un code smell previamente catalogado con evidencia medible? | ✅ |
| **C3** | **Principios SOLID** | ¿Se respeta SRP (responsabilidad única) y OCP (abierto a extensión, cerrado a modificación)? | ✅ |
| **C4** | **Clean Code & Nombres** | ¿Las funciones son pequeñas, con nombres expresivos en lenguaje ubicuo y sin comentarios redundantes? | ✅ |
| **C5** | **Manejo de Errores** | ¿Se eliminaron los retornos mágicos de error (-1, False) y se usan excepciones de dominio tipadas cuando corresponde? | ✅ |
| **C6** | **Pruebas Automatizadas** | ¿El cambio incluye pruebas unitarias aisladas que no ensucien datos productivos y pasan al 100%? | ✅ |
| **C7** | **Trazabilidad en Git** | ¿La rama tiene nombre descriptivo (`feature/...`), commits atómicos y descripción clara del PR? | ✅ |

---

## 2. Registro de Revisiones Cruzadas en GitHub

### 📌 Revisión 1: Pull Request #1
* **Título**: `refactor(registro): introduce parameter object y extract method en registrar_solicitud`
* **Autor**: Juan Pablo Rivero Albornoz (@juanpiRiv)
* **Revisor**: Nahuel Nicolás Riveros (@nahunicoR)
* **Rama origen**: `feature/parameter-object-validaciones` $\rightarrow$ `main`
* **Smells atacados**:
  * Smell #3 (*Long Parameter List / Primitive Obsession*): Se creó `@dataclass(frozen=True) DatosRegistroSolicitud`, reduciendo de 8 parámetros sueltos a 1 único objeto inmutable.
  * Smell #2 (*Long Method*): Se modularizó `registrar_solicitud` en métodos auxiliares de validación y cálculo.
* **Pruebas agregadas**: `test_registro_solicitud.py` (17 pruebas unitarias con archivo temporal).
* **Observación del Revisor**:
  > *"Excelente modularización. Se verifica que el comportamiento externo y los mensajes de error de consola son exactamente los mismos. Se deja coordinada la lógica de prioridades para desacoplar con enums en el siguiente PR."*
* **Dictamen**: **Aprobado y fusionado (MERGED)**.

---

### 📌 Revisión 2: Pull Request #2
* **Título**: `refactor(dominio): move method a Solicitud y enums para estado, prioridad y tipo`
* **Autor**: Nahuel Nicolás Riveros (@nahunicoR)
* **Revisor**: Brian Emanuel Rios (@brianrios97)
* **Rama origen**: `feature/move-method-estados-enums` $\rightarrow$ `main`
* **Smells atacados**:
  * Smell #4 (*Feature Envy / Inappropriate Intimacy*): Se creó la entidad con comportamiento `Solicitud`, trasladando `asignar_responsable()` y `cambiar_estado()`.
  * Smell #5 y #6 (*Switch Statements & Magic Strings*): Creación de `EstadoSolicitud(str, Enum)`, `Prioridad(str, Enum)` y `TipoTramite(str, Enum)` con resolución polimórfica en `TipoTramite.resolver_prioridad()`.
  * Smell #8 (*Exception Swallowing*): Introducción de la excepción de dominio `TransicionInvalidaError`.
* **Pruebas agregadas**: `test_dominio.py` (16 pruebas unitarias de enums y ciclo de vida de la entidad).
* **Observación del Revisor**:
  > *"Gran acierto al convertir el diccionario anémico en la clase con comportamiento Solicitud. La entidad ahora es quien valida si puede resolverse o si ya está finalizada. La herencia de str en los Enums garantiza retrocompatibilidad total con solicitudes.json. Los 33 tests pasan al 100% y test_inicial.py valida que no hay regresiones."*
* **Dictamen**: **Aprobado y fusionado (MERGED)**.

---

## 3. Criterios de Aceptación Técnica Consolidados
1. **Total de pruebas unitarias**: 33 tests automatizados (`test_dominio` y `test_registro_solicitud`) ejecutándose en < 0.03 segundos con 100% de éxito.
2. **Cero regresiones funcionales**: Demostrado mediante la ejecución continua de `test_inicial.py`.
3. **Calidad arquitectónica**: Separación clara entre modelos de dominio (`dominio.py`), objetos de transferencia de datos (`DatosRegistroSolicitud`), lógica de orquestación y repositorio en `app.py`.
