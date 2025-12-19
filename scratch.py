from pathlib import Path
from typing import Final

from snowflake.snowpark import DataFrame

from ...utils.logger import Logger
from ...utils.etl import ETL
from ...utils.decorators import time_function

MODULE_NAME: Final[str] = Path(__file__).name

class BeneficiaryPipeline:
    """Pipeline class"""

    def __init__(self):
        self.logger = Logger()
        self.etl = ETL()

    @time_function("BeneficiaryPipeline.run")
    def run(
        self,
        _write: bool = False
    ):
        self.pipeline(_write)
        self.logger.info(
            message="The beneficiary pipeline completed successfully.",
            context=MODULE_NAME
        )

    def pipeline(
        self,
        _write: bool
    ):
        """Organization of processors"""
        # Custom conditional logic
        df: DataFrame = self.run_processors()
        if _write:
            self._write_to_snowflake(
                df,
                write_mode="overwrite",
                table_path=table_name
            )

    def run_processors(
            self
    ):
        msp_processor = MSPProcessor(...)
        msp_df = msp_processor.process(...)

        # n number of processors
        # ...

        return final_df
    
    def _write_to_snowflake(
            self,
            df: DataFrame,
            write_mode: Literal[
                "append",
                "overwrite",
                "truncate",
                "errorifexists",
                "ignore"
            ],
            table_path: str
    ):
        self.logger.info(
            message=f"Writing DataFrame as table to {table_path}",
            context=MODULE_NAME
        )

        df.write.mode(write_mode).save_as_table(table_path)

        self.logger.info(
            message=f"Successfully saved table to {table_path}",
            context=MODULE_NAME
        )