# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
import math

import numpy as np
import pyarrow as pa
import pytest
from datetime import datetime

from datafusion import SessionContext, column
from datafusion import functions as f
from datafusion import literal

np.seterr(invalid="ignore")


@pytest.fixture
def df():
    ctx = SessionContext()
    # create a RecordBatch and a new DataFrame from it
    batch = pa.RecordBatch.from_arrays(
        [
            pa.array(["Hello", "World", "!"]),
            pa.array([4, 5, 6]),
            pa.array(["hello ", " world ", " !"]),
            pa.array(
                [
                    datetime(2022, 12, 31),
                    datetime(2027, 6, 26),
                    datetime(2020, 7, 2),
                ]
            ),
        ],
        names=["a", "b", "c", "d"],
    )
    return ctx.create_dataframe([[batch]])


def test_literal(df):
    df = df.select(
        literal(1),
        literal("1"),
        literal("OK"),
        literal(3.14),
        literal(True),
        literal(b"hello world"),
    )
    result = df.collect()
    assert len(result) == 1
    result = result[0]
    assert result.column(0) == pa.array([1] * 3)
    assert result.column(1) == pa.array(["1"] * 3)
    assert result.column(2) == pa.array(["OK"] * 3)
    assert result.column(3) == pa.array([3.14] * 3)
    assert result.column(4) == pa.array([True] * 3)
    assert result.column(5) == pa.array([b"hello world"] * 3)


def test_lit_arith(df):
    """
    Test literals with arithmetic operations
    """
    df = df.select(literal(1) + column("b"), f.concat(column("a"), literal("!")))
    result = df.collect()
    assert len(result) == 1
    result = result[0]
    assert result.column(0) == pa.array([5, 6, 7])
    assert result.column(1) == pa.array(["Hello!", "World!", "!!"])


