

- `file_utils.py`: Utilities to rename and resample files. Used by `test_prepare_{nasal, normal}_files.py`


### Scripts
- `test_prepare_{nasal, normal}_files.py`: Prepare nasal and normal files.
- `test_stretch_audio.py`: Pre-stretch faster speech files (usually normal speech) to roughly match the slower ones. Depends on the `pysox` package.
- `test_cut_wavs.py`: Cut the initial part of WAV files; useful to remove the initial transients.
