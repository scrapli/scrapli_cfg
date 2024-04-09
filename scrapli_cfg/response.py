"""scrapli_cfg.response"""

from datetime import datetime
from typing import Iterable, List, Optional, Type, Union

from scrapli.response import MultiResponse, Response
from scrapli_cfg.exceptions import ScrapliCfgException


class ScrapliCfgResponse:
    def __init__(
        self, host: str, raise_for_status_exception: Type[Exception] = ScrapliCfgException
    ) -> None:
        """
        Scrapli CFG Response object

        Args:
            host: host that was operated on
            raise_for_status_exception: exception to raise if response is failed and user calls
                `raise_for_status`

        Returns:
            N/A

        Raises:
            N/A

        """
        self.host = host
        self.start_time = datetime.now()
        self.finish_time: Optional[datetime] = None
        self.elapsed_time: Optional[float] = None

        # scrapli_responses is a "flattened" list of responses from all operations that were
        # performed; meaning that if we used any plural operations like send_commands we'll flatten
        # the MultiResponse bits into a list of singular response objects and store them here
        self.scrapli_responses: List[Response] = []
        self.result: str = ""

        self.raise_for_status_exception = raise_for_status_exception
        self.failed = True

    def __bool__(self) -> bool:
        """
        Magic bool method based on operation being failed or not

        Args:
            N/A

        Returns:
            bool: True/False if channel_input failed

        Raises:
            N/A

        """
        return self.failed

    def __repr__(self) -> str:
        """
        Magic repr method for ScrapliCfgResponse class

        Args:
            N/A

        Returns:
            str: repr for class object

        Raises:
            N/A

        """
        return f"ScrapliCfgResponse <Success: {str(not self.failed)}>"

    def __str__(self) -> str:
        """
        Magic str method for ScrapliCfgResponse class

        Args:
            N/A

        Returns:
            str: str for class object

        Raises:
            N/A

        """
        return f"ScrapliCfgResponse <Success: {str(not self.failed)}>"

    def record_response(
        self, scrapli_responses: Iterable[Union[Response, MultiResponse]], result: str = ""
    ) -> None:
        """
        Record channel_input results and elapsed time of channel input/reading output

        Args:
            scrapli_responses: list of scrapli response/multiresponse objects
            result: string to assign to final result for the scrapli cfg response object

        Returns:
            None

        Raises:
            N/A

        """
        self.finish_time = datetime.now()
        self.elapsed_time = (self.finish_time - self.start_time).total_seconds()

        for response in scrapli_responses:
            if isinstance(response, Response):
                self.scrapli_responses.append(response)
            elif isinstance(response, MultiResponse):
                for sub_response in response:
                    self.scrapli_responses.append(sub_response)

        self.result = result

        if not any(response.failed for response in self.scrapli_responses):
            self.failed = False

    def raise_for_status(self) -> None:
        """
        Raise a `ScrapliCommandFailure` if command/config failed

        Args:
            N/A

        Returns:
            None

        Raises:
            raise_for_status_exception: exception raised is dependent on the type of response object

        """
        if self.failed:
            raise self.raise_for_status_exception()
