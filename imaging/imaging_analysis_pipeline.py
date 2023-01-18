from __future__ import annotations
from typing import Tuple, Union, Callable
import mose_framework.organization
from mose_framework.wrapping import read_wrapper, wrapped_process
from imaging.tool_wrappers.Suite2PModule import Suite2PAnalysis
from imaging.tool_wrappers.FissaModule import FissaAnalysis
from imaging.tool_wrappers.CascadeModule import CascadeAnalysis
from imaging.io import load_all_tiffs, save_raw_binary, repackage_bruker_tiffs
from imaging.image_processing import remove_shutter_artifact
from imaging.signal_processing import calculateFiringRate
from imaging.utilities import mergeTraces
import numpy as np
import json_tricks
import os


def pipeline(Obj, FrameRate, Combo, Name, Config):


    # 0. Compile
    repackage_bruker_tiffs(Obj.folder_dictionary.get("raw_imaging_data").path,
                           Obj.folder_dictionary.get(Name).folders.get("compiled"),
                           Combo)


    # 1. Pre-Process
    _images = load_all_tiffs(Obj.folder_dictionary.get(Name).folders.get("compiled"))
    # _images = wrapped_process(_images, *read_wrapper(Config.get("preprocess")).interface())
    # _images = remove_shutter_artifact(_images)
    save_raw_binary(_images, Obj.folder_dictionary.get(Name).folders.get("compiled"))
    Obj.folder_dictionary.get(Name).clean_up_compilation()
    _frames, _y, _x = _images.shape  # (Any cropping should ALWAYS be taken from the front of the dataset)
    _images = None

    # 1. Motion-Correct
    _ops_file = Config.get("suite2p")
    with open(_ops_file, "r") as f:
        _config_ops = json_tricks.loads(f.read())
    f.close()
    _config_ops = dict(_config_ops)

    _s2p = Suite2PAnalysis(Obj.folder_dictionary.get(Name).folders.get("compiled"),
                           Obj.folder_dictionary.get(Name).path, file_type="binary",
                           ops=_config_ops)
    _s2p.motionCorrect()

    # 2. Denoise
    Obj.folder_dictionary.get(Name).export_registration_to_denoised(_frames, _y, _x)

    # 3. ROI-Detection
    _s2p.ops["meanImg_chan2"] = np.array([0])  # Don't question, needed for now
    _s2p.ops.pop("meanImg_chan2")  # Don't question, needed for now
    _s2p.db = _s2p.ops  # Don't question, needed for now
    _s2p.roiDetection()
    _s2p.extractTraces()
    _s2p.classifyROIs()
    _s2p.spikeExtraction()
    _s2p.save_files()
    Obj.update_folder_dictionary()

    # Trace-Extraction
    _fissa = FissaAnalysis(data_folder=Obj.folder_dictionary.get(Name).path,
                           video_folder=Obj.folder_dictionary.get(Name).folders.get("denoised"),
                           output_folder=Obj.folder_dictionary.get(Name).folders.get("fissa"),
                           frame_rate=FrameRate)
    _fissa.initializeFissa()
    _fissa.extractTraces()
    _fissa.saveFissaPrep()

    # Source-Separation
    _fissa.separateTraces()  # simple, call to separate the traces
    _fissa.saveFissaSep()

    # Post-Processing
    _traces = _fissa.experiment.result,
    # traces = wrapped_process(_traces, *read_wrapper(Config.get("postprocess")).interface())
    _fissa.ProcessedTraces.detrended_merged_dFoF_result = mergeTraces(_traces)
    _fissa.saveProcessedTraces()

    # Spike Probability
    _cascade = CascadeAnalysis(_fissa.ProcessedTraces.detrended_merged_dFoF_result, FrameRate,
                               model_folder="Pretrained_models",
                               SavePath=Obj.folder_dictionary.get(Name).folders.get("cascade"))
    _cascade.model_name = "Global_EXC_10Hz_smoothing100ms"
    _cascade.predictSpikeProb()
    _cascade.ProcessedInferences.firing_rates = calculateFiringRate(_cascade.spike_prob, _cascade.frame_rate)
    _cascade.saveSpikeProb(_cascade.save_path)
    _cascade.saveProcessedInferences(_cascade.save_path)

    # Discrete Spike Inference
    _cascade.inferDiscreteSpikes()
    _cascade.saveSpikeInference(_cascade.output_folder)
    return
