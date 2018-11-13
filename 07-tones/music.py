import sys
import wave
import numpy as np
import math
from struct import unpack

note_names = ['C', 'Cis', 'D', 'Es', 'E', 'F', 'Fis', 'G', 'Gis', 'A', 'Bes', 'B']

def frequency_to_tone(fundamental_freq, freq):
  fundamental_freq_log_scaled = fundamental_freq * pow(2, -(len(note_names) + 9)/len(note_names))
  log_distance = len(note_names) * (math.log2(freq) - math.log2(fundamental_freq_log_scaled))
  
  tones_diff = int(log_distance % len(note_names))
  octaves_diff = int(log_distance // len(note_names))
  cents = float(100 * (log_distance % 1))
  cents = int(round(cents))
  
  if cents >= 50:
    tones_diff += 1
    cents = - (100 - cents)
  
  if tones_diff >= 12:
    tones_diff -= 12
    octaves_diff += 1

  tone = note_names[tones_diff]
  if octaves_diff >= 0:
    tone = tone.lower() + ("'" * octaves_diff)
  else:
    tone = tone + (',' * (-1 * octaves_diff))

  return '{}{:+d}'.format(tone, cents)


def average_over_channels(frame_bytes, num_channels):
  idx = 0

  new_frame_bytes = []
  while idx <= (len(frame_bytes) - num_channels):
    averaged_frame_byte = 0
    for channel_idx in range(num_channels):
      averaged_frame_byte += frame_bytes[idx + channel_idx]
    averaged_frame_byte /= num_channels
    new_frame_bytes += [averaged_frame_byte]
    idx += num_channels


  return new_frame_bytes

def cluster_peaks(window_peaks):
  if len(window_peaks) == 0:
    return []

  current_cluster = []
  all_clustered = []

  for peak in window_peaks:
    freq, ampl = peak

    if (current_cluster[-1][0] if len(current_cluster) > 0 else None) == freq - 1:
      current_cluster += [(freq, ampl)]
    else:
      if len(current_cluster) > 0:
        max_in_cluster = max(current_cluster, key = lambda tuple: tuple[1])
        all_clustered += [max_in_cluster]

      current_cluster = [(freq, ampl)]

  if len(current_cluster) > 0:
    max_in_last_cluster = max(current_cluster, key = lambda tuple: tuple[1])
    all_clustered += [max_in_last_cluster]

  return list(filter(lambda tuple: tuple[0] != 0, all_clustered))

def pick_top_prominent(clustered_peaks, k):
  sorted_peaks_by_ampl = sorted(clustered_peaks, key = lambda tuple: tuple[1])

  top_prominent = sorted_peaks_by_ampl[-k:]

  return top_prominent

def parse_frames(wave_file_handle, frames_per_second, num_of_seconds, num_of_channels):
  parsed_bytes = wave_file_handle.readframes(int(frames_per_second * num_of_seconds))
  parsed_bytes = unpack("%ih" % (int(num_of_channels * frames_per_second * num_of_seconds)), parsed_bytes)
  parsed_bytes = average_over_channels(parsed_bytes, num_of_channels)

  return parsed_bytes


def parse_tones_from_file(fundamental_freq, filename):
  all_peaks = []

  from_window_time = 0
  to_window_time = 0.1
  with wave.open(filename, 'rb') as wave_file_handle:
    # number of frames per second (sampling frequency)
    frames_per_second = wave_file_handle.getframerate()
    number_of_channels = wave_file_handle.getnchannels()

    # number of frames in total
    number_of_frames = wave_file_handle.getnframes()
    total_seconds = number_of_frames / frames_per_second
    window_size = frames_per_second * (1/10)

    number_of_windows = number_of_frames // window_size
    number_of_windows -= number_of_windows % 10
    all_peaks = []

    if total_seconds >= 1:
      last_ten_windows_frames_bytes = parse_frames(wave_file_handle, frames_per_second, num_of_seconds = 1.0, num_of_channels = number_of_channels)

    while from_window_time + 1 <= total_seconds:
      if from_window_time + 1 > total_seconds:
        continue
      clustered_peaks = []

      frequency_information = np.fft.rfft(last_ten_windows_frames_bytes)
      amplitudes = list(map(lambda frequency_information: np.abs(frequency_information), frequency_information))
      avg_amplitude = sum(amplitudes) / len(amplitudes)

      window_peaks = [(frequency, amplitude) for frequency, amplitude in enumerate(amplitudes) if amplitude >= 20 * avg_amplitude and amplitude != 0]

      clustered_peaks = cluster_peaks(window_peaks)
      clustered_peaks = pick_top_prominent(clustered_peaks, 3)

      if len(clustered_peaks) > 0:
        sorted_peaks_by_freq = sorted(clustered_peaks, key = lambda tuple: tuple[0])
        tones_str = ' '.join([frequency_to_tone(fundamental_freq, freq) for freq, ampl in sorted_peaks_by_freq])

        if len(all_peaks) > 0 and all_peaks[-1]['to'] == from_window_time and all_peaks[-1]['tones_str'] == tones_str:
          all_peaks[-1]['to'] = to_window_time
        else:
          all_peaks += [{
            'from': from_window_time,
            'to': to_window_time,
            'peaks': clustered_peaks,
            'tones_str': tones_str
          }]
        

      from_window_time += 0.1
      to_window_time += 0.1

      if from_window_time + 1 < total_seconds:
        last_window_frames_bytes = parse_frames(wave_file_handle, frames_per_second, num_of_seconds = 0.1, num_of_channels = number_of_channels)

      del last_ten_windows_frames_bytes[:(int(window_size))]
      last_ten_windows_frames_bytes += last_window_frames_bytes

  for peak in all_peaks:
    print('%.1f-%.1f %s' %(peak['from'], peak['to'], peak['tones_str']))


if __name__ == "__main__":
  fundamental_freq = int(sys.argv[1])
  filename = sys.argv[2]
  parse_tones_from_file(fundamental_freq, filename)
