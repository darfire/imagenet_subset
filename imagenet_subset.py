import sys
import argparse
import glob
import shutil
import os
import random

import tqdm


def parse_args():
  parser = argparse.ArgumentParser()

  parser.add_argument('-i', '--imagenet-dir', help='The imagenet data (needs to have train and val subdirectories)', required=True)
  parser.add_argument('-o', '--output-dir', help='Output directory', required=True)
                      
  parser.add_argument('-c', '--n-classes', help='number of classes to extract', default=-1, type=int)
  parser.add_argument('-n', '--n-items-per-class', help='number of items per class', default=-1, type=int)
  parser.add_argument('-N', '--n-validation-items', help='number of validation items', default=-1, type=int)

  parser.add_argument('-p', '--percentage-train', help='percentage of training items, applied on each class', default=-1, type=float)
  parser.add_argument('-P', '--percentage-val', help='percentage of validation items', default=-1, type=float)

  return parser.parse_args()


if __name__ == '__main__':
  args = parse_args()

  if os.path.exists(args.output_dir):
    print("Output path  exists. Bailing out")
    sys.exit(1)

  train_dir = os.path.join(args.imagenet_dir, 'train')
  val_dir = os.path.join(args.imagenet_dir, 'val')

  print('Loading file names')

  train_files = glob.glob(f'{train_dir}/*.JPEG')
  val_files = glob.glob(f'{val_dir}/*.JPEG')

  print(f'Found {len(train_files)} training files and {len(val_files)} validation files.')

  print('Extracting classes')

  per_class = {}

  for fname in tqdm.tqdm(train_files):
    bname = os.path.basename(fname)
    suffix, ext = os.path.splitext(bname)

    cls, id = suffix.split('_')

    if cls not in per_class:
      per_class[cls] = []

    per_class[cls].append(fname)

  for k, v in per_class.items():
    print(f'{k}: {len(v)}')

  all_classes = list(per_class.keys())

  random.shuffle(all_classes)

  n_classes = args.n_classes

  if n_classes == -1:
    n_classes = len(all_classes)

  output_train = {}

  for c in all_classes[:n_classes]:
    all_items = list(per_class[c])

    if args.n_items_per_class >= 0:
      n = args.n_items_per_class
    else:
      n = int(args.percentage_train * len(all_items))

    random.shuffle(all_items)

    output_train[c] = all_items[:n]

  if args.n_validation_items >= 0:
    n = args.n_validation_items
  else:
    n = args.percentage_val * len(val_files)

  random.shuffle(val_files)

  output_val_files = val_files[:n]

  output_train_files = sum(output_train.values(), [])

  output_train_dir = os.path.join(args.output_dir, 'train')
  output_val_dir = os.path.join(args.output_dir, 'val')

  os.makedirs(output_train_dir)
  os.makedirs(output_val_dir)

  print("Copying train files")
  for fname in tqdm.tqdm(output_train_files):
    bname = os.path.basename(fname)
    shutil.copyfile(fname, os.path.join(output_train_dir, bname))

  print("Copying val files")
  for fname in tqdm.tqdm(output_val_files):
    bname = os.path.basename(fname)
    shutil.copyfile(fname, os.path.join(output_val_dir, bname))
