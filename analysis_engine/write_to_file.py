"""
Helper for writing to a file - used by unittests
"""

import os


def write_to_file(
        output_file,
        data):
    """write_to_file

    write ``data`` to the ``output_file`` file

    :param output_file: path to file
    :param data: string contents for ``output_file``
    """
    with open(output_file, 'w') as cur_file:
        cur_file.write(data)

    return os.path.exists(output_file)
# end of write_to_file
