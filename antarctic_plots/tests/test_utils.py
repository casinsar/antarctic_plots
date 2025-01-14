# Copyright (c) 2022 The Antarctic-Plots Developers.
# Distributed under the terms of the MIT License.
# SPDX-License-Identifier: MIT
#
# This code is part of the package:
# Antarctic-plots (https://github.com/mdtanker/antarctic_plots)
#
"""
Tests for utils module.
"""
# %%
import numpy as np
import pandas as pd
import pytest
import verde as vd

from antarctic_plots import regions, utils


def dummy_grid():
    (x, y, z) = vd.grid_coordinates(
        region=[-100, 100, 200, 400],
        spacing=100,
        extra_coords=20,
    )

    # create topographic features
    misfit = y**2

    grid = vd.make_xarray_grid(
        (x, y),
        (misfit, z),
        data_names=("misfit", "upward"),
        dims=("northing", "easting"),
    )

    return grid


def test_RMSE():
    """
    test the RMSE function
    """
    # create some dummy data
    data = np.array([1, 2, 3])
    # calculate the RMSE
    rmse = utils.RMSE(data)
    # test that the RMSE is 0
    assert rmse == 2.0


def test_get_grid_info():
    """
    test the get_grid_info function
    """
    grid = dummy_grid()

    info = utils.get_grid_info(grid.misfit)

    assert info == (100.0, [-100.0, 100.0, 200.0, 400.0], 40000.0, 160000.0, "g")


def test_dd2dms():
    """
    test the dd2dms function
    """

    dd = 130.25

    dms = utils.dd2dms(dd)

    assert dms == "130:15:0.0"


def test_region_to_df():
    """
    test the region_to_df function
    """

    reg = regions.ross_ice_shelf

    df = utils.region_to_df(reg)

    expected = pd.DataFrame(
        {
            "x": [
                -680000.0,
                470000.0,
                -680000.0,
                470000.0,
            ],
            "y": [
                -1420000.0,
                -1420000.0,
                -310000.0,
                -310000.0,
            ],
        }
    )

    pd.testing.assert_frame_equal(df, expected)

    reg2 = utils.region_to_df(df, reverse=True)

    assert reg2 == reg


def test_region_xy_to_ll():
    """
    test the GMT_xy_to_ll function
    """

    reg_xy = regions.ross_ice_shelf

    reg_ll = utils.region_xy_to_ll(reg_xy, dms=True)

    assert reg_ll == [
        "-154:24:41.35269126086496",
        "161:41:10.261402247124352",
        "-84:49:17.300473876937758",
        "-75:34:58.96941344602965",
    ]

    reg_ll = utils.region_xy_to_ll(reg_xy)

    assert reg_ll == [
        -154.41148685868356,
        161.6861837228464,
        -84.8214723538547,
        -75.58304705929056,
    ]


def test_region_to_bounding_box():
    """
    test the region_to_bounding_box function
    """

    reg = regions.ross_ice_shelf

    box = utils.region_to_bounding_box(reg)

    assert box == [-680000.0, -1420000.0, 470000.0, -310000.0]


def test_latlon_to_epsg3031():
    """
    test the latlon_to_epsg3031 function
    """

    df_ll = pd.DataFrame(
        {
            "lat": [-75.583047, -76.296586, -83.129754, -84.82147],
            "lon": [-154.411487, 161.686184, -114.507405, 123.407825],
        }
    )

    df_xy = utils.latlon_to_epsg3031(df_ll)

    expected = pd.DataFrame(
        {
            "x": [
                -680000.0,
                470000.0,
                -680000.0,
                470000.0,
            ],
            "y": [
                -1420000.0,
                -1420000.0,
                -310000.0,
                -310000.0,
            ],
        }
    )
    pd.testing.assert_frame_equal(df_xy[["x", "y"]], expected)


def test_latlon_to_epsg3031_region():
    """
    test the latlon_to_epsg3031 function output a region
    """

    df_ll = pd.DataFrame(
        {
            "lat": [-75.583047, -76.296586, -83.129754, -84.82147],
            "lon": [-154.411487, 161.686184, -114.507405, 123.407825],
        }
    )

    reg = utils.latlon_to_epsg3031(df_ll, reg=True)

    assert reg == pytest.approx(regions.ross_ice_shelf, abs=10)


test_latlon_to_epsg3031_region()


def test_epsg3031_to_latlon():
    """
    test the epsg3031_to_latlon function
    """

    df_xy = utils.region_to_df(regions.ross_ice_shelf)

    df_ll = utils.epsg3031_to_latlon(df_xy)

    expected = pd.DataFrame(
        {
            "x": [
                -680000.0,
                470000.0,
                -680000.0,
                470000.0,
            ],
            "y": [
                -1420000.0,
                -1420000.0,
                -310000.0,
                -310000.0,
            ],
            "lat": [-75.583047, -76.296586, -83.129754, -84.82147],
            "lon": [-154.411487, 161.686184, -114.507405, 123.407825],
        }
    )
    pd.testing.assert_frame_equal(df_ll, expected)


def test_epsg3031_to_latlon_region():
    """
    test the epsg3031_to_latlon function output a region
    """

    df_xy = utils.region_to_df(regions.ross_ice_shelf)

    reg = utils.epsg3031_to_latlon(df_xy, reg=True)

    assert reg == pytest.approx([-154.41, 161.69, -84.82, -75.58], abs=0.01)


def test_points_inside_region():
    """
    test the points_inside_region function
    """
    # first point is inside, second is outside
    df = pd.DataFrame(
        {
            "x": [-50e3, 0],
            "y": [-1000e3, 0],
        }
    )

    assert len(df) == 2

    reg = regions.ross_ice_shelf

    df_in = utils.points_inside_region(df, reg)

    assert len(df_in) == 1
    assert df_in.x.iloc[0] == -50e3

    df_out = utils.points_inside_region(df, reg, reverse=True)

    assert len(df_out) == 1
    assert df_out.x.iloc[0] == 0.0
