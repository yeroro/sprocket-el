#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import glob
import os
import pdb
from pprint import pprint
import re
import shutil

import librosa
import numpy as np
import scipy.io.wavfile as wf


def ExpectedMhintKeys():
  group_keys = [f'{i}' for i in range(1, 13)] + [f'{i}A' for i in range(1, 5)]
  ingroup_keys = [f'{i}' for i in range(1, 21)]
  return {f'{a}_{b}' for a in group_keys for b in ingroup_keys}


def Expected1288Keys():
  return set(range(1, 1289))


def MhintKeyTransform(key_pair):
  assert len(key_pair) == 2
  return f'{key_pair[0]}_{key_pair[1]}'


def ReadAndResample(wav_path, sr_target, factor=32768.0):
  sr_source, wav = wf.read(wav_path)
  if not np.issubdtype(wav.dtype, np.int16):
    wav = wav.astype(np.float64) * factor

  y = librosa.core.resample(wav.astype(np.float64), sr_source, sr_target)
  return y.astype(np.int16)


def CollectOutputFiles(files, key_transform, expected_keys, file_pattern):
  print(f'\nProcessing {len(files)} files')

  output_files = {}
  for filename in files:
    basename = os.path.basename(filename)
    root, ext = os.path.splitext(basename)
    if ext != '.wav':
      print('{} is not an WAV file'.format(basename))

    keys = re.findall(file_pattern, root)
    if len(keys) == 0:
      print('Ill-formatted filename: {}'.format(basename))
      continue

    key = key_transform(keys[0])
    if key in output_files:
      print(f'Duplicated: \n\t{basename}\n\t{output_files[key]}')
      print(f'Discarding: \n\t{basename}')
      continue
    else:
      output_files[key] = filename

  actual_keys = set(sorted(output_files.keys()))

  extra = sorted(actual_keys - expected_keys)
  missing = sorted(expected_keys - actual_keys)
  print(f'actual - expected = {len(extra)} files =')
  pprint(extra)
  print(f'expected - actual = {len(missing)} files =')
  pprint(missing)

  print(f'\nCollected {len(output_files)} files')
  return output_files


def ReadAndResampleFiles(files,
                         output_dir,
                         sample_rate=16000,
                         skip_existing=False):
  for key in sorted(files.keys()):
    resampled_filename = os.path.join(output_dir, f'{key}.wav')
    if skip_existing and os.path.exists(resampled_filename):
      print(f'Skipping existing {resampled_filename}')
      continue

    source = files[key]
    resampled_wav = ReadAndResample(source, sample_rate)
    if len(resampled_wav) == 0:
      print(f'Error reading {source}; skipped')
      continue

    print(f'Writing to {resampled_filename}')
    wf.write(resampled_filename, sample_rate, resampled_wav)
