#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import os
import pdb
from pprint import pprint
import re
import shutil

from matplotlib import pyplot as plt
import numpy as np
import scipy.io.wavfile as wf

# SUBDIR = 'nasal_yafan_1288'
# SUBDIR = 'normal_yafan_1288'
# SUBDIR = 'nasal_yafan_mhint_new'
SUBDIR = 'nasal_tsai_mhint_20211128'
CUT_INITIAL_SECS = 0.1
SKIP_EXISTING = True


def main():
  # dataset_dir = ('/usr/local/google/home/yero/Desktop/TSVoice/'
  #                'sprocket/example/data/wav/')
  # input_subdir = 'nasal_tsai_chi/'

  input_base_dir = '/usr/local/google/home/yero/Desktop/TSVoice/datasets/'
  input_subdir = SUBDIR
  output_base_dir = ('/usr/local/google/home/yero/Desktop/TSVoice/'
                     'sprocket/example/data/wav/')
  output_subdir = f'{SUBDIR}_cut[{CUT_INITIAL_SECS:.2f}]/'
  input_dir = os.path.join(input_base_dir, input_subdir)
  output_dir = os.path.join(output_base_dir, output_subdir)

  print('Making output_dir: {}'.format(output_dir))
  os.makedirs(output_dir, exist_ok=True)

  el_files = sorted(glob.glob(os.path.join(input_dir, '*.wav')))
  for el_file in el_files:
    basename, _ = os.path.splitext(os.path.basename(el_file))
    output_wav_filename = os.path.join(output_dir, basename + '.wav')

    if SKIP_EXISTING and os.path.exists(output_wav_filename):
      # print(f'... skipping {basename}')
      continue

    fs, wav = wf.read(el_file)
    new_start = int(CUT_INITIAL_SECS * fs)

    wav = wav[new_start:]
    t = np.arange(0, len(wav)) / fs

    plt.figure(figsize=(10, 2))
    plt.plot(t, wav, linewidth=0.5)
    plt.xticks(np.arange(0, t[-1], 0.1))
    plt.axis('auto')
    plt.tight_layout()

    output_fig_filename = os.path.join(output_dir, basename + '.png')
    plt.savefig(output_fig_filename, dpi=90)
    plt.close()

    wf.write(output_wav_filename, fs, wav)
    print(f'Finished cutting {basename}.wav')


if __name__ == '__main__':
  main()
