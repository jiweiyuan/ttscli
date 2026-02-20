"""Entry point for python -m ttscli."""

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from .cli import main

if __name__ == "__main__":
    main()
