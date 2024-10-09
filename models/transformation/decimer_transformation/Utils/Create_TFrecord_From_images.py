import argparse
import os
import pickle
from datetime import datetime

import gdown
import tensorflow as tf

gpus = tf.config.experimental.list_physical_devices("GPU")
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)

def create_pickle_files(smile_path, base_image_path, tokenizer_path=None):
    
    if tokenizer_path is None:
        gdown.download(
            "https://drive.google.com/uc?id=1WxeBTGK2gwigiEhlD_3IoeaAqcObHZWK",
            "tokenizer_SMILES.pkl",
            quiet=False,
        )
        tokenizer = pickle.load(open("tokenizer_SMILES.pkl", "rb"))
    else:
        tokenizer = pickle.load(open(tokenizer_path, "rb"))

    with open(smile_path, "r") as txt_file:
        smiles = txt_file.read()

    all_smiles = []
    all_img_name = []

    for line in smiles.split("\n"):
        tokens = line.split(",")

        images_id = str(tokens[0]) + ".png"
        modeify_token = " ".join(tokens[1])

        try:
            smiles = (
                "<start> " + str(modeify_token.replace("][", "] [").rstrip()) + " <end>"
            )
        except IndexError as e:
            print(e, flush=True)

        full_image_path = base_image_path + images_id

        all_img_name.append(full_image_path)
        all_smiles.append(smiles)

    train_captions, img_name_vector = (all_smiles, all_img_name)

    print("Total number of selected SMILES Strings: ", len(train_captions), "\n")
    trans_seq = tokenizer.texts_to_sequences(train_captions)

    cap_vector = tf.keras.preprocessing.sequence.pad_sequences(
        trans_seq, padding="post"
    )

    # save the images and captions in a pickle file
    if not os.path.exists("./data"):
        os.makedirs("./data")

    start = 0
    end = 26800
    loop_round = int(len(img_name_vector) / end) if len(img_name_vector) > 26800 else 1
    start_x = 0
    for i in range(loop_round):
        imgs_path = img_name_vector[start : (start + end)]
        caps_path = cap_vector[start : (start + end)]

        with open(
            "./data/Images_Path_" + str(start_x) + "_" + str(start_x) + ".pkl", "wb"
        ) as file:
            pickle.dump(imgs_path, file)

        with open(
            "./data/Capts_Path_" + str(start_x) + "_" + str(start_x) + ".pkl", "wb"
        ) as file:
            pickle.dump(caps_path, file)

        print("Total Train_Images: ", len(imgs_path))
        print("Total SELFIES_Images: ", len(caps_path))

        start = start + len(imgs_path)
        start_x = start_x + 1

    return start_x

def _bytes_feature(value):
    """Returns a bytes_list from a string / byte."""
    if isinstance(value, type(tf.constant(0))):
        value = (
            value.numpy()
        )  # BytesList won't unpack a string from an EagerTensor.
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))


def create_tfrecord_files(ind_last_file):
    for ind in range(ind_last_file):
        train_captions = pickle.load(
            open("./data/Capts_Path_" + str(ind) + "_" + str(ind) + ".pkl", "rb")
        )
        img_name_vector = pickle.load(
            open("./data/Images_Path_" + str(ind) + "_" + str(ind) + ".pkl", "rb")
        )

        writer = tf.io.TFRecordWriter(f"./data/train-{ind}.tfrecord")
        for i in range(len(img_name_vector)):
            feature = {
                "image_raw": _bytes_feature(tf.io.read_file(img_name_vector[i])),
                "caption": _bytes_feature(train_captions[i].tostring()),
            }
            example = tf.train.Example(features=tf.train.Features(feature=feature))
            serialized = example.SerializeToString()
            writer.write(serialized)
            
        print(f"train-{ind}.tfrecord write to tfrecord success!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create TFrecord from images")
    parser.add_argument(
        "--smile_path",
        type=str,
        default="../../example_data/smiles.txt",
        help="Path to the smiles file",
    )

    parser.add_argument(
        "--base_image_path",
        type=str,
        default="../../example_data/",
        help="Path to the images",
    )

    parser.add_argument(
        "--tokenizer_path",
        type=str,
        default=None,
    )

    args = parser.parse_args()
    ind_last_file = create_pickle_files(args.smile_path, args.base_image_path, args.tokenizer_path)
    create_tfrecord_files(ind_last_file)
   
    print(datetime.now().strftime("%Y/%m/%d %H:%M:%S"), "Process completed", flush=True)
