#!/usr/bin/env python3
"""Utilities for CSV file manipulation and editing."""

import os
from contextlib import contextmanager
from pathlib import Path


class CSVEditor:
    """Helper class for editing CSV files with context manager support."""

    def __init__(self, file_reader, file_writer):
        self.file_reader = file_reader
        self.file_writer = file_writer


@contextmanager
def csv_editor(file_path: os.PathLike):
    """Context manager for safely editing CSV files with automatic backup.

    Args:
        file_path: Path to the CSV file to edit

    Yields:
        CSVEditor: File editor instance with reader/writer attributes
    """
    path, full_file = os.path.split(file_path)
    file_name, file_ext = os.path.splitext(full_file)
    temp_filename = f"{file_name}_temp{file_ext}"
    temp_path = os.path.join(path, temp_filename)

    with open(file_path, "r") as file_reader, open(temp_path, "w") as file_writer:
        yield CSVEditor(file_reader, file_writer)
