from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Set


class DomainAdapter(ABC):
    @property
    @abstractmethod
    def adapter_id(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def domain_name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def entity_types(self) -> Set[str]:
        raise NotImplementedError

    @property
    @abstractmethod
    def event_types(self) -> Set[str]:
        raise NotImplementedError

    @abstractmethod
    def scenario_dir(self, repo_root: Path) -> Path:
        raise NotImplementedError

    @abstractmethod
    def default_policy_path(self, repo_root: Path) -> Path:
        raise NotImplementedError

    @abstractmethod
    def adapter_schema_paths(self, repo_root: Path) -> List[Path]:
        raise NotImplementedError

    def validate_entities(self, entities: List[Dict[str, Any]]) -> List[str]:
        errors = []
        for entity in entities:
            entity_type = entity.get("entity_type")
            if entity_type not in self.entity_types:
                errors.append("Unsupported entity_type: %s" % entity_type)
        return errors

    def validate_events(self, events: List[Dict[str, Any]]) -> List[str]:
        errors = []
        for event in events:
            event_type = event.get("event_type")
            if event_type not in self.event_types:
                errors.append("Unsupported event_type: %s" % event_type)
        return errors
