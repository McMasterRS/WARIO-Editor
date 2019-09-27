
def pitch_ceiling(voice):
    broad_pitch = call(voice, "To Pitch (cc)", 0, 50, 15, "yes", 0.03, 0.45, 0.01, 0.35, 0.14, 800)
    broad_mean_f0: float = call(broad_pitch, "Get mean", 0, 0, "hertz")  # get mean pitch
    if broad_mean_f0 < 400:
        pitch2 = call(voice, "To Pitch (cc)", 0, 50, 15, "yes", 0.03, 0.45, 0.01, 0.35, 0.14, 500)
        pitch2_max_f0: float = call(pitch2, "Get maximum", 0, 0, "hertz", "Parabolic")  # get max pitch
    else:
        pitch2 = call(voice, "To Pitch (cc)", 0, 50, 15, "yes", 0.03, 0.45, 0.01, 0.35, 0.14, 800)
        pitch2_max_f0: float = call(pitch2, "Get maximum", 0, 0, "hertz", "Parabolic")  # get max pitch

    ceiling: float = pitch2_max_f0 * 1.1
    return ceiling

def pitch_floor(voice):
    broad_pitch = call(voice, "To Pitch (cc)", 0, 50, 15, "yes", 0.03, 0.45, 0.01, 0.35, 0.14, 800)
    broad_mean_f0: float = call(broad_pitch, "Get mean", 0, 0, "hertz")  # get mean pitch
    if broad_mean_f0 < 400:
        pitch2 = call(voice, "To Pitch (cc)", 0, 50, 15, "yes", 0.03, 0.45, 0.01, 0.35, 0.14, 500)
        pitch2_min_f0: float = call(pitch2, "Get minimum", 0, 0, "hertz", "Parabolic")  # get min pitch
    else:
        pitch2 = call(voice, "To Pitch (cc)", 0, 50, 15, "yes", 0.03, 0.45, 0.01, 0.35, 0.14, 800)
        pitch2_min_f0: float = call(pitch2, "Get minimum", 0, 0, "hertz", "Parabolic")  # get min pitch

    floor: float = pitch2_min_f0 * 0.9
    return floor

def formant_means(voice):
    sound = parselmouth.Sound(voice)
    max_formant = feature_defaults['Formants']['Pitch Ceiling']
    formants = call(sound, "To Formant (burg)", 0.0025, 5, max_formant, 0.025, 50)
    f1 = call(formants, "Get mean", 1, 0, 0, 'Hertz')
    f2 = call(formants, "Get mean", 2, 0, 0, 'Hertz')
    f3 = call(formants, "Get mean", 3, 0, 0, 'Hertz')
    f4 = call(formants, "Get mean", 4, 0, 0, 'Hertz')
    formants = [f1, f2, f3, f4]
    return formants

def formant_max(voice):
    pitch = call(voice, "To Pitch", 0.0, 50, 500)  # check pitch to set formant settings
    mean_f0 = call(pitch, "Get mean", 0, 0, "Hertz")
    if 170 <= mean_f0 <= 300:
        max_formant = 5500
    elif mean_f0 < 170:
        max_formant = 5000
    else:
        max_formant = 8000
    return max_formant
