import argparse
import os


def train(
    data: str = "/home/example_data", 
    save_folder: str = "/home/train_model",
    initial_epochs: int = 1,
    fine_tune_epochs: int = 2
) -> None:
    # Import libraries
    import matplotlib.pyplot as plt
    import tensorflow as tf
    import tensorflow.keras as keras
    from tensorflow.keras.layers.experimental import preprocessing
    
    # Enable TensorFlow logs to see device placement
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Set to '0' to see all logs
    os.environ['CUDA_VISIBLE_DEVICES'] = '0'  # Set to the GPU ID you want to use


    # Establish GPU growth
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            # Set memory growth to avoid using all GPU memory
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            logical_gpus = tf.config.experimental.list_logical_devices('GPU')
            print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
        except RuntimeError as e:
            print(e)
    else:
        print("No GPU available, using CPU")

    # use example data from the DECIMER project if data is not available
    if not os.path.exists(data):
        raise FileNotFoundError(f"Directory {data} does not exist")

    print(f"Data available in {data}")
    print(f"setting train and validation directories to {data}")
    train_dir = f"{data}/train"
    validation_dir = f"{data}/validation"

    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    print(f"Saving model to {save_folder}")

    # Define batch and image size
    BATCH_SIZE = 650
    IMG_SIZE = (224, 224)

    # Import datasets
    train_dataset = keras.preprocessing.image_dataset_from_directory(
        train_dir, shuffle=True, batch_size=BATCH_SIZE, image_size=IMG_SIZE
    )
    validation_dataset = keras.preprocessing.image_dataset_from_directory(
        validation_dir, shuffle=True, batch_size=BATCH_SIZE, image_size=IMG_SIZE
    )

    # Use buffered prefetching to load images from disk
    AUTOTUNE = tf.data.AUTOTUNE
    train_dataset = train_dataset.prefetch(buffer_size=AUTOTUNE)
    validation_dataset = validation_dataset.prefetch(buffer_size=AUTOTUNE)

    # Define image augmentations and preprocessing steps
    data_augmentation = keras.Sequential(
        [
            preprocessing.RandomFlip("horizontal"),
            preprocessing.RandomFlip("vertical"),
            preprocessing.RandomRotation(0.2),
            preprocessing.RandomContrast(0.1),
            preprocessing.RandomZoom(0.1),
        ]
    )
    preprocess_input = keras.applications.efficientnet.preprocess_input

    # Create the base model from the pre-trained model EfficientNetB0
    # using ImageNet weights and without including the
    IMG_SHAPE = IMG_SIZE + (3,)
    base_model = tf.keras.applications.efficientnet.EfficientNetB0(
        input_shape=IMG_SHAPE, include_top=False, weights="imagenet"
    )
    image_batch, label_batch = next(iter(train_dataset))
    feature_batch = base_model(image_batch)
    print(feature_batch.shape)  # (individual observations,height, width, color)

    # Block the base model layers
    base_model.trainable = False
    base_model.summary()

    # Add classification head, convert features to a single
    # 1280-element vector per image
    global_average_layer = keras.layers.GlobalAveragePooling2D()
    feature_batch_average = global_average_layer(feature_batch)
    print(feature_batch_average.shape)

    # Apply a Dense layer to convert the features into a single
    # prediction per image
    prediction_layer = keras.layers.Dense(1)
    prediction_batch = prediction_layer(feature_batch_average)
    print(prediction_batch.shape)

    # Build the model
    inputs = keras.Input(shape=(224, 224, 3))
    x = data_augmentation(inputs)
    x = preprocess_input(x)
    x = base_model(x, training=False)
    x = global_average_layer(x)
    x = keras.layers.Dropout(0.2)(x)
    outputs = prediction_layer(x)
    model = keras.Model(inputs, outputs)

    # Define the the learning rate and compile the model
    base_learning_rate = 0.0001
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=base_learning_rate),
        loss=keras.losses.BinaryCrossentropy(from_logits=True),
        metrics=["accuracy"],
    )
    model.summary()

    # Run an initial epoch without unfreezing the base model layers
    loss0, accuracy0 = model.evaluate(validation_dataset)

    print("initial loss: {:.2f}".format(loss0))
    print("initial accuracy: {:.2f}".format(accuracy0))

    history = model.fit(
        train_dataset, epochs=initial_epochs, validation_data=validation_dataset
    )

    # If wanted, save that initial model.
    # model.save(
    #   save_folder+'DECIMER-Image-classifier_EfficientNetB0_1_epochs_not_fine_tuned')

    # Generate plot after the first epoch with a fully freezed base model.
    acc = history.history["accuracy"]
    val_acc = history.history["val_accuracy"]
    loss = history.history["loss"]
    val_loss = history.history["val_loss"]

    plt.figure(figsize=(8, 8))
    plt.subplot(2, 1, 1)
    plt.plot(acc, label="Training Accuracy")
    plt.plot(val_acc, label="Validation Accuracy")
    plt.legend(loc="lower right")
    plt.ylabel("Accuracy")
    plt.ylim([min(plt.ylim()), 1])
    plt.title("Training and Validation Accuracy")

    plt.subplot(2, 1, 2)
    plt.plot(loss, label="Training Loss")
    plt.plot(val_loss, label="Validation Loss")
    plt.legend(loc="upper right")
    plt.ylabel("Cross Entropy")
    plt.ylim([0, 1.0])
    plt.title("Training and Validation Loss")
    plt.xlabel("epoch")
    plt.savefig(save_folder + "/ENB0_1_nft.png")
    plt.show()

    # Let's take a look to see how many layers are in the base model
    print("Number of layers in the base model: ", len(base_model.layers))

    # Unfreeze the base model layers
    base_model.trainable = True

    # Fine-tune from this layer onwards
    fine_tune_at = 230

    # Freeze all the layers before the `fine_tune_at` layer
    for layer in base_model.layers[:fine_tune_at]:
        layer.trainable = False

    # Recompile the model
    model.compile(
        loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
        optimizer=tf.keras.optimizers.RMSprop(learning_rate=base_learning_rate / 10),
        metrics=["accuracy"],
    )

    model.summary()

    print(str(len(model.trainable_variables)))

    # Fine tune the model
    total_epochs = initial_epochs + fine_tune_epochs

    history_fine = model.fit(
        train_dataset,
        epochs=total_epochs,
        initial_epoch=history.epoch[-1],
        validation_data=validation_dataset,
    )

    # Save the model
    model.save(save_folder)

    # Generate plot to compare before and after the fine tuning of the base model
    acc += history_fine.history["accuracy"]
    val_acc += history_fine.history["val_accuracy"]
    loss += history_fine.history["loss"]
    val_loss += history_fine.history["val_loss"]

    plt.figure(figsize=(8, 8))
    plt.subplot(2, 1, 1)
    plt.plot(acc, label="Training Accuracy")
    plt.plot(val_acc, label="Validation Accuracy")
    plt.ylim([0.8, 1])
    plt.plot(
        [initial_epochs - 1, initial_epochs - 1], plt.ylim(), label="Start Fine Tuning"
    )
    plt.legend(loc="lower right")
    plt.title("Training and Validation Accuracy")

    plt.subplot(2, 1, 2)
    plt.plot(loss, label="Training Loss")
    plt.plot(val_loss, label="Validation Loss")
    plt.ylim([0, 1.0])
    plt.plot(
        [initial_epochs - 1, initial_epochs - 1], plt.ylim(), label="Start Fine Tuning"
    )
    plt.legend(loc="upper right")
    plt.title("Training and Validation Loss")
    plt.xlabel("epoch")
    plt.savefig(save_folder + "/ENB0_1_nft_2_ft.png")
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train a model")

    parser.add_argument(
        "--data",
        type=str,
        required=False,
        help="Directory containing training data",
        default="/home/example_data",
    )

    parser.add_argument(
        "--save_folder",
        type=str,
        required=False,
        help="Folder to save the trained model",
        default="/home/train_model",
    )
    
    parser.add_argument(
        "--initial_epochs",
        type=int,
        required=False,
        help="Number of initial epochs",
        default=1,
    )
    
    parser.add_argument(
        "--fine_tune_epochs",
        type=int,
        required=False,
        help="Number of fine tuning epochs",
        default=2,
    )

    args = parser.parse_args()
    print("Summary of arguments:")
    print(f"data: {args.data}")
    print(f"save_folder: {args.save_folder}")
    print(f"initial_epochs: {args.initial_epochs}")
    print(f"fine_tune_epochs: {args.fine_tune_epochs}")
    
    train(
        data=args.data,
        save_folder=args.save_folder,
        initial_epochs=args.initial_epochs,
        fine_tune_epochs=args.fine_tune_epochs
    )
    
