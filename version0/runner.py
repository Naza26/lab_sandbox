# runner.py
import argparse

from isx_loader import ensure_isx
from isx_pipeline import ISXPipeline


def main():
    parser = argparse.ArgumentParser(description="Run or test ISX pipeline")
    parser.add_argument("--input", required=True, help="Path to input .isxd (relative or absolute)")
    parser.add_argument("--output", required=True, help="Output directory or file prefix")
    parser.add_argument("--test", action="store_true", help="Run in test/validation mode")
    args = parser.parse_args()

    # Load isx (dependency injection)
    isx = ensure_isx()

    # Instantiate pipeline
    pipe = ISXPipeline.new(isx, args.input, args.output)

    # Before run: snapshot
    before = pipe.info()

    # Run the core logic
    pipe.preprocess_videos()

    # After run: snapshot
    after = pipe.info()

    print("Before:", before)
    print("After:", after)

    if args.test:
        # Simple validation: ensure step was recorded and output path changed
        if before["steps"] == after["steps"]:
            raise RuntimeError("Test failed: pipeline did not add any steps")
        if before["output"] == after["output"]:
            raise RuntimeError("Test failed: output unchanged")
        print("Test mode: validation passed")


if __name__ == "__main__":
    main()
