from __future__ import annotations
from typing import Optional
import json_tricks
import os
from mose_framework.user_interfaces import validate_path_string, validate_string


def default_config() -> dict:
    """
    Generates a default configuration


    :return: Dictionary containing configuration parameters
    """

    return {
        "cascade": None,
        "deepcad": None,
        "fissa": None,
        "pipeline": "imaging.imaging_analysis_pipeline",
        "preprocess": None,
        "postprocess": None,
        "suite2p": "imaging\\suite2p_config.json"
    }


def write_config(Config: dict, Filename: Optional[str] = None, Path: Optional[str] = None) -> None:
    """
    Writes a default configuration

    :param Config: configuration dictionary
    :type Config: dict
    :param Filename: Filename for saved .json
    :type Filename: str
    :param Path: Path to save file in
    :type Path: str
    :return:
    """
    if Filename is None:
        Filename = "config.json"

    # Validate user input
    if not validate_string(Filename):
        ValueError("Please use only standard ascii letters and digits")
    if not validate_path_string(Filename):
        ValueError("Please use only standard ascii letters and digits")
    if ".json" not in Filename:
        Filename = "".join([Filename, ".json"])
    if Path is not None:
        Filename = "".join([Path, "\\", Filename])
    else:
        Filename = "".join([os.getcwd(), "\\", Filename])

    with open(Filename, "w") as _file:
        _file.write(json_tricks.dumps(Config, indent=0))

    print("Saved configuration to file.")


