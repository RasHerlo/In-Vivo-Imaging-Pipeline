import os
from datetime import date, datetime
import pickle as pkl
import numpy as np
import pandas as pd
from IPython import get_ipython
import pathlib

import ExperimentManagement.BrukerMetaModule
from ExperimentManagement.BrukerMetaModule import BrukerMeta
from MigrationTools.Converters import renamed_load
import math

# yo some dis ugly


class ExperimentData:
    """
    Class for Organizing & Managing Experimental Data Across Sessions

    **Class Methods**
        | **loadHierarchy** : Function that loads the entire experimental hierarchy
    """

    def __init__(self, **kwargs):
        # Hidden
        self._mouse_id_assigned = False # to make sure mouse id only set once
        self._log_file_assigned = False # to make sure log file only set once
        self._experimental_condition_assigned = False # to make set condition only once
        # Protected In Practice
        self._log_file = kwargs.get('LogFile', None)
        self._mouse_id = kwargs.get('Mouse', None)
        self._experimental_condition = kwargs.get('Condition', None)
        self.__instance_date = self.getDate()
        #
        self.directory = kwargs.get('Directory', None)
        self.study = kwargs.get('Study', None)
        self.study_mouse = kwargs.get('StudyMouse', None)
        self.modifications = [(self.getDate(), self.getTime())]
        self.stages = []

        # Create log file if one does not exist
        if self._log_file_assigned is False and self.directory is not None:
            self.log_file = self.directory + "\\log_file.log"
            print("Logging file assigned as :" + self.log_file)

        # start logging if log file exists
        if self._log_file_assigned:
            self.startLog()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.endLog()

    @property
    def experimental_condition(self):
        """
        Experiment condition of the mouse

        :rtype: str
        """
        return self._experimental_condition

    @experimental_condition.setter
    def experimental_condition(self, Condition):
        if self._experimental_condition_assigned is False:
            self._experimental_condition = Condition
            self._experimental_condition_assigned = True
        else:
            print("Experimental condition can only be assigned ONCE.")

    @property
    def log_file(self):
        return self._log_file

    @log_file.setter
    def log_file(self, LogFile):
        if self._log_file_assigned is False:
            self._log_file = LogFile
            self._log_file_assigned = True
        else:
            print("Log file can only be assigned ONCE.")

    @property
    def mouse_id(self):
        return self._mouse_id

    @mouse_id.setter
    def mouse_id(self, ID):
        if self._mouse_id_assigned is False:
            self._mouse_id = ID
            self._mouse_id_assigned = True
        else:
            print("Mouse ID can only be set ONCE.")

    @property
    def instance_date(self):
        return self._ExperimentData__instance_date

    @classmethod
    def loadHierarchy(cls, ExperimentDirectory):
        """
        Function that loads the entire experimental hierarchy

        :param ExperimentDirectory: Directory containing the experimental hierarchy pickle file
        :type ExperimentDirectory: str
        :return: ExperimentData
        :rtype: ExperimentManagement.ExperimentHierarchy.ExperimentData
        """
        print("Loading Experimental Hierarchy...")
        _input_file = ExperimentDirectory + "\\ExperimentalHierarchy"
        _input_pickle = open(_input_file, 'rb')
        _pickles = pkl.load(_input_pickle)
        _keys = _pickles.keys()
        MouseData = ExperimentData()
        for _key in _keys:
            MouseData.__dict__.update(_pickles)
        print("Finished.")

        if MouseData._log_file_assigned:
            MouseData.startLog()
        return MouseData

    @classmethod
    def getDate(cls):
        return date.isoformat(date.today())

    @classmethod
    def getTime(cls):
        return datetime.now().strftime("%H:%M:%S")

    @classmethod
    def checkPath(cls, Path):
        return os.path.exists(Path)

    @classmethod
    def generateDirectoryHierarchy(cls, MouseDirectory, **kwargs):
        _gen_histology = kwargs.get('Histology', True)
        _gen_roi_matching_index = kwargs.get('ROIMatchingIndex', True)
        _gen_stage = kwargs.get('Stage', True)
        _gen_lab_notebook = kwargs.get('LabNotebook', True)

        if _gen_histology:
            cls.generateHistology(MouseDirectory)
        if _gen_roi_matching_index:
            cls.generateROIMatchingIndex(MouseDirectory)
        if _gen_stage:
            cls.generateStage(MouseDirectory)
        if _gen_lab_notebook:
            os.makedirs(MouseDirectory + "\\LabNotebook")

    @classmethod
    def generateHistology(cls, MouseDirectory, **kwargs):
        _visual_hist_title = kwargs.get('Title', None)
        _base_hist_dir = MouseDirectory + "\\Histology"
        if _visual_hist_title is not None:
            _visual_hist_dir = _base_hist_dir + "\\" + _visual_hist_title
        else:
            _visual_hist_dir = _base_hist_dir + "\\Visualization"

        _read_me_file = _visual_hist_dir + "\\ReadMe.txt"

        os.makedirs(_base_hist_dir)
        os.makedirs(_visual_hist_dir)

        cls.generateReadMe(_read_me_file, "Read-Me for Associated Histological Data")

    @classmethod
    def generateROIMatchingIndex(cls, MouseDirectory):
        _roi_matching_index_dir = MouseDirectory + "\\ROIMatchingIndex"
        _roi_matching_index_read_me = _roi_matching_index_dir + "\\ReadMe.txt"

        os.makedirs(_roi_matching_index_dir)
        cls.generateReadMe(_roi_matching_index_read_me,
                           "Read-Me for Index of Longitudinally-Matched ROIs")

    @classmethod
    def generateStage(cls, MouseDirectory, **kwargs):
        _include_behavior = kwargs.get('Behavior', True)
        _include_imaging = kwargs.get('Imaging', True)
        _include_computation = kwargs.get('Computation', True)
        _stage_title = kwargs.get('Title', 'Stage')
        _stage_directory = MouseDirectory + "\\" + _stage_title

        if _include_behavior:
            cls.generateBehavior(_stage_directory)
        if _include_imaging:
            cls.generateImaging(_stage_directory)
        if _include_computation:
            cls.generateComputation(_stage_directory)

    @classmethod
    def generateBehavior(cls, StageDirectory):
        _base_behav_dir = StageDirectory + "\\Behavior"
        _raw_behavioral_data = _base_behav_dir + "\\RawBehavioralData"
        _behavioral_exports = _base_behav_dir + "\\BehavioralExports"
        _deep_lab_cut_data = _base_behav_dir + "\\DeepLabCutData"
        _processed_data = _base_behav_dir + "\\ProcessedData"
        _analog_burrow_data = _base_behav_dir + "\\AnalogBurrowData"
        os.makedirs(_base_behav_dir)
        os.makedirs(_raw_behavioral_data)
        os.makedirs(_behavioral_exports)
        os.makedirs(_deep_lab_cut_data)
        os.makedirs(_processed_data)
        os.makedirs(_analog_burrow_data)

    @classmethod
    def generateImaging(cls, StageDirectory, **kwargs):
        _sample_frequency = kwargs.get('SampleFrequency', 30)
        _sample_frequency_string = str(_sample_frequency) + "Hz"
        _base_image_dir = StageDirectory + "\\Imaging"
        _sample_frequency_dir = _base_image_dir + "\\" + _sample_frequency_string
        _raw_imaging_data = _base_image_dir + "\\RawImagingData"
        _bruker_meta_data = _base_image_dir + "\\BrukerMetaData"
        os.makedirs(_base_image_dir)
        os.makedirs(_raw_imaging_data)
        os.makedirs(_bruker_meta_data)
        cls.generateSampFreq(_sample_frequency_dir)

    @classmethod
    def generateSampFreq(cls, SampFreqDirectory):
        _suite2p = SampFreqDirectory + "\\suite2p"
        _fissa = SampFreqDirectory + "\\fissa"
        _roi_sorting = SampFreqDirectory + "\\sorting"
        _denoised = SampFreqDirectory + "\\denoised"
        os.makedirs(_suite2p)
        os.makedirs(_fissa)
        os.makedirs(_denoised)
        os.makedirs(_roi_sorting)
        cls.generateReadMe(_roi_sorting+"\\ReadMe.txt", "Read-Me for ROI Sorting")

    @classmethod
    def generateComputation(cls, StageDirectory, **kwargs):
        _analysis_title = kwargs.get('Title', 'AnalysisTechnique')
        _base_comp_dir = StageDirectory + "\\Computational"
        _neural_data_dir = _base_comp_dir + "\\NeuralData"
        _analysis_dir = _base_comp_dir + "\\" + _analysis_title
        os.makedirs(_base_comp_dir)
        os.makedirs(_neural_data_dir)

    @classmethod
    def generateAnalysisTechnique(cls, BaseCompDirectory, AnalysisTitle):
        _analysis_dir = BaseCompDirectory+"\\"+AnalysisTitle
        os.makedirs(_analysis_dir)
        cls.generateReadMe(_analysis_dir+"\\ReadMe.txt", "Read-Me for Analysis Technique")

    @staticmethod
    def generateReadMe(AbsoluteFilePath, Text):
        with open(AbsoluteFilePath, 'w') as _read_me:
            _read_me.write(Text)
            _read_me.close()

    def passMeta(self):
        return self.directory, self.mouse_id

    def recordMod(self, *args):
        """
        Record modification of experiment (Data, Time, *args)

        **Modifies**
            | self.modifications

        :param args: A string explaining the modification
        :rtype: None
        """
        # noinspection PyTypeChecker
        self.modifications.append((self.getDate(), self.getTime(), *args))

    def saveHierarchy(self):
        print("Saving Experimental Hierarchy...")
        if hasattr('self', '_IP'):
            # noinspection PyAttributeOutsideInit
            self._IP = True
        else:
            # noinspection PyAttributeOutsideInit
            self._IP = False

        _output_file = self.directory + "\\" + "ExperimentalHierarchy"
        _output_pickle = open(_output_file, 'wb')

        _output_dict = dict()
        _keys = self.__dict__.keys()
        # noinspection PyTypeChecker

        for _key in _keys:
            if not isinstance(self.__dict__.get(_key), np.ndarray):
                _output_dict[_key] = self.__dict__.get(_key)

        pkl.dump(_output_dict, _output_pickle)
        _output_pickle.close()
        print("Finished.")

        if self._IP:
            # noinspection PyAttributeOutsideInit
            self._IP = get_ipython()

    def createLogFile(self):
        self.log_file = self.directory + "\\log_file.log"

    # noinspection All
    def startLog(self):
        self._IP = get_ipython()
        _magic_arguments = '-o -r -t ' + self.log_file + ' append'
        self._IP.run_line_magic('logstart', _magic_arguments)
        return print("Logging Initiated")

    # noinspection All
    def endLog(self):
        self._IP.run_line_magic('logstop', '')

    # noinspection All
    def checkLog(self): # noinspection All
        self._IP.run_line_magic('logstate', '')
        return


