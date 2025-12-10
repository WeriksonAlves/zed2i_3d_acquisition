import datetime
import pathlib


class ExperimentPathManager:
    """
    Manage experiment output directories and file naming.

    This helper is responsible for creating a unique directory per experiment,
    keeping the naming logic in a single place.
    """

    def __init__(self, base_dir: str) -> None:
        self._base_dir = pathlib.Path(base_dir)
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def create_experiment_dir(self, experiment_name: str) -> pathlib.Path:
        """
        Create a unique directory for the experiment, for example:

        <base_dir>/<experiment_name>_<YYYYMMDD_HHMMSS>

        :param experiment_name: Logical name for the experiment.
        :return: Full path to the newly created directory.
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        full_name = f"{experiment_name}_{timestamp}"
        experiment_dir = self._base_dir / full_name
        experiment_dir.mkdir(parents=True, exist_ok=True)
        return experiment_dir
