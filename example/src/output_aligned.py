# -*- coding: utf-8 -*-
import argparse
import os
import pdb
import sys

from matplotlib import pyplot as plt
import numpy as np
from scipy import signal
from scipy.io import wavfile
# from sklearn.externals import joblib
import joblib

#from sprocket.model import GV, GMMConvertor, GMMTrainer
from sprocket.speech import FeatureExtractor, Synthesizer
from sprocket.util import HDF5, extfrm, static_delta
from yml import SpeakerYML, PairYML
from .misc import read_feats, low_cut_filter, extsddata
# from misc import read_feats, extsddata, transform_jnt

def main(*argv):
    argv = argv if argv else sys.argv[1:]
    # Options for python
    description = 'Output aligned audio'
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('org_list_file', type=str,
                        help='List file of original speaker')
    parser.add_argument('tar_list_file', type=str,
                        help='List file of target speaker')
    parser.add_argument('org', type=str,
                        help='Original speaker')
    parser.add_argument('tar', type=str,
                        help='Target speaker')
    parser.add_argument('org_yml', type=str,
                        help='Yml file of the original speaker')
    parser.add_argument('tar_yml', type=str,
                        help='Yml file of the target speaker')
    parser.add_argument('pair_yml', type=str,
                        help='Yml file of the speaker pair')
    parser.add_argument('wav_dir', type=str,
                        help='Directory path of source spekaer')
    parser.add_argument('pair_dir', type=str,
                        help='Directory path of pair directory')