def test_math_functions():
    ctx = SessionContext()
    # create a RecordBatch and a new DataFrame from it
    batch = pa.RecordBatch.from_arrays(
        [pa.array([0.1, -0.7, 0.55]), pa.array([float("nan"), 0, 2.0])],
        names=["value", "na_value"],
    )
    df = ctx.create_dataframe([[batch]])

    values = np.array([0.1, -0.7, 0.55])
    na_values = np.array([np.nan, 0, 2.0])
    col_v = column("value")
    col_nav = column("na_value")
    df = df.select(
        f.abs(col_v),
        f.sin(col_v),
        f.cos(col_v),
        f.tan(col_v),
        f.asin(col_v),
        f.acos(col_v),
        f.exp(col_v),
        f.ln(col_v + literal(pa.scalar(1))),
        f.log2(col_v + literal(pa.scalar(1))),
        f.log10(col_v + literal(pa.scalar(1))),
        f.random(),
        f.atan(col_v),
        f.atan2(col_v, literal(pa.scalar(1.1))),
        f.ceil(col_v),
        f.floor(col_v),
        f.power(col_v, literal(pa.scalar(3))),
        f.pow(col_v, literal(pa.scalar(4))),
        f.round(col_v),
        f.sqrt(col_v),
        f.signum(col_v),
        f.trunc(col_v),
        f.asinh(col_v),
        f.acosh(col_v),
        f.atanh(col_v),
        f.cbrt(col_v),
        f.cosh(col_v),
        f.degrees(col_v),
        f.gcd(literal(9), literal(3)),
        f.lcm(literal(6), literal(4)),
        f.nanvl(col_nav, literal(5)),
        f.pi(),
        f.radians(col_v),
        f.sinh(col_v),
        f.tanh(col_v),
        f.factorial(literal(6)),
        f.isnan(col_nav),
        f.iszero(col_nav),
        f.log(literal(3), col_v + literal(pa.scalar(1))),
    )
    batches = df.collect()
    assert len(batches) == 1
    result = batches[0]

    np.testing.assert_array_almost_equal(result.column(0), np.abs(values))
    np.testing.assert_array_almost_equal(result.column(1), np.sin(values))
    np.testing.assert_array_almost_equal(result.column(2), np.cos(values))
    np.testing.assert_array_almost_equal(result.column(3), np.tan(values))
    np.testing.assert_array_almost_equal(result.column(4), np.arcsin(values))
    np.testing.assert_array_almost_equal(result.column(5), np.arccos(values))
    np.testing.assert_array_almost_equal(result.column(6), np.exp(values))
    np.testing.assert_array_almost_equal(result.column(7), np.log(values + 1.0))
    np.testing.assert_array_almost_equal(result.column(8), np.log2(values + 1.0))
    np.testing.assert_array_almost_equal(result.column(9), np.log10(values + 1.0))
    np.testing.assert_array_less(result.column(10), np.ones_like(values))
    np.testing.assert_array_almost_equal(result.column(11), np.arctan(values))
    np.testing.assert_array_almost_equal(result.column(12), np.arctan2(values, 1.1))
    np.testing.assert_array_almost_equal(result.column(13), np.ceil(values))
    np.testing.assert_array_almost_equal(result.column(14), np.floor(values))
    np.testing.assert_array_almost_equal(result.column(15), np.power(values, 3))
    np.testing.assert_array_almost_equal(result.column(16), np.power(values, 4))
    np.testing.assert_array_almost_equal(result.column(17), np.round(values))
    np.testing.assert_array_almost_equal(result.column(18), np.sqrt(values))
    np.testing.assert_array_almost_equal(result.column(19), np.sign(values))
    np.testing.assert_array_almost_equal(result.column(20), np.trunc(values))
    np.testing.assert_array_almost_equal(result.column(21), np.arcsinh(values))
    np.testing.assert_array_almost_equal(result.column(22), np.arccosh(values))
    np.testing.assert_array_almost_equal(result.column(23), np.arctanh(values))
    np.testing.assert_array_almost_equal(result.column(24), np.cbrt(values))
    np.testing.assert_array_almost_equal(result.column(25), np.cosh(values))
    np.testing.assert_array_almost_equal(result.column(26), np.degrees(values))
    np.testing.assert_array_almost_equal(result.column(27), np.gcd(9, 3))
    np.testing.assert_array_almost_equal(result.column(28), np.lcm(6, 4))
    np.testing.assert_array_almost_equal(
        result.column(29), np.where(np.isnan(na_values), 5, na_values)
    )
    np.testing.assert_array_almost_equal(result.column(30), np.pi)
    np.testing.assert_array_almost_equal(result.column(31), np.radians(values))
    np.testing.assert_array_almost_equal(result.column(32), np.sinh(values))
    np.testing.assert_array_almost_equal(result.column(33), np.tanh(values))
    np.testing.assert_array_almost_equal(result.column(34), math.factorial(6))
    np.testing.assert_array_almost_equal(result.column(35), np.isnan(na_values))
    np.testing.assert_array_almost_equal(result.column(36), na_values == 0)
    np.testing.assert_array_almost_equal(
        result.column(37), np.emath.logn(3, values + 1.0)
    )


