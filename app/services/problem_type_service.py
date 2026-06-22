from collections.abc import Mapping

from app.domain.enums import ProblemScope
from app.domain.models import ProblemType
from app.repositories.problem_type_repository import ProblemTypeRepository


INITIAL_PROBLEM_TYPES: tuple[dict[str, object], ...] = (
    {
        "code": 1110,
        "scope": ProblemScope.LABORATORY,
        "name": "Falha eletrica geral do laboratorio",
        "description": "Classificacao tecnica para falhas eletricas que afetam o laboratorio como ambiente.",
    },
    {
        "code": 1210,
        "scope": ProblemScope.LABORATORY,
        "name": "Indisponibilidade de rede no laboratorio",
        "description": "Classificacao tecnica para indisponibilidade ou instabilidade de rede geral.",
    },
    {
        "code": 1310,
        "scope": ProblemScope.LABORATORY,
        "name": "Reorganizacao de equipamentos",
        "description": "Classificacao tecnica para reorganizacao fisica ou redistribuicao de equipamentos.",
    },
    {
        "code": 2110,
        "scope": ProblemScope.WORKSTATION,
        "name": "Falha no ponto de rede da estacao",
        "description": "Classificacao tecnica para falhas ligadas ao ponto de rede da estacao.",
    },
    {
        "code": 2210,
        "scope": ProblemScope.WORKSTATION,
        "name": "Falha eletrica na estacao",
        "description": "Classificacao tecnica para falhas eletricas localizadas na estacao.",
    },
    {
        "code": 2330,
        "scope": ProblemScope.WORKSTATION,
        "name": "Estacao incompleta ou indisponivel",
        "description": "Classificacao tecnica para estacoes sem ativo necessario ou sem condicao de uso.",
    },
    {
        "code": 3010,
        "scope": ProblemScope.COMPUTER_CASE,
        "name": "Falha de energia do gabinete",
        "description": "Classificacao tecnica para falhas de energia associadas ao gabinete.",
    },
    {
        "code": 3020,
        "scope": ProblemScope.COMPUTER_CASE,
        "name": "Falha de inicializacao",
        "description": "Classificacao tecnica para gabinete que nao conclui inicializacao.",
    },
    {
        "code": 3110,
        "scope": ProblemScope.COMPUTER_CASE,
        "name": "Correcao de sistema operacional",
        "description": "Classificacao tecnica para manutencoes de sistema operacional.",
    },
    {
        "code": 3210,
        "scope": ProblemScope.COMPUTER_CASE,
        "name": "Falha de armazenamento",
        "description": "Classificacao tecnica para falhas em SSD, HD ou armazenamento do gabinete.",
    },
    {
        "code": 3320,
        "scope": ProblemScope.COMPUTER_CASE,
        "name": "Baixo desempenho",
        "description": "Classificacao tecnica para lentidao ou desempenho insuficiente do gabinete.",
    },
    {
        "code": 4010,
        "scope": ProblemScope.MONITOR,
        "name": "Falha de energia do monitor",
        "description": "Classificacao tecnica para falhas de ligamento ou energia do monitor.",
    },
    {
        "code": 4110,
        "scope": ProblemScope.MONITOR,
        "name": "Ausencia de imagem",
        "description": "Classificacao tecnica para monitor sem exibicao de imagem.",
    },
    {
        "code": 4210,
        "scope": ProblemScope.MONITOR,
        "name": "Cabo de video",
        "description": "Classificacao tecnica para falha, ausencia ou troca de cabo de video.",
    },
    {
        "code": 4310,
        "scope": ProblemScope.MONITOR,
        "name": "Resolucao ou escala incorreta",
        "description": "Classificacao tecnica para ajustes de resolucao, escala ou configuracao de video.",
    },
)


