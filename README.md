# Sistema de Gestión de Solicitudes Académicas
**Trabajo Práctico Integrador — Metodología de Sistemas II**

## 👥 Integrantes
* Rios, Brian Emanuel
* Rivero Albornoz, Juan Pablo
* Riveros Valgañon, Nahuel Nicolás

---

## 📌 Descripción del Proyecto
Sistema desarrollado en Python para la administración de trámites y solicitudes de estudiantes universitarios (equivalencias, certificados, reclamos de exámenes, cambios de comisión/carrera). Permite registrar solicitudes, asignar responsables departamentales, controlar estados del flujo administrativo y emitir reportes de gestión.

El proyecto está diseñado bajo un enfoque pedagógico de **evolución y refactorización**:
1. **Versión Inicial (`estado-inicial`)**: Sistema funcional a nivel externo pero con deuda técnica y *code smells* embebidos intencionalmente.
2. **Versión Refactorizada (`estadorefactorizado`)**: Sistema reestructurado aplicando principios SOLID, Clean Code, patrones y técnicas formales de refactoring, conservando el comportamiento observable y garantizado con pruebas.

---

## 🚀 Requisitos e Instalación

### Requisitos:
* Python 3.10 o superior (no requiere librerías externas para la versión base).

### Ejecución:
Para ejecutar la interfaz por consola interactiva:
```bash
python app.py
```

Para ejecutar la verificación automatizada del estado inicial:
```bash
python test_inicial.py
```

---

## 🛠️ Tecnologías y Persistencia
* **Lenguaje**: Python 3
* **Persistencia**: Archivo JSON estructurado (`data/solicitudes.json`)
* **Control de versiones**: Git & GitHub con flujo de branches y PRs
* **Documentación técnica**: Markdown en carpeta `/docs`

---

## 🏷️ Hitos del Repositorio (Tags Obligatorios)
El avance del trabajo práctico se traza mediante los siguientes 6 tags:
1. `estado-inicial`: Entrega del prototipo funcional con deuda técnica y code smells.
2. `etapa-diagnostico`: Informe de diagnóstico de calidad externa vs. interna y catálogo de 8 code smells.
3. `etapa-refactoring`: Aplicación documentada de los 4 refactorings obligatorios.
4. `etapa-pruebas`: Casos de prueba automatizados y matriz de verificación antes/después.
5. `etapa-docs`: Checklist de code review completado, registro de prompts de IA y anexos.
6. `estadorefactorizado`: Entrega final del código limpio y desacoplado.