class BehavioralStage:
    """
    **Self Methods**
        | **recordMod** : Records a modification made to the behavioral stage (Date & Time)
        | **createFolderDictionary** : Creates a dictionary of locations for specific files
        | **fillImagingDictionary** :  Generates folders and a dictionary of imaging files (Raw, Meta, Compiled)
        | **addImageSamplingFolder** : Generates a folder for containing imaging data of a specific sampling rate
        | **addImageProcessingFolder** : Generates a folder for containing processed imaging data

    **Properties**
        | **mouse_id** : Identifies which mouse this data belongs to
        | **instance_data** : Identifies when this behavioral stage was created

    **Attributes**
        | **modifications** : List of modifications made to this behavioral stage
        | **folder_dictionary** : A dictionary of relevant folders for this behavioral stage
    """
    def __init__(self, Meta, Stage):
        # PROTECTED
        self.__mouse_id = Meta[1]
        self.__instance_date = ExperimentData.getDate()
        #
        self.modifications = [(ExperimentData.getDate(), ExperimentData.getTime())]
        self.folder_dictionary = dict()
        # self.data = pd.DataFrame
        self.data_frame = pd.DataFrame
        self.meta_data = None
        self.sync_key = None

        _mouse_directory = Meta[0]
        self.createFolderDictionary(_mouse_directory, Stage)
        self.fillImagingFolderDictionary()

    @property
    def mouse_id(self):
        return self._BehavioralStage__mouse_id

    @property
    def instance_date(self):
        return self._BehavioralStage__instance_date

    def recordMod(self):
        """
        Records a modification made to the behavioral stage (Date & Time)
        """
        self.modifications.append((ExperimentData.getDate(), ExperimentData.getTime()))

    def createFolderDictionary(self, MouseDirectory, Stage):
        """
        Creates a dictionary of locations for specific files

        **Modifies**
            | self.folder_dictionary

        :param MouseDirectory: Directory containing mouse data (passed meta)
        :type MouseDirectory: str
        :param Stage: The Stage ID
        :type Stage: str

        """
        _stage_directory = MouseDirectory + "\\" + Stage
        self.folder_dictionary = {
            'mouse_directory': MouseDirectory,
            'stage_directory': _stage_directory,
            'computation_folder': _stage_directory + "\\Computation",
            'imaging_folder': _stage_directory + "\\Imaging",
            'behavior_folder': _stage_directory + "\\Behavior",
        }

    def fillImagingFolderDictionary(self):
        """
        Generates folders and a dictionary of imaging files (Raw, Meta, Compiled)

        **Requires**
            | self.folder_dictionary

        **Modifies**
            | self.folder_dictionary
        """
        # RAW
        _raw_data_folder = self.folder_dictionary['imaging_folder'] + "\\RawImagingData"
        try:
            os.makedirs(_raw_data_folder)
        except FileExistsError:
            print("Existing Raw Data Folder Detected")
        self.folder_dictionary['raw_imaging_data'] = _raw_data_folder
        # META
        _bruker_meta_folder = self.folder_dictionary['imaging_folder'] + "\\BrukerMetaData"
        try:
            os.makedirs(_bruker_meta_folder)
        except FileExistsError:
            print("Existing Bruker Meta Data Folder Detected")
        self.folder_dictionary['bruker_meta_data'] = CollectedDataFolder(_bruker_meta_folder)
        # COMPILED
        _compiled_imaging_data_folder = self.folder_dictionary['imaging_folder'] + "\\CompiledImagingData"
        try:
            os.makedirs(_compiled_imaging_data_folder)
        except FileExistsError:
            print("Existing Compiled Data Folder Detected")

        self.folder_dictionary['compiled_imaging_data_folder'] = CollectedDataFolder(_compiled_imaging_data_folder)

    def addImageSamplingFolder(self, SamplingRate):
        """
        Generates a folder for containing imaging data of a specific sampling rate

        :param SamplingRate: Sampling Rate of Dataset in Hz
        :type SamplingRate: int
        """
        SamplingRate = str(SamplingRate) # Because we know I'll always forget and send an int anyway
        _folder_name = self.folder_dictionary['imaging_folder'] + "\\" + SamplingRate + "Hz"
        try:
            os.makedirs(_folder_name)
        except FileExistsError:
            print("The sampling folder already exists. Adding to folder dictionary")
        self.folder_dictionary[SamplingRate + "Hz"] = CollectedImagingFolder(_folder_name)
        ExperimentData.generateSampFreq(_folder_name)

    def addImageProcessingFolder(self, Title):
        """
        Generates a folder for containing processed imaging data

        :param Title: The name of the folder
        :type Title:  str
        """
        _folder_name = self.folder_dictionary['imaging_folder'] + "\\" + Title
        try:
            os.makedirs(_folder_name)
        except FileExistsError:
            print("The image processing folder already exists. Adding to folder dictionary")
        self.folder_dictionary[Title] = CollectedDataFolder(_folder_name)

    def addImagingAnalysis(self, SamplingRate):
        try:
            self.folder_dictionary.get(str(SamplingRate) + "Hz")
        except KeyError:
            self.addImageProcessingFolder(SamplingRate)

        self.__dict__["imaging_" + str(SamplingRate) + "_Hz"] = {
            'suite2p': None,
            'fissa': None,
            'cascade': None,
        }

    def loadBrukerMetaData(self):
        self.folder_dictionary["bruker_meta_data"].reIndex()
        _files = self.folder_dictionary["bruker_meta_data"].find_all_ext("xml")
        self.meta_data = BrukerMeta(_files[0], _files[2], _files[1])
        self.meta_data.import_meta_data()
        self.meta_data.creation_date = ExperimentData.getDate()

    def loadBrukerAnalogRecordings(self):
        self.folder_dictionary["bruker_meta_data"].reIndex()
        _files = self.folder_dictionary["bruker_meta_data"].find_all_ext("csv")
        return self.load_bruker_analog_recordings(_files[-1])

    def loadAdditionalBrukerAnalogRecordings(self, Tag):
        self.folder_dictionary["".join(["bruker_meta_data_", str(Tag)])].reIndex()
        _files = self.folder_dictionary["".join(["bruker_meta_data_", str(Tag)])].find_all_ext("csv")
        return self.load_bruker_analog_recordings(_files[-1])

    def loadAdditionalBrukerMetaData(self, Tag):
        self.folder_dictionary["".join(["bruker_meta_data_", str(Tag)])].reIndex()
        _files = self.folder_dictionary["".join(["bruker_meta_data_", str(Tag)])].find_all_ext("xml")
        _meta_data = BrukerMeta(_files[0], _files[2], _files[1])
        _meta_data.import_meta_data()
        _meta_data.creation_date = ExperimentData.getDate()
        return _meta_data

    # noinspection PyMethodMayBeStatic
    def mergeAdditionalBruker(self, AnalogRecordings):
        print(" Was not overwritten")
        return

    @staticmethod
    def load_bruker_analog_recordings(File):
        return pd.read_csv(File)

    @staticmethod
    def sync_bruker_recordings(DataFrame, AnalogRecordings, MetaData,  StateCastedDict, SyncKey, **kwargs):
        """

        :param DataFrame:
        :type DataFrame: pd.DataFrame
        :param AnalogRecordings:
        :type AnalogRecordings: pd.DataFrame
        :param MetaData:
        :type MetaData: BrukerMeta
        :param StateCastedDict:
        :type StateCastedDict: dict
        :param SyncKey:
        :type SyncKey: tuple or None
        :return:
        """

        _fill_method = kwargs.get("fill", "backward")
        if SyncKey is None:
            SyncKey = ("State Integer", " TrialIndicator")
        # Sync by matching first peak of the sync_key columns
        _DF_signal = DataFrame[SyncKey[0]].values.copy()
        _AR_signal = AnalogRecordings[SyncKey[1]].values.copy()
        _AR_first_peak = np.where(np.diff(_AR_signal) > 1.0)[0][0]+1
        assert(_AR_signal[_AR_first_peak] >= 3.3)

        _first_peak_diff = np.where(_DF_signal == StateCastedDict.get("Trial"))[0][0] - _AR_first_peak


        if _first_peak_diff > 0:
            print("NOT YET IMPLEMENTED")
            return
            # noinspection PyUnreachableCode
            _AR_signal = np.pad(_AR_signal, (_first_peak_diff, 0), constant_values=0)
        elif _first_peak_diff < 0:
            _first_peak_diff *= -1
            _AR_signal = pd.DataFrame(AnalogRecordings.iloc[_first_peak_diff:, 1:].values,
                                      index=np.around(
                                          (AnalogRecordings.index.values[_first_peak_diff:] - _first_peak_diff) /
                                          int(MetaData.acquisition_rate), decimals=3) + DataFrame.index.values[0])
            _AR_signal.columns = AnalogRecordings.columns[1:]

            _frames = pd.Series(np.arange(0, MetaData.imaging_metadata.get("relativeTimes").__len__(), 1),
                                index=np.around(MetaData.imaging_metadata.get("relativeTimes") -
                                                AnalogRecordings["Time(ms)"].values[_first_peak_diff] / int(
                                    MetaData.acquisition_rate), decimals=3) + DataFrame.index.values[0])
            _frames = _frames[_frames.index >= 0 + DataFrame.index.values[0]].copy(deep=True)
            _frames.name = "Imaging Frame"
        else:
            print("Already Synced")

        # Here I just make sure shape-match
        if _DF_signal.shape[0] < _AR_signal.shape[0]:
            _AR_signal = _AR_signal.iloc[0:_DF_signal.shape[0], :]
            _frames = _frames[_frames.index <= DataFrame.index.values[-1]].copy(deep=True)
            print("Cropped Bruker Signals")
        elif _DF_signal.shape[0] > _AR_signal.shape[0]:
            # _AR_signal.values = np.pad(_AR_signal.values, pad_width=((0, _DF_signal.shape[0] - _AR_signal.shape[0]), (0, 0)),
                                # mode="constant", constant_values=0)

            _AR_signal = _AR_signal.reindex(DataFrame.index)
            # _frames = _frames.reindex(DataFrame.index) no need, happens below anyway

        # Merge/Export Analog
        # DataFrame = DataFrame.join(_AR_signal.copy(deep=True))
        DataFrame = DataFrame.join(_AR_signal)

        # Merge/Export Images
        DataFrame = DataFrame.join(_frames.copy(deep=True))
        # na filling column
        _frames = pd.DataFrame(_frames).copy(deep=True)
        _frames = _frames.reindex(DataFrame.index)
        if _fill_method == "backward":
            _frames.bfill(inplace=True)
        elif _fill_method == "forward":
            _frames.ffill(inplace=True)
        elif _fill_method == "nearest":
            _frames.interpolate(method="nearest", inplace=True)
        _frames = _frames.rename(columns={"Imaging Frame": "[FILLED] Imaging Frame"})
        DataFrame = DataFrame.join(_frames.copy(deep=True))
        return DataFrame

    @staticmethod
    def sync_downsampled_images(DataFrame, MetaData, **kwargs):
        _downsample_size = kwargs.get("downsample_multiplier", 3)
        _fill_method = kwargs.get("fill", "backward")
        _two_files = kwargs.get("two_files", False)
        _meta_data_2 = kwargs.get("second_meta", ExperimentManagement.BrukerMetaModule.BrukerMeta)

        if _fill_method != "backward":
            print("Not Yet Implemented")
            return

        if _two_files:
            _total_frames_1 = MetaData.imaging_metadata.get("relativeTimes").__len__()
            _downsample_frames_1 = np.arange(0, _total_frames_1, _downsample_size)
            _downsample_frames_idx_1 = np.where(np.in1d(_downsample_frames_1, DataFrame["Imaging Frame"].values))[0]
            _time_stamps_1 = DataFrame.index.values[np.where(np.in1d(DataFrame["Imaging Frame"].values,
                                                                   _downsample_frames_1[_downsample_frames_idx_1]))[0]]
            _frames_1 = pd.Series(_downsample_frames_idx_1, index=_time_stamps_1)
            _frames_1.name = "Downsampled Frame"
            _frames_1 = _frames_1.reindex(DataFrame.index)
            _frames_1 = _frames_1[~_frames_1.isnull()]

            _total_frames_2 = _meta_data_2.imaging_metadata.get("relativeTimes").__len__()
            _downsample_frames_2 = np.arange(0, _total_frames_2, _downsample_size)
            _downsample_frames_2 += _total_frames_1
            _downsample_frames_idx_2 = np.where(np.in1d(_downsample_frames_2, DataFrame["Imaging Frame"].values))[0]
            _time_stamps_2 = DataFrame.index.values[np.where(np.in1d(DataFrame["Imaging Frame"].values,
                                                                   _downsample_frames_2[_downsample_frames_idx_2]))[0]]
            _frames_2 = pd.Series(_downsample_frames_idx_2, index=_time_stamps_2)
            _frames_2.name = "Downsampled Frame"
            _frames_2.reindex(DataFrame.index)
            _frames_2 = _frames_2[~_frames_2.isnull()]

            _frames_merged = pd.concat([_frames_1, _frames_2])
            _frames_merged.name = "Downsampled Frame"
            DataFrame = DataFrame.join(_frames_merged.copy(deep=True))
            _frames = pd.DataFrame(_frames_merged)
            _frames.bfill(inplace=True)
            _frames = _frames_merged.name = "[FILLED] Downsampled Frame"
            DataFrame = DataFrame.join(_frames_merged.copy(deep=True))

        else:
            _total_frames = MetaData.imaging_metadata.get("relativeTimes").__len__()
            _imaging_frames = DataFrame["Imaging Frame"].values.copy()

            if _fill_method == "backward":
                _downsample_frames = np.arange(_downsample_size-1, _total_frames, _downsample_size)
                _downsample_frames_idx = np.where(np.in1d(_downsample_frames, DataFrame["Imaging Frame"].values))[0]
                _time_stamps = DataFrame.index.values[np.where(np.in1d(DataFrame["Imaging Frame"].values,
                                                                   _downsample_frames[_downsample_frames_idx]))[0]]
                _frames = pd.Series(_downsample_frames_idx, index=_time_stamps)
                _frames.name = "Downsampled Frame"
                _frames = _frames.reindex(DataFrame.index)
                DataFrame = DataFrame.join(_frames.copy(deep=True))
                _frames = pd.DataFrame(_frames)
                _frames.bfill(inplace=True)
                _frames = _frames.rename(columns={"Downsampled Frame": "[FILLED] Downsampled Frame"})
                DataFrame = DataFrame.join(_frames.copy(deep=True))
        return DataFrame


