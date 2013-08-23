import cloud
import datetime
import glob
import os
import utils.hdf5_getters as hdf5getters

# import numpy
# import sqlite3
# import sys
# import time


def get_base_path():
    if cloud.running_on_cloud():
        base_path = "/data/million_song_data/"
    else:
        base_path = "/Users/andrebattagello/Projects/TG/million_song/data/"

    return base_path


subset_path = os.path.join(get_base_path() + "million_song_subset")
subset_data_path = os.path.join(subset_path, "data")
subset_additional_file_data_path = os.path.join(subset_path, "additional_files")

print subset_path

assert os.path.isdir(subset_path), "Wrong base path"


def strtimedelta(start_time, stop_time):
    return str(datetime.timedelta(seconds=stop_time-start_time))


def apply_to_all_files(base_dir, func=lambda x: x, file_extension=".h5"):
    """
    Traverse a base directory and all its subdirectories,
    and apply the function `func` to all the files with the extension `file_extension`
    When there's no `func`, the method only the counts the number of songs files
    """

    file_count = 0
    for root, dirs, files in os.walk(base_dir):
        files = glob.glob(os.path.join(root, "*" + file_extension))
        file_count += len(files)
        for f in files:
            # print f
            func(f)

    return file_count

all_artists_name = set()


def get_artist_name_from_track(track_filename):
    print "[Processing file]: ", track_filename
    h5_file = hdf5getters.open_h5_file_read(track_filename)
    artist_name = hdf5getters.get_artist_name(h5_file)
    num_songs = hdf5getters.get_num_songs(h5_file)
    print "\t- [Artist name found]: ", artist_name
    print "\t- [Num songs]:", num_songs
    all_artists_name.add(artist_name)
    h5_file.close()



# if __name__ == '__main__':
#     # jid = cloud.call(apply_to_all_files, subset__vol="dataset-volume")
