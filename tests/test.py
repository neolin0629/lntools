from pprint import pprint

import pandas as pd
import polars as pl


def test_config_utils():
    from lntools.config import read_pkg_ini

    config = read_pkg_ini("config/test.ini",)
    config.add_section('section1')
    config.set('section1', 'key1', 'new_value')
    pprint(config["owner"]["name"])
    pprint(config.get("owner", "organization"))
    pprint(config.get("database", "server"))
    pprint(config.get("section1", "key1"))

    ##########
    # [owner]
    # name=John Doe
    # organization=Acme Products

    # [database]
    # server=192.0.2.42 ; Use IP in case network name is not working
    # port=143
    # file="payroll.dat"
    #########


def test_mail():
    df = pl.DataFrame({"a": [1, 2], "b": [3, 4]})
    from lntools.mail import MailPlus
    m = MailPlus()
    success = (
        m
        .newemail(to="125179847@qq.com", subject="test mail python")
        .add_title("This is lntools test mail")
        .add_content("from Neo lntools")
        .add_images(["/home/lin/download/11d30.png", "/home/lin/download/11d31.png"])
        .add_href(href="https://git.qxtech.cc/johnny/lntools", title="lntools")
        .add_attachments([
            "/home/lin/data/wind/PITFinancialFactor_数据字典.pdf",
            "/home/lin/data/wind/ConsensusExpectationFactor_数据字典.pdf"])
        .add_table(df)
        .sendmail()
    )
    pprint(success)


def test_timeutils():
    from lntools.timeutils import (
        adjust, diff, get, now, day_of_week,
        str2dt, str2ts, ts2dt, ts2str, dt2str, dt2ts,
    )

    pprint(adjust("today"))
    pprint(get(20240601, "today"))
    pprint(diff(20240601, "today"))
    pprint(now())
    pprint(day_of_week())
    pprint(str2dt("today"))
    pprint(str2ts("today"))
    pprint(dt2str(now(), "standard"))
    pprint(dt2ts(now()))
    import time
    pprint(ts2dt(time.time()))
    pprint(ts2str(time.time(), "wide"))
    pprint(adjust("20240601"))


def test_cli():
    from lntools import CLI
    cli = CLI()
    cli.add("-p", "--portfolio", type=int, nargs="+", action="store", required=True, help="portfolio id")
    cli.add("-m", "--money", type=float, nargs="+", action="store", required=True, help="initial money")
    cli.add("-s", "--save", action="store_true", help="whether save result")
    cli.add("-un", "--unsave", action="store_false", help="whether don't save result")
    cli.add("-n", "--name", type=str, nargs="*", action="store", required=True, help="pm name")
    cli.add("-e", "--email", type=str, nargs="*", action="store", help="client email")
    cli.add("-a", "--address", action="append", help="client address")
    cli.add("-t", "--count", action="count", default=0)
    cli.add("-c", "--const", action="store_const", const=42)
    # * Run in shell
    # python tests/test.py -p 20 100 200 -m 1999 1000 2000 -n linnan neo huajie -e lnonly@163.com -a sz -a sh -a hk -t -t -t -t -c  # pylint: disable=line-too-long # noqa: E501

    # cli.add("-v", "--version", action="version", version="1.0")
    # * Run in shell
    # python tests/test.py -v
    pprint(cli.get())


def test_directory():
    from lntools.utils.directory import Directory
    d = Directory("/home/lin/data/quote/etfdaily")
    read_params = {"lib": "polars", "file_pattern": "{date}.parquet", "date_format": "%Y%m%d", "use_tcal": True}
    pprint(d.read(sdt="2023-12-28", edt="2024-01-05", **read_params))


def test_fliesystem():
    from pathlib import Path
    from lntools.utils.filesystem import (
        is_dir, is_file, handle_path, read_file,
        make_dirs, move, rename, remove, file_time, 
        get_all, get_files, get_dirs, read_directory
    )
    sysroot = Path.home()
    pprint(is_dir(Path(sysroot, "data", "wind")))
    pprint(is_file(Path(sysroot, "data", "wind", "AShareSEO.parquet")))
    pprint(handle_path(Path(sysroot, "data", "quote", "stockinfo", "20240105.parquet")))
    pprint(read_file(Path(sysroot, "data", "quote", "stockinfo", "20240105.parquet")))
    pprint(make_dirs(Path(sysroot, "data", "quote", "px1")))
    pprint(move(Path(sysroot, "data", "quote", "stockinfo", "20240105.parquet"), Path(sysroot, "data", "quote", "px1")))
    pprint(move(Path(sysroot, "data", "quote", "px1"), Path(sysroot, "data"), keep_old=False, exist_ok=True))
    pprint(rename(Path(sysroot, "data", "px1"), Path(sysroot, "data", "px")))
    pprint(file_time(Path(sysroot, "data", "quote", "stockinfo", "20240105.parquet")))
    pprint(get_all(Path("/home/lin/data/factor")))
    pprint(get_files(Path("/home/lin/data/factor/QIML/2023-05")))
    pprint(get_dirs(Path("/home/lin/data/factor/QIML")))
    remove(Path(sysroot, "data", "px", "20240105.parquet"))
    remove(Path(sysroot, "data", "px"))
    pprint(read_directory(Path("/home/lin/data/quote/etfdaily"),
                          sdt="2023-12-28", edt="2024-01-05", date_format="%Y%m%d", file_pattern="{date}.parquet"))


def test_human():
    """
    # path,
    # unit,
    # sec2str,
    # lists,
    # ranges,
    # datetime
    """
    from lntools import (
        path, unit, sec2str, lists, ranges, datetime
    )
    pprint(path("~/data/quote/stockinfo"))
    pprint(unit(3.141, "second", decimal=2))
    pprint(sec2str(1024))
    pprint(lists([1, 2, 3, 4, 5, 6, 7, 8, 9, 0]))
    pprint(ranges(pd.date_range("2021-01-01", "2022-01-10", freq="D").to_list()))
    pprint(datetime("today", "wide"))


def test_track():
    from time import sleep
    from lntools import track, fprint
    for i in track(range(100), msg="test enumerate"):
        fprint(i)
        sleep(0.1)


def test_log():
    from lntools import Logger, handle_path
    log_path = handle_path("~/project/test1.log")
    log = Logger(
        module_name="test",
        output_method=["console", "file"],
        file=log_path
    )
    log.set_level("warning")
    log.info("information from test.")
    log.warning("warning from test.")
    log.debug("debug from test.")
    log.set_level("debug")
    log.info("information from test.")
    log.warning("warning from test.")
    log.debug("debug from test.")


if __name__ == '__main__':
    test_mail()
    # test_timeutils()
    # test_cli()
    # test_directory()
    # test_fliesystem()
    # test_human()
    # test_track()
    # test_log()
