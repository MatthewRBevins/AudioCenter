from spleeter.separator import Separator
separator = Separator('spleeter:2stems')
print("hi")
if __name__ == '__main__':
    separator.separate_to_file('static/audio/nevergonnabase.wav','static/output')