"""Model of Evergreen TestMapping that needs to be analyzed."""
import structlog

from datetime import datetime, timedelta
from pymongo.errors import DuplicateKeyError

LOGGER = structlog.get_logger()
WORK_ITEM_TTL = timedelta(weeks=2).total_seconds()


class ProjectTaskMappingWorkItem(object):
    """A work item for an evergreen task_mapping."""

    def __init__(
        self,
        start_time,
        end_time,
        created_on: datetime,
        project: str,
        source_file_regex: str,
        module: str,
        module_source_file_regex: str,
        build_variant_regex: str,
    ):
        """
        Create a task_mapping work item.

        :param start_time: Time work was started on item.
        :param end_time: Time work completed on item.
        :param created_on: Time work item was created.
        :param project: The name of the evergreen project to analyze.
        :param source_file_regex: Regex pattern to match changed source files against.
        :param module: The name of the module to analyze.
        :param module_source_file_regex: Regex pattern to match changed module source files against.
        :param build_variant_regex:  Regex pattern to match build variants' display name against.
        """
        self.start_time = start_time
        self.end_time = end_time
        self.created_on = created_on
        self.project = project
        self.source_file_regex = source_file_regex
        self.module = module
        self.module_source_file_regex = module_source_file_regex
        self.build_variant_regex = build_variant_regex

    @classmethod
    def new_task_mappings(
        cls,
        project: str,
        source_file_regex: str,
        module: str = None,
        module_source_file_regex: str = None,
        build_variant_regex: str = None,
    ):
        """
        Create a new work item.

        :param project: The name of the evergreen project to analyze.
        :param source_file_regex: Regex pattern to match changed source files against.
        :param module: The name of the module to analyze.
        :param module_source_file_regex: Regex pattern to match changed module source files against.
        :param build_variant_regex: Regex pattern to match build variants' display name against.
        :return: ProjectTestMappingWorkItem instance for work item.
        """
        return cls(
            None,
            None,
            datetime.utcnow(),
            project,
            source_file_regex,
            module,
            module_source_file_regex,
            build_variant_regex,
        )

    def insert(self, collection) -> bool:
        """
        Add this work item to the Mongo collection.

        :param collection: Mongo collection containing queue.
        :return: True if item was new record was added to collection.
        """
        LOGGER.info("Adding new task_mapping work item for project", project=self.project)
        to_insert = {
            "created_on": self.created_on,
            "project": self.project,
            "source_file_regex": self.source_file_regex,
        }
        if self.module:
            to_insert["module"] = self.module
            to_insert["module_source_file_regex"] = self.module_source_file_regex
        if self.build_variant_regex:
            to_insert["build_variant_regex"] = self.build_variant_regex
        try:
            result = collection.insert_one(to_insert)
            return result.acknowledged
        except DuplicateKeyError:
            return False