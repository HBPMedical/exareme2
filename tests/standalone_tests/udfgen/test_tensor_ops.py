# type: ignore
from string import Template

import pytest

from mipengine.datatypes import DType
from mipengine.node_tasks_DTOs import ColumnInfo
from mipengine.node_tasks_DTOs import TableInfo
from mipengine.node_tasks_DTOs import TableSchema
from mipengine.node_tasks_DTOs import TableType
from mipengine.udfgen.iotypes import LiteralArg
from mipengine.udfgen.iotypes import TensorArg
from mipengine.udfgen.tensor_ops import TensorBinaryOp
from mipengine.udfgen.tensor_ops import get_matrix_transpose_template
from mipengine.udfgen.tensor_ops import get_tensor_binary_op_template
from mipengine.udfgen.udfgen_DTOs import UDFGenTableResult
from tests.standalone_tests.udfgen.test_udfgenerator import TestUDFGenBase
from tests.standalone_tests.udfgen.test_udfgenerator import _TestGenerateUDFQueries

pytest.skip(allow_module_level=True, msg="The tensor_ops module is deprecated.")


class TestUDFGen_SQLTensorMultOut1D(TestUDFGenBase, _TestGenerateUDFQueries):
    @pytest.fixture(scope="class")
    def funcname(self):
        return TensorBinaryOp.MATMUL.name

    @pytest.fixture(scope="class")
    def positional_args(self):
        return [
            TableInfo(
                name="tensor1",
                schema_=TableSchema(
                    columns=[
                        ColumnInfo(name="dim0", dtype=DType.INT),
                        ColumnInfo(name="dim1", dtype=DType.INT),
                        ColumnInfo(name="val", dtype=DType.INT),
                    ]
                ),
                type_=TableType.NORMAL,
            ),
            TableInfo(
                name="tensor2",
                schema_=TableSchema(
                    columns=[
                        ColumnInfo(name="dim0", dtype=DType.INT),
                        ColumnInfo(name="val", dtype=DType.INT),
                    ]
                ),
                type_=TableType.NORMAL,
            ),
        ]

    @pytest.fixture(scope="class")
    def expected_udfdef(self):
        return ""

    @pytest.fixture(scope="class")
    def expected_udfsel(self):
        return """\
INSERT INTO $main_output_table_name
SELECT
    tensor_0."dim0" AS dim0,
    SUM("tensor_0.\"val\" * tensor_1.\"val\"") AS val
FROM
    tensor1 AS tensor_0,
    tensor2 AS tensor_1
WHERE
    tensor_0."dim1"=tensor_1."dim0"
GROUP BY
    tensor_0."dim0"
ORDER BY
    "dim0";"""

    @pytest.fixture(scope="class")
    def expected_udf_outputs(self):
        return [
            UDFGenTableResult(
                tablename_placeholder="main_output_table_name",
                table_schema=[
                    ("dim0", DType.INT),
                    ("val", DType.FLOAT),
                ],
                drop_query=Template("DROP TABLE IF EXISTS $main_output_table_name;"),
                create_query=Template(
                    'CREATE TABLE $main_output_table_name("dim0" INT,"val" DOUBLE);'
                ),
            )
        ]


