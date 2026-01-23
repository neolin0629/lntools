from pprint import pprint

import pandas as pd
import polars as pl


def test_config_utils() -> None:
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


def test_mail() -> None:
    df = pl.DataFrame({"a": [1, 2], "b": [3, 4]})
    from lntools.mail import MailPlus
    m = MailPlus()
    success = (
        m
        .newemail(to="125179847@qq.com", subject="test mail python")
        .add_title("This is lntools test mail")
        .add_content("from Neo lntools")
        .add_images(["D:\\1.png", "D:\\1767941843347_d.png"])
        .add_href(href="https://git.qxtech.cc/johnny/lntools", title="lntools")
        .add_attachments([
            "D:\\download\\12524412.xlsx",
            "E:\\document\\getrich系统设计v1.1.md"])
        .add_table(df)
        .sendmail()
    )
    pprint(success)


def test_timeutils() -> None:
    from lntools.timeutils import adjust, day_of_week, diff, dt2str, get_range, to_timestamp, ts2str

    pprint(adjust("today"))
    pprint(get_range(20260101, "today"))
    pprint(diff(20260101, "today"))
    pprint(day_of_week())
    pprint(dt2str(to_timestamp("today"), "standard"))
    pprint(to_timestamp("today"))
    import time
    pprint(ts2str(time.time(), "wide"))
    pprint(adjust("20260101"))


def test_cli() -> None:
    from lntools.utils import CLI
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


def test_fliesystem() -> None:
    from pathlib import Path

    from lntools.utils import (
        file_time,
        get_all,
        get_dirs,
        get_files,
        handle_path,
        is_dir,
        is_file,
        make_dirs,
        move,
        read_directory,
        read_file,
    )
    sysroot = "E:\\data"
    pprint(is_dir(Path(sysroot, "ricequant")))
    pprint(is_file(Path(sysroot, "ricequant", "all_instruments_CS.parquet")))
    pprint(handle_path(Path(sysroot, "ricequant", "quote", "stockinfo", "CS.parquet")))
    pprint(read_file(Path(sysroot, "ricequant", "all_instruments", "CS.parquet")))
    make_dirs(Path(sysroot, "ricequant", "quote"))
    pprint(Path(sysroot, "ricequant", "quote").exists())
    move(Path(sysroot, "ricequant", "all_instruments", "CS.parquet"), Path(sysroot, "ricequant", "quote"))
    pprint(Path(sysroot, "ricequant", "quote", "CS.parquet").exists())
    # pprint(move(Path(sysroot, "ricequant", "quote", "px1"),
    #   Path(sysroot, "ricequant"), keep_old=False, exist_ok=True))
    # pprint(rename(Path(sysroot, "ricequant", "px1"), Path(sysroot, "ricequant", "px")))
    pprint(file_time(Path(sysroot, "ricequant", "all_instruments", "CS.parquet")))
    pprint(get_all(Path("E:\\data\\ricequant\\all_instruments")))
    pprint(get_files(Path("E:\\data\\ricequant\\all_instruments")))
    pprint(get_dirs(Path("E:\\data\\ricequant")))
    # remove(Path(sysroot, "data", "px", "20240105.parquet"))
    # remove(Path(sysroot, "data", "px"))
    dates = ['2023-12-28', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05']
    pprint(
        read_directory(
            Path(r"E:\data\ricequant\daybar+info\日线数据\股票"),
            sdt="2023-12-28", edt="2024-01-05", date_format="%Y-%m-%d", file_pattern="{date}.parquet",
            trading_dates=dates
        )
    )


def test_human() -> None:
    """
    # path,
    # unit,
    # sec2str,
    # lists,
    # ranges,
    # datetime
    """
    from lntools.utils import datetime_str, lists, path, ranges, sec2str, unit
    pprint(path("~/data/quote/stockinfo"))
    pprint(unit(3.141, "second", decimal=2))
    pprint(sec2str(1024))
    pprint(lists([1, 2, 3, 4, 5, 6, 7, 8, 9, 0]))
    pprint(ranges(pd.date_range("2021-01-01", "2022-01-10", freq="D").to_list()))
    pprint(datetime_str("today", "wide"))


def test_track() -> None:
    from concurrent.futures import ThreadPoolExecutor
    import time

    from lntools.utils import RichProgressManager, track_simple
    for _ in track_simple(50, msg="test enumerate"):
        # fprint(i)
        time.sleep(0.02)

    with RichProgressManager() as rpm:
        for _ in rpm.track(50, msg="Rich progress manager test"):
            time.sleep(0.02)

    def worker(job_id: int, manager: RichProgressManager) -> None:
        total_steps = 50
        delay = 0.05 + (job_id * 0.01)

        # 演示任务完成后移除进度条的效果
        for _ in manager.track(total_steps, msg=f"[cyan]Worker-{job_id} downloading"):
            time.sleep(delay)

    # 开启 remove_task_on_finish=True，看下动态移除效果
    with RichProgressManager(remove_task_on_finish=True) as rpm, ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(worker, i, rpm) for i in range(1, 5)]
        for f in futures:
            f.result()


def test_log() -> None:
    from lntools.utils import Logger, handle_path
    log_path = handle_path("E://temp/test1.log")
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
    # test_mail()
    # test_timeutils()
    # test_cli()
    # test_fliesystem()
    # test_human()
    # test_track()
    test_log()