class CollectedDataFolder:
    """
    This is a class for managing a folder of unorganized data files

**Self Methods**
        | **searchInFolder** : Search THIS object for the *first* file which matches the description
        | **reIndex** : Function that indexed the files within folder again

**Static Methods**
        | **fileParts** : Function returns each identifier of a file and its extension
        | **fileLocator** : Find the file which matches the description


    """
    def __init__(self, Path):
        # Protected In Practice
        self.__instance_date = ExperimentData.getDate()
        self._path = str()
        self._path_assigned = False

        # Properties
        self._files = []
        self.path = Path
        self.files = self.path

    @property
    def instance_date(self):
        return self._CollectedDataFolder__instance_date

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, Path):
        if self._path_assigned is False:
            self._path = Path
            self._path_assigned = True
        else:
            print("Path can only be assigned ONCE.")

    @property
    def files(self):
        return self._files

    @files.setter
    def files(self, Path):
        self._files = os.listdir(Path)

    def reIndex(self):
        """
        Function that indexed the files within folder again
        """
        self.files = self.path

    def searchInFolder(self, ID):
        """
        Search THIS object for the *first* file which matches the description

        :param ID: The description
        :type ID: str
        :return: The absolute file path of the matching filename
        :rtype: str
        """
        return self.path + "\\" + CollectedDataFolder.fileLocator(self.files, ID)

    def find_all_ext(self, ext):
        _ext = "".join(["*.", ext])
        Files = list(pathlib.Path(self.path).glob(_ext))
        for i in range(Files.__len__()):
            Files[i] = Files[i].__str__()
        return Files

    @staticmethod
    def fileLocator(files, ID):
        """
        Find the *first* file which matches the description

        :param files: A list of files
        :type files: list
        :param ID: The description
        :type ID: str
        :return: The matching filename
        :rtype: str
        """
        for i in range(len(files)):
            for _id in CollectedDataFolder.fileParts(files[i]):
                if ID == _id:
                    return files[i]
        return "Nil"

    @staticmethod
    def fileParts(file):
        """
        Function returns each identifier of a file and its extension

        :param file: Filename to be parsed
        :type file: str
        :return: stage, animal, ...[unique file identifiers]..., extension
        :rtype: list
        """
        return file.split("_")[0:-1] + file.split("_")[-1].split(".")


