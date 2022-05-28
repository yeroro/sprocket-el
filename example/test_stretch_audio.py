#%% Imports.
import glob
import os

#import librosa
from matplotlib import pyplot as plt
import numpy as np
# from pyrubberband import pyrb
from scipy.io import wavfile as wf
import sox

#%%
wav_dir = 'data/wav/normal_tsai_chi_single'
file_list = sorted(glob.glob(os.path.join(wav_dir, '*.wav')))
output_dir = 'data/wav/normal_tsai_chi_single_stretched'

factor = 0.60

tfm = sox.Transformer()
tfm.tempo(factor=factor, audio_type='s')

for i, file in enumerate(file_list):
  basename = os.path.basename(os.path.splitext(file)[0])
  output_path = os.path.join(output_dir, basename + '.wav')
  if os.path.exists(output_path):
    print(f'Skipping existing {output_path}')
    continue

  print('[{}/{}] {}'.format(i + 1, len(file_list), basename))
  sr, wav = wf.read(file)
  wav = wav.astype(float) / 32768.0

  #  stretched_wav = librosa.effects.time_stretch(wav, factor)
  # stretched_wav = pyrb.time_stretch(wav, sr, factor)
  stretched_wav = tfm.build_array(
    input_array=wav, sample_rate_in=16000)

  ii16 = np.iinfo(np.int16)
  stretched_wav = np.clip(stretched_wav * 32768.0, ii16.min,
                          ii16.max).astype(np.int16)
  wf.write(output_path, sr, stretched_wav)

# %%
