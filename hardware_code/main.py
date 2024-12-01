import numpy as np
import pywt
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, butter, lfilter, savgol_filter
from collections import deque
import serial
import matplotlib.animation as animation

# Serial setup for real-time ECG data acquisition
ser = serial.Serial('COM14', 115200, timeout=1)
ser.flush()

# Parameters for Butterworth filter
def butter_lowpass(cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order)
    return lfilter(b, a, data)

# Parameters for wavelet analysis
sampling_rate = 100.0  # Hz
cutoff_frequency = 20  # Hz
prev_signal = deque(maxlen=1000)

# Visualization setup
fig, ax = plt.subplots(2, 1, figsize=(10, 8))

# Real-time ECG plot
ax[0].set_ylim(0, 2000)
ax[0].set_xlim(0, 1000)
ecg_line, = ax[0].plot([], [], lw=0.5)
ax[0].set_title("Real-Time ECG Signal")
ax[0].set_xlabel("Time (samples)")
ax[0].set_ylabel("Amplitude")
ax[0].grid(True)

# Processed heart rate plot
ax[1].set_xlim(0, 1000)
ax[1].set_ylim(0, 100)
processed_line, = ax[1].plot([], [], lw=0.5)
ax[1].set_title("Heart Rate Peaks")
ax[1].set_xlabel("Time (samples)")
ax[1].grid(True)

# Signal buffers
ecg_buffer = deque(maxlen=1000)
processed_signal_buffer = deque(maxlen=1000)

# Heart rate computation
def compute_heart_rate(ecg_signal, fs):
    # Perform a 4-level stationary wavelet decomposition using 'sym4'
    # print("ahem0")
    try:
        coeffs = pywt.swt(ecg_signal, 'sym4', level=3)
        # print("ahem1")
    except Exception as e:
        print(f"Error in pywt.swt: {e}")
        return None, None, None
    coeffs_for_reconstruction = []
    for i, (a, d) in enumerate(coeffs):
        # print("ahem2")
        if i in [2, 3]:  # Keep d3 and d4 coefficients as is
            coeffs_for_reconstruction.append((np.zeros_like(a), d))
        else:
            coeffs_for_reconstruction.append((np.zeros_like(a), np.zeros_like(d)))
    # print("ahem3")
    reconstructed_signal = pywt.iswt(coeffs_for_reconstruction, 'sym4')
    y = np.abs(reconstructed_signal) ** 2  # Magnitude square
    avg = np.mean(y)
    Rpeaks, _ = find_peaks(y, height=8 * avg, distance=int(fs / 2))  # Adjust distance based on Fs
    # print("ahem4")
    heart_rate = (len(Rpeaks) * 60) / (len(ecg_signal) / fs)
    return heart_rate, y, Rpeaks

# Animation update function
def update(frame):
    if ser.in_waiting > 0:
        try:
            data = ser.readline().decode('utf-8').strip()
            raw_value = float(data)
            ecg_buffer.append(raw_value)
            print(len(ecg_buffer))

            # Process ECG data for heart rate
            if len(ecg_buffer) >= 1000:  # Ensure buffer is full
                # print("check1")
                filtered_signal = butter_lowpass_filter(list(ecg_buffer), cutoff_frequency, sampling_rate)
                # print("check3")
                filtered_signal = savgol_filter(filtered_signal, window_length=15, polyorder=3)
                # print("check4")
                heart_rate, processed_signal, Rpeaks = compute_heart_rate(filtered_signal, sampling_rate)
                # print("check5")
                if processed_signal is not None:
                    processed_signal_buffer.clear()
                    processed_signal_buffer.extend(processed_signal)

                    # Update processed signal plot
                    processed_line.set_data(range(len(processed_signal_buffer)), processed_signal_buffer)
                    for peak in Rpeaks:
                        ax[1].plot(peak, processed_signal[peak], 'ro')
                        # print("check2")

                    print(f"Heart Rate: {heart_rate:.2f} BPM")

            # Update real-time ECG plot
            ecg_line.set_data(range(len(ecg_buffer)), ecg_buffer)

        except ValueError:
            pass

    return ecg_line, processed_line

ani = animation.FuncAnimation(fig, update, frames=None, blit=True, interval=10, repeat=False)
plt.tight_layout()
plt.show()


##########################################33

