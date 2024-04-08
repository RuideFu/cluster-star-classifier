import math
import sqlite3
from os import error

from numpy import arcsin, cos, deg2rad, rad2deg, sin

data_dir = "/Users/reedfu/Skynet/astromancer-server/data/gaia_clusters_photometry.sqlite"


def import_astrometry(ra, dec):
    radius = 0.01
    data = local_get_data({'ra': ra, 'dec': dec, 'radius': radius})
    while len(data) < 5000:
        radius += 0.01
        tmp = local_get_data({'ra': ra, 'dec': dec, 'radius': radius})
        if len(tmp) > 5000:
            break
        data = tmp
    print("ra: {}, dec: {}, radius: {}, #stars: {}".format(ra, dec, radius, len(data)))
    return data


def local_get_data(query_range):
    try:
        dec = float(query_range['dec'])
        ra = float(query_range['ra'])
        r = float(query_range['radius'])
    except:
        raise error({"error": "Input invalid type"})
    if not 0 <= ra < 360:
        raise error({'error': 'Expected RA in the range [0, 360)'})
    if not -90 <= dec < 90:
        raise error({'error': 'Expected Dec in the range [-90, +90]'})
    if not 0 < r < 90:
        raise error({'error': 'Expected query radius in the range (0, 90)'})

    # Compute the RA/Dec query ranges; handle poles and RA=0/360 wrap
    dec_min, dec_max = dec - r, dec + r
    if dec_min < -90:
        # South Pole in FOV, use the whole RA range
        where = 'dec <= ?'
        args = (dec_max,)
    elif dec_max > 90:
        # North Pole in FOV, use the whole RA range
        where = 'dec >= ?'
        args = (dec_min,)
    else:
        # See http://janmatuschek.de/LatitudeLongitudeBoundingCoordinates
        dra = rad2deg(arcsin(sin(deg2rad(r)) / cos(deg2rad(dec))))
        ra_min, ra_max = ra - dra, ra + dra
        if ra_max >= ra_min + 360:
            # RA spans the whole 360 range
            where = 'dec >= ? and dec <= ?'
            args = (dec_min, dec_max)
        elif ra_min < 0:
            # RA range encloses RA=0 => two separate RA ranges:
            # ra_min + 360 <= ra <= 360 and 0 <= ra <= ra_max
            where = '(ra >= ? or ra <= ?) and dec >= ? and dec <= ?'
            args = (ra_min + 360, ra_max, dec_min, dec_max)
        elif ra_max > 360:
            # RA range encloses RA=360 => two separate RA ranges:
            # ra_min <= ra <= 360 and 0 <= ra <= ra_max - 360
            where = '(ra >= ? or ra <= ?) and dec >= ? and dec <= ?'
            args = (ra_min, ra_max - 360, dec_min, dec_max)
        else:
            # RA range fully within [0, 360)
            where = 'ra >= ? and ra <= ? and dec >= ? and dec <= ?'
            args = (ra_min, ra_max, dec_min, dec_max)
    sqlite_filename = data_dir
    conn = sqlite3.connect(sqlite_filename)
    try:
        # Query RA/Dec region(s) using constraints defined above (should be
        # fast thanks to the indexes) in a subquery; the outer query returns
        # only sources within the circle of radius r using the haversine
        # formula, which is more accurate for small distances
        cur = conn.cursor()
        conn.create_function('asin', 1, math.asin)
        conn.create_function('sqrt', 1, math.sqrt)
        conn.create_function('sin', 1, math.sin)
        conn.create_function('cos', 1, math.cos)
        conn.create_function('radians', 1, math.radians)
        conn.create_function('pow', 2, math.pow)
        sources = cur.execute(
            'select * from (select * from clusters where ' + where +
            ') where asin(sqrt(pow(sin(radians(dec - ?)/2), 2) + '
            'pow(sin(radians(ra - ?)/2), 2)*cos(radians(dec))*?)) <= ?',
            args + (dec, ra, cos(deg2rad(dec)), deg2rad(r) / 2)
        ).fetchall()
    except Exception as e:
        raise error({'error': "Cannot Pull GAIA Database"})
    finally:
        conn.close()
    # Output sources in CSV
    # for source in sources:
    # source_id, ra, dec, r, pmra, pmdec
    # print(','.join(str(x) for x in source))
    return sources
