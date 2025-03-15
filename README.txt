1) Change path in open_plotter.bat to where python script lives.
2) Edit windows settings to open CSV file with the batch file.

This plotter will open a CSV file and plot the data into a graph.

If the column names is 'name:0', it will be ignored from plotting.
If the column names have 'name:2' or 'name:3' or 'name:4', the plotter will plot that data on the secondary/tertiary/quaternary axis respectively.

If the column names are not formatted like that, they will be plotted on the primary axis.

You are able to select a specific line which will highlight, you can then move the mouse and the data for that highlighted line closest to the mouse will be displayed in the bottom right of the figure.