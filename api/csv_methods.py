from contextlib import contextmanager
import os.path


# class CSVEditor:
#     def __init__(self, file_reader, file_writer):
#         self.file_reader = file_reader
#         self.file_writer = file_writer
#
# @contextmanager
# def csv_editor(file_path: os.PathLike):
#         path, full_file = os.path.split(file_path)
#         file_name, file_ext = os.path.splitext(full_file)
#         temp_filename = f"{file_name}_temp{file_ext}"
#         temp_path = os.path.join(path, temp_filename)
#         with open(file_path, "r") as file_reader, open(temp_path, "w") as file_writer:
#             yield CSVEditor(file_reader, file_writer)
#
#
# if __name__ == "__main__":
#     with csv_editor("databases/last_fetched.csv") as csv_e:
#         pass