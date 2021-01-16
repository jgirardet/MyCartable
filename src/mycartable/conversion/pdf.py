from multiprocessing import cpu_count, Pool
from pathlib import Path
from typing import Union, List
import fitz


class PDFSplitter:
    def __call__(
        self,
        filename: Union[Path, str],
        output_dir: Path,
        cpu: int = None,
    ) -> List[Path]:
        """
        Split un pdf de n pages, n PNG.
        :param filename: le fichier pdf source
        :param output_dir: le répertoire d'écriture ds png créés
        :param cpu: un nombre de cpu donné. default=multiprocessing.cpu_count
        :return: une list des  fichiers PNG dans l'ordre des pages
        """
        cpu = cpu or max(1, (cpu_count() - 1))

        doc = fitz.open(filename)
        nb_pages = int(doc.pageCount)  # cast pour ne pas retaper dans doc closed
        doc.close()

        # on crée les chunks qui seront repartis dans les process
        chuncks = [(i, cpu, filename, output_dir) for i in range(min(cpu, nb_pages))]
        with Pool(cpu) as poo:
            poo.starmap(save_pdf_pages_to_png, chuncks)
            poo.close()
            poo.join()

        return sorted(
            list(output_dir.glob("*.png")), key=lambda x: int(x.name.split(".")[0])
        )


def save_pdf_pages_to_png(
    index: int, cpu: int, filename: Union[Path, str], output_dir: Path
):
    """
    Convertie un portion de pdf en png
    :param index: index de la portion
    :param cpu: cpucount
    :param filename: pdf source
    :param output_dir: directory output
    :return: None
    """

    doc = fitz.open(filename)
    num_pages = len(doc)

    # pages per segment: make sure that cpu * seg_size >= num_pages!
    seg_size = int(num_pages / cpu + 1)
    seg_from = index * seg_size  # our first page number
    seg_to = min(seg_from + seg_size, num_pages)  # last page number
    for i in range(seg_from, seg_to):  # work through our page segment
        page = doc[i]
        pix = page.getPixmap(
            alpha=False, colorspace="RGB", matrix=fitz.Matrix(2, 2)
        )  # (2,2) meilleur qualité

        pix.writePNG(f"{ output_dir / f'{i}.png'}")
    doc.close()