class TestUDFGen_SQLTensorMultOut2D(TestUDFGenBase, _TestGenerateUDFQueries):
    @pytest.fixture(scope="class")
    def funcname(self):
        return TensorBinaryOp.MATMUL.name

    @pytest.fixture(scope="class")
    def positional_args(self):
        return [
            TableInfo(
                name="tensor1",
                schema_=TableSchema(
                    columns=[
                        ColumnInfo(name="dim0", dtype=DType.INT),
                        ColumnInfo(name="dim1", dtype=DType.INT),
                        ColumnInfo(name="val", dtype=DType.INT),
                    ]
                ),
                type_=TableType.NORMAL,
            ),
            TableInfo(
                name="tensor2",
                schema_=TableSchema(
                    columns=[
                        ColumnInfo(name="dim0", dtype=DType.INT),
                        ColumnInfo(name="dim1", dtype=DType.INT),
                        ColumnInfo(name="val", dtype=DType.INT),
                    ]
                ),
                type_=TableType.NORMAL,
            ),
        ]

    @pytest.fixture(scope="class")
    def expected_udfdef(self):
        return ""

    @pytest.fixture(scope="class")
    def expected_udfsel(self):
        return """\
INSERT INTO $main_output_table_name
SELECT
    tensor_0."dim0" AS dim0,
    tensor_1."dim1" AS dim1,
    SUM("tensor_0.\"val\" * tensor_1.\"val\"") AS val
FROM
    tensor1 AS tensor_0,
    tensor2 AS tensor_1
WHERE
    tensor_0."dim1"=tensor_1."dim0"
GROUP BY
    tensor_0."dim0",
    tensor_1."dim1"
ORDER BY
    dim0,
    dim1;"""

    @pytest.fixture(scope="class")
    def expected_udf_outputs(self):
        return [
            UDFGenTableResult(
                tablename_placeholder="main_output_table_name",
                table_schema=[
                    ("dim0", DType.INT),
                    ("dim1", DType.INT),
                    ("val", DType.FLOAT),
                ],
                drop_query=Template("DROP TABLE IF EXISTS $main_output_table_name;"),
                create_query=Template(
                    'CREATE TABLE $main_output_table_name("dim0" INT,"dim1" INT,"val" DOUBLE);'
                ),
            )
        ]


class TestUDFGen_SQLTensorSubLiteralArg(TestUDFGenBase, _TestGenerateUDFQueries):
    @pytest.fixture(scope="class")
    def funcname(self):
        return TensorBinaryOp.SUB.name

    @pytest.fixture(scope="class")
    def positional_args(self):
        return [
            1,
            TableInfo(
                name="tensor1",
                schema_=TableSchema(
                    columns=[
                        ColumnInfo(name="dim0", dtype=DType.INT),
                        ColumnInfo(name="val", dtype=DType.INT),
                    ]
                ),
                type_=TableType.NORMAL,
            ),
        ]

    @pytest.fixture(scope="class")
    def expected_udfdef(self):
        return ""

    @pytest.fixture(scope="class")
    def expected_udfsel(self):
        return """\
INSERT INTO $main_output_table_name
SELECT
    tensor_0."dim0" AS dim0,
    1 - tensor_0."val" AS val
FROM
    tensor1 AS tensor_0;"""

    @pytest.fixture(scope="class")
    def expected_udf_outputs(self):
        return [
            UDFGenTableResult(
                tablename_placeholder="main_output_table_name",
                table_schema=[
                    ("dim0", DType.INT),
                    ("val", DType.FLOAT),
                ],
                drop_query=Template("DROP TABLE IF EXISTS $main_output_table_name;"),
                create_query=Template(
                    'CREATE TABLE $main_output_table_name("dim0" INT,"val" DOUBLE);'
                ),
            )
        ]


def test_tensor_elementwise_binary_op_1dim():
    tensor_0 = TensorArg(table_name="tens0", dtype=None, ndims=1)
    tensor_1 = TensorArg(table_name="tens1", dtype=None, ndims=1)
    op = TensorBinaryOp.ADD
    expected = """\
SELECT
    tensor_0.dim0 AS dim0,
    tensor_0.val + tensor_1.val AS val
FROM
    tens0 AS tensor_0,
    tens1 AS tensor_1
WHERE
    tensor_0.dim0=tensor_1.dim0"""
    result = get_tensor_binary_op_template(tensor_0, tensor_1, op)
    assert result == expected


def test_tensor_elementwise_binary_op_2dim():
    tensor_0 = TensorArg(table_name="tens0", dtype=None, ndims=2)
    tensor_1 = TensorArg(table_name="tens1", dtype=None, ndims=2)
    op = TensorBinaryOp.ADD
    expected = """\
SELECT
    tensor_0.dim0 AS dim0,
    tensor_0.dim1 AS dim1,
    tensor_0.val + tensor_1.val AS val
FROM
    tens0 AS tensor_0,
    tens1 AS tensor_1
WHERE
    tensor_0.dim0=tensor_1.dim0 AND
    tensor_0.dim1=tensor_1.dim1"""
    result = get_tensor_binary_op_template(tensor_0, tensor_1, op)
    assert result == expected