class CollectedImagingFolder(CollectedDataFolder):
    """ this is a super class containing methods for"""
    def __init__(self, Path):
        super().__init__(Path)

    def load_fissa_exports(self):
        """
        This function loads the prepared and separated files exported from Fissa

        :return: Prepared, Separated
        """

        try:
            Prepared = np.load(self.searchInFolder("prepared"), allow_pickle=True)
        except FileNotFoundError:
            print("Could Not Locate Fissa Prepared File")
            Prepared = None

        try:
            Separated = np.load(self.searchInFolder("separated"), allow_pickle=True)
        except FileNotFoundError:
            print("Could Not Locate Fissa Separated File")
            Separated = None

        return Prepared, Separated

    def load_cascade_exports(self):
        """
        This function loads the Spike Times, Spike Prob, and Discrete Approximation files exported from Cascade

        :return: SpikeTimes, SpikeProb, DiscreteApproximation
        """

        try:
            SpikeTimes = np.load(self.searchInFolder("times"), allow_pickle=True)
        except FileNotFoundError:
            print("Could not locate Cascade spike times file.")
            SpikeTimes = None

        try:
            SpikeProb = np.load(self.searchInFolder("prob"), allow_pickle=True)
        except FileNotFoundError:
            print("Could not locate Cascade spike prob file.")
            SpikeProb = None

        try:
            DiscreteApproximation = np.load(self.searchInFolder("discrete"), allow_pickle=True)
        except FileNotFoundError:
            print("Could not locate Cascade discrete approximation file.")
            DiscreteApproximation = None

        return SpikeTimes, SpikeProb, DiscreteApproximation

    def load_suite2p(self):
        return

    def import_proc_traces(self):
        try:
            return self.load_proc_traces(absolute_path=self.searchInFolder("ProcessedTraces"))
        except ModuleNotFoundError:
            print("Detected Deprecated Save. Migrating...")
            with open(self.searchInFolder("ProcessedTraces"), "rb") as _file:
                _ = renamed_load(_file)
            _file.close()
            with open(self.searchInFolder("ProcessedTraces"), "wb") as _file:
                pkl.dump(_, _file)
            _file.close()
            # noinspection PyBroadException
            try:
                return self.load_proc_traces(absolute_path=self.searchInFolder("ProcessedTraces"))
            except Exception:
                print("Migration Unsuccessful")
                return

    def import_proc_inferences(self):
        try:
            return self.load_proc_inferences(absolute_path=self.searchInFolder("ProcessedInferences"))
        except ModuleNotFoundError:
            print("Detected Deprecated Save. Migrating...")
            with open(self.searchInFolder("ProcessedInferences"), "rb") as _file:
                _ = renamed_load(_file)
            _file.close()
            with open(self.searchInFolder("ProcessedInferences"), "wb") as _file:
                pkl.dump(_, _file)
            _file.close()
            # noinspection PyBroadException
            try:
                return self.load_proc_inferences(absolute_path=self.searchInFolder("ProcessedInferences"))
            except Exception:
                print("Migration Unsuccessful")
                return

    @staticmethod
    def load_proc_inferences(**kwargs):
        """
        Load Processed Inferences from file

        :keyword load_path: Path containing processed inferences
        :keyword absolute_path: Absolute filepath
        :rtype: object
        """

        _load_path = kwargs.get('load_path')
        _absolute_path = kwargs.get('absolute_path')
        try:
            if _load_path is not None:
                _filename = _load_path + "ProcessedInferences"
            elif _absolute_path is not None:
                _filename = _absolute_path
            else:
                print("Location of Processed Inferences Not Adequate")
                raise RuntimeError

            print("Loading Processed Inferences...")
            _input_pickle = open(_filename, 'rb')
            ProcessedInferences = pkl.load(_input_pickle)
            _input_pickle.close()
            print("Finished Loading Processed Inferences.")

        except RuntimeError:
            print("Unable to load processed inferences. Check supplied path.")
            return

        return ProcessedInferences

    @staticmethod
    def load_proc_traces(**kwargs):
        """
        Load Processed Traces from file

        :keyword load_path: Path containing processed traces
        :keyword absolute_path: Absolute filepath
        :rtype: object
        """

        _load_path = kwargs.get('load_path')
        _absolute_path = kwargs.get('absolute_path')
        try:
            if _load_path is not None:
                _filename = _load_path + "ProcessedTraces"
            elif _absolute_path is not None:
                _filename = _absolute_path
            else:
                print("Location of Processed Traces Not Adequate")
                raise RuntimeError

            print("Loading Processed Traces...")
            _input_pickle = open(_filename, 'rb')
            ProcessedTraces = pkl.load(_input_pickle)
            _input_pickle.close()
            print("Finished Loading Processed Traces.")

        except RuntimeError:
            print("Unable to load processed traces. Check supplied path.")
            return

        return ProcessedTraces