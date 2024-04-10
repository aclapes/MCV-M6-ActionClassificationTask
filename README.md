# Action classification on HMDB51

## Download the dataset

0. Before downloading any data, install the `unrar` and `ffmpeg` packages with your package manager. In Debian-based distros (e.g., Ubuntu), that is done with the following command: `sudo apt install unrar ffmpeg`.

1. Now, download the videos from the authors' website and decompress them with `unrar`:

    ```bash
        # Download the compressed dataset
        $ wget http://serre-lab.clps.brown.edu/wp-content/uploads/2013/10/hmdb51_org.rar
        # Extract the file
        $ unrar x hmdb51_org.rar
        # Rename the decompressed folder from hmdb51_org -> videos
        $ mv hmdb51_org videos
        # Inspect the contents of the uncompressed folder
        $ ls videos
    ```

You should see 51 folders, one for each action category (`brush_hair`, `cartwheel`, etc), containing video data (`.avi` files):

    ```
        videos/
        |____ brush_hair/
        |     |____ April_09_brush_hair_u_nm_np1_ba_goo_0.avi
        |     |____ April_09_brush_hair_u_nm_np1_ba_goo_1.avi
        |     |____ ...
        |
        |____ cartwheel/
        |     |____ ...
        |
        |____ ...
    ```

For the later training, we'll need the videos converted to frames. This way we don't have to decompress the videos repeatedly every time we want to sample a clip from a video in batch-training.

## Data preparation

We will extract the frames in a separate directory, namely `frames`. Then:

    ```bash
    # Make sure you are in the same directory that contains the videos/ folder
    $ find videos -name "*.avi" -print0 | xargs -0 -I {} sh -c 'original="{}"; modified=$(echo "$original" | sed -e "s|videos|frames|" | sed -e "s|\.[^.]*$||"); mkdir -p $modified; ffmpeg -i $original -loglevel error $modified/frame%05d.jpg'
    ```
    
If run correctly, such long command will create the `frames/` directory with the same structure as `videos/`, but replacing each video file by a directory containing the frames (in .jpg format). It might take from 30' to an hour to extract the frames. 

Graphically:

    ```
    frames/
    |____ brush_hair/
    |     |____ April_09_brush_hair_u_nm_np1_ba_goo_0/
    |     |     |____ frame00001.jpg
    |     |     |____ frame00002.jpg
    |     |     |____ frame00003.jpg
    |     |     |____ ...
    |     |____ April_09_brush_hair_u_nm_np1_ba_goo_1/
    |           |____ frame00001.jpg
    |           |____ frame00002.jpg
    |           |____ frame00003.jpg
    |           |____ ...
    |
    |____ cartwheel/
    |     |____ ...
    |
    |____ ...
    ```

## Custom groundtruth

Do not download and use the groundtruth annotations from the authors' webpage, as we will be a custom version of them that you find in `data/hmbd51/testTrainMulti_601030_splits`.

Differently from the original groundtruth, we will reserve a fixed set of training videos for validation. Therefore, instead of being 70% training and 30% testing data, we will do 60% training, 10% validation, and 30% testing.

Take into account also that HMDB51 was thought to be evaluated in 3-fold cross validation. This means having 3 different train-test partitions, namely split1, split2, and split3. If you check the provided annotations you'll see a file per action category and split (i.e, `<action_label>_test_split<1, 2, or 3>.txt`). However, we will focus on split1 only (ignore split2 and split3 files).

Go and examine any `<action_label>_test_split1.txt` file. As you'll see, there's a line per video with the video name followed by an integer that represents the train-test-validation partition for this particular split. Concretely, 1 indicates this is a training video, 2 for testing, and 3 for validation.

## Run the baseline code

0. You'll need to install the required Python dependencies first. These are in the `requirements.txt` file. Assuming you are using PIP, you can just run:

    ```bash
    $ pip3 install -r requirements.txt
    ```

1. The baseline can then be run executing the `src/train.py` script, which expects one positional argument (the directory of the frames created before) and accept other multiple arguments (or options):

    ```
    $ python3 src/train.py --help
        usage: train.py [-h] [--annotations-dir ANNOTATIONS_DIR]
                        [--clip-length CLIP_LENGTH] [--crop-size CROP_SIZE]
                        [--temporal-subsampling TEMPORAL_SUBSAMPLING]
                        [--model-name MODEL_NAME] [--load-pretrain]
                        [--optimizer-name OPTIMIZER_NAME] [--lr LR] [--epochs EPOCHS]
                        [--batch-size BATCH_SIZE] [--batch-size-eval BATCH_SIZE_EVAL]
                        [--validate-every VALIDATE_EVERY] [--num-workers NUM_WORKERS]
                        [--device DEVICE]
                        frames-dir

        Train a video classification model on HMDB51 dataset.

        positional arguments:
        frames-dir            Directory containing video files

        options:
        -h, --help            show this help message and exit
        --annotations-dir ANNOTATIONS_DIR
                                Directory containing annotation files
        --clip-length CLIP_LENGTH
                                Number of frames of the clips
        --crop-size CROP_SIZE
                                Size of spatial crops (squares)
        --temporal-subsampling TEMPORAL_SUBSAMPLING
                                Receptive field of the model will be (clip_length *
                                temporal_subsampling) / FPS
        --model-name MODEL_NAME
                                Model name as defined in models/model_creator.py
        --load-pretrain       Load pretrained weights for the model (if available)
        --optimizer-name OPTIMIZER_NAME
                                Optimizer name (supported: "adam" and "sgd" for now)
        --lr LR               Learning rate
        --epochs EPOCHS       Number of epochs
        --batch-size BATCH_SIZE
                                Batch size for the training data loader
        --batch-size-eval BATCH_SIZE_EVAL
                                Batch size for the evaluation data loader
        --validate-every VALIDATE_EVERY
                                Number of epochs after which to validate the model
        --num-workers NUM_WORKERS
                                Number of worker processes for data loading
        --device DEVICE       Device to use for training (cuda or cpu)
    ```

If not specified, default values are taken. Check the implementation for that.
