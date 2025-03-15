import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os
import pandas as pd
import seaborn as sns
import sys

from matplotlib.legend import Legend
from matplotlib.lines import Line2D
from matplotlib.widgets import Button


"""
Class that will open and plot data inside a given CSV file.
"""
class Plotter:
    IGNORE_COLUMNS = []
    PRIMARY_COLUMNS = []
    SECONDARY_COLUMNS = []
    TERTIARY_COLUMNS = []
    QUATERNARY_COLUMNS = []
    MARGIN_FACTOR = 1.05
    selected_line = None

    """
    Identifies which axes each column should be on based on the ':' identifier in the CSV column name.

    @param columns: All columns to filter through.
    """
    @staticmethod
    def identifyAxes(columns):
        for index, column in enumerate(columns):
            if column.endswith(':0'):
                Plotter.IGNORE_COLUMNS.append(index)
            elif column.endswith(':2'):
                Plotter.SECONDARY_COLUMNS.append(index)
            elif column.endswith(':3'):
                Plotter.TERTIARY_COLUMNS.append(index)
            elif column.endswith(':4'):
                Plotter.QUATERNARY_COLUMNS.append(index)
            else:
                Plotter.PRIMARY_COLUMNS.append(index)

        print(f"Primary Columns: {Plotter.PRIMARY_COLUMNS}")
        print(f"Secondary Columns: {Plotter.SECONDARY_COLUMNS}")
        print(f"Tertiary Columns: {Plotter.TERTIARY_COLUMNS}")
        print(f"Quaternary Columns: {Plotter.QUATERNARY_COLUMNS}")
        print(f"Ignore Columns: {Plotter.IGNORE_COLUMNS}")


    """
    Sets up the figure axes.

    @param fig: The figure object.
    @param filename: The name of the file being plotted, this is used as the figure title.

    @return 4 configured axes.
    """
    @staticmethod
    def setupAxes(fig, filename):
        ax1 = fig.add_subplot(111)
        ax2 = ax1.twinx()
        ax3 = ax1.twinx()
        ax4 = ax1.twinx()

        # Adjust primary and secondary axes
        ax2.yaxis.tick_left()
        ax2.yaxis.set_label_position("left")
        ax1.spines['left'].set_position(("outward", 0))
        ax2.spines['left'].set_position(("outward", 80))
        ax2.spines["left"].set_visible(True)

        # Adjust tertionary and quaternary axes
        ax3.spines['right'].set_position(('outward', 0))
        ax4.spines['right'].set_position(('outward', 80))
        ax3.spines['right'].set_visible(True)
        ax4.spines['right'].set_visible(True)

        # Set the gridlines and tick parameters
        ax1.grid(True, linestyle='--', alpha=0.7)
        ax1.xaxis.grid(True, which='major', linestyle='--', alpha=0.5)
        ax1.yaxis.grid(True, linestyle='--', alpha=0.5)
        ax1.xaxis.set_major_locator(ticker.MaxNLocator(nbins=20))

        # Disable scientific notation
        ax1.ticklabel_format(style='plain', axis='both', useOffset=False)
        ax2.ticklabel_format(style='plain', axis='both', useOffset=False)
        ax3.ticklabel_format(style='plain', axis='both', useOffset=False)
        ax4.ticklabel_format(style='plain', axis='both', useOffset=False)

        # Set figure titles
        ax1.set_title(os.path.split(filename)[1])
        ax1.set_xlabel("Tick (Milliseconds)")
        ax1.set_ylabel("Primary Axis Values")
        ax2.set_ylabel("Secondary Axis Values")
        ax3.set_ylabel("Tertiary Axis Values")
        ax4.set_ylabel("Quaternary Axis Values")

        # Adjust the titles of the axes so they are a little closer to the labels
        ax1.yaxis.set_label_coords(-0.025, 0.5)
        ax2.yaxis.set_label_coords(-0.1, 0.5)
        ax3.yaxis.set_label_coords(1.025, 0.5)
        ax4.yaxis.set_label_coords(1.1, 0.5)

        return ax1, ax2, ax3, ax4


    """
    Calculates the maximum absolute values for the primary, secondary, tertiary, and quaternary axes. This aligns all axes at the zero point.

    @param df: The data frame object.
    @param column_names: The names of all columns with data to plot.
    @param num_columns: List of column indices.

    @return max absolute values for all axes.
    """
    @staticmethod
    def calculateMaxAbsValues(df, column_names, num_columns):
        max_value_primary = 0
        max_value_secondary = 0
        max_value_tertiary = 0
        max_value_quaternary = 0

        for x in num_columns:
            if x not in Plotter.IGNORE_COLUMNS:
                column_name = column_names[x]
                max_axis_value = max(abs(df[column_name].max()), abs(df[column_name].min()))
                if x in Plotter.SECONDARY_COLUMNS:
                    max_value_secondary = max(max_value_secondary, max_axis_value)
                elif x in Plotter.TERTIARY_COLUMNS:
                    max_value_tertiary = max(max_value_tertiary, max_axis_value)
                elif x in Plotter.QUATERNARY_COLUMNS:
                    max_value_quaternary = max(max_value_quaternary, max_axis_value)
                else:
                    max_value_primary = max(max_value_primary, max_axis_value)

        return max_value_primary, max_value_secondary, max_value_tertiary, max_value_quaternary


    """
    Sets the limits for the columns on the y-axis. This allows all columns to line up at the zero point.

    @param ax1: The primary axis.
    @param ax2: The secondary axis.
    @param ax3: The tertiary axis.
    @param ax4: The quaternary axis.
    @param max_abs_values: The maximum absolute values for the primary, secondary, tertiary, and quaternary columns.
    """
    @staticmethod
    def setYLimits(ax1, ax2, ax3, ax4, max_abs_values):
        max_abs_value_primary, max_abs_value_secondary, max_abs_value_tertiary, max_abs_value_quaternary = max_abs_values
        min_range = 0.1

        # Primary axis
        if max_abs_value_primary > 0:
            ax1.set_ylim(-max_abs_value_primary * Plotter.MARGIN_FACTOR, max_abs_value_primary * Plotter.MARGIN_FACTOR)
        else:
            ax1.set_ylim(-min_range, min_range)

        # Secondary axis
        if max_abs_value_secondary > 0:
            ax2.set_ylim(-max_abs_value_secondary * Plotter.MARGIN_FACTOR, max_abs_value_secondary * Plotter.MARGIN_FACTOR)
        else:
            ax2.set_ylim(-min_range, min_range)

        # Tertiary axis
        if max_abs_value_tertiary > 0:
            ax3.set_ylim(-max_abs_value_tertiary * Plotter.MARGIN_FACTOR, max_abs_value_tertiary * Plotter.MARGIN_FACTOR)
        else:
            ax3.set_ylim(-min_range, min_range)

        # Quaternary axis
        if max_abs_value_quaternary > 0:
            ax4.set_ylim(-max_abs_value_quaternary * Plotter.MARGIN_FACTOR, max_abs_value_quaternary * Plotter.MARGIN_FACTOR)
        else:
            ax4.set_ylim(-min_range, min_range)


    """
    Plots the data for each axis.

    @param ax1: The primary axis.
    @param ax2: The secondary axis.
    @param ax3: The tertiary axis.
    @param ax4: The quaternary axis.
    @param df: The data frame.
    @param columns: The total columns with data to plot.
    @param num_columns: List of column indices.
    @param column_colours: Dictionary mapping column indices to specific colours.

    @return primary, secondary, tertiary, and quaternary lines.
    """
    @staticmethod
    def plotDataOnAxis(ax1, ax2, ax3, ax4, df, columns, num_columns, column_colours):
        primary_lines = []
        secondary_lines = []
        tertiary_lines = []
        quaternary_lines = []

        for x in num_columns:
            if x not in Plotter.IGNORE_COLUMNS:
                column_name = columns[x]
                line_colour = column_colours.get(x, 'black') # Default line colour to black if it does not exist in the column_colour dictionary
                label = column_name.rsplit(':', 1)[0] # Strip the axes suffix from the column name for the legend
                if x in Plotter.SECONDARY_COLUMNS:
                    line, = ax2.plot(df[columns[1]], df[column_name], label=label, linestyle=':', color=line_colour)
                    secondary_lines.append(line)
                elif x in Plotter.TERTIARY_COLUMNS:
                    line, = ax3.plot(df[columns[1]], df[column_name], label=label, linestyle='--', color=line_colour)
                    tertiary_lines.append(line)
                elif x in Plotter.QUATERNARY_COLUMNS:
                    line, = ax4.plot(df[columns[1]], df[column_name], label=label, color=line_colour)
                    quaternary_lines.append(line)
                else:
                    # Plot primary axis.
                    line, = ax1.plot(df[columns[1]], df[column_name], label=label, color=line_colour)
                    primary_lines.append(line)

        return primary_lines, secondary_lines, tertiary_lines, quaternary_lines


    """
    Returns the legend properties for the plot.
    """
    @staticmethod
    def getLegendProperties():
        return {'fontsize': 9, 'framealpha': 0.8, 'edgecolor': '#666666', 'handlelength': 4, 'handleheight': 1}


    """
    Function that traces the mouse cursor x position when hovering over a selected line and tries to identify the value of the closest point on the selected line.

    @param x: The x-coordinate of the mouse cursor.
    @return The formatted string to display in the text box.
    """
    @staticmethod
    def custom_coord_formatter(x):
        # Only consider the selected line if there is one
        if Plotter.selected_line and Plotter.selected_line.get_visible():
            try:
                x_data = Plotter.selected_line.get_xdata()
                y_data = Plotter.selected_line.get_ydata()

                if len(x_data) > 0:
                    # Find closest point based on x-coordinate
                    closest_index = min(range(len(x_data)), key=lambda i: abs(x_data[i] - x))

                    # Get data point coordinates
                    point_x = x_data[closest_index]
                    point_y = y_data[closest_index]

                    label = Plotter.selected_line.get_label().strip().replace('|', '').replace('\n', ' ')

                    if label == "currentPosition" or label == "targetPosition":
                        return f"Line: {label}\nValue: {int(point_y)} m°"
                    elif label == "currentSpeed" or label == "targetSpeed":
                        return f"Line: {label}\nValue: {int(point_y)} m°/s"
                    elif label == "output":
                        return f"Line: {label}\nValue: {int(point_y)} % Duty Cycle"
                    elif label == "current":
                        return f"Line: {label}\nValue: {int(point_y)} mA"
                    else:
                        return f"Line: {label}\nValue: {int(point_y)}"
            except Exception as e:
                print(f"Error processing selected line: {e}")

        # Return default string
        return "Click a line to view data"


    """
    Entry function. Plots data in csv file. The order of code in this function is very important.

    @param df: The csv data frame.
    @param filename: The name of the file.
    """
    @staticmethod
    def plotData(df, filename):
        print(f"Plotting data from {filename}")

        # Gather column names with data to plot
        columns = df.columns.values.tolist()
        num_columns = [i for i in range(len(columns))]
        for x in num_columns:
            print(f"{df[columns[num_columns[x]]].name} = {str(x)}")

        # Work out what axes each column should be on
        Plotter.identifyAxes(columns)

        # Adjust the size of figure and margins
        fig = plt.figure(figsize=(17, 9.5))
        fig.subplots_adjust(top=0.95, left=0.1)
        ax1, ax2, ax3, ax4 = Plotter.setupAxes(fig, filename)

        # Colour palette for each plot line. If you want to customise another column, you must add in its ID and colour.
        column_colours = {
            2: sns.color_palette('tab20')[2],    # Orange - Current Position
            3: sns.color_palette('tab20')[4],    # Green - Target Position
            4: sns.color_palette('tab20')[2],    # Orange - Current Speed
            5: sns.color_palette('tab20')[4],    # Green - Target Speed
            6: sns.color_palette('tab20')[6],    # Red - Error
            7: sns.color_palette('tab20')[18],   # Light Blue - Integral
            9: sns.color_palette('tab20')[6],    # Red - Speed Error
            10: sns.color_palette('tab20')[18],  # Light Blue - Integral Speed
            12: sns.color_palette('tab20b')[2],  # Purple - P Term
            13: sns.color_palette('tab20b')[6],  # Green - I Term
            14: sns.color_palette('tab20b')[10], # Gold - D Term
            15: sns.color_palette('tab20b')[18], # Pink - F Term
            16: sns.color_palette('tab20c')[1],  # Blue - P Speed Term
            17: sns.color_palette('tab20c')[5],  # Orange - I Speed Term
            18: sns.color_palette('tab20c')[9],  # Green - D Speed Term
            19: sns.color_palette('Set1')[6],    # Brown - Output
            20: sns.color_palette('Dark2')[3],   # Purple - Current
        }

        # Calculate the max values and set the limits of the Y axes, this align zero with all axes
        max_abs_values = Plotter.calculateMaxAbsValues(df, columns, num_columns)
        Plotter.setYLimits(ax1, ax2, ax3, ax4, max_abs_values)

        # Get the plot lines for each axis
        primary_lines, secondary_lines, tertiary_lines, quaternary_lines = Plotter.plotDataOnAxis(ax1, ax2, ax3, ax4, df, columns, num_columns, column_colours)

        # Spaces out the individual axes plot lines
        spacer1_line = Line2D([0], [0], color='white', lw=0, label=' ')
        spacer2_line = Line2D([0], [0], color='white', lw=0, label=' ')
        spacer3_line = Line2D([0], [0], color='white', lw=0, label=' ')

        # Combine all lines and labels
        all_lines = primary_lines + [spacer1_line] + secondary_lines + [spacer2_line] + tertiary_lines + [spacer3_line] + quaternary_lines
        all_labels = [line.get_label() for line in all_lines]

        # Define all_axes to include the axes for each line
        all_axes = [ax1] * len(primary_lines) + [None] + [ax2] * len(secondary_lines) + [None] + [ax3] * len(tertiary_lines) + [None] + [ax4] * len(quaternary_lines)

        # Create the legend
        legend_properties = Plotter.getLegendProperties()
        legend = fig.legend(all_lines, all_labels, fancybox=True, shadow=True, bbox_to_anchor=(0.20, 0.52), **legend_properties)
        legend.set_draggable(True)

        # Make legend interactive
        lined = {}
        for legline, legtext, origline in zip(legend.get_lines(), legend.get_texts(), all_lines):
            legline.set_picker(True)
            legtext.set_picker(True)
            lined[legline] = origline
            lined[legtext] = origline

        #----------------------------------------------- ON PICK -----------------------------------------------
        """
        Event handler for picking legend items to show/hide corresponding plot lines.

        This function toggles the visibility of the plot line associated with the clicked legend item.
        It also adjusts the transparency of the legend entry to indicate visibility.
        """
        def onPick(event):
            clicked_object = event.artist
            if isinstance(clicked_object, Legend):
                return
            else:
                origline = lined[clicked_object]
                visible = not origline.get_visible()
                origline.set_visible(visible)
                for legline, legtext in zip(legend.get_lines(), legend.get_texts()):
                    if lined[legline] == origline:
                        legline.set_alpha(1.0 if visible else 0.2)
                        legtext.set_alpha(1.0 if visible else 0.2)
                fig.canvas.draw()

        # Connect the onPick event
        fig.canvas.mpl_connect('pick_event', onPick)

        #----------------------------------------------- LINE VALUE BOX -----------------------------------------------

        text_display = fig.text(0.825, 0.02, "Click a line to view data",
                            ha='center', va='bottom',
                            bbox=dict(facecolor='white', alpha=0.9, edgecolor='red', boxstyle='round,pad=0.5'),
                            fontsize=12)

        def onHover(event):
            if event.inaxes:
                # Only update if we have a selected line
                if Plotter.selected_line and Plotter.selected_line.get_visible():
                    x = event.xdata
                    string = Plotter.custom_coord_formatter(x)
                    text_display.set_text(string)
                    fig.canvas.draw_idle()

        # Connect the onHover event
        fig.canvas.mpl_connect('motion_notify_event', onHover)

        #----------------------------------------------- ON CLICK -----------------------------------------------

        """
        Click event.
        Finds the closest point on a line to the click and selects it. Locates the data for chosen line and mouse cursor location and updates text value box
        """
        def onClick(event):
            # First check if we're inside one of the plot axes
            if event.inaxes in [ax1, ax2, ax3, ax4]:
                # Check if the click was inside the legend's bbox
                if legend.get_window_extent().contains(event.x, event.y):
                    # Click is inside legend, do nothing
                    return

                # Get the data coordinates of the click
                x = event.xdata
                y = event.ydata

                # Convert click point to display coordinates (pixels)
                click_display = event.inaxes.transData.transform((x, y))

                # Find the closest line to the click
                min_distance = float('inf')
                closest_line = None

                for line, ax in zip(all_lines, all_axes):
                    # Skip spacer lines or invisible lines
                    if ax is None or not line.get_visible():
                        continue

                    try:
                        # Get the data from the line
                        x_data = line.get_xdata()
                        y_data = line.get_ydata()

                        if len(x_data) > 0:
                            # Find closest x-coordinate point on this line
                            closest_index = min(range(len(x_data)), key=lambda i: abs(x_data[i] - x))
                            point_x = x_data[closest_index]
                            point_y = y_data[closest_index]

                            # Convert data point to display coordinates (pixels)
                            display_coords = ax.transData.transform((point_x, point_y))

                            # Calculate distance in pixel space (screen coordinates)
                            distance = ((display_coords[0] - click_display[0])**2 +
                                        (display_coords[1] - click_display[1])**2)**0.5

                            if distance < min_distance:
                                min_distance = distance
                                closest_line = line
                    except Exception as e:
                        print(f"Error finding closest point: {e}")
                        continue

                # Check if we're clicking on the already selected line
                if Plotter.selected_line and Plotter.selected_line.get_label() == closest_line.get_label():
                    Plotter.selected_line = None

                    # Reset all lines to normal width
                    for line in all_lines:
                        if isinstance(line, Line2D) and line.get_visible():
                            line.set_linewidth(1.5)

                    # Reset all legend text to normal weight
                    for legtext in legend.get_texts():
                        legtext.set_color('black')

                    # Clear the text box
                    text_display.set_text("Click a line to view data")
                else:
                    # Update the selected line
                    Plotter.selected_line = closest_line

                    # Reset all line widths
                    for line in all_lines:
                        if isinstance(line, Line2D) and line.get_visible():
                            line.set_linewidth(1.5)

                    # Reset all legend text to normal weight
                    for legtext in legend.get_texts():
                        legtext.set_color('black')

                    # Make the selected line thicker
                    if Plotter.selected_line:
                        Plotter.selected_line.set_linewidth(3.0)

                        # Find and highlight selected line text in the legend
                        selected_label = Plotter.selected_line.get_label()
                        for i, legline in enumerate(legend.get_lines()):
                            if i < len(legend.get_texts()) and lined[legline].get_label() == selected_label:
                                legend.get_texts()[i].set_color('red')
                                break

                fig.canvas.draw_idle()  # Refresh figure

        # Connect the click handler
        fig.canvas.mpl_connect('button_press_event', onClick)

        #----------------------------------------------- SHOW/HIDE BUTTON -----------------------------------------------

        # Create a button to show/hide all lines
        show_hide_button = plt.axes([0.01, 0.01, 0.08, 0.05])
        button_show_hide = Button(show_hide_button, 'Hide All')
        hide_all_lines = False

        """
        Button event.
        Toggles the visibility of all selected lines/axes.
        """
        def toggleShowHideAll(event):
            nonlocal hide_all_lines
            hide_all_lines = not hide_all_lines
            button_show_hide.label.set_text('Show All' if hide_all_lines else 'Hide All')

            if hide_all_lines:
                if not hide_primary_lines:
                    toggleShowHidePrimary(event)
                if not hide_secondary_lines:
                    toggleShowHideSecondary(event)
                if not hide_tertiary_lines:
                    toggleShowHideTertiary(event)
                if not hide_quaternary_lines:
                    toggleShowHideQuaternary(event)
            else:
                if hide_primary_lines:
                    toggleShowHidePrimary(event)
                if hide_secondary_lines:
                    toggleShowHideSecondary(event)
                if hide_tertiary_lines:
                    toggleShowHideTertiary(event)
                if hide_quaternary_lines:
                    toggleShowHideQuaternary(event)

            fig.canvas.draw_idle()

        # Connect show/hide button event
        button_show_hide.on_clicked(toggleShowHideAll)

        #----------------------------------------------- PRIMARY BUTTON -----------------------------------------------

        # Create a button to show/hide primary lines
        primary_show_hide_button = plt.axes([0.10, 0.01, 0.08, 0.05])  # Adjust the position to place it next to the show/hide all button
        button_primary_show_hide = Button(primary_show_hide_button, 'Hide Primary')
        hide_primary_lines = False

        """
        Button event.
        Toggles the visibility of primary plot lines and adjusts the transparency of the corresponding legend entries.
        """
        def toggleShowHidePrimary(event):
            nonlocal hide_primary_lines
            if hide_primary_lines:
                # Now show primary lines
                for line in primary_lines:
                    line.set_visible(True)
                    for legline, legtext in zip(legend.get_lines(), legend.get_texts()):
                        if lined[legline] == line:
                            # Change transparency of line and text to visible
                            legline.set_alpha(1.0)
                            legtext.set_alpha(1.0)
                button_primary_show_hide.label.set_text('Hide Primary')
            else:
                # Now hide primary lines
                for line in primary_lines:
                    line.set_visible(False)
                    for legline, legtext in zip(legend.get_lines(), legend.get_texts()):
                        if lined[legline] == line:
                            # Change transparency of line and text to barely visible
                            legline.set_alpha(0.2)
                            legtext.set_alpha(0.2)
                button_primary_show_hide.label.set_text('Show Primary')
            hide_primary_lines = not hide_primary_lines
            fig.canvas.draw_idle()

        # Connect show/hide primary button event
        button_primary_show_hide.on_clicked(toggleShowHidePrimary)

        #----------------------------------------------- SECONDARY BUTTON -----------------------------------------------

        # Create a button to show/hide secondary lines
        secondary_show_hide_button = plt.axes([0.19, 0.01, 0.08, 0.05])  # Adjust the position to place it next to the show/hide all button
        button_secondary_show_hide = Button(secondary_show_hide_button, 'Hide Secondary')
        hide_secondary_lines = False

        """
        Button event.
        Toggles the visibility of secondary plot lines and adjusts the transparency of the corresponding legend entries.
        """
        def toggleShowHideSecondary(event):
            nonlocal hide_secondary_lines
            if hide_secondary_lines:
                # Now show secondary lines
                for line in secondary_lines:
                    line.set_visible(True)
                    for legline, legtext in zip(legend.get_lines(), legend.get_texts()):
                        if lined[legline] == line:
                            # Change transparency of line and text to visible
                            legline.set_alpha(1.0)
                            legtext.set_alpha(1.0)
                button_secondary_show_hide.label.set_text('Hide Secondary')
            else:
                # Now hide secondary lines
                for line in secondary_lines:
                    line.set_visible(False)
                    for legline, legtext in zip(legend.get_lines(), legend.get_texts()):
                        if lined[legline] == line:
                            # Change transparency of line and text to barely visible
                            legline.set_alpha(0.2)
                            legtext.set_alpha(0.2)
                button_secondary_show_hide.label.set_text('Show Secondary')
            hide_secondary_lines = not hide_secondary_lines
            fig.canvas.draw_idle()

        # Connect show/hide secondary button event
        button_secondary_show_hide.on_clicked(toggleShowHideSecondary)

        #----------------------------------------------- TERTIARY BUTTON -----------------------------------------------

        # Create a button to show/hide tertiary lines
        tertiary_show_hide_button = plt.axes([0.28, 0.01, 0.08, 0.05])  # Adjust the position to place it next to the show/hide all button
        button_tertiary_show_hide = Button(tertiary_show_hide_button, 'Hide Tertiary')
        hide_tertiary_lines = False

        """
        Button event.
        Toggles the visibility of tertiary plot lines and adjusts the transparency of the corresponding legend entries.
        """
        def toggleShowHideTertiary(event):
            nonlocal hide_tertiary_lines
            if hide_tertiary_lines:
                # Now show tertiary lines
                for line in tertiary_lines:
                    line.set_visible(True)
                    for legline, legtext in zip(legend.get_lines(), legend.get_texts()):
                        if lined[legline] == line:
                            # Change transparency of line and text to visible
                            legline.set_alpha(1.0)
                            legtext.set_alpha(1.0)
                button_tertiary_show_hide.label.set_text('Hide Tertiary')
            else:
                # Now hide tertiary lines
                for line in tertiary_lines:
                    line.set_visible(False)
                    for legline, legtext in zip(legend.get_lines(), legend.get_texts()):
                        if lined[legline] == line:
                            # Change transparency of line and text to barely visible
                            legline.set_alpha(0.2)
                            legtext.set_alpha(0.2)
                button_tertiary_show_hide.label.set_text('Show Tertiary')
            hide_tertiary_lines = not hide_tertiary_lines
            fig.canvas.draw_idle()

        # Connect show/hide tertiary button event
        button_tertiary_show_hide.on_clicked(toggleShowHideTertiary)

        #----------------------------------------------- QUATERNARY BUTTON -----------------------------------------------

        # Create a button to show/hide quaternary lines
        quaternary_show_hide_button = plt.axes([0.37, 0.01, 0.08, 0.05])  # Adjust the position to place it next to the show/hide all button
        button_quaternary_show_hide = Button(quaternary_show_hide_button, 'Hide Quaternary')
        hide_quaternary_lines = False

        """
        Button event.
        Toggles the visibility of quaternary plot lines and adjusts the transparency of the corresponding legend entries.
        """
        def toggleShowHideQuaternary(event):
            nonlocal hide_quaternary_lines
            if hide_quaternary_lines:
                # Now show quaternary lines
                for line in quaternary_lines:
                    line.set_visible(True)
                    for legline, legtext in zip(legend.get_lines(), legend.get_texts()):
                        if lined[legline] == line:
                            # Change transparency of line and text to visible
                            legline.set_alpha(1.0)
                            legtext.set_alpha(1.0)
                button_quaternary_show_hide.label.set_text('Hide Quaternary')
            else:
                # Now hide quaternary lines
                for line in quaternary_lines:
                    line.set_visible(False)
                    for legline, legtext in zip(legend.get_lines(), legend.get_texts()):
                        if lined[legline] == line:
                            # Change transparency of line and text to barely visible
                            legline.set_alpha(0.2)
                            legtext.set_alpha(0.2)
                button_quaternary_show_hide.label.set_text('Show Quaternary')
            hide_quaternary_lines = not hide_quaternary_lines
            fig.canvas.draw_idle()

        # Connect show/hide quaternary button event
        button_quaternary_show_hide.on_clicked(toggleShowHideQuaternary)

        #----------------------------------------------- END -----------------------------------------------
        plt.show()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Missing parameters")
        sys.exit(1)

    filename = sys.argv[1]
    try:
        df = pd.read_csv(filename)
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        sys.exit(1)

    Plotter.plotData(df, filename)