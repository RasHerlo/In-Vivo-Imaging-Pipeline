from __future__ import annotations

import importlib

import json_tricks
from typing import Union, Tuple, List, Optional
import os
from collections import OrderedDict
from datetime import date, datetime
import pickle as pkl
import numpy as np
import pandas as pd
from IPython import get_ipython
import pathlib
from tqdm import tqdm
from shutil import copytree
from Imaging.IO import save_raw_binary, determine_bruker_folder_contents, repackage_bruker_tiffs, \
    pretty_print_bruker_command, load_all_tiffs
from MigrationTools.Converters import renamed_load
from Management.UserInterfaces import select_directory, verbose_copying, validate_string, validate_path_string, \
    select_file, validate_config_format
from Imaging.BrukerMetaModule import BrukerMeta
from itertools import product
from Imaging.ToolWrappers.Suite2PModule import Suite2PAnalysis
from Management.Wrapping import read_wrapper

_channels, _planes = determine_bruker_folder_contents(
    IM.folder_dictionary.get("raw_imaging_data").path)[0:2]
_combos = [range(_channels), range(_planes)]

_string_of_combo = "".join(["_channel_", str(_combo[0]), "_plane_", str(_combo[1])])
IM.add_image_analysis_folder(str(FrameRate), _string_of_combo)