def default_suite2p() -> dict:
    """
    This is the default
    """
    return {
        # file input/output settings
        'look_one_level_down': False,  # whether to look in all subfolders when searching for tiffs
        'save_path0': [],  # stores results, defaults to first item in data_path
        'save_folder': [],
        'subfolders': [],
        'move_bin': False,  # if 1, and fast_disk is different than save_disk, binary file is moved to save_disk

        # main settings
        'nplanes': 1,  # each tiff has these many planes in sequence
        'nchannels': 1,  # each tiff has these many channels per plane
        'functional_chan': 1,  # this channel is used to extract functional ROIs (1-based)
        'tau': 1.,  # this is the main parameter for deconvolution
        'fs': 10.,  # sampling rate (PER PLANE e.g. for 12 plane recordings it will be around 2.5)
        'force_sktiff': False,  # whether or not to use scikit-image for tiff reading
        'frames_include': -1,
        'multiplane_parallel': False,  # whether or not to run on server
        'ignore_flyback': [],

        # output settings
        'preclassify': 0.,  # apply classifier before signal extraction with probability 0.3
        'save_mat': False,  # whether to save output as matlab files
        'save_NWB': False,  # whether to save output as NWB file
        'combined': True,  # combine multiple planes into a single result /single canvas for GUI
        'aspect': 1.0,  # um/pixels in X / um/pixels in Y (for correct aspect ratio in GUI)

        # bidirectional phase offset
        'do_bidiphase': False,
        'bidiphase': 0,
        'bidi_corrected': False,

        # registration settings
        'do_registration': 1,  # whether to register data (2 forces re-registration)
        'two_step_registration': False,
        'keep_movie_raw': False,
        'nimg_init': 300,  # subsampled frames for finding reference image
        'batch_size': 500,  # number of frames per batch
        'maxregshift': 0.1,  # max allowed registration shift, as a fraction of frame max(width and height)
        'align_by_chan': 1,  # when multi-channel, you can align by non-functional channel (1-based)
        'reg_tif': False,  # whether to save registered tiffs
        'reg_tif_chan2': False,  # whether to save channel 2 registered tiffs
        'subpixel': 10,  # precision of subpixel registration (1/subpixel steps)
        'smooth_sigma_time': 0,  # gaussian smoothing in time
        'smooth_sigma': 1.15,  # ~1 good for 2P recordings, recommend 3-5 for 1P recordings
        'th_badframes': 1.0,
        # this parameter determines which frames to exclude when determining cropping - set it smaller to exclude more frames
        'norm_frames': True,  # normalize frames when detecting shifts
        'force_refImg': False,  # if True, use refImg stored in ops if available
        'pad_fft': False,

        # non rigid registration settings
        'nonrigid': True,  # whether to use nonrigid registration
        'block_size': [128, 128],  # block size to register (** keep this a multiple of 2 **)
        'snr_thresh': 1.2,
        # if any nonrigid block is below this threshold, it gets smoothed until above this threshold. 1.0 results in no smoothing
        'maxregshiftNR': 5,  # maximum pixel shift allowed for nonrigid, relative to rigid

        # 1P settings
        '1Preg': False,  # whether to perform high-pass filtering and tapering
        'spatial_hp': 42,  # window for spatial high-pass filtering before registration
        'spatial_hp_reg': 42,  # window for spatial high-pass filtering before registration
        'pre_smooth': 0,  # whether to smooth before high-pass filtering before registration
        'spatial_taper': 40,
        # how much to ignore on edges (important for vignetted windows, for FFT padding do not set BELOW 3*ops['smooth_sigma'])

        # cell detection settings with suite2p
        'roidetect': True,  # whether or not to run ROI extraction
        'spikedetect': True,  # whether or not to run spike deconvolution
        'sparse_mode': True,  # whether or not to run sparse_mode
        'spatial_scale': 0,  # 0: multi-scale; 1: 6 pixels, 2: 12 pixels, 3: 24 pixels, 4: 48 pixels
        'connected': True,  # whether or not to keep ROIs fully connected (set to 0 for dendrites)
        'nbinned': 5000,  # max number of binned frames for cell detection
        'max_iterations': 20,  # maximum number of iterations to do cell detection
        'threshold_scaling': 1.0,  # adjust the automatically determined threshold by this scalar multiplier
        'max_overlap': 0.75,  # cells with more overlap than this get removed during triage, before refinement
        'high_pass': 100,  # running mean subtraction with window of size 'high_pass' (use low values for 1P)
        'spatial_hp_detect': 25,  # window for spatial high-pass filtering for neuropil subtraction before detection
        'denoise': False,  # denoise binned movie for cell detection in sparse_mode

        # cell detection settings with cellpose (used if anatomical_only > 0)
        'anatomical_only': 0,
        # run cellpose to get masks on 1: max_proj / mean_img; 2: mean_img; 3: mean_img enhanced, 4: max_proj
        'diameter': 0,  # use diameter for cellpose, if 0 estimate diameter
        'cellprob_threshold': 0.0,  # cellprob_threshold for cellpose
        'flow_threshold': 1.5,  # flow_threshold for cellpose
        'spatial_hp_cp': 0,  # high-pass image spatially by a multiple of the diameter
        'pretrained_model': 'cyto',  # path to pretrained model or model type string in Cellpose (can be user model)

        # classification parameters
        'soma_crop': True,  # crop dendrites for cell classification stats like compactness
        # ROI extraction parameters
        'neuropil_extract': True,  # whether or not to extract neuropil; if False, Fneu is set to zero
        'inner_neuropil_radius': 2,  # number of pixels to keep between ROI and neuropil donut
        'min_neuropil_pixels': 350,  # minimum number of pixels in the neuropil
        'lam_percentile': 50.,
        # percentile of lambda within area to ignore when excluding cell pixels for neuropil extraction
        'allow_overlap': False,  # pixels that are overlapping are thrown out (False) or added to both ROIs (True)
        'use_builtin_classifier': False,  # whether or not to use built-in classifier for cell detection (overrides
        # classifier specified in classifier_path if set to True)
        'classifier_path': 0,  # path to classifier

        # channel 2 detection settings (stat[n]['chan2'], stat[n]['not_chan2'])
        'chan2_thres': 0.65,  # minimum for detection of brightness on channel 2

        # deconvolution settings
        'baseline': 'maximin',  # baselining mode (can also choose 'prctile')
        'win_baseline': 60.,  # window for maximin
        'sig_baseline': 10.,  # smoothing constant for gaussian filter
        'prctile_baseline': 8.,  # optional (whether to use a percentile baseline)
        'neucoeff': .7,  # neuropil coefficient
    }