# import serial
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation
# from scipy.signal import butter, lfilter, savgol_filter
# from collections import deque
#
# # Serial setup
# ser = serial.Serial('COM14', 115200, timeout=1)
# ser.flush()
#
# # Butterworth filter functions
# def butter_lowpass(cutoff, fs, order=5):
#     nyquist = 0.5 * fs
#     normal_cutoff = cutoff / nyquist
#     b, a = butter(order, normal_cutoff, btype='low', analog=False)
#     return b, a
#
# def butter_lowpass_filter(data, cutoff, fs, order=5):
#     b, a = butter_lowpass(cutoff, fs, order)
#     return lfilter(b, a, data)
#
# # Plot setup
# fig, ax = plt.subplots()
# ax.set_ylim(0, 2000)
# ax.set_xlim(0, 1000)
# line, = ax.plot([], [], lw=0.5)
# ydata = deque(maxlen=1000)
#
# # Animation init
# def init():
#     line.set_data([], [])
#     return line,
#
# # Parameters for filtering
# cutoff_frequency = 20  # Hz
# sampling_rate = 100.0   # Hz
# prev_signal = []
#
# # Update function
# def update(frame):
#     global prev_signal
#     if ser.in_waiting > 0:
#         try:
#             data = ser.readline().decode('utf-8').strip()
#             raw_value = float(data)
#
#             # Apply Butterworth low-pass filter (real-time approach)
#             prev_signal.append(raw_value)
#             if len(prev_signal) > 200:  # Keep enough data for filtering
#                 prev_signal.pop(0)
#
#             # Smooth with Savitzky-Golay (optional, for real-time data)
#             smoothed_signal = savgol_filter(prev_signal, window_length=15, polyorder=3)
#
#             ydata.append(smoothed_signal[-1])
#             line.set_data(range(len(ydata)), ydata)
#
#         except ValueError:
#             pass
#
#     return line,
#
# ani = animation.FuncAnimation(fig, update, frames=None, init_func=init, blit=True, interval=10)
# plt.xlabel("Time (samples)")
# plt.ylabel("ECG Amplitude (mV)")
# plt.title("Real-Time ECG Signal")
# plt.grid(True)
# plt.show()
#
#