def test_array_functions():
    data = [[1.0, 2.0, 3.0, 3.0], [4.0, 5.0, 3.0], [6.0]]
    ctx = SessionContext()
    batch = pa.RecordBatch.from_arrays([np.array(data, dtype=object)], names=["arr"])
    df = ctx.create_dataframe([[batch]])

    def py_indexof(arr, v):
        try:
            return arr.index(v) + 1
        except ValueError:
            return np.nan

    def py_arr_remove(arr, v, n=None):
        new_arr = arr[:]
        found = 0
        while found != n:
            try:
                new_arr.remove(v)
                found += 1
            except ValueError:
                break

        return new_arr

    def py_arr_replace(arr, from_, to, n=None):
        new_arr = arr[:]
        found = 0
        while found != n:
            try:
                idx = new_arr.index(from_)
                new_arr[idx] = to
                found += 1
            except ValueError:
                break

        return new_arr

    def py_flatten(arr):
        result = []
        for elem in arr:
            if isinstance(elem, list):
                result.extend(py_flatten(elem))
            else:
                result.append(elem)
        return result

    col = column("arr")
    test_items = [
        [
            f.array_append(col, literal(99.0)),
            lambda: [np.append(arr, 99.0) for arr in data],
        ],
        [
            f.array_push_back(col, literal(99.0)),
            lambda: [np.append(arr, 99.0) for arr in data],
        ],
        [
            f.list_append(col, literal(99.0)),
            lambda: [np.append(arr, 99.0) for arr in data],
        ],
        [
            f.list_push_back(col, literal(99.0)),
            lambda: [np.append(arr, 99.0) for arr in data],
        ],
        [
            f.array_concat(col, col),
            lambda: [np.concatenate([arr, arr]) for arr in data],
        ],
        [
            f.array_cat(col, col),
            lambda: [np.concatenate([arr, arr]) for arr in data],
        ],
        [
            f.array_dims(col),
            lambda: [[len(r)] for r in data],
        ],
        [
            f.list_dims(col),
            lambda: [[len(r)] for r in data],
        ],
        [
            f.array_element(col, literal(1)),
            lambda: [r[0] for r in data],
        ],
        [
            f.array_extract(col, literal(1)),
            lambda: [r[0] for r in data],
        ],
        [
            f.list_element(col, literal(1)),
            lambda: [r[0] for r in data],
        ],
        [
            f.list_extract(col, literal(1)),
            lambda: [r[0] for r in data],
        ],
        [
            f.array_length(col),
            lambda: [len(r) for r in data],
        ],
        [
            f.list_length(col),
            lambda: [len(r) for r in data],
        ],
        [
            f.array_has(col, literal(1.0)),
            lambda: [1.0 in r for r in data],
        ],
        [
            f.array_has_all(col, f.make_array(*[literal(v) for v in [1.0, 3.0, 5.0]])),
            lambda: [np.all([v in r for v in [1.0, 3.0, 5.0]]) for r in data],
        ],
        [
            f.array_has_any(col, f.make_array(*[literal(v) for v in [1.0, 3.0, 5.0]])),
            lambda: [np.any([v in r for v in [1.0, 3.0, 5.0]]) for r in data],
        ],
        [
            f.array_position(col, literal(1.0)),
            lambda: [py_indexof(r, 1.0) for r in data],
        ],
        [
            f.array_indexof(col, literal(1.0)),
            lambda: [py_indexof(r, 1.0) for r in data],
        ],
        [
            f.list_position(col, literal(1.0)),
            lambda: [py_indexof(r, 1.0) for r in data],
        ],
        [
            f.list_indexof(col, literal(1.0)),
            lambda: [py_indexof(r, 1.0) for r in data],
        ],
        [
            f.array_positions(col, literal(1.0)),
            lambda: [[i + 1 for i, _v in enumerate(r) if _v == 1.0] for r in data],
        ],
        [
            f.list_positions(col, literal(1.0)),
            lambda: [[i + 1 for i, _v in enumerate(r) if _v == 1.0] for r in data],
        ],
        [
            f.array_ndims(col),
            lambda: [np.array(r).ndim for r in data],
        ],
        [
            f.list_ndims(col),
            lambda: [np.array(r).ndim for r in data],
        ],
        [
            f.array_prepend(literal(99.0), col),
            lambda: [np.insert(arr, 0, 99.0) for arr in data],
        ],
        [
            f.array_push_front(literal(99.0), col),
            lambda: [np.insert(arr, 0, 99.0) for arr in data],
        ],
        [
            f.list_prepend(literal(99.0), col),
            lambda: [np.insert(arr, 0, 99.0) for arr in data],
        ],
        [
            f.list_push_front(literal(99.0), col),
            lambda: [np.insert(arr, 0, 99.0) for arr in data],
        ],
        [
            f.array_pop_back(col),
            lambda: [arr[:-1] for arr in data],
        ],
        [
            f.array_pop_front(col),
            lambda: [arr[1:] for arr in data],
        ],
        [
            f.array_remove(col, literal(3.0)),
            lambda: [py_arr_remove(arr, 3.0, 1) for arr in data],
        ],
        [
            f.list_remove(col, literal(3.0)),
            lambda: [py_arr_remove(arr, 3.0, 1) for arr in data],
        ],
        [
            f.array_remove_n(col, literal(3.0), literal(2)),
            lambda: [py_arr_remove(arr, 3.0, 2) for arr in data],
        ],
        [
            f.list_remove_n(col, literal(3.0), literal(2)),
            lambda: [py_arr_remove(arr, 3.0, 2) for arr in data],
        ],
        [
            f.array_remove_all(col, literal(3.0)),
            lambda: [py_arr_remove(arr, 3.0) for arr in data],
        ],
        [
            f.list_remove_all(col, literal(3.0)),
            lambda: [py_arr_remove(arr, 3.0) for arr in data],
        ],
        [
            f.array_repeat(col, literal(2)),
            lambda: [[arr] * 2 for arr in data],
        ],
        [
            f.array_replace(col, literal(3.0), literal(4.0)),
            lambda: [py_arr_replace(arr, 3.0, 4.0, 1) for arr in data],
        ],
        [
            f.list_replace(col, literal(3.0), literal(4.0)),
            lambda: [py_arr_replace(arr, 3.0, 4.0, 1) for arr in data],
        ],
        [
            f.array_replace_n(col, literal(3.0), literal(4.0), literal(1)),
            lambda: [py_arr_replace(arr, 3.0, 4.0, 1) for arr in data],
        ],
        [
            f.list_replace_n(col, literal(3.0), literal(4.0), literal(2)),
            lambda: [py_arr_replace(arr, 3.0, 4.0, 2) for arr in data],
        ],
        [
            f.array_replace_all(col, literal(3.0), literal(4.0)),
            lambda: [py_arr_replace(arr, 3.0, 4.0) for arr in data],
        ],
        [
            f.list_replace_all(col, literal(3.0), literal(4.0)),
            lambda: [py_arr_replace(arr, 3.0, 4.0) for arr in data],
        ],
        [
            f.array_slice(col, literal(2), literal(4)),
            lambda: [arr[1:4] for arr in data],
        ],
        [
            f.list_slice(col, literal(-1), literal(2)),
            lambda: [arr[-1:2] for arr in data],
        ],
        [f.flatten(literal(data)), lambda: [py_flatten(data)]],
    ]

    for stmt, py_expr in test_items:
        query_result = df.select(stmt).collect()[0].column(0)
        for a, b in zip(query_result, py_expr()):
            np.testing.assert_array_almost_equal(
                np.array(a.as_py(), dtype=float), np.array(b, dtype=float)
            )

    obj_test_items = [
        [
            f.array_to_string(col, literal(",")),
            lambda: [",".join([str(int(v)) for v in r]) for r in data],
        ],
        [
            f.array_join(col, literal(",")),
            lambda: [",".join([str(int(v)) for v in r]) for r in data],
        ],
        [
            f.list_to_string(col, literal(",")),
            lambda: [",".join([str(int(v)) for v in r]) for r in data],
        ],
        [
            f.list_join(col, literal(",")),
            lambda: [",".join([str(int(v)) for v in r]) for r in data],
        ],
    ]

    for stmt, py_expr in obj_test_items:
        query_result = np.array(df.select(stmt).collect()[0].column(0))
        for a, b in zip(query_result, py_expr()):
            assert a == b


