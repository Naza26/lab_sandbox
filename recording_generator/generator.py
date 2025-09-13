pixel_sizes = [600,728] #alto x ancho # de un ejemplo de multiplane recordings
max_drift = 7 #en cada direccion
N_neurons = 5 # cuantas neuronas a simular
max_cell_diameter = 10 # max diametro de la neurona en pixeles
min_cell_diameter = 7 # min diametro de la neurona en pixeles
seconds_time = 20 #1 minuto
period_ms = 50 # tiempo entre frames en ms (20 Hz => 50 ms)
min_firerate = 1 #1 a 20 por minuto
max_firerate = 20 #1 a 20 por minuto https://elifesciences.org/articles/66048
num_samples = int(seconds_time*(1000/period_ms))
noise_level = 0.06
background_scale = 0.5
corrupted_frame_p = 0# 0.001 # no viene al caso para ustedes
ca_level = [2,4]
filename = '../seminar/videos/simulation.isxd'
