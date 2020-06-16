# Running The Pipeline

On completing a flowchart, it can be sent to the built-in pipeline backend to be executed.

## Running A New Pipeline

When nodes exist in the flowchart window but the flowchart has yet to be saved, WARIO will prompt the user to save before moving on to the pipeline execution step. Once the file has been saved at least once, this prompt will be skipped until the flowchart has been cleared. 

With the file saved, the file is passed to the pipeline execution code and the output of the code will be displayed in the command prompt used to run WARIO. 

Unless threadless mode (currently in development) is enabled, the pipeline is ran on a seperate thread. This means that you can continue to interact with the flowchart as normal, but changes made will not affect the pipeline run in progress. Threadless mode is used for running pipelines that require matplotlib but dont have any dedicated handler for the plots that can allow them to be shown while running in a seperate thread (e.g. the EEG toolkit)

The nodes in the pipeline will change colour to signify their current status based on the following colour key:

| Colour | Meaning | 
| :--- | :---: | 
| Red | Yet to run | 
| Blue | Currently running | 
| Green | Completed | 

If the pipeline is set to run multiple iterations (e.g. if running over multiple files), the node colours will be reset to red between each iteration.

## Running An Existing Pipeline

If the user attempts to run a pipeline with no file loaded and no nodes placed in the flowchart interface, WARIO will prompt them to open a compatable JSON file to be executed. The pipeline will also be loaded into the flowchart interface and can additional runs can be performed without the load prompt in an identical manner as described for the new pipeline.

## Running Pipelines Without WARIO

The pipeline code can be ran without requiring WARIO by using the RunPipeline.py file included in the main WARIO directory. The same file is used by WARIO itself when executing pipelines so the output should be identical, with the exception of plots which can only be viewed interactively when the pipeline is executed from within WARIO.

To use this file, run the command

```bash
    python RunPipeline.py "file\goes\here.json"
```

## Selecting A Frontend

The WARIO editor supports custom frontend code and the current frontend can be selected on the Wario Settings window (ctrl+T)

## Current Pipeline Limitations

* Pipeline does not currently support pausing or blocking nodes
* File locations must be redefined if a pipeline save file is transferred between computers unless the absolute file path for all set save and load locations are identical between the two computers
