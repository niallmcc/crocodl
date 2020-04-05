# Copyright 2020 Niall McCarroll
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import h5py
import json

def add_metadata(path,metadata):
	f = h5py.File(path, "r+")
	dt = h5py.string_dtype()
	dset = f.create_dataset("simpledl",shape=(0,),dtype=dt)
	dset.attrs["json"] = json.dumps(metadata)
	f.close()

def read_metadata(path):
	f = h5py.File(path, "r")
	dset = f["simpledl"]
	s = dset.attrs["json"]
	return json.loads(s)
