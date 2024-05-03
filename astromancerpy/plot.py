import math

import matplotlib.pyplot as plt
import numpy as np


def get_pm_boundary(_cluster):
    segments = 80
    bndry_x = []
    bndry_y = []

    min_pmra = _cluster["pm_ra_range"][0]
    max_pmra = _cluster["pm_ra_range"][1]
    min_pmdec = _cluster["pm_dec_range"][0]
    max_pmdec = _cluster["pm_dec_range"][1]
    bndry_delta = 2 * math.pi / segments
    a = (max_pmra - min_pmra) / 2
    b = (max_pmdec - min_pmdec) / 2
    center_pmra = (max_pmra + min_pmra) / 2
    center_pmdec = (max_pmdec + min_pmdec) / 2
    for i in range(segments):
        theta = i * bndry_delta
        bndry_x.append(a * math.cos(theta) + center_pmra)
        bndry_y.append(b * math.sin(theta) + center_pmdec)
    return [bndry_x, bndry_y]


def get_pm_space_scatter(_data_dict):
    x = [x['pmra'] for x in _data_dict]
    y = [x['pmdec'] for x in _data_dict]

    rf = 0.01  # rejection factor
    x_ordered = x.copy()
    x_ordered.sort()
    y_ordered = y.copy()
    y_ordered.sort()
    x_min = x_ordered[int(len(x_ordered) * rf)]
    x_max = x_ordered[int(len(x_ordered) * (1 - rf))]
    y_min = y_ordered[int(len(y_ordered) * rf)]
    y_max = y_ordered[int(len(y_ordered) * (1 - rf))]

    x = []
    y = []
    for i in range(len(_data_dict)):
        if x_min < _data_dict[i]['pmra'] < x_max and y_min < _data_dict[i]['pmdec'] < y_max:
            x.append(_data_dict[i]['pmra'])
            y.append(_data_dict[i]['pmdec'])
    return [x, y, x_min, x_max, y_min, y_max]


def plot_pm_histogram(_cluster, _data):
    # Start with a square Figure.
    fig = plt.figure(figsize=(20, 20))
    # Add a gridspec with two rows and two columns and a ratio of 1 to 4 between
    # the size of the marginal axes and the main axes in both directions.
    # Also adjust the subplot parameters for a square plot.
    gs = fig.add_gridspec(2, 2, width_ratios=(4, 1), height_ratios=(1, 4),
                          left=0.1, right=0.9, bottom=0.1, top=0.9,
                          wspace=0.05, hspace=0.05)
    # Create the Axes.
    ax = fig.add_subplot(gs[1, 0])
    ax_histx = fig.add_subplot(gs[0, 0], sharex=ax)
    ax_histy = fig.add_subplot(gs[1, 1], sharey=ax)
    # Draw the scatter plot and marginals.
    [x, y, x_min, x_max, y_min, y_max] = get_pm_space_scatter(_data)
    ax.scatter(x, y, marker='.')
    bndry_x, bndry_y = get_pm_boundary(_cluster)
    ax.plot(bndry_x, bndry_y, color='red')
    ax.set(xlim=(x_min, x_max), ylim=(y_min, y_max))
    binwidth = 0.1
    xymax = max(np.max(np.abs(x)), np.max(np.abs(y)))
    lim = (int(xymax / binwidth) + 1) * binwidth
    bins = np.arange(-lim, lim + binwidth, binwidth)
    ax_histx.hist(x, bins=bins)
    ax_histy.hist(y, bins=bins, orientation='horizontal')
    plt.show()


def plot_cluster(_data, rf=1):
    """ Plot a cluster in equatorial and proper motion space side by side
    :param _data: np array; 5 tuples: [ra, dec, pmra, pmdec, label]
    :param rf: number; outlier rejection factor for pm chart in percentile
    """

    fig, ax = plt.subplots(1, 2, figsize=(12, 6))

    cluster_stars = np.array([star for star in _data if star[-1] == 1])
    field_stars = np.array([star for star in _data if star[-1] == 0])

    pmra_min = np.percentile(_data[:, 2], rf)
    pmra_max = np.percentile(_data[:, 2], 100 - rf)
    pmdec_min = np.percentile(_data[:, 3], rf)
    pmdec_max = np.percentile(_data[:, 3], 100 - rf)

    # print(pmra_min, pmra_max, pmdec_min, pmdec_max)
    ax[0].scatter(cluster_stars[:, 0], cluster_stars[:, 1], s=1, color='red')
    ax[0].scatter(field_stars[:, 0], field_stars[:, 1], s=1, color='blue')
    ax[0].set_xlabel("ra")
    ax[0].set_ylabel("dec")

    ax[1].scatter(cluster_stars[:, 2], cluster_stars[:, 3], s=1, color='red')
    ax[1].scatter(field_stars[:, 2], field_stars[:, 3], s=1, color='blue')
    ax[1].set_xlabel("pmra")
    ax[1].set_ylabel("pmdec")
    ax[1].set(xlim=(pmra_min, pmra_max), ylim=(pmdec_min, pmdec_max))

    plt.show()


def plot_cluster_w_test(x_train, y_train, x_test, y_test, rf=1):
    fig, ax = plt.subplots(1, 2, figsize=(12, 6))

    train_cluster_stars = np.array([x_train[i] for i in range(len(x_train)) if y_train[i] == 1])
    train_field_stars = np.array([x_train[i] for i in range(len(x_train)) if y_train[i] == 0])
    test_cluster_stars = np.array([x_test[i] for i in range(len(x_test)) if y_test[i] == 1])
    test_field_stars = np.array([x_test[i] for i in range(len(x_test)) if y_test[i] == 0])

    pmra_min = np.percentile(x_train[:, 0], rf)
    pmra_max = np.percentile(x_train[:, 0], 100 - rf)
    pmdec_min = np.percentile(x_train[:, 1], rf)
    pmdec_max = np.percentile(x_train[:, 1], 100 - rf)

    ax[0].scatter(train_cluster_stars[:, 0], train_cluster_stars[:, 1], s=1, color='red')
    ax[0].scatter(train_field_stars[:, 0], train_field_stars[:, 1], s=1, color='blue')
    ax[0].set(xlim=(pmra_min, pmra_max), ylim=(pmdec_min, pmdec_max))
    ax[0].set_xlabel("pm ra")
    ax[0].set_ylabel("pm dec")
    ax[0].set_title("Training Data")

    pmra_min = np.percentile(x_test[:, 0], rf)
    pmra_max = np.percentile(x_test[:, 0], 100 - rf)
    pmdec_min = np.percentile(x_test[:, 1], rf)
    pmdec_max = np.percentile(x_test[:, 1], 100 - rf)

    ax[1].scatter(test_cluster_stars[:, 0], test_cluster_stars[:, 1], s=1, color='red')
    ax[1].scatter(test_field_stars[:, 0], test_field_stars[:, 1], s=1, color='blue')
    ax[1].set(xlim=(pmra_min, pmra_max), ylim=(pmdec_min, pmdec_max))
    ax[1].set_xlabel("pm ra")
    ax[1].set_ylabel("pm dec")
    ax[1].set_title("Test Data")

    plt.show()
