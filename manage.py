import os
import sys
import pymysql

pymysql.install_as_MySQLdb()

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Django import error") from exc
    execute_from_command_line(sys.argv)
