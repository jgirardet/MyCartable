from operator import attrgetter, methodcaller
from subprocess import run, CalledProcessError

from pathlib import Path
import sys
import logging

from PySide2.QtCore import QDir
from mako.lookup import TemplateLookup
from package import DATA, BINARY
from package.utils import read_qrc
from pony.orm import Set, db_session

LOG = logging.getLogger(__name__)


def get_binary_path(name):
    name = name + ".exe" if sys.platform == "win32" else name
    exec_path = BINARY / name
    return exec_path


def get_command_line_pdftopng(pdf, png_root, resolution):
    cmd = [
        get_binary_path("pdftopng"),
        "-r",
        resolution,
        pdf,
        png_root,
    ]
    return [str(i) for i in cmd]


def collect_files(root: Path, pref="", ext: str = ""):
    res = sorted(root.glob(f"{pref}*{ext}"), key=lambda p: p.name)
    return res


def run_convert_pdf(pdf, png_root, prefix="xxx", resolution=200, timeout=30):
    root = Path(png_root)
    if not root.is_dir():
        root.mkdir(parents=True)

    expected_out = root / prefix

    cmd = get_command_line_pdftopng(pdf, str(expected_out), resolution=resolution)

    try:
        run(cmd, timeout=timeout, check=True, capture_output=True)
    except CalledProcessError as err:
        LOG.error(err.stderr)
        return []
    except TimeoutError as err:
        LOG.error(err.stderr)
        return []

    files = collect_files(root, pref=prefix, ext=".png")
    return files


"""

                       Files other than Impress documents are opened in        
                       default mode , regardless of previous mode.             
   --convert-to OutputFileExtension[:OutputFilterName] \                      
     [--outdir output_dir] [--convert-images-to]                               
                       Batch convert files (implies --headless). If --outdir   
                       isn't specified, then current working directory is used 
                       as output_dir. If --convert-images-to is given, its     
                       parameter is taken as the target filter format for *all*
                       images written to the output format. If --convert-to is 
                       used more than once, the last value of                  
                       OutputFileExtension[:OutputFilterName] is effective. If 
                       --outdir is used more than once, only its last value is 
                       effective. For example:                                 
                   --convert-to pdf *.odt                                      
                   --convert-to epub *.doc                                     
                   --convert-to pdf:writer_pdf_Export --outdir /home/user *.doc
                   --convert-to "html:XHTML Writer File:UTF8" \             
                                --convert-images-to "jpg" *.doc              
                   --convert-to "txt:Text (encoded):UTF8" *.doc              
   --print-to-file [--printer-name printer_name] [--outdir output_dir]         
                       Batch print files to file. If --outdir is not specified,
                       then current working directory is used as output_dir.   
                       If --printer-name or --outdir used multiple times, only 
                       last value of each is effective. Also, {Printername} of 
                       --pt switch interferes with --printer-name.             
  
"""


class LibreOfficeConverter:
    def __init__(self):
        pass


def create_lookup():
    lookup = TemplateLookup()
    for file in QDir(":/templates").entryInfoList():
        lookup.put_string(file.fileName(), read_qrc(file.absoluteFilePath()))
    return lookup


html_lookup = create_lookup()


def parse_node(entity):
    res = entity.to_dict(with_collections=True, with_lazy=True, related_objects=True)
    for k, v in res.items():
        if isinstance(v, Set):
            partial_res = []

            res[k] = parse_node()
    return res


@db_session
def create_context(section_id):
    pass
