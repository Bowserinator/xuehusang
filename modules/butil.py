# Bowsers utils
import signal
import io
import os

class Timeout:
    def __init__(self, seconds=1, error_message='Timed out'):
        self.seconds = seconds
        self.error_message = error_message

    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, type, value, traceback):
        signal.alarm(0)


BYTES_PER_FILE = 1000000
NUM_BUFFERS = 4

"""
A cyclic file buffer using n-files to cycle between, keeping only the last n
files of the sizes above
"""
class CyclicWave(io.IOBase):
    def __init__(self, name):
        self.mode = 'wb'
        self.name = name
        self._tell = 0
        self.int_files = []
        self.int_file_names = []

        for i in range(NUM_BUFFERS):
            n = f'{name}.{i}.wav'
            self.int_file_names.append(n)
            self.int_files.append(open(n, 'wb'))

    def _curr_file(self):
        return self.int_files[(self._tell // BYTES_PER_FILE) % NUM_BUFFERS]

    def writable(self) -> bool:
        return True

    def write(self, b):
        self._tell += len(b)
        self._curr_file().write(b)

    def seekable(self) -> bool:
        return True

    def tell(self):
        return self._tell

    def seek(self, offset, whence=os.SEEK_SET):
        if whence == os.SEEK_SET:
            self._tell = offset
        elif whence == os.SEEK_CUR:
            self._tell += offset
        else:
            raise RuntimeError('Unsupported whence: ' + str(whence))
        return self._curr_file().seek(self._tell % BYTES_PER_FILE, os.SEEK_SET)

    def flush(self):
        self._curr_file().flush()

    def close(self):
        for file in self.int_files:
            file.close()

        # Write all the files together into 1 wav
        with open('out-test.wav', 'ab') as f:
            for fname in self.int_file_names:
                with open(fname, 'rb') as f2:
                    f.write(f2.read())

    def __exit__(self):
        self.close()
