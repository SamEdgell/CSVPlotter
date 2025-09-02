This plotter will open a CSV file and plot the data into a graph using matplotlib.

1) Change the path in open_plotter.bat to where the python script lives.
2) Edit windows settings to open CSV file with the batch file.

If the columns name ends with ':0', it will be ignored from plotting.
If the columns name ends with ':2', ':3' or ':4', the plotter will plot the data in that column on the secondary/tertiary/quaternary axis respectively.
If the columns name is not formatted like the above, they will be plotted on the primary axis.

You can select a specific line in the graph within the legend, which will be highlighted with a thicker stroke when selected. As you move the mouse, the value of the selected line closest to the mouse’s x-position will be displayed in the bottom right corner of the figure.
