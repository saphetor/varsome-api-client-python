from types import TracebackType

import pyarrow as pa
import pyarrow.parquet as pq

from models import PARQUET_SCHEMA, to_parquet_row
from varsome_api.models.slim.annotation import AnnotatedVariant


class ParquetWriter:

    def __init__(
        self,
        output_path: str,
        schema: pa.Schema = PARQUET_SCHEMA,
    ) -> None:
        self._output_path = output_path
        self._schema = schema
        self._rows: list[dict] = []

    def add(self, variant: AnnotatedVariant) -> None:
        self._rows.append(to_parquet_row(variant))

    def write(self) -> int:
        table = self._build_table()
        pq.write_table(table, self._output_path, compression="lz4")
        return len(self._rows)

    def __enter__(self) -> "ParquetWriter":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is None:
            self.write()


    def _build_table(self) -> pa.Table:
        columns: dict[str, list] = {field.name: [] for field in self._schema}

        for row in self._rows:
            for field in self._schema:
                columns[field.name].append(row.get(field.name))

        arrays: list[pa.Array] = [
            pa.array(columns[field.name], type=field.type)
            for field in self._schema
        ]
        return pa.Table.from_arrays(arrays, schema=self._schema)
