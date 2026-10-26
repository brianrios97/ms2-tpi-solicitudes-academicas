"""Modelo de dominio del Sistema de Gestión de Solicitudes Académicas.

* Refactoring N°4 (Replace Magic Strings and Conditionals whit Enums):
    EstadoSolicitud, Prioridad y TipoTramite reemplazan los textos quemados
    ("PENDIENTE", "ALTA", "Reclamo de Examen", ...) y la cadena if-elif
    que forzaba la prioridad según el tipo de trémite

* Refactoring #2 (Move Method / Reubicacion de responsabilidad):
    La clase Solicitud concentra las reglas de asignacion de responsable y de
    transicion de estado, que antes vivian en el gestor (Feature Envy).
"""

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional


class EstadoSolicitud(str, Enum):
    PENDIENTE = "PENDIENTE"
    EN_CURSO = "EN_CURSO"
    RESUELTA = "RESUELTA"
    RECHAZADA = "RECHAZADA"

    @classmethod
    def desde_texto(cls, texto: Optional[str]) -> Optional["EstadoSolicitud"]:
        """Convierte un texto ingresado por el usuario, devuelve None si no es válido"""
        normalizado = (texto or "").upper().strip()
        return next((estado for estado in cls if estado.value == normalizado), None)

    @classmethod
    def valores(cls) -> list:
        return [estado.value for estado in cls]

    @property
    def es_final(self) -> bool:
        return self in (EstadoSolicitud.RESUELTA, EstadoSolicitud.RECHAZADA)


class Prioridad(str, Enum):
    ALTA = "ALTA"
    MEDIA = "MEDIA"
    BAJA = "BAJA"

    @classmethod
    def desde_texto(cls, texto: Optional[str]) -> Optional["Prioridad"]:
        normalizado = (texto or "").upper().strip()
        return next(
            (prioridad for prioridad in cls if prioridad.value == normalizado), None
        )

    @classmethod
    def valores(cls) -> list:
        return [prioridad.value for prioridad in cls]


class TipoTramite(str, Enum):
    EQUIVALENCIA = "Equivalencia de Materia"
    CERTIFICADO_REGULAR = "Certificado de Alumno Regular"
    RECLAMO_EXAMEN = "Reclamo de Examen"
    PASE_CARRERA = "Pase de Carrera"

    @classmethod
    def desde_texto(cls, texto: Optional[str]) -> Optional["TipoTramite"]:
        return next((tipo for tipo in cls if tipo.value == texto), None)

    @classmethod
    def valores(cls) -> list:
        return [tipo.value for tipo in cls]

    def resolver_prioridad(self, solicitada: Optional[Prioridad]) -> Prioridad:
        """
        Reemplaza la cadena if-elif: cada tipo de trámite sabe que 'prioridad' le corresponde. Si el tipo no fija una, se respeta la solicitada y, si esta
        no es válida, s eusa la prioridad por defecto.
        """
        fija = _PRIORIDAD_FIJA_POR_TIPO.get(self)
        if fija is not None:
            return fija
        return solicitada or _PRIORIDAD_POR_DEFECTO_POR_TIPO[self]


_PRIORIDAD_FIJA_POR_TIPO = {
    TipoTramite.CERTIFICADO_REGULAR: Prioridad.MEDIA,
    TipoTramite.RECLAMO_EXAMEN: Prioridad.ALTA,
    TipoTramite.PASE_CARRERA: Prioridad.BAJA,
}

_PRIORIDAD_POR_DEFECTO_POR_TIPO = {
    TipoTramite.EQUIVALENCIA: Prioridad.ALTA,
}

PRIORIDAD_SI_NO_SE_INFORMA = Prioridad.MEDIA


class TransicionInvalidaError(Exception):
    """Se lanza cuando una operacion viola las reglas del ciclo de vida de la solicitud."""


@dataclass
class Solicitud:
    """
    Entidad de dominio con comportamiento (ya no es un diccionario anemico).
    El orden de los campos respeta el formato del JSON persistido.
    """

    id: int
    estudiante_legajo: str
    estudiante_nombre: str
    estudiante_email: str
    estudiante_carrera: str
    tipo: str
    descripcion: str
    fecha_creacion: str
    prioridad: str
    estado: EstadoSolicitud
    responsable_id: Optional[str] = None
    observaciones: str = ""

    @classmethod
    def desde_dict(cls, datos: dict) -> "Solicitud":
        campos = dict(datos)
        campos["estado"] = EstadoSolicitud(campos["estado"])
        campos.setdefault("observaciones", "")
        return cls(**campos)

    def a_dict(self) -> dict:
        datos = asdict(self)
        datos["estado"] = self.estado.value
        return datos

    @property
    def esta_finalizada(self) -> bool:
        return self.estado.es_final

    @property
    def tiene_responsable(self) -> bool:
        return bool(self.responsable_id)

    def asignar_responsable(self, id_responsable: str) -> None:
        """Al asignar un responsable, una solicitud PENDIENTE pasa a EN_CURSO."""
        self.responsable_id = id_responsable
        if self.estado == EstadoSolicitud.PENDIENTE:
            self.estado = EstadoSolicitud.EN_CURSO

    def cambiar_estado(
        self, nuevo_estado: EstadoSolicitud, observacion: str = ""
    ) -> None:
        if self.esta_finalizada:
            raise TransicionInvalidaError(
                f"La solicitud {self.id} ya esta finalizada ({self.estado.value})."
            )
        if nuevo_estado == EstadoSolicitud.RESUELTA and not self.tiene_responsable:
            raise TransicionInvalidaError(
                "No se puede resolver una solicitud sin un responsable asignado."
            )
        self.estado = nuevo_estado
        self.agregar_observacion(observacion)

    def agregar_observacion(self, observacion: str) -> None:
        if observacion:
            self.observaciones = (self.observaciones + " | " + observacion).strip(" | ")
