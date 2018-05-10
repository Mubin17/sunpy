from __future__ import absolute_import, division, print_function

from datetime import datetime, date
import re

from sunpy import time
from sunpy.time import parse_time, is_time_in_given_format, get_day, find_time
import sunpy.time.astropy_time as ap

import astropy.time
import numpy as np
import pandas
from sunpy.extern.six.moves import range

import pytest

LANDING = ap.Time('1966-02-03', format='isot')


def test_parse_time_24():
    dt = parse_time("2010-10-10T24:00:00")
    assert dt == ap.Time('2010-10-11')
    assert dt.format == 'isot'
    assert dt.scale == 'utc'


def test_parse_time_24_2():
    dt = parse_time("2010-10-10T24:00:00.000000")
    assert dt == ap.Time('2010-10-11')
    assert dt.format == 'isot'
    assert dt.scale == 'utc'


def test_parse_time_trailing_zeros():
    # see issue #289 at https://github.com/sunpy/sunpy/issues/289
    dt = parse_time('2010-10-10T00:00:00.00000000')
    assert dt == ap.Time('2010-10-10')
    assert dt.format == 'isot'
    assert dt.scale == 'utc'


def test_parse_time_tuple():
    dt = parse_time((1966, 2, 3))
    assert dt == LANDING
    assert dt.format == 'iso'
    assert dt.scale == 'utc'


def test_parse_time_int():
    # Once https://github.com/astropy/astropy/issues/6970 is fixed,
    # remove .jd from equality check
    dt1 = parse_time(765548612.0, 'utime')
    assert dt1.jd == ap.Time('2003-4-5T12:23:32').jd
    assert dt1.format == 'utime'

    dt2 = parse_time(1009685652.0, 'utime')
    assert dt2.jd == ap.Time('2010-12-30T4:14:12').jd
    assert dt2.format == 'utime'


def test_parse_time_pandas_timestamp():
    ts = pandas.Timestamp(datetime(1966, 2, 3))

    dt = parse_time(ts)

    assert isinstance(dt, astropy.time.Time)
    assert dt == LANDING


def test_parse_time_pandas_series():
    inputs = [datetime(2012, 1, i) for i in range(1, 13)]
    ind = pandas.Series(inputs)
    as_inps = ap.Time(inputs)

    dts = parse_time(ind)

    assert isinstance(dts, astropy.time.Time)
    assert np.all(dts == as_inps)


def test_parse_time_pandas_series_2():
    inputs = [[datetime(2012, 1, 1, 0, 0), datetime(2012, 1, 2, 0, 0)],
              [datetime(2012, 1, 3, 0, 0), datetime(2012, 1, 4, 0, 0)]]
    ind = pandas.Series(inputs)
    as_inps = ap.Time(inputs)

    apts = parse_time(ind)

    assert isinstance(apts, astropy.time.Time)
    assert np.all(apts == as_inps)
    assert apts.shape == as_inps.shape


def test_parse_time_pandas_index():
    inputs = [datetime(2012, 1, i) for i in range(1, 13)]
    ind = pandas.DatetimeIndex(inputs)
    as_inps = ap.Time(inputs)

    dts = parse_time(ind)

    assert isinstance(dts, astropy.time.Time)
    assert np.all(dts == as_inps)


def test_parse_time_numpy_date():
    inputs = np.arange('2005-02', '2005-03', dtype='datetime64[D]')

    dts = parse_time(inputs)

    assert isinstance(dts, astropy.time.Time)


def test_parse_time_numpy_datetime():
    inputs = np.arange('2005-02-01T00', '2005-02-01T10', dtype='datetime64')

    dts = parse_time(inputs)

    assert isinstance(dts, astropy.time.Time)


def test_parse_time_individual_numpy_datetime():
    dt64 = np.datetime64('2005-02-01T00')
    dt = parse_time(dt64)

    assert isinstance(dt, astropy.time.Time)
    assert dt == ap.Time('2005-02-01', format='isot')


def test_parse_time_numpy_datetime_timezone():
    dt64 = np.datetime64('2014-02-07T16:47:51-0500')
    dt = parse_time(dt64)

    assert dt == ap.Time('2014-02-07T21:47:51', format='isot')


