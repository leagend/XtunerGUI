# python3
# Create Date: 2024-01-30
# Author: 爱科研的瞌睡虫

import argparse

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer


def parse_args():
    parser = argparse.ArgumentParser(
        description='Merge a HuggingFace adapter to LLM')
    # parser.add_argument('model_name_or_path', help='model name or path')
    # parser.add_argument('adapter_name_or_path', help='adapter name or path')
    # parser.add_argument(
    #     'save_dir', help='the directory to save the merged model')
    parser.add_argument(
        '--max-shard-size',
        type=str,
        default='2GB',
        help='Only applicable for LLM. The maximum size for '
        'each sharded checkpoint.')
    parser.add_argument(
        '--offload-folder',
        default=None,
        help='The folder in which to offload the model weights (or where '
        'the model weights are already offloaded).')
    args = parser.parse_args()
    return args


def merge(model_path, adapter_hf_path, save_dir):
    args = parse_args()
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True,
        device_map='auto',
        offload_folder=args.offload_folder,
        trust_remote_code=True)
    tokenizer = AutoTokenizer.from_pretrained(
        model_path,
        trust_remote_code=True,
        encode_special_tokens=True)
    try:
        try_method(adapter_hf_path, args, 'auto', model, save_dir)
    except:
        try_method(adapter_hf_path, args, 'cuda', model, save_dir)

    tokenizer.save_pretrained(save_dir)
    print('Merged All done!')


def try_method(adapter_hf_path, args, device, model, save_dir):
    model_unmerged = PeftModel.from_pretrained(
        model,
        adapter_hf_path,
        device_map=device,
        torch_dtype=torch.float16,
        offload_folder=args.offload_folder,
        is_trainable=False)
    model_merged = model_unmerged.merge_and_unload()
    print(f'Merged Saving to {save_dir}...')
    model_merged.save_pretrained(
        save_dir, max_shard_size=args.max_shard_size)


if __name__ == '__main__':

    model_path = '/root/ft-oasst1/internlm-chat-7b'
    adapter_hf_path = '/root/ft-oasst1/hf4'
    save_dir = '/root/ft-oasst1/merged5'

    merge(model_path, adapter_hf_path, save_dir)