#    parser.add_argument('--fake_f0', type=float, default=None,
#                        help='Fake f0 value to synthesize EL voices')
#    parser.add_argument(
#        '--fake_f0_med_filter_kernel', type=int, default=0,
#        help='Kernel size to median-filter the fake f0 values.')
#    parser.add_argument('--gain_kernel', type=int, default=0,
#                        help='Kernel size to mean fitler the gains.')
    args = parser.parse_args(argv)

    # read pair-dependent yml file
    pconf = PairYML(args.pair_yml)

    # read parameters from speaker yml
    org_conf = SpeakerYML(args.org_yml)
    tar_conf = SpeakerYML(args.tar_yml)

    # Construct FeatureExtractor classes.
    org_feat = FeatureExtractor(analyzer=org_conf.analyzer,
                                fs=org_conf.wav_fs,
                                fftl=org_conf.wav_fftl,
                                shiftms=org_conf.wav_shiftms,
                                minf0=org_conf.f0_minf0,
                                maxf0=org_conf.f0_maxf0,
                                f0_fake=org_conf.f0_fake)
    tar_feat = FeatureExtractor(analyzer=tar_conf.analyzer,
                                fs=tar_conf.wav_fs,
                                fftl=tar_conf.wav_fftl,
                                shiftms=tar_conf.wav_shiftms,
                                minf0=tar_conf.f0_minf0,
                                maxf0=tar_conf.f0_maxf0,
                                f0_fake=tar_conf.f0_fake)

    # Construct Synthesizer classes.
    org_synthesizer = Synthesizer(fs=org_conf.wav_fs,
                                  fftl=org_conf.wav_fftl,
                                  shiftms=org_conf.wav_shiftms)
    tar_synthesizer = Synthesizer(fs=tar_conf.wav_fs,
                                  fftl=tar_conf.wav_fftl,
                                  shiftms=tar_conf.wav_shiftms)

    # Aligned directory
    aligned_dir = os.path.join(args.pair_dir, 'aligned')
    os.makedirs(os.path.join(aligned_dir, args.org), exist_ok=True)
    os.makedirs(os.path.join(aligned_dir, args.tar), exist_ok=True)


    # read joint feature vector
    # jntf = os.path.join(args.pair_dir, 'jnt',
    #                     'it' + str(pconf.jnt_n_iter) + '_jnt.h5')
    # jnth5 = HDF5(jntf, mode='r')
    # jnt = jnth5.read(ext='mcep')
    # jnt_codeap = jnth5.read(ext='codeap')

    # pdb.set_trace()

    # mcep_dim = jnt.shape[1] // 4
    # original_mcep = jnt[:, :mcep_dim]
    # target_mcep = jnt[:, (2 * mcep_dim):(3 * mcep_dim)]

    # original_codeap = jnt_codeap[:, :1]
    # target_codeap = jnt_codeap[:, 2:3]

    # mcep_0th = 5.0

    # n_frames = jnt.shape[0]
    # n_frames_per_file = 1000
    # for mcep in (original_mcep, target_mcep):
    #   for i in range(n_frames // n_frames_per_file):
    #     mcep_i = mcep[(i * n_frames_per_file):((i + 1) * n_frames_per_file), :]
    #     mcep_i = np.hstack((np.ones((mcep_i.shape[0], 1)) * mcep_0th, mcep_i))

    # Read the powers. Used to remove silence.
    h5_dir = os.path.join(args.pair_dir, 'h5')
    org_npows = read_feats(args.org_list_file, h5_dir, ext='npow')
    tar_npows = read_feats(args.tar_list_file, h5_dir, ext='npow')
    org_mceps = read_feats(args.org_list_file, h5_dir, ext='mcep')
    tar_mceps = read_feats(args.tar_list_file, h5_dir, ext='mcep')

    # Read joint feature vectors for individual files
    jnt_dir = os.path.join(args.pair_dir, 'jnt')

    org_fp = open(args.org_list_file, 'r')
    org_lines = list(org_fp)

    tar_fp = open(args.tar_list_file, 'r')
    tar_lines = list(tar_fp)

    assert len(org_lines) == len(tar_lines)
    assert len(org_lines) == len(org_npows)
    assert len(tar_lines) == len(tar_npows)

    for org_line, org_npow, org_mcep, tar_line, tar_npow, tar_mcep in zip(
        org_lines, org_npows, org_mceps, tar_lines, tar_npows, tar_mceps):
        org_f = org_line.rstrip()
        org_f_base = os.path.basename(org_f)
        print(org_f_base)

        tar_f = tar_line.rstrip()
        tar_f_base = os.path.basename(tar_f)
        print(tar_f_base)

        f_base = org_f_base

        jntpath = os.path.join(jnt_dir, f_base + '_jnt.h5')

        jnth5 = HDF5(jntpath, mode='a')
        # mcep = jnth5.read(ext='mcep')
        # codeap = jnth5.read(ext='codeap')
        twf = jnth5.read(ext='twf')

        filtered_onpow = signal.medfilt(org_npow, 21)

        # Get the original f0.
        for s, (f, npow, mcep, feat, synth, conf) in enumerate((
            (org_f, filtered_onpow, org_mcep, org_feat, org_synthesizer, org_conf),
            (tar_f, tar_npow, tar_mcep, tar_feat, tar_synthesizer, tar_conf))):
            wavf = os.path.join(args.wav_dir, f + '.wav')
            fs, x = wavfile.read(wavf)
            x = x.astype(np.float)
            x = low_cut_filter(x, fs, cutoff=70)
            assert fs == org_conf.wav_fs

            # analyze F0, mcep, and ap
            f0, spc, ap = feat.analyze(x)

            # Extract F0 and AP for power greater than threshold.
            f0_ext = extfrm(f0, npow, power_threshold=conf.power_threshold)
            ap_ext = extfrm(ap, npow, power_threshold=conf.power_threshold)
            mcep_ext = extfrm(mcep, npow, power_threshold=conf.power_threshold)


            # Aligned F0 and AP.
            f0_aligned = f0_ext[twf[s]]
            ap_aligned = ap_ext[twf[s]]

            # Aligned mcep and codeap.
            # mcep_aligned = np.split(mcep, 4, axis=-1)[2 * s]
            mcep_aligned = mcep_ext[twf[s]]
            # codeap_aligned = np.split(codeap, 2, axis=-1)[s]

            plt.figure()
            ax1 = plt.subplot(311)
            plt.plot(f0_aligned)
            plt.subplot(312, sharex=ax1)
            plt.imshow(mcep_aligned.T, origin='lower')
            plt.axis('auto')
            plt.subplot(313, sharex=ax1)
            # plt.imshow(codeap_aligned.T, origin='lower')
            plt.imshow(ap_aligned.T, origin='lower')
            plt.axis('auto')
            plot_path = os.path.join(aligned_dir, f + '.png')
            plt.savefig(plot_path, dpi=300, pad_inches=0.0)
            plt.close()

            # Synthesize!!
            wav_aligned = synth.synthesis(f0_aligned,
                                          mcep_aligned,
                                          ap_aligned,
                                          rmcep=None,
                                          alpha=conf.mcep_alpha)
            wav_aligned = np.clip(wav_aligned, -32768, 32767)
            wavpath = os.path.join(aligned_dir, f + '.wav')
            print(wavpath)
            wavfile.write(wavpath, fs, wav_aligned.astype(np.int16))
