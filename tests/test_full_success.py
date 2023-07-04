
from pathlib import Path

from pytest_httpx import HTTPXMock

from .utils_success import prepare_mocks
from hubstaff_app import main

CUR_DIR = Path(__file__).resolve().parent


def test_success_ascii(capsys, httpx_mock: HTTPXMock):
    " Test successful run with ASCII table output "
    prepare_mocks(httpx_mock)

    args = ['-c', str(CUR_DIR) + '/settings_success.yaml', '-v', '--format', 'ascii']
    exitcode = main(args)
    assert exitcode == 0

    captured = capsys.readouterr()
    # Path(CUR_DIR, 'output_success.ascii').write_text(captured.out)  # use this to rewrite expected results
    expected = Path(CUR_DIR, 'output_success.ascii').read_text()
    assert expected == captured.out


def test_success_html(capsys, httpx_mock: HTTPXMock):
    " Test successful run with HTML table output "
    prepare_mocks(httpx_mock)

    args = ['-c', str(CUR_DIR) + '/settings_success.yaml', '-v', '--format', 'html']
    exitcode = main(args)
    assert exitcode == 0

    captured = capsys.readouterr()
    # Path(CUR_DIR, 'output_success.html').write_text(captured.out)  # use this to rewrite expected results
    expected = Path(CUR_DIR, 'output_success.html').read_text()
    assert expected == captured.out
