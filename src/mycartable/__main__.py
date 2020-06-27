import sys

from pathlib import Path

package_path = Path(__file__).parent
sys.path.append(package_path.as_posix())
print(sys.path)
from mycartable.main import main

if __name__ == "__main__":
    main()
