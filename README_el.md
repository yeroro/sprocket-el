# How to run
1. Prepare wav files. Use `test_prepare_*_files.py` to rename, resample to
   16 kHz, and copy files from source to the working folder, i.e. under
   `example/data/wav/`.
2. Also use `test_cut_wavs.py` and `test_stretch_audio.py` to cut initial
   transients and pre-stretch WAV fiels if needed.
3. Run `initialize.py` steps 1, 2, and 3.
4. Modify the `*.yml` and `*.list` files if needed.
   - Add `fake` in the YML file if needed.
   - Use the `f0` and `npow` histograms under `conf/figure` to set reasonable
     thresholds.
  - See `example/conf/speaker/nasal_tsai_mhint_20211128_cut[0.10].yml` for an
    example.
5. Run `run_sprocket.py` steps 1, 2, 3, and 6. The results will be stored in
   `example/data/pair/*/aligned/`.


# Files
## Modified files
- `example/src/yml.py`,
- `example/src/extract_features.py`,
- `sprocket/speech/feature_extrator.py`,
- `sprocket/speech/analyzer.py`: Add the ability to provide fake f0 (e.g.
    100 Hz electrolarynx excitations) and median-filter the extracted f0
    by specifying the kernel size.
- `sprocket/speech/extfrm.py`: Log the number of non-silent frames extracted.
- `example/src/estimate_twf_and_jnt.py`: Median-filter the power and also
    save the joint feature vectors in the HDF5 file format. Useful for
    outputting the aligned WAV files.
- `example/run_sprocket.py`: Add an extra step 6, which outputs the aligned
    WAV files. Also disable step 4 & 5.

## Added files
- `example/file_utils.py`: Add utilites to rename and resample files. Used by
    `test_prepare_{nasal, normal}_files.py`
- `example/src/output_aligned.py`: Take the results of sprocket step 3
    (aligning) and resynthesize aligned WAVs. Used in sprocket step 6.

## Scripts
- `example/test_prepare_{nasal, normal}_files.py`: Prepare nasal and normal
    files.
- `example/test_stretch_audio.py`: Pre-stretch faster speech files (usually
    normal speech) to roughly match the slower ones. This depends on the
    `pysox` package.
- `example/test_cut_wavs.py`: Cut the initial part of WAV files; useful to
    remove the initial transients.