def test_parse_time_numpy_datetime_ns():
    dt64 = np.datetime64('2014-02-07T16:47:51.008288000')
    dt = parse_time(dt64)

    assert dt == ap.Time('2014-02-07T16:47:51.008288000', format='isot')

    dt64 = np.datetime64('2014-02-07T16:47:51.008288123')
    dt = parse_time(dt64)

    assert dt == ap.Time('2014-02-07T16:47:51.008288123', format='isot')

    dt64 = np.datetime64('2014-02-07T16:47:51.234565999')
    dt = parse_time(dt64)

    assert dt == ap.Time('2014-02-07T16:47:51.234565999')


def test_parse_time_astropy():
    ip = astropy.time.Time(['2016-01-02T23:00:01'])
    astropy_time = parse_time(ip)

    assert astropy_time == ip
    assert astropy_time.format == 'isot'


def test_parse_time_datetime():
    dt = datetime(2014, 2, 7, 16, 47, 51, 8288)
    assert parse_time(dt) == dt
    assert parse_time(dt).format == 'datetime'


def test_parse_time_date():
    dt = parse_time(date(1966, 2, 3))
    assert dt == datetime(1966, 2, 3)
    assert dt.format == 'iso'


def test_parse_time_now():
    """
    Ensure 'parse_time' can be called with 'now' argument to get utc
    """
    # TODO: once mocking support is merged in, we can perform a like for like comparison,
    #       the following at least ensures that 'now' is a legal argument.
    now = parse_time('now')
    assert isinstance(now, astropy.time.Time) is True
    assert now.format == 'datetime'
    assert now.scale == 'utc'


def test_parse_time_ISO():
    dt1 = ap.Time('1966-02-03T20:17:40')
    assert parse_time('1966-02-03').jd == LANDING.jd
    assert (
        parse_time('1966-02-03T20:17:40') == dt1
    )
    assert (
        parse_time('19660203T201740') == dt1
    )

    dt2 = ap.Time('2007-05-04T21:08:12.999999')
    dt3 = ap.Time('2007-05-04T21:08:12')
    dt4 = ap.Time('2007-05-04T21:08:00')
    dt5 = ap.Time('2007-05-04')

    lst = [
        ('2007-05-04T21:08:12.999999', dt2),
        ('20070504T210812.999999', dt2),
        ('2007/05/04 21:08:12.999999', dt2),
        ('2007-05-04 21:08:12.999999', dt2),
        ('2007/05/04 21:08:12', dt3),
        ('2007-05-04 21:08:12', dt3),
        ('2007-05-04 21:08', dt4),
        ('2007-05-04T21:08:12', dt3),
        ('20070504T210812', dt3),
        ('2007-May-04 21:08:12', dt3),
        ('2007-May-04 21:08', dt4),
        ('2007-May-04', dt5),
        ('2007-05-04', dt5),
        ('2007/05/04', dt5),
        ('04-May-2007', dt5),
        ('04-May-2007 21:08:12.999999', dt2),
        ('20070504_210812', dt3),
    ]

    for k, v in lst:
        dt = parse_time(k)
        assert dt == v
        dt.format == 'isot'


def test_parse_time_tai():
    dt = ap.Time('2007-05-04T21:08:12', scale='tai')
    dt2 = parse_time('2007.05.04_21:08:12_TAI')

    assert dt == dt2
    assert dt.scale == dt2.scale


@pytest.mark.parametrize("ts,fmt", [
    (1950.0, 'byear'),
    ('B1950.0', 'byear_str'),
    (63072064.184, 'cxcsec'),
    (datetime(2000, 1, 2, 12, 0, 0), 'datetime'),
    (2000.45, 'decimalyear'),
    ('2000-01-01T00:00:00.000(TAI)', 'fits'),
    (630720013.0, 'gps'),
    ('2000-01-01 00:00:00.000', 'iso'),
    ('2000-01-01T00:00:00.000', 'isot'),
    (2451544.5, 'jd'),
    (2000.0, 'jyear'),
    ('J2000.0', 'jyear_str'),
    (51544.0, 'mjd'),
    (730120.0003703703, 'plot_date'),
    (946684800.0, 'unix'),
    ('2000:001:00:00:00.000', 'yday')
])
def test_parse_time_astropy_formats(ts, fmt):
    dt = parse_time(ts, format=fmt)
    assert dt.format == fmt


