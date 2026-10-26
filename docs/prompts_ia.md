# Registro de Prompts e Interacción con Inteligencia Artificial

**Proyecto**: Sistema de Gestión de Solicitudes Académicas  
**Asignatura**: Metodología de Sistemas II — Ciclo Lectivo 2026  
**Integrantes**: Rios Brian, Rivero Albornoz Juan Pablo, Riveros Valgañon Nahuel  
**Herramienta de IA de asistencia**: Antigravity / Gemini CLI  

---

## 1. Declaración de Uso de IA (Sección 7 de la Consigna)
En conformidad con las pautas de la cátedra de Metodología de Sistemas II, se declara que las herramientas de Inteligencia Artificial fueron utilizadas exclusivamente como **asistente técnico consultivo, copiloto de diseño y soporte de redacción profesional**. 

La autoría de la arquitectura, la comprensión y defensa de cada refactoring, la autoría de las pruebas unitarias y el análisis crítico de cada decisión de diseño pertenecen enteramente a los integrantes del equipo.

---

## 2. Bitácora de Prompts Relevantes y Decisiones Técnicas

### Interacción 1: Selección del Sistema Base y Estrategia de Smells Intencionales
* **Finalidad**: Delimitar el alcance mínimo del sistema para cumplir los requerimientos de la cátedra sin incurrir en sobrediseño innecesario.
* **Prompt representativo**:
  > *"Tenemos que hacer este TPI de Metodología de Sistemas II. La consigna pide un sistema con 3 entidades, 4 operaciones y persistencia JSON, donde primero se muestre una versión base con problemas y luego se apliquen refactorings. ¿Qué sistema base podemos proponer que contenga deliberadamente 8 code smells reales para luego poder refactorizarlos?"*
* **Resultado / Decisión adoptada**:
  Se adoptó el dominio de *Gestión de Solicitudes Académicas* con persistencia JSON. Se diseñó la clase monolítica `SistemaGestionAcademica` en `app.py` embebiendo deliberadamente los smells de *God Class, Long Method, Long Parameter List, Feature Envy, Switch Statements, Magic Strings, Duplicate Code* y *Exception Swallowing*.

---

### Interacción 2: Planificación del Flujo de Trabajo Asincrónico y Criterios de Evaluación
* **Finalidad**: Organizar el trabajo en Git con ramas, PRs y roles cruzados para garantizar participación equilibrada y no violar la regla *"nadie queda encargado exclusivamente de programar, documentar o probar"*.
* **Prompt representativo**:
  > *"¿Cómo podemos dividir las tareas de forma equitativa entre los 3 integrantes para avanzar de forma asincrónica, asegurando que todos programen, todos documenten y todos hagan code review?"*
* **Resultado / Decisión adoptada**:
  Se adoptó una división vertical por técnicas de refactoring:
  - Brian: Sistema base, setup de repositorio, diagnóstico formal (Etapas 1, 2 y 3) y Code Review a Nahuel.
  - Juan Pablo: Parameter Object + Extract Method + Tests unitarios de registro (Etapas 4, 5-A y 6).
  - Nahuel: Move Method + Enums y OCP + Tests unitarios de dominio + Code Review a Juan Pablo (Etapas 4, 5-B y 7).

---

### Interacción 3: Revisión Técnica de Pull Requests y Auditoría de Pruebas
* **Finalidad**: Verificar estáticamente el código del PR #2, verificar ausencia de regresiones funcionales y aplicar el checklist de revisión técnica.
* **Prompt representativo**:
  > *"Ahora me toca el review de Nahuel en el PR #2, ¿podés ayudarme a revisar si lo que hizo está bien, si los tests pasan y si se mantuvieron los contratos del JSON?"*
* **Resultado / Decisión adoptada**:
  Se constató que la subclase `class EstadoSolicitud(str, Enum)` resolvió elegantemente el problema de los strings mágicos preservando intacta la compatibilidad con el archivo `solicitudes.json`. Se aprobaron formalmente los 33 tests y se confeccionó el checklist de aceptación técnica en `docs/checklist_review.md`.