def test_string_functions(df):
    df = df.select(
        f.ascii(column("a")),
        f.bit_length(column("a")),
        f.btrim(literal(" World ")),
        f.character_length(column("a")),
        f.chr(literal(68)),
        f.concat_ws("-", column("a"), literal("test")),
        f.concat(column("a"), literal("?")),
        f.initcap(column("c")),
        f.left(column("a"), literal(3)),
        f.length(column("c")),
        f.lower(column("a")),
        f.lpad(column("a"), literal(7)),
        f.ltrim(column("c")),
        f.md5(column("a")),
        f.octet_length(column("a")),
        f.repeat(column("a"), literal(2)),
        f.replace(column("a"), literal("l"), literal("?")),
        f.reverse(column("a")),
        f.right(column("a"), literal(4)),
        f.rpad(column("a"), literal(8)),
        f.rtrim(column("c")),
        f.split_part(column("a"), literal("l"), literal(1)),
        f.starts_with(column("a"), literal("Wor")),
        f.strpos(column("a"), literal("o")),
        f.substr(column("a"), literal(3)),
        f.translate(column("a"), literal("or"), literal("ld")),
        f.trim(column("c")),
        f.upper(column("c")),
    )
    result = df.collect()
    assert len(result) == 1
    result = result[0]
    assert result.column(0) == pa.array(
        [72, 87, 33], type=pa.int32()
    )  # H = 72; W = 87; ! = 33
    assert result.column(1) == pa.array([40, 40, 8], type=pa.int32())
    assert result.column(2) == pa.array(["World", "World", "World"])
    assert result.column(3) == pa.array([5, 5, 1], type=pa.int32())
    assert result.column(4) == pa.array(["D", "D", "D"])
    assert result.column(5) == pa.array(["Hello-test", "World-test", "!-test"])
    assert result.column(6) == pa.array(["Hello?", "World?", "!?"])
    assert result.column(7) == pa.array(["Hello ", " World ", " !"])
    assert result.column(8) == pa.array(["Hel", "Wor", "!"])
    assert result.column(9) == pa.array([6, 7, 2], type=pa.int32())
    assert result.column(10) == pa.array(["hello", "world", "!"])
    assert result.column(11) == pa.array(["  Hello", "  World", "      !"])
    assert result.column(12) == pa.array(["hello ", "world ", "!"])
    assert result.column(13) == pa.array(
        [
            "8b1a9953c4611296a827abf8c47804d7",
            "f5a7924e621e84c9280a9a27e1bcb7f6",
            "9033e0e305f247c0c3c80d0c7848c8b3",
        ]
    )
    assert result.column(14) == pa.array([5, 5, 1], type=pa.int32())
    assert result.column(15) == pa.array(["HelloHello", "WorldWorld", "!!"])
    assert result.column(16) == pa.array(["He??o", "Wor?d", "!"])
    assert result.column(17) == pa.array(["olleH", "dlroW", "!"])
    assert result.column(18) == pa.array(["ello", "orld", "!"])
    assert result.column(19) == pa.array(["Hello   ", "World   ", "!       "])
    assert result.column(20) == pa.array(["hello", " world", " !"])
    assert result.column(21) == pa.array(["He", "Wor", "!"])
    assert result.column(22) == pa.array([False, True, False])
    assert result.column(23) == pa.array([5, 2, 0], type=pa.int32())
    assert result.column(24) == pa.array(["llo", "rld", ""])
    assert result.column(25) == pa.array(["Helll", "Wldld", "!"])
    assert result.column(26) == pa.array(["hello", "world", "!"])
    assert result.column(27) == pa.array(["HELLO ", " WORLD ", " !"])


