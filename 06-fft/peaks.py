from struct import unpack
import wave
import sys
import numpy as np

def get_measurement_from_frame(one_frame_data, number_of_channels):
  format_str = ''.join(['h' for x in range(0, number_of_channels)])

  one_frame_data_unpacked = unpack(format_str, one_frame_data)
  measurement_data = 0
  # average across channels
  for i in range(0, number_of_channels):
    measurement_data += one_frame_data_unpacked[i]
  measurement_data /= number_of_channels

  return measurement_data

def get_peaks_from_one_second_window(wave_file_handle, number_of_channels, frames_per_second):
  window_measurements = []
  for _ in range(0, frames_per_second):
    frame_data = wave_file_handle.readframes(1)

    measurement = get_measurement_from_frame(frame_data, number_of_channels)
    window_measurements += [measurement]


  frequency_information = np.fft.rfft(window_measurements)
  amplitudes = list(map(lambda frequency_information: np.abs(frequency_information), frequency_information))

  avg_amplitude = sum(amplitudes) / len(amplitudes)

  window_peaks = []
  for frequency in range(0, len(amplitudes)):
    curr_amplitude = amplitudes[frequency]

    if curr_amplitude >= (20 * avg_amplitude):
      window_peaks += [frequency]
  

  return window_peaks

with wave.open(sys.argv[1], 'rb') as file:
  # number of frames per second (sampling frequency)
  frames_per_second = file.getframerate()
  number_of_channels = file.getnchannels()

  # number of frames in total
  number_of_frames = file.getnframes()
  number_of_windows = number_of_frames // frames_per_second
  all_peaks = []
  for window_number in range(0, number_of_windows):
    all_peaks += get_peaks_from_one_second_window(file, number_of_channels, frames_per_second)

  if len(all_peaks) > 0:
    high_peak = np.max(all_peaks)
    low_peak = np.min(all_peaks)
    print('low = %i, high = %i' % (low_peak, high_peak))
  else:
    print("no peaks")
  