#
# import os
# import threading
# import time
# import tkinter.messagebox
# from tkinter import *
# from tkinter import filedialog
#
# from tkinter import ttk
# from ttkthemes import themed_tk as tk
#
# from mutagen.mp3 import MP3
# from pygame import mixer
#
# root = tk.ThemedTk()
# root.get_themes()                 # Returns a list of all themes that can be set
# root.set_theme("radiance")         # Sets an available theme
#
# # Fonts - Arial (corresponds to Helvetica), Courier New (Courier), Comic Sans MS, Fixedsys,
# # MS Sans Serif, MS Serif, Symbol, System, Times New Roman (Times), and Verdana
# #
# # Styles - normal, bold, roman, italic, underline, and overstrike.
#
# statusbar = ttk.Label(root, text="Welcome to Melody", relief=SUNKEN, anchor=W, font='Times 10 italic')
# statusbar.pack(side=BOTTOM, fill=X)
#
# # Create the menubar
# menubar = Menu(root)
# root.config(menu=menubar)
#
# # Create the submenu
#
# subMenu = Menu(menubar, tearoff=0)
#
# playlist = []
#
#
# # playlist - contains the full path + filename
# # playlistbox - contains just the filename
# # Fullpath + filename is required to play the music inside play_music load function
#
# def browse_file():
#     global filename_path
#     filename_path = filedialog.askopenfilename()
#     add_to_playlist(filename_path)
#
#     mixer.music.queue(filename_path)
#
#
# def add_to_playlist(filename):
#     filename = os.path.basename(filename)
#     index = 0
#     playlistbox.insert(index, filename)
#     playlist.insert(index, filename_path)
#     index += 1
#
#
# menubar.add_cascade(label="File", menu=subMenu)
# subMenu.add_command(label="Open", command=browse_file)
# subMenu.add_command(label="Exit", command=root.destroy)
#
#
# def about_us():
#     tkinter.messagebox.showinfo('About Melody', 'This is a music player build using Python Tkinter by @attreyabhatt')
#
#
# subMenu = Menu(menubar, tearoff=0)
# menubar.add_cascade(label="Help", menu=subMenu)
# subMenu.add_command(label="About Us", command=about_us)
#
# mixer.init()  # initializing the mixer
#
# root.title("Melody")
# root.iconbitmap(r'images/melody.ico')
#
# # Root Window - StatusBar, LeftFrame, RightFrame
# # LeftFrame - The listbox (playlist)
# # RightFrame - TopFrame,MiddleFrame and the BottomFrame
#
# leftframe = Frame(root)
# leftframe.pack(side=LEFT, padx=30, pady=30)
#
# playlistbox = Listbox(leftframe)
# playlistbox.pack()
#
# addBtn = ttk.Button(leftframe, text="+ Add", command=browse_file)
# addBtn.pack(side=LEFT)
#
#
# def del_song():
#     selected_song = playlistbox.curselection()
#     selected_song = int(selected_song[0])
#     playlistbox.delete(selected_song)
#     playlist.pop(selected_song)
#
#
# delBtn = ttk.Button(leftframe, text="- Del", command=del_song)
# delBtn.pack(side=LEFT)
#
# rightframe = Frame(root)
# rightframe.pack(pady=30)
#
# topframe = Frame(rightframe)
# topframe.pack()
#
# lengthlabel = ttk.Label(topframe, text='Total Length : --:--')
# lengthlabel.pack(pady=5)
#
# currenttimelabel = ttk.Label(topframe, text='Current Time : --:--', relief=GROOVE)
# currenttimelabel.pack()
#
#
# def show_details(play_song):
#     file_data = os.path.splitext(play_song)
#
#     if file_data[1] == '.mp3':
#         audio = MP3(play_song)
#         total_length = audio.info.length
#     else:
#         a = mixer.Sound(play_song)
#         total_length = a.get_length()
#
#     # div - total_length/60, mod - total_length % 60
#     mins, secs = divmod(total_length, 60)
#     mins = round(mins)
#     secs = round(secs)
#     timeformat = '{:02d}:{:02d}'.format(mins, secs)
#     lengthlabel['text'] = "Total Length" + ' - ' + timeformat
#
#     t1 = threading.Thread(target=start_count, args=(total_length,))
#     t1.start()
#
#
# def start_count(t):
#     global paused
#     # mixer.music.get_busy(): - Returns FALSE when we press the stop button (music stop playing)
#     # Continue - Ignores all of the statements below it. We check if music is paused or not.
#     current_time = 0
#     while current_time <= t and mixer.music.get_busy():
#         if paused:
#             continue
#         else:
#             mins, secs = divmod(current_time, 60)
#             mins = round(mins)
#             secs = round(secs)
#             timeformat = '{:02d}:{:02d}'.format(mins, secs)
#             currenttimelabel['text'] = "Current Time" + ' - ' + timeformat
#             time.sleep(1)
#             current_time += 1
#
#
# def play_music():
#     global paused
#
#     if paused:
#         mixer.music.unpause()
#         statusbar['text'] = "Music Resumed"
#         paused = FALSE
#     else:
#         try:
#             stop_music()
#             time.sleep(1)
#             selected_song = playlistbox.curselection()
#             selected_song = int(selected_song[0])
#             play_it = playlist[selected_song]
#             mixer.music.load(play_it)
#             mixer.music.play()
#             statusbar['text'] = "Playing music" + ' - ' + os.path.basename(play_it)
#             show_details(play_it)
#         except:
#             tkinter.messagebox.showerror('File not found', 'Melody could not find the file. Please check again.')
#
#
# def stop_music():
#     mixer.music.stop()
#     statusbar['text'] = "Music Stopped"
#
#
# paused = FALSE
#
#
# def pause_music():
#     global paused
#     paused = TRUE
#     mixer.music.pause()
#     statusbar['text'] = "Music Paused"
#
#
# def rewind_music():
#     play_music()
#     statusbar['text'] = "Music Rewinded"
#
#
# def set_vol(val):
#     volume = float(val) / 100
#     mixer.music.set_volume(volume)
#     # set_volume of mixer takes value only from 0 to 1. Example - 0, 0.1,0.55,0.54.0.99,1
#
#
# muted = FALSE
#
#
# def mute_music():
#     global muted
#     if muted:  # Unmute the music
#         mixer.music.set_volume(0.7)
#         volumeBtn.configure(image=volumePhoto)
#         scale.set(70)
#         muted = FALSE
#     else:  # mute the music
#         mixer.music.set_volume(0)
#         volumeBtn.configure(image=mutePhoto)
#         scale.set(0)
#         muted = TRUE
#
#
# middleframe = Frame(rightframe)
# middleframe.pack(pady=30, padx=30)
#
# playPhoto = PhotoImage(file='images/play.png')
# playBtn = ttk.Button(middleframe, image=playPhoto, command=play_music)
# playBtn.grid(row=0, column=0, padx=10)
#
# stopPhoto = PhotoImage(file='images/stop.png')
# stopBtn = ttk.Button(middleframe, image=stopPhoto, command=stop_music)
# stopBtn.grid(row=0, column=1, padx=10)
#
# pausePhoto = PhotoImage(file='images/pause.png')
# pauseBtn = ttk.Button(middleframe, image=pausePhoto, command=pause_music)
# pauseBtn.grid(row=0, column=2, padx=10)
#
# # Bottom Frame for volume, rewind, mute etc.
#
# bottomframe = Frame(rightframe)
# bottomframe.pack()
#
# rewindPhoto = PhotoImage(file='images/rewind.png')
# rewindBtn = ttk.Button(bottomframe, image=rewindPhoto, command=rewind_music)
# rewindBtn.grid(row=0, column=0)
#
# mutePhoto = PhotoImage(file='images/mute.png')
# volumePhoto = PhotoImage(file='images/volume.png')
# volumeBtn = ttk.Button(bottomframe, image=volumePhoto, command=mute_music)
# volumeBtn.grid(row=0, column=1)
#
# scale = ttk.Scale(bottomframe, from_=0, to=100, orient=HORIZONTAL, command=set_vol)
# scale.set(70)  # implement the default value of scale when music player starts
# mixer.music.set_volume(0.7)
# scale.grid(row=0, column=2, pady=15, padx=30)
#
#
# def on_closing():
#     stop_music()
#     root.destroy()
#
#
# root.protocol("WM_DELETE_WINDOW", on_closing)
# root.mainloop()