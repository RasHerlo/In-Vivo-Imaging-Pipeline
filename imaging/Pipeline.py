


def run_pipeline(Fold Config):





    def pipeline(Obj: Management.Organization.ImagingExperiment, FrameRate: float, Name: str, Config: dict):
        # 0. Pre-Process
        _images = load_all_tiffs(Obj.folder_dictionary.get(Name).folders.get("compiled"))
        _images = wrapped_process(_images, *read_wrapper(Config.get("preprocess")).interface())
        save_raw_binary(_images, Obj.folder_dictionary.get(Name).folders.get("compiled"))
        _frames, _y, _x = _images.shape  # (Any cropping should ALWAYS be taken from the front of the dataset)
        _images = None

        # 1. Motion-Correct
        _s2p = Suite2PAnalysis(Obj.folder_dictionary.get(Name).folders.get("compiled"),
                               Obj.folder_dictionary.get(Name).path, file_type="binary",
                               ops=Config.get("suite2p"))
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
                               video_folder=Obj.folder_dictionary.get(Name).folders.get("denoised").path,
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
        _traces = wrapped_process(_traces, *read_wrapper(Config.get("postprocess")).interface())
        _fissa.ProcessedTraces.detrended_merged_dFoF_result, = _traces
        _fissa.saveProcessedTraces()

        # Spike Probability
        _cascade = CascadeAnalysis(_fissa.ProcessedTraces.detrended_merged_dFoF_result, FrameRate,
                                   model_folder=Config.get("cascade").get("model_folder"),
                                   SavePath=Obj.folder_dictionary.get(Name).folders.get("cascade"))
        _cascade.model_name = Config.get("cascade").get("model_name")
        _cascade.predictSpikeProb()
        _cascade.ProcessedInferences.firing_rates = Processing.calculateFiringRate(_cascade.spike_prob,
                                                                                   _cascade.frame_rate)
        _cascade.saveSpikeProb(_cascade.save_path)
        _cascade.saveProcessedInferences(_cascade.save_path)

        # Discrete Spike Inference
        _cascade.inferDiscreteSpikes()
        _cascade.saveSpikeInference(_cascade.output_folder)

        return
