## Game Playing Agents

This assignment lets you understand how a variant of Minimax and Monte-Carlo Tree Search work. Students need to code in the Jupyter notebook provided. 

### Running the code

There are a couple of ways you can run the notebook. You can run it locally using Jupyter Notebook or vsCode or through Google Colab. This assignment does not require GPUs so the free version of Colab would suffice. 

The assignment is not heavily dependent on libraries. It requires Python standard libraries, GraphViz and PyDot. 

#### Steps to run the notebook locally

1. Through Anaconda and Jupyter
To run Jupyter Notebook through terminal on MacOS, Linux or Windows, one needs to install Conda. 

After installing Conda, you need to run:

```
conda install jupyter
```
Now jupyter notebook can be run through terminal (MacOS or Linux) or through Anaconda Prompt (Windows).

Extra Reading: https://services.dartmouth.edu/TDClient/1806/Portal/KB/ArticleDet?ID=127558

2. Through VSCode and Conda Environment
You would need to activate the Conda environment on vscode when you open the notebook. Make sure correct python interpretor is selected. And then you can run the notebook.

Extra Reading: https://code.visualstudio.com/docs/datascience/jupyter-notebooks

#### Steps to run the notebook on Colab
There are two ways you can use to open the notebook on Colab:
1. Upload to GDrive and then double-click to get started on Colab.
2. When you enter through Colab Home Interface (https://colab.research.google.com/), it provides a prompt to ask which file you want to open. You can specify the file here. 


Extra Reading: https://developers.google.com/earth-engine/guides/python_install-colab#:~:text=ipynb'%20file%20extension.,from%20the%20file's%20context%20menu.

### TODO for Students

Students would need to complete the missing code or functions. Below is a list of functions that you need to complete. 

1. def maximax(*)
2. def ucb(*)
3. def mcts(*)

### Grading

This assignment does not have an autograder. It will be tested based on cell outputs and the notebook you submit. 

Maximax and MCTS will be run on 3x3 and 5x5 maps and it should score above the given thresholds in the notebooks. The points will be allocated accordingly. The point breakdwon is below:
1. Maximax on 3x3 (5 pts)
2. Maximax on 5x5 (5 pts)
3. MCTS on 3x3 (5pts)
4. MCTS on 5x5 (5pts)

Chosen 3x3 Map: state3x3
Chosen 5x5 Map: state_example

There will be 10 separate tests on UCB function cumaltively worth 5 points. 

The total assignment is worth 25 points. 

### Submission

The assignment needs to be submitted on Gradescope. This includes the notebook with saved cell outputs. Please make sure that you have configured your notebook to save cell output. 


