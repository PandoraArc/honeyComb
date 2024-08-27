# © Kohulan Rajan - 2020
import os
import pickle
from datetime import datetime

import tensorflow as tf

print(datetime.now().strftime("%Y/%m/%d %H:%M:%S"), "Process started", flush=True)

# Initial Setup for GPU
os.environ["CUDA_VISIBLE_DEVICES"] = "2"

gpus = tf.config.experimental.list_physical_devices("GPU")
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)


def main():
    Smiles_Path = "train_data/decimal_results.csv"
    
    # Images_Path = "example_data/DECIMER_test_1.png"

    img_name_vector, cap_vector, tokenizer, max_length, img_name_val = data_loader(Smiles_Path)

    print("Tokens: ", tokenizer, flush=True)
    print("Max length of attention weights: ", max_length, flush=True)
    print("Total train files:", len(img_name_vector), flush=True)

    with open("pkl/tokenizer_TPU_Stereo.pkl", "wb") as file:
        pickle.dump(tokenizer, file)

    with open("pkl/max_length_TPU_Stereo.pkl", "wb") as file:
        pickle.dump(max_length, file)

    start = 0
    end = 2
    start_x = 0

    for i in range(int(len(img_name_vector) / end)):

        imgs_path = img_name_vector[start : (start + end)]
        caps_path = cap_vector[start : (start + end)]


        
        with open(
            "pkl/Images_" + str(start_x) + "_" + str(start_x) + ".pkl", "wb"
        ) as file:
            pickle.dump(imgs_path, file)

        with open(
            "pkl/Capts_" + str(start_x) + "_" + str(start_x) + ".pkl", "wb"
        ) as file:
            pickle.dump(caps_path, file)

        print("Total Train_Images: ", len(imgs_path), flush=True)
        print("Total SELFIES_Images: ", len(caps_path), flush=True)

        start = start + len(imgs_path)
        start_x = start_x + 1


    # #try single pic
    # for i in range(int(len(img_name_vector))):
    #     imgs_path = img_name_vector[start_x]
    #     caps_path = cap_vector[start_x]

    #     with open(
    #         "pkl/Images" + str(start_x) + "_" + str(start_x) + ".pkl", "wb"
    #     ) as file:
    #         pickle.dump(imgs_path, file)

    #     with open(
    #         "pkl/Capts" + str(start_x) + "_" + str(start_x) + ".pkl", "wb"
    #     ) as file:
    #         pickle.dump(caps_path, file)

    #     print("Total Train_Images: ", len(imgs_path), flush=True)
    #     print("Total SELFIES_Images: ", len(caps_path), flush=True)

    #     start = start + len(imgs_path)
    #     start_x = start_x + 1

    print(datetime.now().strftime("%Y/%m/%d %H:%M:%S"), "Process completed", flush=True)


def data_loader(Smiles_Path):
    # read the Captions file
    with open(Smiles_Path, "r") as txt_file:
        smiles = txt_file.read()

    # storing the captions and the image name in vectors
    all_smiles = []
    all_img_name = []

    for line in smiles.split("\n"):
        # Split the ID and SMILES to separate tokens
        tokens = line.split(",")
        
        # Check if tokens have at least 2 elements (ID and SMILES)
        if len(tokens) < 2:
            continue  # Skip lines that don't have both an ID and a SMILES string
    

        image_id = str(tokens[0]) + ".png"
        # Add start and end annotations to SMILES string
        try:
            SMILES_ = (
                "<start> " + str(tokens[1].replace("][", "] [").rstrip()) + " <end>"
            )
        except IndexError as e:
            print(e, flush=True)

        # PATH of training images
        full_image_path = "train_data/" + image_id

        all_img_name.append(full_image_path)
        all_smiles.append(SMILES_)

    train_captions, img_name_vector = (all_smiles, all_img_name)

    print("Total number of selected SMILES Strings: ", len(train_captions), flush=True)

    # Defining the maximum number of tokens to generate
    def calc_max_length(tensor):
        return max(len(t) for t in tensor)

    # choosing the top 500 words from the vocabulary
    top_k = 500
    tokenizer = tf.keras.preprocessing.text.Tokenizer(
        num_words=top_k, oov_token="<unk>", lower=False, filters=""
    )
    tokenizer.fit_on_texts(train_captions)
    train_seqs = tokenizer.texts_to_sequences(train_captions)

    tokenizer.word_index["<pad>"] = 0
    tokenizer.index_word[0] = "<pad>"

    # padding each vector to the max_length of the captions, if the max_length parameter is not provided, pad_sequences calculates that automatically
    cap_vector = tf.keras.preprocessing.sequence.pad_sequences(
        train_seqs, padding="post"
    )

    # calculating the max_length used to store the attention weights
    max_length = calc_max_length(train_seqs)

    # img_name_train, img_name_val, cap_train, cap_val = (
    #     img_name_vector[0:1340000],
    #     img_name_vector[1340000:1440000],
    #     cap_vector[0:1340000],
    #     cap_vector[1340000:1440000],
    # )
    
    #9:1 train:validation
    total_images = len(train_captions)
    split_index = int(0.9 * total_images)  
    img_name_train = img_name_vector[:split_index]  
    img_name_val = img_name_vector[split_index:]    
    cap_train = cap_vector[:split_index] 
    cap_val = cap_vector[split_index:]    


    print(
        str(len(img_name_train)),
        str(len(img_name_val)),
        str(len(cap_train)),
        str(len(cap_val)),
    )

    return img_name_train, cap_train, tokenizer, max_length, img_name_val


if __name__ == "__main__":
    main()
