# Copyright 2021 AlQuraishi Laboratory
# Copyright 2021 DeepMind Technologies Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import torch.nn as nn
from Model.primitives import Linear


class PerResidueLDDTCaPredictor(nn.Module):
    def __init__(self, no_bins=50, c_in=384, c_hidden=128):
        super(PerResidueLDDTCaPredictor, self).__init__()

        self.no_bins = no_bins
        self.c_in = c_in
        self.c_hidden = c_hidden

        self.layer_norm = nn.LayerNorm(self.c_in)

        self.linear_1 = Linear(self.c_in, self.c_hidden, init="relu")
        self.linear_2 = Linear(self.c_hidden, self.c_hidden, init="relu")
        self.linear_3 = Linear(self.c_hidden, self.no_bins, init="final")

        self.relu = nn.ReLU()

    def forward(self, s):
        s = self.layer_norm(s)
        s = self.linear_1(s)
        s = self.relu(s)
        s = self.linear_2(s)
        s = self.relu(s)
        s = self.linear_3(s)

        return s

class ExperimentallyResolvedHead(nn.Module):
    """
    For use in computation of "experimentally resolved" loss, subsection
    1.9.10
    """

    def __init__(self, c_s=384, c_out=37, **kwargs):
        """
        Args:
            c_s:
                Input channel dimension
            c_out:
                Number of distogram bins
        """
        super(ExperimentallyResolvedHead, self).__init__()

        self.c_s = c_s
        self.c_out = c_out

        self.linear = Linear(self.c_s, self.c_out, init="final")

    def forward(self, s):
        """
        Args:
            s:
                [*, N_res, C_s] single embedding
        Returns:
            [*, N, C_out] logits
        """
        # [*, N, C_out]
        logits = self.linear(s)
        return logits