def test_break_time():
    t = datetime(2007, 5, 4, 21, 8, 12)
    assert time.break_time(t) == '20070504_210812'


def test_day_of_year():
    # Note that 2008 is a leap year, 2011 is a standard year
    # test that it starts at 1
    assert time.day_of_year('2011/01/01') == 1.0
    # test fractional day
    assert time.day_of_year('2011/01/01 06:00') == 1.25
    assert time.day_of_year('2011/01/01 12:00') == 1.50
    assert time.day_of_year('2011/01/01 18:00') == 1.75
    # test correct number of days in a (standard) year
    assert time.day_of_year('2011/12/31') == 365
    # test correct number of days in a (leap) year
    assert time.day_of_year('2008/12/31') == 366
    # test a few extra dates in standard year
    assert time.day_of_year('2011/08/01') == 213
    assert time.day_of_year('2011/04/10') == 100
    assert time.day_of_year('2011/01/31') == 31
    assert time.day_of_year('2011/09/30') == 273
    # test a few extra dates in a leap year
    assert time.day_of_year('2008/08/01') == 214
    assert time.day_of_year('2008/04/10') == 101
    assert time.day_of_year('2008/01/31') == 31
    assert time.day_of_year('2008/09/30') == 274


def test_day_of_year_leapsecond():
    # 2015 had a leap second.
    # 30/06/2015 23:59:60 was a leap second
    assert time.day_of_year('2015/01/31') == 31
    assert time.day_of_year('2015/04/10') == 100
    assert time.day_of_year('2015/06/30 23:59:60') == 182
    assert time.day_of_year('2015/08/01') == 213.00001157407408
    assert time.day_of_year('2015/09/30') == 273.00001157407405


def test_time_string_parse_format():
    assert parse_time('01/06/2012',
                      _time_string_parse_format='%d/%m/%Y') == datetime(2012, 6, 1, 0, 0)
    assert parse_time('06/01/2012',
                      _time_string_parse_format='%d/%m/%Y') == datetime(2012, 1, 6, 0, 0)
    assert parse_time('06/01/85',
                      _time_string_parse_format='%d/%m/%y') == datetime(1985, 1, 6, 0, 0)
    assert parse_time('6/1/85',
                      _time_string_parse_format='%d/%m/%y') == datetime(1985, 1, 6, 0, 0)
    with pytest.raises(ValueError):
        parse_time('01/06/2012')
    with pytest.raises(ValueError):
        parse_time('01/06/2012', _time_string_parse_format='%d/%Y/%m')
    with pytest.raises(re.error):
        parse_time('01/06/2012', _time_string_parse_format='%d/%m/%m')

    with pytest.raises(ValueError):
        parse_time('2016', _time_string_parse_format='zz')


def test__iter_empty():

    class CountDown(object):

        def __init__(self, start_from=0):
            self.start = start_from

        def __iter__(self):
            return self

        def __next__(self):
            self.start -= 1

            if self.start < 0:
                raise StopIteration

            return self.start

        next = __next__   # Support Py2.x

    one_count = CountDown(1)
    assert time.time._iter_empty(one_count) is False
    assert time.time._iter_empty(one_count) is True



def test_is_time():
    assert time.is_time(datetime.utcnow()) is True
    assert time.is_time('2017-02-14 08:08:12.999') is True

    assert time.is_time(None) is False
    assert time.is_time('2016-14-14 19:08') is False


def test_is_time_in_given_format():
    assert is_time_in_given_format('2017-02-14 08:08:12.999', "%Y-%m-%d %H:%M:%S.%f") is True
    assert is_time_in_given_format('2017-02-14 08:08:12.999', "%Y-%m-%dT%H:%M:%S.%f") is False


def test_get_day():
    end_of_day = datetime(year=2017, month=1, day=1, hour=23, minute=59, second=59,
                          microsecond=999)

    begining_of_day = get_day(end_of_day)
    assert begining_of_day.year == 2017
    assert begining_of_day.month == 1
    assert begining_of_day.day == 1
    assert begining_of_day.hour == 0
    assert begining_of_day.minute == 0
    assert begining_of_day.second == 0
    assert begining_of_day.microsecond == 0
