import numpy as np
import isx

# N_neurons = 5 # cuantas neuronas a simular
# max_cell_diameter = 10 # max diametro de la neurona en pixeles
# min_cell_diameter = 7 # min diametro de la neurona en pixeles
# min_firerate = 1 #1 a 20 por minuto
# max_firerate = 20 #1 a 20 por minuto https://elifesciences.org/articles/66048
period_ms = 50 # tiempo entre frames en ms (20 Hz => 50 ms)
seconds_time = 20 #1 minuto
num_samples = int(seconds_time*(1000/period_ms))
max_drift = 7  # en cada direccion
video_size = [600, 728]
# ca_level = [2,4]
# filename = '../seminar/videos/simulation.isxd'


def camera_movement():
    x = np.zeros(num_samples)
    y = np.zeros(num_samples)

    def move_and_bounce(vprev, b):
        step = np.random.choice([1, 0, -1], p=[0.01, 0.98, 0.01])
        v = vprev + step
        if v > b:
            return b - 2
        elif v < -b:
            return -b + 2
        else:
            return v

    for i in range(1, num_samples):
        x[i] = move_and_bounce(x[i - 1], max_drift)
        y[i] = move_and_bounce(y[i - 1], max_drift)

    return x, y

def data_drift():
    noise_level = 0.06
    background_scale = 0.5
    corrupted_frame_p = 0# 0.001 # no viene al caso para ustedes
    data_drift = np.zeros((video_size + [num_samples]), dtype=np.float32)

    for i in range(num_samples):
        xd = int(max_drift + x[i])
        yd = int(max_drift + y[i])
        if np.random.random() < corrupted_frame_p:
            data_drift[:, :, i] = data.max()
        else:
            data_drift[:, :, i] = data[xd:xd + video_size[0], yd:yd + video_size[1], i]

    return data_drift + noise_level * np.random.rand(np.prod(video_size + [num_samples])).reshape(
        video_size + [num_samples])

def create_movie(filename, data_drift):
    timing = isx.Timing(num_samples=num_samples, period=isx.Duration.from_msecs(period_ms))
    spacing = isx.Spacing(num_pixels=video_size)
    movie = isx.Movie.write(filename, timing, spacing, np.float32)
    for i in range(timing.num_samples):
        movie.set_frame_data(i, data_drift[:, :, i].astype(np.float32))
    movie.flush()
    del movie

create_movie('../seminar/videos/simulation2.isxd', )