from pathlib import Path


class CommonDependencies(object):
    def exists(self, path: Path) -> bool:
        raise NotImplementedError()
