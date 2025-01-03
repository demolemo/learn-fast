import os
import torch
import whisper
import logging
import argparse
from pydub import AudioSegment
from transformers import AutoTokenizer, AutoModelForCausalLM

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CHUNK_SIZE_MB = 24 # from pydub docs
MODEL_NAME = 'Qwen/Qwen2.5-7B-Instruct'
MAX_CONTEXT_LENGTH = 131072
MAX_NEW_TOKENS = 8192


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file-name', type=str, default='lecture2.mp3')
    parser.add_argument('--cold-start', type=bool, default=True, action=argparse.BooleanOptionalAction)
    return parser.parse_args()


def chunk_audio(file_name):
    audio_segment = AudioSegment.from_mp3(file_name)
    total_len_ms = int(audio_segment.duration_seconds * 1000)

    file_size_mb = os.path.getsize(file_name) / (1024 * 1024)
    number_of_chunks = int(file_size_mb // CHUNK_SIZE_MB) + 1
    stamps = range(0, total_len_ms + 1, total_len_ms // number_of_chunks)

    # create a folder to store the chunks
    os.makedirs('temp_audio_chunks', exist_ok=True)

    chunk_paths_mp3 = []
    clean_file_name = file_name.split('.')[0]

    for start, finish in zip(stamps[:-1], stamps[1:]):
        current_audio_segment = audio_segment[start:finish]
        chunk_name = f'{clean_file_name}_{start}_{finish}'
        chunk_name_mp3 = chunk_name + '.mp3'
        chunk_path_mp3 = os.path.join('temp_audio_chunks', chunk_name_mp3)
        chunk_paths_mp3.append(chunk_path_mp3)

        current_audio_segment.export(chunk_path_mp3, format='mp3')
        logging.info(f'audio chunk exported: {chunk_path_mp3}')
    return chunk_paths_mp3


def load_whisper_model():
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = whisper.load_model('turbo', device=device)
    return model


def transcribe_chunks(model):
    input_dir = 'temp_audio_chunks'
    output_dir = 'temp_text_chunks'
    os.makedirs(output_dir, exist_ok=True)
    
    for filename in sorted(os.listdir(input_dir)):
        transcribe_chunk(model, filename, input_dir, output_dir) 
    torch.cuda.empty_cache()
    return None


def transcribe_chunk(model, filename, input_dir, output_dir):
    chunk_path_mp3 = os.path.join(input_dir, filename)
    result = model.transcribe(chunk_path_mp3)
    chunk_text = result['text']
    chunk_path_txt = os.path.join(output_dir, filename.split('.')[0] + '.txt')
    with open(chunk_path_txt, 'a') as f:
        f.write(chunk_text)
    f.close()
    logging.info(f'text chunk transcribed: {chunk_path_txt}')
    return None


def merge_chunks():
    '''merge text chunks in order to get a single text file'''

    chunks_texts = []
    for chunk_name in sorted(os.listdir('temp_text_chunks')):
        chunk_path_txt = os.path.join('temp_text_chunks', chunk_name)
        with open(chunk_path_txt, 'r') as f:
            chunk_text = f.read()
        f.close()
        chunks_texts.append(chunk_text)
    return ''.join(chunks_texts)


def load_model_and_tokenizer():
    logger.info('Loading summarization model')
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        device_map='sequential',
        torch_dtype='auto'
    )
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    return model, tokenizer


def save_merged_text(merged_text):
    with open('merged_text.txt', 'w') as f:
        f.write(merged_text)
    f.close()
    return None


def open_merged_text():
    with open('merged_text.txt', 'r') as f:
        merged_text = f.read()
    f.close()
    return merged_text


def summarize_text(merged_text, model, tokenizer):
    prompt = "Summarize the following text in the language of the text: " 

    messages = [
        {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
        {"role": "user", "content": prompt + merged_text}
    ]

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    if len(text) > MAX_CONTEXT_LENGTH:
        logging.info(f'Text length exceeds the maximum context length of {MAX_CONTEXT_LENGTH} tokens.')
        text = text[:MAX_CONTEXT_LENGTH]

    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=MAX_NEW_TOKENS,
    )

    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    print(len(response))
    return response


def save_summary(summary):
    with open('summary.txt', 'w') as f:
        f.write(summary)
    f.close()
    return None


def clean_up():
    if os.path.exists('temp_audio_chunks'):
        for filename in os.listdir('temp_audio_chunks'):
            os.remove(os.path.join('temp_audio_chunks', filename))

    if os.path.exists('temp_text_chunks'):
        for filename in os.listdir('temp_text_chunks'):
            os.remove(os.path.join('temp_text_chunks', filename))

    #if os.path.exists('merged_text.txt'):
    #    os.remove('merged_text.txt')

    try:
        if os.path.exists('temp_audio_chunks'): 
            os.rmdir('temp_audio_chunks')
    except OSError as e:
        logging.error(f'Error deleting temp_audio_chunks: {e}')
    except Exception as e:
        logging.error(f'Error deleting temp_audio_chunks: {e}')

    try:
        if os.path.exists('temp_text_chunks'):
            os.rmdir('temp_text_chunks')
    except OSError as e:
        logging.error(f'Error deleting temp_text_chunks: {e}')
    except Exception as e:
        logging.error(f'Error deleting temp_text_chunks: {e}')  


def summarize_text_pipeline(file_name):
    logger.info(f'Processing file: {file_name}')
    chunk_audio(file_name)
    model = load_whisper_model()
    transcribe_chunks(model)
    merged_text = merge_chunks()
    save_merged_text(merged_text)
    
    merged_text = open_merged_text()
    model, tokenizer = load_model_and_tokenizer()
    summary = summarize_text(merged_text, model, tokenizer)
    save_summary(summary)
    clean_up()
    return None
