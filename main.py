from Audio.audio import record
from Desktop.gnome import make_gnome_timer
from multiprocessing import Lock
import Audio
import model

timer_lock = Lock()


while True:
    p = make_gnome_timer(timer_lock, title="Timer", seconds=5*60)
    print("mainthread")
    # p.join()
    wf = record()
    output = model.runModel("Assets/recorded.wav")
    for line in output:
        print(line)



