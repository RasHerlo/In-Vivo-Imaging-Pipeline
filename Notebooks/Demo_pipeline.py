from __future__ import annotations
from typing import Tuple, Union, Callable
import Management.Organization
from Management.Wrapping import read_wrapper, wrapped_process
from Imaging.ToolWrappers.Suite2PModule import Suite2PAnalysis
from Imaging.ToolWrappers.FissaModule import FissaAnalysis
from Imaging.ToolWrappers.CascadeModule import CascadeAnalysis
from Imaging.IO import load_all_tiffs, save_raw_binary, repackage_bruker_tiffs
import numpy as np


def pipeline(Obj, FrameRate, Combo, Name, Config):

    # 0. Compile
    repackage_bruker_tiffs(Obj.folder_dictionary.get("raw_imaging_data").path,
                           Obj.folder_dictionary.get(Name).folders.get("compiled"),
                           Combo)

    # 1. Pre-Process
    _images = load_all_tiffs(Obj.folder_dictionary.get(Name).folders.get("compiled"))
    # _images = wrapped_process(_images, *read_wrapper(Config.get("preprocess")).interface())
    save_raw_binary(_images, Obj.folder_dictionary.get(Name).folders.get("compiled"))
    _frames, _y, _x = _images.shape  # (Any cropping should ALWAYS be taken from the front of the dataset)
    _images = None

    # 1. Motion-Correct
    _s2p = Suite2PAnalysis(Obj.folder_dictionary.get(Name).folders.get("compiled"),
                           Obj.folder_dictionary.get(Name).path, file_type="binary")
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
    #traces = wrapped_process(_traces, *read_wrapper(Config.get("postprocess")).interface())
    _fissa.ProcessedTraces.detrended_merged_dFoF_result, = _traces
    _fissa.saveProcessedTraces()

    # Spike Probability
    _cascade = CascadeAnalysis(_fissa.ProcessedTraces.detrended_merged_dFoF_result, FrameRate,
                               model_folder="C:\\ProgramData\\Anaconda3\\envs\\Calcium-Imaging-Analysis-Pipeline\\Pretrained_models",
                               SavePath=Obj.folder_dictionary.get(Name).folders.get("cascade"))
    _cascade.model_name = "Global_EXC_10Hz_smoothing100ms"
    _cascade.predictSpikeProb()
    _cascade.ProcessedInferences.firing_rates = Processing.calculateFiringRate(_cascade.spike_prob, _cascade.frame_rate)
    _cascade.saveSpikeProb(_cascade.save_path)
    _cascade.saveProcessedInferences(_cascade.save_path)

    # Discrete Spike Inference
    _cascade.inferDiscreteSpikes()
    _cascade.saveSpikeInference(_cascade.output_folder)
    return