def test_vector_dot_vector_template():
    tensor_0 = TensorArg(table_name="vec0", dtype=None, ndims=1)
    tensor_1 = TensorArg(table_name="vec1", dtype=None, ndims=1)
    op = TensorBinaryOp.MATMUL
    expected = '''\
SELECT
    SUM("tensor_0.\"val\" * tensor_1.\"val\"") AS val
FROM
    vec0 AS tensor_0,
    vec1 AS tensor_1
WHERE
    tensor_0."dim0"=tensor_1."dim0"'''
    result = get_tensor_binary_op_template(tensor_0, tensor_1, op)
    assert result == expected


def test_matrix_dot_matrix_template():
    tensor_0 = TensorArg(table_name="mat0", dtype=None, ndims=2)
    tensor_1 = TensorArg(table_name="mat1", dtype=None, ndims=2)
    op = TensorBinaryOp.MATMUL
    expected = """\
SELECT
    tensor_0.dim0 AS dim0,
    tensor_1.dim1 AS dim1,
    SUM(tensor_0.val * tensor_1.val) AS val
FROM
    mat0 AS tensor_0,
    mat1 AS tensor_1
WHERE
    tensor_0.dim1=tensor_1.dim0
GROUP BY
    tensor_0.dim0,
    tensor_1.dim1
ORDER BY
    dim0,
    dim1"""
    result = get_tensor_binary_op_template(tensor_0, tensor_1, op)
    assert result == expected


def test_matrix_dot_vector_template():
    tensor_0 = TensorArg(table_name="mat0", dtype=None, ndims=2)
    tensor_1 = TensorArg(table_name="vec1", dtype=None, ndims=1)
    op = TensorBinaryOp.MATMUL
    expected = """\
SELECT
    tensor_0.dim0 AS dim0,
    SUM(tensor_0.val * tensor_1.val) AS val
FROM
    mat0 AS tensor_0,
    vec1 AS tensor_1
WHERE
    tensor_0.dim1=tensor_1.dim0
GROUP BY
    tensor_0.dim0
ORDER BY
    dim0"""
    result = get_tensor_binary_op_template(tensor_0, tensor_1, op)
    assert result == expected


def test_vector_dot_matrix_template():
    tensor_0 = TensorArg(table_name="vec0", dtype=None, ndims=1)
    tensor_1 = TensorArg(table_name="mat1", dtype=None, ndims=2)
    op = TensorBinaryOp.MATMUL
    expected = """\
SELECT
    tensor_1.dim1 AS dim0,
    SUM(tensor_0.val * tensor_1.val) AS val
FROM
    vec0 AS tensor_0,
    mat1 AS tensor_1
WHERE
    tensor_0.dim0=tensor_1.dim0
GROUP BY
    tensor_1.dim1
ORDER BY
    dim0"""
    result = get_tensor_binary_op_template(tensor_0, tensor_1, op)
    assert result == expected


def test_sql_matrix_transpose():
    tens = TensorArg(table_name="tens0", dtype=None, ndims=2)
    expected = """\
SELECT
    tensor_0."dim1" AS dim0,
    tensor_0."dim0" AS dim1,
    tensor_0."val" AS val
FROM
    tens0 AS tensor_0"""
    result = get_matrix_transpose_template(tens)
    assert result == expected


def test_tensor_number_binary_op_1dim():
    operand_0 = TensorArg(table_name="tens0", dtype=None, ndims=1)
    operand_1 = LiteralArg(value=1)
    op = TensorBinaryOp.ADD
    expected = """\
SELECT
    tensor_0.dim0 AS dim0,
    tensor_0.val + 1 AS val
FROM
    tens0 AS tensor_0"""
    result = get_tensor_binary_op_template(operand_0, operand_1, op)
    assert result == expected


def test_number_tensor_binary_op_1dim():
    operand_0 = LiteralArg(value=1)
    operand_1 = TensorArg(table_name="tens1", dtype=None, ndims=1)
    op = TensorBinaryOp.SUB
    expected = """\
SELECT
    tensor_0.dim0 AS dim0,
    1 - tensor_0.val AS val
FROM
    tens1 AS tensor_0"""
    result = get_tensor_binary_op_template(operand_0, operand_1, op)
    assert result == expected
