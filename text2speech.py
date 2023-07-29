# encoding: utf-8
import argparse
import os
import xml.etree.ElementTree as ET
import codecs

import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.speech import AudioDataStream


def get_ssml(args):
    root = ET.Element('speak', version='1.0')
    root.set('xmlns', 'http://www.w3.org/2001/10/synthesis')
    root.set('xmlns:mstts', 'https://www.w3.org/2001/mstts')
    root.set('xml:lang', args.lang)
    voice = ET.SubElement(root, 'voice', name='zh-CN-XiaomoNeural' if args.lang == 'zh-CN' else 'en-US-AriaNeural')
    express_as = ET.SubElement(voice, 'mstts:express-as', style=args.emotion, styledegree=str(args.intensity))
    express_as.text = args.text
    return ET.tostring(root, method='xml').decode('utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--save_path', type=str, default='audio')
    parser.add_argument('--text', type=str, default='')
    parser.add_argument('--lang', type=str, choices=['zh-CN', 'en-US'], default='zh-CN')
    parser.add_argument('--emotion', type=str, choices=['neutral', 'happy', 'sad',
                                                        'angry', 'fearful', 'contempt'
                                                        'disgust', 'surprised'], default='neutral')
    parser.add_argument('--intensity', type=int, default=1)

    args = parser.parse_args()
    assert 0 < args.intensity <= 2

    with open('key.txt') as f:
        key, region = f.read().split(' ')
    speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
    if not os.path.exists(args.save_path):
        os.makedirs(args.save_path)
    audio_config = speechsdk.audio.AudioOutputConfig(filename=os.path.join(args.save_path, 'file.wav'),
                                                     use_default_speaker=False)
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    ssml = get_ssml(args)
    # print(ssml)
    result = speech_synthesizer.speak_ssml_async(ssml).get()  # 这个是SSML文本
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print('Done')
        stream = AudioDataStream(result)
        stream.save_to_wav_file(os.path.join(args.save_path, 'file.wav'))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")
