import numpy as np
data = np.load('features/train_mfcc-chroma-mel_AHNPS_3898.npy')
np.savetxt('npfile.csv', data, delimiter=',')