class ProblemTypeService:
    """Use cases for technical problem classifications used by maintenance workflows."""

    CODE_RANGES = {
        ProblemScope.LABORATORY: (1000, 1999),
        ProblemScope.WORKSTATION: (2000, 2999),
        ProblemScope.COMPUTER_CASE: (3000, 3999),
        ProblemScope.MONITOR: (4000, 4999),
    }

    STABLE_FIELD_MESSAGE = "Problem type code and scope cannot be changed after creation."

    def __init__(self, problem_type_repository: ProblemTypeRepository | None = None) -> None:
        self.problem_type_repository = problem_type_repository or ProblemTypeRepository()

    def create_problem_type(self, data: Mapping[str, object]) -> ProblemType:
        problem_type = self._build_problem_type(data)
        self._ensure_code_matches_scope(problem_type.code, problem_type.scope)
        self._ensure_unique_code(problem_type.code)
        return self.problem_type_repository.save(problem_type)

    def update_problem_type(self, problem_type: ProblemType, data: Mapping[str, object]) -> ProblemType:
        """Update only descriptive fields so historical statistics keep their original meaning."""
        self._ensure_stable_fields_were_not_submitted(data)
        problem_type.name = self._normalize_required_text(data.get("name", ""), "Name is required.")
        problem_type.description = self._normalize_optional_text(data.get("description", ""))
        return self.problem_type_repository.commit(problem_type)

    def set_problem_type_status(self, problem_type: ProblemType, active: bool) -> ProblemType:
        problem_type.active = bool(active)
        return self.problem_type_repository.commit(problem_type)

    def list_problem_types(self, filters: dict | None = None) -> list[ProblemType]:
        normalized_filters = self._normalize_filters(filters or {})
        return self.problem_type_repository.list_all(normalized_filters)

    def list_active_by_scope(self, scope: ProblemScope | str) -> list[ProblemType]:
        return self.problem_type_repository.list_active_by_scope(self._normalize_scope(scope))

    def get_problem_type(self, problem_type_id: int) -> ProblemType:
        problem_type = self.problem_type_repository.find_by_id(problem_type_id)
        if problem_type is None:
            raise LookupError("Problem type not found.")

        return problem_type

    def seed_initial_problem_types(self) -> dict[str, int]:
        """Create the starter taxonomy without overwriting user-maintained classifications."""
        created = 0
        skipped = 0

        for item in INITIAL_PROBLEM_TYPES:
            code = self._normalize_code(item["code"])
            existing = self.problem_type_repository.find_by_code(code)
            if existing is not None:
                self._ensure_code_matches_scope(existing.code, existing.scope)
                skipped += 1
                continue

            self.create_problem_type(item)
            created += 1

        return {"created": created, "skipped": skipped}

    def _build_problem_type(self, data: Mapping[str, object]) -> ProblemType:
        code = self._normalize_code(data.get("code", ""))
        scope = self._normalize_scope(data.get("scope", ""))
        return ProblemType(
            code=code,
            scope=scope,
            name=self._normalize_required_text(data.get("name", ""), "Name is required."),
            description=self._normalize_optional_text(data.get("description", "")),
            active=True,
        )

    def _normalize_filters(self, filters: dict) -> dict:
        normalized: dict[str, object] = {}

        scope = filters.get("scope")
        if scope:
            normalized["scope"] = self._normalize_scope(scope)

        active = filters.get("active")
        if active in (True, False):
            normalized["active"] = active
        elif isinstance(active, str) and active.lower() in {"true", "false"}:
            normalized["active"] = active.lower() == "true"

        return normalized

    @staticmethod
    def _normalize_required_text(value: object, message: str) -> str:
        normalized = str(value).strip()
        if not normalized:
            raise ValueError(message)

        return normalized

    @staticmethod
    def _normalize_optional_text(value: object) -> str | None:
        normalized = str(value).strip()
        return normalized or None

    @staticmethod
    def _normalize_code(value: object) -> int:
        try:
            code = int(str(value).strip())
        except (TypeError, ValueError) as exc:
            raise ValueError("Problem type code must be an integer.") from exc

        if code < 1000 or code > 4999:
            raise ValueError("Problem type code must be between 1000 and 4999.")

        return code

    @staticmethod
    def _normalize_scope(value: ProblemScope | str) -> ProblemScope:
        if isinstance(value, ProblemScope):
            return value

        normalized = str(value).strip().upper()
        try:
            return ProblemScope(normalized)
        except ValueError as exc:
            raise ValueError("Invalid problem scope.") from exc

    def _ensure_code_matches_scope(self, code: int, scope: ProblemScope) -> None:
        first_code, last_code = self.CODE_RANGES[scope]
        if not first_code <= code <= last_code:
            raise ValueError(
                f"Code {code} is incompatible with scope {scope.value}. "
                f"Expected range: {first_code}-{last_code}."
            )

    def _ensure_unique_code(self, code: int) -> None:
        if self.problem_type_repository.find_by_code(code) is not None:
            raise ValueError("Problem type code already exists.")

    def _ensure_stable_fields_were_not_submitted(self, data: Mapping[str, object]) -> None:
        # Code and scope are classification keys; changing them would corrupt future trend analysis.
        if "code" in data or "scope" in data:
            raise ValueError(self.STABLE_FIELD_MESSAGE)
