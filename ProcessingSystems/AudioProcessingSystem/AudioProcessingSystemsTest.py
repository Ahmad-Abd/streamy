aps =  PsdEstimationBasedAudioDenoiser(fs=16000,threshold=0)
p = os.getcwd()+'//' + \
    'ProcessingSystems//AudioProcessingSystem//DemucsBasedAudioDenoiser//' + 'splitted_cc2.wav'
print(p)
sr,wav = wavfile.read(p)
data = aps.late_processing(wav,sr)
data = np.array(data).astype(np.int16)
wavfile.write('filename.wav', 16000, data)
f, t, Zxx = signal.stft(data, sr, nperseg=2048)
plt.figure(figsize=(20,10))
plt.subplot(2,1,1)
plt.title('Noisy Audio')
#Zxx[np.abs(Zxx) < 5] = 0
plt.pcolormesh(t, f, np.abs(Zxx), vmin=0, vmax=1, shading='gouraud',cmap='gray')
#plt.plot(data)
plt.show()