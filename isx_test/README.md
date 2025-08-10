# isx_test

This project demonstrates how to use the Inscopix Python API and the `ISXPipeline` class for video processing.

## Requirements

- Python 3.10
- The `isx` package must be installed and importable from your local Python package library.
- The `version0.isx_pipeline` module must be available in your Python path.

## Usage

First, ensure you can import `isx` and `ISXPipeline`:

```python
import isx
from version0.isx_pipeline import ISXPipeline
```

### Example

```python
# Create a new pipeline instance
pipe = ISXPipeline.new(isx, "videos", "output")

# Call pipeline methods in a chained style
(pipe
    # Chain steps
    .preprocess_videos()
    .bandpass_filter_videos()
    .motion_correction_videos()
    ...
 )
```

Replace `"videos"` with your input folder and `"output"` with your desired output directory.

### Advanced Usage

#### Parameters
You can also use the pipeline in a more advanced way by passing additional parameters to each method:

```python
(pipe
    .preprocess_videos()
    .spatial_filter(low_cutoff=0.005, high_cutoff=0.5)
)
```

#### Custom Steps
You can call custom steps directly on the pipeline instance by calling the `step` method:

```def step(self, step_name, step_function, *args, **kwargs)```
You can use both positional and keyword arguments for custom steps. Here's an example:

```python
(pipe
    .preprocess_videos()
    .step("custom_step_name", self.custom_step_name, positional_arg, named_arg=value2))
)
```

You can define the `custom_step_name` function in your code, which will handle the custom processing logic. Here's an example of how to define it:
```python
def custom_step_name(pipe, positional_arg, named_arg=None):
    # Custom processing logic here
    # For example, call a function from the isx package thats not implemented in the pipeline
    pass
```

Or you can use a lambda function:

```python
(pipe
    .preprocess_videos()
    .step("custom_step_name", lambda p: p.custom_step_name(positional_arg, named_arg=value2))
)
```

## Tracing
There are some tracing methods available to help you debug the pipeline:

In any step, you can call `pipe.trace()` or `pipe.info()` to print the current state of the pipeline, including the current step and any parameters set so far.

