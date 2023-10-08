from collections import Counter
from PIL import Image
from midiutil import MIDIFile
from mingus.core import chords

IMAGEN_NAME = 'images/fire.jpeg'
RESOLUTION = (100, 100)
tempo = 30
chord_progression = ["Cmaj7", "Dm7", "Em7", "Fmaj7", "G7", "Am7", "Bm7b5", "Cmaj7"]
# chord_progression = ["Gm", "Cm", "Dm"]
INSTRUMENTS = [[96,96],[45,46],[25,26], [34,35]]
# 0: Scifi 
# 1: Strings
# 2: Guitar
INSTRUMENTS_TYPE = 0




NOTES = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
OCTAVES = list(range(11))
NOTES_IN_OCTAVE = len(NOTES)

errors = {
    'notes': 'Bad input, please refer this spec-\n'
}


def swap_accidentals(note):
    if note == 'Db':
        return 'C#'
    if note == 'D#':
        return 'Eb'
    if note == 'E#':
        return 'F'
    if note == 'Gb':
        return 'F#'
    if note == 'G#':
        return 'Ab'
    if note == 'A#':
        return 'Bb'
    if note == 'B#':
        return 'C'

    return note

def note_to_number(note: str, octave: int) -> int:
    note = swap_accidentals(note)
    assert note in NOTES, errors['notes']
    assert octave in OCTAVES, errors['notes']

    note = NOTES.index(note)
    note += (NOTES_IN_OCTAVE * octave)

    assert 0 <= note <= 127, errors['notes']

    return note

def map_range(value, from_min, from_max, to_min, to_max):

    value = max(min(value, from_max), from_min)
    
    mapped_value = (value - from_min) * (to_max - to_min) / (from_max - from_min) + to_min
    
    return mapped_value

def mantener_elementos_unicos_seguidos(lista):
    lista_resultado = [lista[0]]
    
    for i in range(1, len(lista)):
        if lista[i] != lista[i - 1]:
            lista_resultado.append(lista[i])
    
    return lista_resultado

def convertir_rango(arr, n):

    if n <= 0:
        raise ValueError("El valor de 'n' debe ser mayor que 0")

    max_valor = max(arr)
    
    factor_escala = n / max_valor

    nuevo_arr = [int(valor * factor_escala) for valor in arr]

    return nuevo_arr

def imageToMidi():


    imagen = Image.open(IMAGEN_NAME)  
    nueva_resolucion = RESOLUTION  
    imagen = imagen.resize(nueva_resolucion, Image.NEAREST)
    rgb_im = imagen.convert('RGB')


    array_of_notes = []
    for chord in chord_progression:
        array_of_notes.extend(chords.from_shorthand(chord))



    array_of_note_numbers = []
    for note in array_of_notes:
        OCTAVE = 4
        array_of_note_numbers.append(note_to_number(note, OCTAVE))


    ancho, alto = imagen.size

    pixel_rgb = []

    for y in range(alto):
        for x in range(ancho):
            r, g, b = rgb_im.getpixel((x, y))

            aux = int((r + g + b) / 3)
            pixel_rgb.append(aux)

        
    finalPixel = mantener_elementos_unicos_seguidos(pixel_rgb)


    finalPixel = convertir_rango(finalPixel, len(array_of_note_numbers)-1)

    finalPixel = finalPixel[:1024]

    track = 0
    channel = 0
    time = 0  
    duration = 1/4  
    volume = 100  


    midi = MIDIFile(2)

    midi.addTempo(0, 0, tempo)


    trayectoria = list(range(0, 128, 8)) + list(range(128, 0, -8))
    velocidad = list(range(60, 120, 6)) + list(range(120, 60, -6))


    for i, pitch in enumerate(finalPixel):
        tiempo = i / 4  

        deg = trayectoria[i%len(trayectoria)]
        vel = velocidad[i%len(velocidad)]

        midi.addControllerEvent(0, channel, tiempo, 10, deg)
        midi.addControllerEvent(0, channel, tiempo, 7, vel)  

        if(i%1==0):
            midi.addNote(0, channel, array_of_note_numbers[pitch] + 7, tiempo, duration, volume)
        
        if(i%16==0):
            midi.addNote(1, 1, array_of_note_numbers[pitch], tiempo, 4, volume)


    midi.addProgramChange(0,0,0,INSTRUMENTS[INSTRUMENTS_TYPE][0])
    midi.addProgramChange(1,1,0,INSTRUMENTS[INSTRUMENTS_TYPE][1])




    with open('output.mid', 'wb') as archivo_midi:
        midi.writeFile(archivo_midi)

    print("Archivo MIDI creado ✅")

def midi_to_mp3():

    from pydub import AudioSegment
    import os


    archivo_midi = "./output.mid"
    archivo_mp3 = "./audio/salida.mp3"

    fluidsynth_cmd = "fluidsynth -T wav -F ./audio/sonification.wav ./soundfont.sf2 " + archivo_midi
    os.system(fluidsynth_cmd)

    print("Archivo WAV generado: sonification.wav")




imageToMidi()
midi_to_mp3()