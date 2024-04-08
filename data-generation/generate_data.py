import time

from import_labels import import_labels
from import_astrometries import import_astrometry


def main():
    start_time = time.time()
    object_list = import_labels()
    for obj in object_list:
        ra, dec = obj['ra'], obj['dec']
        import_astrometry(ra, dec)
    print("Total time: {}s".format(time.time() - start_time))



if __name__ == '__main__':
    main()
