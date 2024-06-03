from bot.other.singleton_base import SingletonBase


class FileUtil(SingletonBase):

    def __init__(self):
        pass  # No initialization required for singleton

    def write_data(self, filename, data):
        """Write data to the file, overwriting any existing content."""
        with open(filename, "w") as file:
            file.write(data)
        print(f"Data written to {filename}")

    def append_data(self, filename, data):
        """Append data to the file."""
        with open(filename, "a") as file:
            file.write(data)
        print(f"Data appended to {filename}")

    def read_data(self, filename):
        """Read the contents of the file."""
        with open(filename, "r") as file:
            data = file.read()
        print(f"Data read from {filename}")
        return data

    def write_lines(self, filename, lines):
        """Write a list of lines to the file, overwriting any existing content."""
        with open(filename, "w") as file:
            file.writelines(lines)
        print(f"Lines written to {filename}")

    def append_lines(self, filename, lines):
        """Append a list of lines to the file."""
        with open(filename, "a") as file:
            file.writelines(lines)
        print(f"Lines appended to {filename}")
