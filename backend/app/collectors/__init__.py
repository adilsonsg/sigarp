from app.collectors.pncp import PNCPCollector
from app.collectors.registry import collector_registry

collector_registry.register(PNCPCollector.name, PNCPCollector, replace=True)

__all__ = ["PNCPCollector", "collector_registry"]
