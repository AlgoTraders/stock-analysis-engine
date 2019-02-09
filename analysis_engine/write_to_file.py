"""
Helper for writing to a file - used by unittests
"""

import os
import json


def write_to_file(
        output_file,
        data):
    """write_to_file

    write ``data`` to the ``output_file`` file

    :param output_file: path to file
    :param data: string contents for ``output_file``
    """
    use_str = data
    try:
        use_str = json.dumps(data)
    except Exception:
        use_str = data
    with open(output_file, 'w') as cur_file:
        cur_file.write(use_str)

    return os.path.exists(output_file)
# end of write_to_file
