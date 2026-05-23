from abc import ABC
from abc import abstractmethod

class BaseFlasher(ABC):

    @abstractmethod
    def flash(
        self,
        port,
        package_dir,
        manifest
    ):
        pass