def test_hash_functions(df):
    exprs = [
        f.digest(column("a"), literal(m))
        for m in (
            "md5",
            "sha224",
            "sha256",
            "sha384",
            "sha512",
            "blake2s",
            "blake3",
        )
    ]
    df = df.select(
        *exprs,
        f.sha224(column("a")),
        f.sha256(column("a")),
        f.sha384(column("a")),
        f.sha512(column("a")),
    )
    result = df.collect()
    assert len(result) == 1
    result = result[0]
    b = bytearray.fromhex
    assert result.column(0) == pa.array(
        [
            b("8B1A9953C4611296A827ABF8C47804D7"),
            b("F5A7924E621E84C9280A9A27E1BCB7F6"),
            b("9033E0E305F247C0C3C80D0C7848C8B3"),
        ]
    )
    assert result.column(1) == pa.array(
        [
            b("4149DA18AA8BFC2B1E382C6C26556D01A92C261B6436DAD5E3BE3FCC"),
            b("12972632B6D3B6AA52BD6434552F08C1303D56B817119406466E9236"),
            b("6641A7E8278BCD49E476E7ACAE158F4105B2952D22AEB2E0B9A231A0"),
        ]
    )
    assert result.column(2) == pa.array(
        [
            b("185F8DB32271FE25F561A6FC938B2E26" "4306EC304EDA518007D1764826381969"),
            b("78AE647DC5544D227130A0682A51E30B" "C7777FBB6D8A8F17007463A3ECD1D524"),
            b("BB7208BC9B5D7C04F1236A82A0093A5E" "33F40423D5BA8D4266F7092C3BA43B62"),
        ]
    )
    assert result.column(3) == pa.array(
        [
            b(
                "3519FE5AD2C596EFE3E276A6F351B8FC"
                "0B03DB861782490D45F7598EBD0AB5FD"
                "5520ED102F38C4A5EC834E98668035FC"
            ),
            b(
                "ED7CED84875773603AF90402E42C65F3"
                "B48A5E77F84ADC7A19E8F3E8D3101010"
                "22F552AEC70E9E1087B225930C1D260A"
            ),
            b(
                "1D0EC8C84EE9521E21F06774DE232367"
                "B64DE628474CB5B2E372B699A1F55AE3"
                "35CC37193EF823E33324DFD9A70738A6"
            ),
        ]
    )
    assert result.column(4) == pa.array(
        [
            b(
                "3615F80C9D293ED7402687F94B22D58E"
                "529B8CC7916F8FAC7FDDF7FBD5AF4CF7"
                "77D3D795A7A00A16BF7E7F3FB9561EE9"
                "BAAE480DA9FE7A18769E71886B03F315"
            ),
            b(
                "8EA77393A42AB8FA92500FB077A9509C"
                "C32BC95E72712EFA116EDAF2EDFAE34F"
                "BB682EFDD6C5DD13C117E08BD4AAEF71"
                "291D8AACE2F890273081D0677C16DF0F"
            ),
            b(
                "3831A6A6155E509DEE59A7F451EB3532"
                "4D8F8F2DF6E3708894740F98FDEE2388"
                "9F4DE5ADB0C5010DFB555CDA77C8AB5D"
                "C902094C52DE3278F35A75EBC25F093A"
            ),
        ]
    )
    assert result.column(5) == pa.array(
        [
            b("F73A5FBF881F89B814871F46E26AD3FA" "37CB2921C5E8561618639015B3CCBB71"),
            b("B792A0383FB9E7A189EC150686579532" "854E44B71AC394831DAED169BA85CCC5"),
            b("27988A0E51812297C77A433F63523334" "6AEE29A829DCF4F46E0F58F402C6CFCB"),
        ]
    )
    assert result.column(6) == pa.array(
        [
            b("FBC2B0516EE8744D293B980779178A35" "08850FDCFE965985782C39601B65794F"),
            b("BF73D18575A736E4037D45F9E316085B" "86C19BE6363DE6AA789E13DEAACC1C4E"),
            b("C8D11B9F7237E4034ADBCD2005735F9B" "C4C597C75AD89F4492BEC8F77D15F7EB"),
        ]
    )
    assert result.column(7) == result.column(1)  # SHA-224
    assert result.column(8) == result.column(2)  # SHA-256
    assert result.column(9) == result.column(3)  # SHA-384
    assert result.column(10) == result.column(4)  # SHA-512


