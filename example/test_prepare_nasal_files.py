#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import itertools
import os
import pdb
from pprint import pprint
import re
import shutil

import file_utils
import numpy as np
import scipy.io.wavfile as wf

# KEY_PATTERN = r'(\w+_\d+)_.*'
# KEY_PATTERN = r'[\d_]+_(\d+)_.*'  # This is suitable for 1288 datasets.
KEY_PATTERN = r'[\d_]+_(\d+A?)_(\d+)_.*'  # This is suitable for mhint datasets.
# DATASET_DIR = '/usr/local/google/home/yero/Desktop/TSVoice/datasets/nasal_yafan_1288/'
# DATASET_DIR = '/usr/local/google/home/yero/Desktop/TSVoice/datasets/nasal_yafan_mhint_new/'
DATASET_DIR = '/usr/local/google/home/yero/Desktop/TSVoice/datasets/nasal_tsai_mhint_20211128/'
SAMPLE_RATE = 16000


def main():
  el_files = sorted(glob.glob(os.path.join(DATASET_DIR, '**/*.wav')))

  expected_keys = file_utils.ExpectedMhintKeys()
  output_files = file_utils.CollectOutputFiles(el_files,
                                               file_utils.MhintKeyTransform,
                                               expected_keys, KEY_PATTERN)

  # Read, resample, and write to the `DATSET_DIR` itself.
  file_utils.ReadAndResampleFiles(output_files, DATASET_DIR, skip_existing=True)


if __name__ == '__main__':
  main()
