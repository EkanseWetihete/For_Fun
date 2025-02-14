# -*- coding: utf-8 -*-
from transformers import pipeline
import os
import re

def load_txt(file_path):
    print(f"Loading text file {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

def save_txt(file_path, text):
    print(f"Saving summary to file {file_path}...")
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text)

def split_into_chunks(text, chunk_size=1024, overlap=200):
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    current_chunk = []

    current_length = 0
    for sentence in sentences:
        sentence_length = len(sentence)
        if current_length + sentence_length + 1 <= chunk_size:
            current_chunk.append(sentence)
            current_length += sentence_length + 1
        else:
            chunks.append(' '.join(current_chunk))
            current_chunk = [sentence]
            current_length = sentence_length + 1

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    for i in range(1, len(chunks)):
        overlap_chunk = ' '.join(chunks[i - 1].split()[-overlap:])
        chunks[i] = overlap_chunk + ' ' + chunks[i]

    return chunks

def process_files(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    summarizer = pipeline("summarization")

    for file_name in os.listdir(input_folder):
        if file_name.endswith('.txt'):
            file_path = os.path.join(input_folder, file_name)
            text_data = load_txt(file_path)

            print("Chunking text data...")
            chunk_size = 824
            overlap = 200
            chunks = split_into_chunks(text_data, chunk_size, overlap)
            print("Chunking was successful!")
            
            print("Summarizing each chunk...")
            summaries = []
            
            failed = False
            for index, chunk in enumerate(chunks):
                try:
                    print()
                    print(chunks[index])
                    print(f"Chunk {index + 1} out of {len(chunks)}")
                    min_length = min(25, len(chunk.split()))
                    summary = summarizer(chunks[index], max_length=50, min_length=min_length, do_sample=False)
                    summaries.append(summary[0]['summary_text'])
                except Exception as e:
                    print(f"Error processing file {file_name}: {e}")
                    failed = True
                    
            output_file_path = os.path.join(output_folder, file_name)
            
            if failed:
                try:
                    print("Summerization had some problems. Saving unfinished data.")
                    output_file_path = os.path.join(output_file_path, " - Possibly failed data")
                except Exception:
                    print("change output directory failed.")
            else: 
                print("Summarization completed!")

            combined_summary = " ".join(summaries)
            save_txt(output_file_path, combined_summary)
            print(f"Summarization saved successfully for {file_name}!\n")
            

def main():
    input_folder = "TXT_files"
    output_folder = "Summaries"

    process_files(input_folder, output_folder)

main()