def test_temporal_functions(df):
    df = df.select(
        f.date_part(literal("month"), column("d")),
        f.datepart(literal("year"), column("d")),
        f.date_trunc(literal("month"), column("d")),
        f.datetrunc(literal("day"), column("d")),
        f.date_bin(
            literal("15 minutes"),
            column("d"),
            literal("2001-01-01 00:02:30"),
        ),
        f.from_unixtime(literal(1673383974)),
        f.to_timestamp(literal("2023-09-07 05:06:14.523952")),
        f.to_timestamp_seconds(literal("2023-09-07 05:06:14.523952")),
        f.to_timestamp_millis(literal("2023-09-07 05:06:14.523952")),
        f.to_timestamp_micros(literal("2023-09-07 05:06:14.523952")),
    )
    result = df.collect()
    assert len(result) == 1
    result = result[0]
    assert result.column(0) == pa.array([12, 6, 7], type=pa.float64())
    assert result.column(1) == pa.array([2022, 2027, 2020], type=pa.float64())
    assert result.column(2) == pa.array(
        [datetime(2022, 12, 1), datetime(2027, 6, 1), datetime(2020, 7, 1)],
        type=pa.timestamp("us"),
    )
    assert result.column(3) == pa.array(
        [datetime(2022, 12, 31), datetime(2027, 6, 26), datetime(2020, 7, 2)],
        type=pa.timestamp("us"),
    )
    assert result.column(4) == pa.array(
        [
            datetime(2022, 12, 30, 23, 47, 30),
            datetime(2027, 6, 25, 23, 47, 30),
            datetime(2020, 7, 1, 23, 47, 30),
        ],
        type=pa.timestamp("ns"),
    )
    assert result.column(5) == pa.array(
        [datetime(2023, 1, 10, 20, 52, 54)] * 3, type=pa.timestamp("s")
    )
    assert result.column(6) == pa.array(
        [datetime(2023, 9, 7, 5, 6, 14, 523952)] * 3, type=pa.timestamp("ns")
    )
    assert result.column(7) == pa.array(
        [datetime(2023, 9, 7, 5, 6, 14)] * 3, type=pa.timestamp("s")
    )
    assert result.column(8) == pa.array(
        [datetime(2023, 9, 7, 5, 6, 14, 523000)] * 3, type=pa.timestamp("ms")
    )
    assert result.column(9) == pa.array(
        [datetime(2023, 9, 7, 5, 6, 14, 523952)] * 3, type=pa.timestamp("us")
    )


