from __future__ import annotations
import sys

import numpy as np
import suite2p
from suite2p import gui
from natsort import natsorted
import os
import glob
from imaging.io import load_raw_binary, save_raw_binary
from typing import Tuple, List, Union, Optional
from datetime import date, datetime


class Suite2PAnalysis:
    """
    Helper Module for Suite2P Analysis

    **Required Inputs**
        | *ImageDirectory* : Images ImageDirectory
        | *OutputDirectory* : ImageDirectory to save in

    **Keyword Arguments**
        | *meta_file* : file containing binary metadata (str, default None)
        | *meta* : binary metadata (tuple[int, int, int, str], default None)
        | *video* : images (np.ndarray, default None)
        | *file_type* :  video file type (str [tiff or binary], default "tiff")
        | *ops* : Suite2P ops (dict, default None)


    """
    def __init__(self, ImageDirectory: str, OutputDirectory: str, **kwargs: Union[dict, str, Tuple[int]]):
        """
        Instances A Suite2P Analysis

        :param ImageDirectory: directory containing binary metadata
        :type ImageDirectory: str
        :param OutputDirectory: directory to save in
        :type OutputDirectory: str
        :keyword meta_file: file containing binary metadata (str, default None)
        :keyword meta: binary metadata (tuple[int, int, int,str], default None)
        :keyword video: images (np.ndarray, default None)
        :keyword file_type: video file type (str, default None)
        :keyword ops: suite2p ops (dict, default None)
        """

        _meta_file = kwargs.get("meta_file", None)
        _meta = kwargs.get("meta", None)
        _video_file = kwargs.get("video", None)
        self.file_type = kwargs.get("file_type", "tiff")
        self.ops = kwargs.get("ops", None)

        # Initialized
        self.db = {
            'data_path': ImageDirectory,
            'save_path0': OutputDirectory,
            "save_path": "".join([OutputDirectory, "\\suite2p\\plane0"])
        }
        try:
            os.makedirs(self.db.get("save_path"))
        except FileExistsError:
            print("Warning Folder Already Exists and Will be Overwritten")
            pass

        self.iscell = None
        self.stat = None
        self.F = None
        self.Fneu = None
        self.spks = None

        # Protected
        self.__instance_date = get_date()

        # Check Filename Types, only support binary of tiff
        if self.file_type == "tiff" or self.file_type == "tif" or self.file_type == ".tiff" or self.file_type == ".tif":
            self.db = {**self.db, **{"tiff_list": Suite2PAnalysis.make_list_tiffs(ImageDirectory)[0]}}
        elif self.file_type == "binary":
            if _meta is None and _meta_file is None:
                try: # Try to infer the file location
                    _meta = self.load_binary_meta("".join([ImageDirectory, "\\video_meta.txt"]))
                except FileNotFoundError:
                    AssertionError("Using binary is impossible with shape and endianness")
            elif _meta is None and _meta_file is not None:
                _meta = self.load_binary_meta(_meta_file)

            if _video_file is None:
                try: # Try to infer the file location
                    os.path.isfile("".join([ImageDirectory, "\\binary_video"]))
                    _video_file = "".join([ImageDirectory, "\\binary_video"])
                except FileNotFoundError:
                    AssertionError("Unable to locate a valid binary file")

            _db = {
                "input_format": "binary",
                "raw_file": _video_file,
                "Lx": _meta[2],
                "Ly": _meta[1],
                "nframes": _meta[0],
            }
            self.db = {**self.db, **_db}

        # Default Ops
        if self.ops is None:
            self.ops = {**suite2p.default_ops(), **self.my_default_ops()}

        # Final Overwrite
        self.ops = {**self.ops, **self.db}

    @property
    def instance_date(self) -> str:
        return self._Suite2PModule__instance_date

    @property
    def cell_index_path(self) -> str:
        return "".join([self.ops.get('save_path'), "\\iscell.npy"])

    @property
    def stat_file_path(self) -> str:
        return "".join([self.ops.get('save_path'), "\\stat.npy"])

    @property
    def ops_file_path(self) -> str:
        return "".join([self.ops.get("save_path"), "\\ops.npy"])

    @property
    def reg_tiff_path(self) -> str:
        return "".join([self.ops.get('save_path'), "\\reg_tif"])

    @property
    def reg_binary_path(self) -> str:
        return self.ops.get("reg_file")

    def _run(self) -> Self:
        """
        Runs a Full Suite2P Analysis
        Deprecated?

        :return: None
        :rtype: None
        """
        self.ops.update(suite2p.run_s2p(self.ops, self.db))

    def save_stats(self) -> None:
        """
        Saves stat file

        :return: None
        :rtype: None
        """
        np.save(self.stat_file_path, self.stat, allow_pickle=True)

    def save_ops(self) -> None:
        """
        Save ops file

        :return: None
        :rtype: None
        """
        np.save(self.ops_file_path, self.ops, allow_pickle=True)

    def save_cells(self) -> None:
        """
        Saves iscell file

        :return: None
        :rtype: None
        """
        np.save(self.cell_index_path, self.iscell, allow_pickle=True)

    def load_files(self) -> Self:
        """
        Loads S2P iscell, stat, and ops files

        :return: None
        :rtype: None
        """
        self.iscell = np.load(self.cell_index_path, allow_pickle=True)
        self.stat = np.load(self.stat_file_path, allow_pickle=True)
        self.ops = np.load(self.ops_file_path, allow_pickle=True).item()

    def save_files(self) -> None:
        """
        Saves S2P stat, ops, iscell files

        :return: None
        :rtype: None
        """
        self.save_stats()
        self.save_ops()
        self.save_cells()

    def openGUI(self) -> None:
        """
        Opens Suite2P GUI

        :return: None
        :rtype: None
        """
        gui.run(self.stat_file_path)

    def _motionCorrect(self) -> Self:
        """
        DEPRECATED

        :return: None
        :rtype: None
        """
        self.ops['roidetect'] = False
        self.ops['spikedetect'] = False
        self.ops['neuropil_extract'] = False
        self.ops.update(suite2p.run_s2p(self.ops, self.db))

    def motionCorrect(self) -> Self:
        """
        Function simply runs suite2p motion correction
        Note that it assumes you have already converted video to binary

        :return: None
        :rtype: None
        """
        # Ingest ops (parameters)
        self.ops = {**self.ops, **self.db}
        # Set Registered Data Filename
        self.ops["reg_file"] = "".join([self.ops.get("save_path0"), "\\suite2p\\plane0\\registered_data.bin"])
        # Read in raw tif corresponding to our example tif
        f_raw = suite2p.io.BinaryRWFile(Ly=self.ops.get("Ly"), Lx=self.ops.get("Lx"), filename=self.ops.get("raw_file"))
        f_reg = suite2p.io.BinaryRWFile(Ly=self.ops.get("Ly"), Lx=self.ops.get("Lx"), filename=self.ops.get("reg_file"))

        refImg, rmin, rmax, meanImg, rigid_offsets, \
        nonrigid_offsets, zest, meanImg_chan2, badframes, \
        yrange, xrange = suite2p.registration_wrapper(f_reg, f_raw=f_raw, f_reg_chan2=None,
                                                      f_raw_chan2=None, refImg=None,
                                                      align_by_chan2=False, ops=self.ops)
        self.ops = {**self.ops,
                        **{
                            "refImg": refImg,
                            "rmin": rmin,
                            "rmax": rmax,
                            "meanImg": meanImg,
                            "rigid_offsets": rigid_offsets,
                            "nonrigid_offsets": nonrigid_offsets,
                            "zest": zest,
                            "meanImg_chan2": meanImg_chan2,
                            "badframes": badframes,
                            "yrange": yrange,
                            "xrange": xrange,
                        }
                    }

    def roiDetection(self) -> Self:
        """
        Runs Suite2P ROI Detection

        :return: None
        :rtype: None
        """
        self.ops = {**self.ops, **self.db}

        try:
            if not isinstance(self.ops.get("reg_file"), str):
                self.ops["reg_file"] = "".join([self.ops.get("data_path"), "\\binary_video"])
        except KeyError:
            self.ops["reg_file"] = "".join([self.ops.get("data_path"), "\\binary_video"])
        # This was not elegant, but it does work

        try:
            _video_meta = self.load_binary_meta("".join([self.ops.get("data_path"), "\\video_meta.txt"]))
            if _video_meta[-1] != "int16":
                _binary_video = load_raw_binary("", "", self.ops.get("data_path"))
                _binary_video = self.convert_binary(_binary_video)
                _new_data_path = "".join([self.ops.get("data_path"), "\\converted"])
                self.ops["data_path"] = _new_data_path
                self.db["data_path"] = _new_data_path
                self.ops["reg_file"] = "".join([self.ops.get("data_path"), "\\binary_video"])
                # Db overwrites, this to prevent using converted some places and not others
                os.makedirs(_new_data_path, exist_ok=True)
                save_raw_binary(_binary_video, _new_data_path)
                del _binary_video
                del _video_meta
                # collect garbage

        except FileNotFoundError:
            print("Could not find meta file. Proceeding anyway...")
        # This was not elegant, but it does work

        f_reg = suite2p.io.BinaryRWFile(Ly=self.ops.get("Ly"), Lx=self.ops.get("Lx"),
                                        filename=self.ops.get("reg_file"))

        self.ops, self.stat = suite2p.detection_wrapper(f_reg=f_reg, ops=self.ops,
                                                        classfile=suite2p.classification.builtin_classfile)

    def extractTraces(self, *args: Optional[Union[np.ndarray, str]]) -> Self:
        """
        Extracts Traces

        :param args: Registration Binary np.ndarray or filepath
        :return: None
        :rtype: None
        """


        if len(args) == 0:
            f_reg = suite2p.io.BinaryRWFile(Ly=self.ops.get("Ly"), Lx=self.ops.get("Lx"),
                                            filename=self.ops.get("reg_file"))
        else:
            f_reg = args[0]

        self.stat, self.F, self.Fneu, _, _ = suite2p.extraction_wrapper(self.stat, f_reg, f_reg_chan2=None, ops=self.ops)

        # Save F, Fneu
        np.save("".join([self.ops.get("save_path"), "\\F.npy"]), self.F, allow_pickle=True)
        np.save("".join([self.ops.get("save_path"), "\\Fneu.npy"]), self.Fneu, allow_pickle=True)

    def classifyROIs(self) -> Self:
        """
        Classify ROIs

        :return: None
        :rtype: None
        """

        self.iscell = suite2p.classify(stat=self.stat, classfile=suite2p.classification.builtin_classfile)

    def spikeExtraction(self) -> Self:
        """
        Suite2P Spike Extraction by OASIS... Necessary for GUI

        :return: None
        :rtype: None
        """
        dF = self.F.copy() - self.ops["neucoeff"]*self.Fneu
        # Apply preprocessing step for deconvolution
        dF = suite2p.extraction.preprocess(
            F=dF,
            baseline=self.ops['baseline'],
            win_baseline=self.ops['win_baseline'],
            sig_baseline=self.ops['sig_baseline'],
            fs=self.ops['fs'],
            prctile_baseline=self.ops['prctile_baseline']
        )
        # Identify spikes
        self.spks = suite2p.extraction.oasis(F=dF, batch_size=self.ops['batch_size'], tau=self.ops['tau'],
                                             fs=self.ops['fs'])
        np.save("".join([self.ops.get("save_path"), "\\spks.npy"]), self.spks, allow_pickle=True)

    def integrateMotionCorrectionDenoising(self) -> Self:
        """
        Computes reference and mean images, adds x & y ranges using denoised image
        without motion correcting

        :rtype: Any
        """
        _images = load_raw_binary("", "", self.ops.get("data_path"))
        # shape
        _num_frames, self.ops["yrange"], self.ops["xrange"] = _images.shape
        self.ops["yrange"] = [0, self.ops.get("yrange")]
        self.ops["xrange"] = [0, self.ops.get("xrange")]
        # references
        _frames = _images[
            np.linspace(0, _num_frames, 1 + np.minimum(self.ops['nimg_init'], _num_frames), dtype=int)[:-1]]
        self.ops["refImgO"] = suite2p.registration.register.compute_reference(_frames, self.ops)
        self.ops["refImg"], self.ops["rmin"], self.ops["rmax"] = \
            suite2p.registration.register.normalize_reference_image(self.ops.get("refImgO"))
        # mean
        _mean_img = np.zeros((self.ops.get("yrange")[-1], self.ops.get("xrange")[-1]), dtype='float32')
        _batch_size = self.ops.get("batch_size")
        for k in np.arange(0, _num_frames, _batch_size):
            frames = _images[k: min(k + _batch_size, _num_frames)].astype('float32')
            _mean_img += frames.sum(axis=0) / _num_frames
        self.ops["meanImg"] = _mean_img
        # Enhanced Mean
        self.ops = suite2p.registration.register.enhanced_mean_image(self.ops)

    @classmethod
    def exportCroppedCorrection(cls, Ops: dict) -> sys.stdout:
        """
        Export Binary Filename Cropped According to Motion Correction

        :param Ops: Suite2P "ops"
        :type Ops: dict
        :return: None
        """
        _xrange = Ops.get("xrange")
        _yrange = Ops.get("yrange")
        _images = cls.load_suite2p_binary(Ops.get("reg_file"))
        _images = np.reshape(_images, (-1, Ops.get("Ly"), Ops.get("Lx")))
        _images = _images[:, _yrange[0]:_yrange[-1], _xrange[0]:_xrange[-1]]
        save_raw_binary(_images, Ops.get("save_path"))
        return print("Exported Cropped Motion-Corrected Images")

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def replaceTraces(self, NewTraces: Any) -> sys.stdout:
        return print("Not Yet Implemented")

    @staticmethod
    def remove_small_neurons(Cells: np.ndarray, Stats: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Remove small diameter neurons

        :param Cells: Suite2P "iscell"
        :type Cells: Any
        :param Stats: Suite2P "stat"
        :type Stats: Any
        :return: modified cells, stats
        :rtype: Any
        """
        _num_rois = Stats.shape[0]
        diameters = Suite2PAnalysis.find_diameters(Stats)

        _rem_idx = np.where(diameters < 10)[0]
        Cells[_rem_idx, 0] = 0
        for _roi in range(_num_rois):
            Stats[_roi]['diameter'] = diameters[_roi]
        return Cells, Stats

    @staticmethod
    def make_list_tiffs(ImageDirectory: str) -> Tuple[List[str], np.ndarray]:
        """
        Returns a list of tiffs in directory

        :param ImageDirectory: Directory Path
        :type ImageDirectory: str
        :return: files, first_tiffs
        :rtype: Any
        """

        _pathPlusExt = os.path.join(ImageDirectory, "*.tif")
        files = []
        files.extend(glob.glob(_pathPlusExt))
        files = natsorted(set(files))
        if len(files) > 0:
            first_tiffs = np.zeros((len(files),), np.bool)
            first_tiffs[0] = True
        else:
            first_tiffs = np.zeros(0, np.bool)

        return files, first_tiffs

    @staticmethod
    def find_diameters(Stats: np.ndarray[np.ndarray]) -> np.ndarray:
        """
        Return roi diameters

        :param Stats: Suite2P "stats"
        :type Stats: Any
        :return: roi diameters
        :rtype: Any
        """
        _num_rois = Stats.shape[0]
        diameters = np.zeros(_num_rois)
        for _roi in range(_num_rois):
            diameters[_roi] = Stats[_roi].get('radius') * 2
        return diameters


    @staticmethod
    def load_binary_meta(Filename: str) -> Tuple[int, int, int, str]:
        """
        Loads meta file for binary video

        :param Filename: The meta file (.txt ext)
        :type Filename: str
        :return: A tuple containing the number of frames, y pixels, and x pixels
        :rtype: tuple[int, int, int, str]
        """
        _num_frames, _y_pixels, _x_pixels, _type = np.genfromtxt(Filename, delimiter=",", dtype="str")
        return int(_num_frames), int(_y_pixels), int(_x_pixels), _type

    @staticmethod
    def my_default_ops() -> dict:
        """
        Returns default ops settings

        :return:  ops
        :rtype: dict
        """
        ops = {
                'fs': 10,
                'keep_movie_raw': True,
                'nimg_init': 1000,
                'batch_size': 7000,
                'reg_tif': True,
                'nonrigid': False,
                'denoise': True,
                'anatomical_only': True,
                'diameter': 14,
                'tau': 1.5,
                'spikedetect': True,
                'neuropil_extract': True,
                'roidetect': True,
            }
        return ops

    @staticmethod
    def load_suite2p_binary(Filename: str) -> np.ndarray:
        """
        Loads suite2p binary file

        :param Filename: Filename path
        :type Filename: str
        :return: np.ndarray containing images data [Z x Y x X] [int16]
        """
        return np.fromfile(Filename, dtype=np.int16)

    @staticmethod
    def convert_binary(Images: np.ndarray) -> np.ndarray:
        """
        Converts binary to match the form of suite2p binaries

        :param Images: Numpy array containing binary video [Z x Y x X]
        :type Images: Any
        :return: Binary Images Numpy Array [Int 16]
        :rtype: Any
        """

        if Images.dtype.type == np.uint16:
            return (Images // 2).astype(np.int16)
        elif Images.dtype.type == np.int16 or Images.dtype.type == int16:
            print("No conversion was necessary!!!")
            return Images
        else:
            return Images.astype(np.int16)


def get_date():
    return date.isoformat(date.today())


def get_time():
    return datetime.now().strftime("%H:%M:%S")