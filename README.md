# Hosta.ai Interview-Task submission

Elliot Rivers's submission for the [Hosta.ai](hosta.ai) [interview task](./doc/Task.md).

# Overview

Given a set of input "image" json files with broken parent links and a csv file containing
parent/child information, restore as many parent-relationships as possible by correlating
across different ID types between files.

(See [task](./doc/Task.md) for more information)

## Solution description

My solution broadly involves these steps:
1. Parse the input data
2. Forall image files, forall ops\_3d elements:
    - From the correction file, get any correction for this Op3d's item\_id
    - Get the host\_id of the correction and convert it to a pertinent Image ObjectId
    - Convert the ObjectId to a unique\_id by cross-referencing with the image files
3. Save modified json

Whereas the data transformations are relatively straightforward, in my discussions with
Yury, we discussed the possible need for a refined data model for Hosta's internal data.
With that in mind, my solution focuses on an example of one such data model for this
application (using [pydantic](https://docs.pydantic.dev), at the risk of some additional
verbocity.

The [`hosta_homework.model`](./hosta_homework/model/) module contains an implementation
and discussion of this data model. As mentioned over there, the intent of this exercise
is not to design nor evaluate the data formats, so it is a fairly naive translation
(for lack of context), but I believe it should highlight the benefits nonetheless.

My solution _should_ work on any number of images, not just 3, even though the inputs
are currently hard-coded in the main entrypoint

Also, I have instrumented it with logging calls at different levels, as I would if I
were writing production software. By default, executing the solution prints everything
at `INFO` level and above.

## Repository structure

- [`data/`](./data/): Where the provided and generated data lives
    - [`out/`](./data/out/): Generated data from my solution, if you don't want to run it yourself
- [`doc/`](./doc/): Where docs would live. The task lives there at least
- [`hosta_homework/`](./hosta_homework/): Python source code
- [`tests/`](./tests/): Some very basic pytest tests that I used to test some things. Not exhaustive by any means

# Guided software tour

## main

The main entrypoint to my solution is the [`__main__` module](./hosta_homework/__main__.py).
There, I have implemented a very basic CLI to execute my submission, callable with 
`python3 -m hosta_homework`.

The output that is present in [`data/out`](./data/out/) was generated with:
```bash
poetry run python3 -m hosta_homework 2> data/out/hosta_homework.log
```

If you want to reproduce my results, you may need to add the `--force-overwrite` flag
to rewrite the output files.

## data

[`hosta_homework.data`](./hosta_homework/data.py) contains just some static paths

## model

[`hosta_homework.model`](./hosta_homework/model/) is the data model contains the meat of my solution.

I have thoroughly commented that module, so I won't repeat myself much here, but here are some general points:
- [`hosta_homework.model.image_file`](./hosta_homework/model/image_file.py) contains the actual merging logic (around ln 134)
    - The call structure can be traced back from the main module
- I did not completely describe every field in the module, only some as an example (see comments)
- I have chosen to implement the methods in an Object-Oriented manner for this, but the transforms could just as easily be free functions in a different module

# Technical information

## Tooling information

Dependencies and builds are managed by [poetry](https://python-poetry.org/).

After cloning, use `poetry install --with dev` to install dependencies in a virtual environment.

Execute with 
```bash
# Run the main module and print help message
poetry run python3 -m host_homework --help

# Execute the pytests
poetry run pytest
```


## Dependencies

- `pydantic` for data model
- `pytest` for testing