def test_case(df):
    df = df.select(
        f.case(column("b")).when(literal(4), literal(10)).otherwise(literal(8)),
        f.case(column("a"))
        .when(literal("Hello"), literal("Hola"))
        .when(literal("World"), literal("Mundo"))
        .otherwise(literal("!!")),
        f.case(column("a"))
        .when(literal("Hello"), literal("Hola"))
        .when(literal("World"), literal("Mundo"))
        .end(),
    )

    result = df.collect()
    result = result[0]
    assert result.column(0) == pa.array([10, 8, 8])
    assert result.column(1) == pa.array(["Hola", "Mundo", "!!"])
    assert result.column(2) == pa.array(["Hola", "Mundo", None])


def test_regr_funcs(df):
    # test case base on
    # https://github.com/apache/arrow-datafusion/blob/d1361d56b9a9e0c165d3d71a8df6795d2a5f51dd/datafusion/core/tests/sqllogictests/test_files/aggregate.slt#L2330
    ctx = SessionContext()
    result = ctx.sql(
        "select regr_slope(1,1), regr_intercept(1,1), "
        "regr_count(1,1), regr_r2(1,1), regr_avgx(1,1), "
        "regr_avgy(1,1), regr_sxx(1,1), regr_syy(1,1), "
        "regr_sxy(1,1);"
    ).collect()

    assert result[0].column(0) == pa.array([None], type=pa.float64())
    assert result[0].column(1) == pa.array([None], type=pa.float64())
    assert result[0].column(2) == pa.array([1], type=pa.float64())
    assert result[0].column(3) == pa.array([None], type=pa.float64())
    assert result[0].column(4) == pa.array([1], type=pa.float64())
    assert result[0].column(5) == pa.array([1], type=pa.float64())
    assert result[0].column(6) == pa.array([0], type=pa.float64())
    assert result[0].column(7) == pa.array([0], type=pa.float64())
    assert result[0].column(8) == pa.array([0], type=pa.float64())


def test_first_last_value(df):
    df = df.aggregate(
        [],
        [
            f.first_value(column("a")),
            f.first_value(column("b")),
            f.first_value(column("d")),
            f.last_value(column("a")),
            f.last_value(column("b")),
            f.last_value(column("d")),
        ],
    )

    result = df.collect()
    result = result[0]
    assert result.column(0) == pa.array(["Hello"])
    assert result.column(1) == pa.array([4])
    assert result.column(2) == pa.array([datetime(2022, 12, 31)])
    assert result.column(3) == pa.array(["!"])
    assert result.column(4) == pa.array([6])
    assert result.column(5) == pa.array([datetime(2020, 7, 2)])


def test_binary_string_functions(df):
    df = df.select(
        f.encode(column("a"), literal("base64")),
        f.decode(f.encode(column("a"), literal("base64")), literal("base64")),
    )
    result = df.collect()
    assert len(result) == 1
    result = result[0]
    assert result.column(0) == pa.array(["SGVsbG8", "V29ybGQ", "IQ"])
    assert pa.array(result.column(1)).cast(pa.string()) == pa.array(
        ["Hello", "World", "!"]
    )
