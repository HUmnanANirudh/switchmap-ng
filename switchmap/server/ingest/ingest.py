"""switchmap classes that manage the DB uploading of polled data."""

import os.path
import os
import tempfile

# Import project libraries
from multiprocessing import Pool
from switchmap.core import log
from switchmap.core import files
from switchmap.core import general
from switchmap.server.db.table import IEvent
from switchmap.server.db.table import IZone
from switchmap.server.db.table import IRoot
from switchmap.server.db.table import event as _event
from switchmap.server.db.table import zone as _zone
from switchmap.server.db.table import root as _root
from switchmap.server import ZoneData
from switchmap.server.ingest import topology


class Ingest:
    """Read cache files in the DB."""

    def __init__(self, config, test=False, test_cache_directory=None):
        """Initialize class.

        Args:
            config: ConfigServer object
            test: True if testing
            test_cache_directory: Ingest directory. Only used when testing.

        Returns:
            None

        """
        # Initialize key variables
        self._config = config
        self._test = test
        self._test_cache_directory = test_cache_directory
        self._name = "ingest"

    def process(self):
        """Process files in the cache.

        Args:
            None

        Returns:
            None

        """
        # Initialize key variables
        cache_directory = (
            self._config.cache_directory()
            if bool(self._test) is False
            else self._test_cache_directory
        )

        # Test for the lock file
        lock_file = files.lock_file(self._name, self._config)
        if os.path.isfile(lock_file) is True:
            log_message = """\
Ingest lock file {} exists. Is an ingest process already running?\
""".format(
                lock_file
            )
            log.log2debug(1054, log_message)
            return

        # Create lock file
        open(lock_file, "a").close()

        # Process files
        with tempfile.TemporaryDirectory(
            dir=self._config.ingest_directory()
        ) as _stream:
            # Copy files from cache to ingest
            files.move_yaml_files(cache_directory, _stream.name)

            # Parallel process the files
            self.parallel()

        # Delete lock file
        os.remove(lock_file)

    def parallel(self):
        """Ingest the files in parallel.

        Args:
            None

        Returns:
            None

        """
        # Initialize key variables
        zones = []
        src = self._config.ingest_directory()

        # Get the number of threads to use in the pool
        pool_size = self._config.agent_subprocesses()

        # Create a list of files to process
        filepaths = _filepaths(src)

        # Parallel processing
        if bool(filepaths) is True:
            # Create an event
            event = _create_event()

            # Get the zone data from each file
            for filepath in filepaths:
                zones.append(_get_zone(event, filepath))

            if bool(self._test) is False:
                ############################
                # Process files in parallel
                ############################

                # Create a pool of sub process resources
                with Pool(processes=pool_size) as pool:
                    # Create sub processes from the pool
                    pool.map(single, zones)

                # Update the event pointer in the root table
                # We don't do this for testing
                root = _root.idx_exists(1)
                if bool(root):
                    _root.update_row(
                        root.idx_root,
                        IRoot(
                            idx_event=event.idx_event,
                            name=root.name,
                            enabled=1,
                        ),
                    )
            else:
                ############################
                # Process files sequentially
                ############################
                for zone in zones:
                    single(zone)

                # TODO Delete all DB records related to the event
                _event.delete(event.idx_event)


def single(item):
    """Ingest a single file.

    Args:
        item: ZoneData object

    Returns:
        None

    """
    # Process the ingested data
    topology.process(item.data, item.idx_zone)


def _create_event():
    """Get and _event ID for the next polling cycle.

    Args:
        None

    Returns:
        result: Event ID that doesn't already exist

    """
    # Get configuration
    while True:
        event = general.random_hash()
        exists = _event.exists(event)
        if bool(exists) is False:
            break

    # Get REvent object
    row = IEvent(name=event, enabled=1)
    _event.insert_row(row)
    result = _event.exists(event)
    return result


def _filepaths(src):
    """Get and _event ID for the next polling cycle.

    Args:
        src: Source directory

    Returns:
        filepaths: List of all yaml files in the directory

    """
    # Initialize key variables
    filepaths = []

    # Process files
    src_files = os.listdir(src)
    for filename in src_files:
        filepath = os.path.join(src, filename)
        if os.path.isfile(filepath) and filepath.lower().endswith(".yaml"):
            filepaths.append(filepath)
    return filepaths


def _get_zone(event, filepath):
    """Create an RZone object from YAML file data.

    Args:
        event: RZone object
        filepath: YAML filepath

    Returns:
        result: ZoneData object

    """
    # Read the yaml file
    data = files.read_yaml_file(filepath)

    # Get the zone information
    name = data["misc"]["zone"]
    exists = _zone.exists(event.idx_event, name)
    if bool(exists) is False:
        _zone.insert(
            IZone(
                idx_event=event.idx_event,
                name=name,
                company_name=None,
                address_0=None,
                address_1=None,
                address_2=None,
                city=None,
                state=None,
                country=None,
                postal_code=None,
                phone=None,
                notes=None,
                enabled=1,
            )
        )
        exists = _zone.exists(event.idx_event, name)

    # Return
    result = ZoneData(idx_zone=exists.idx_zone, data=data)
    return result
