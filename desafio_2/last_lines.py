
import os
import io
import pathlib

from typing import Union


def last_lines(file_path: Union[pathlib.Path, str], buf_size: int = io.DEFAULT_BUFFER_SIZE):
    """A generator that returns the lines of a file in reverse order
    
    Args:
        file_path: path to the desired file
        buf_size: how many bytes to read to get each line, Defaults to io.DEFAULT_BUFFER_SIZE

    Yield:
        Next line in reverse order from file: -1, -2, -3...

    Usage:
        for line in reverse_readline(file_path): print(line)
    """
    with open(file_path, "rb") as fh:
        offset, segment = 0, None

        fh.seek(0, os.SEEK_END)
        file_size = remaining_size = fh.tell()
        while remaining_size > 0:
            offset = min(file_size, offset + buf_size)
            fh.seek(file_size - offset)
            buffer = fh.read(min(remaining_size, buf_size))

            # remove file's last "\n" if it exists, only for the first buffer
            if remaining_size == file_size and buffer[-1] == ord('\n'):
                buffer = buffer[:-1]
            remaining_size -= buf_size
            lines = buffer.split('\n'.encode(encoding="utf-8"))
            
            # append last chunk's segment to this chunk's last line
            if segment is not None:
                lines[-1] += segment
            segment = lines[0]
            lines = lines[1:]

            # yield lines in this chunk except the segment
            for line in reversed(lines):
                # only decode on a parsed line, to avoid utf-8 decode error
                yield (line + '\n'.encode(encoding="utf-8")).decode(encoding="utf-8") 

            # Don't yield None if the file was empty
            if segment is not None:
                yield segment.decode(encoding="utf-8")


if __name__ == "__main__":
    # Define sample file path
    file_path = pathlib.Path(__file__).parent.resolve() / "sample.txt"

    # Reverse iterate file and print lines
    for line in last_lines(file_path): 
        print(line, end='')
