# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

import unittest

import torch
from executorch.backends.xnnpack.test.tester import Tester


class TestPermute(unittest.TestCase):
    class Permute(torch.nn.Module):
        def __init__(self, dims):
            self.dims = dims
            super().__init__()

        def forward(self, x):
            return torch.permute(x, self.dims)

    def test_fp32_permute(self):
        inputs = (torch.randn(1, 1, 4, 4),)
        (
            Tester(self.Permute([0, 2, 3, 1]), inputs)
            .export()
            .check_count({"torch.ops.aten.permute.default": 1})
            .to_edge()
            .check_count(
                {"executorch_exir_dialects_edge__ops_aten_permute_copy_default": 1}
            )
            .partition()
            .check_count({"torch.ops.higher_order.executorch_call_delegate": 1})
            .check_not(["executorch_exir_dialects_edge__ops_aten_permute_copy_default"])
            .to_executorch()
            .serialize()
            .run_method()
            .compare_outputs()
        )
