import logging
import sys

# Logging Settings
logger = logging.getLogger()
logger.setLevel(logging.INFO)

log_formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s: %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S"
    )

stdout_hanlder = logging.StreamHandler(sys.stdout)
stdout_hanlder.setFormatter(log_formatter)
logger.addHandler(stdout_hanlder)

file_handler = logging.FileHandler(
    'import.log',
    mode='w',
    encoding='utf-8')
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)

debug_file_handler = logging.FileHandler(
    'import_debug.log',
    mode='w',
    encoding='utf-8')
debug_file_handler.setFormatter(log_formatter)
debug_file_handler.setLevel(logging.DEBUG)
logger.addHandler(debug_file_handler)

# a seperate Report Logger
report_logger = logging.getLogger()
report_formatter = logging.Formatter(
        fmt='%(message)s',
        datefmt="%Y-%m-%d %H:%M:%S"
    )
report_file_handler = logging.FileHandler(
    'import_report.log',
    mode='w',
    encoding='utf-8')
report_file_handler.setFormatter(report_formatter)
report_logger.addHandler(report_file_handler)
report_logger.setLevel(logging.INFO)
