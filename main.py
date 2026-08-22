"""Entry point for the Shamba Advisor application."""

from pathlib import Path
import runpy


if __name__ == "__main__":
	advisor_script = Path(__file__).with_name("Shamba advisor.py")
	runpy.run_path(str(advisor_script), run_name="__main__")