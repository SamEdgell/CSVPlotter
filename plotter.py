import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os
import pandas as pd
import seaborn as sns
import sys

from matplotlib.legend import Legend
from matplotlib.lines import Line2D
from matplotlib.widgets import Button


MARGIN_FACTOR = 1.05


def identifyAxes(columns):
    """
    Identifies which axes each column should be on based on the ':' identifier.

    Args:
        columns: List of column names to sort through.

    Returns:
        Tuple of lists, each containing the indices of columns assigned to that axis.
    """
    ignore_columns = []
    primary_columns = []
    secondary_columns = []
    tertiary_columns = []
    quaternary_columns = []
    for index, column in enumerate(columns):
        if column.endswith(':0'):
            ignore_columns.append(index)
        elif column.endswith(':2'):
            secondary_columns.append(index)
        elif column.endswith(':3'):
            tertiary_columns.append(index)
        elif column.endswith(':4'):
            quaternary_columns.append(index)
        else:
            primary_columns.append(index) # Default to primary.
    print(f"\nIdentified Columns Below:")
    print(f"Ignore: {ignore_columns}")
    print(f"Primary: {primary_columns}")
    print(f"Secondary: {secondary_columns}")
    print(f"Tertiary: {tertiary_columns}")
    print(f"Quaternary: {quaternary_columns}\n")

    return ignore_columns, primary_columns, secondary_columns, tertiary_columns, quaternary_columns


def setupAxes(fig, filename):
    """
    Sets up the figure axes for plotting with up to four y-axes.

    Args:
        fig:        The matplotlib figure object.
        filename:   The name of the file being plotted (used as the figure title).

    Returns:
        Tuple of four configured axes.
    """
    ax1 = fig.add_subplot(111)
    ax2 = ax1.twinx()
    ax3 = ax1.twinx()
    ax4 = ax1.twinx()

    # Adjust primary and secondary axes.
    ax2.yaxis.tick_left()
    ax2.yaxis.set_label_position("left")
    ax1.spines['left'].set_position(("outward", 0))
    ax2.spines['left'].set_position(("outward", 80))
    ax2.spines["left"].set_visible(True)

    # Adjust tertiary and quaternary axes.
    ax3.spines['right'].set_position(('outward', 0))
    ax4.spines['right'].set_position(('outward', 80))
    ax3.spines['right'].set_visible(True)
    ax4.spines['right'].set_visible(True)

    # Set the gridlines and tick parameters.
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.xaxis.grid(True, which='major', linestyle='--', alpha=0.5)
    ax1.yaxis.grid(True, linestyle='--', alpha=0.5)
    ax1.xaxis.set_major_locator(ticker.MaxNLocator(nbins=20))

    # Disable scientific notation.
    ax1.ticklabel_format(style='plain', axis='both', useOffset=False)
    ax2.ticklabel_format(style='plain', axis='both', useOffset=False)
    ax3.ticklabel_format(style='plain', axis='both', useOffset=False)
    ax4.ticklabel_format(style='plain', axis='both', useOffset=False)

    # Set figure titles.
    ax1.set_title(os.path.split(filename)[1])
    ax1.set_xlabel("Tick (Milliseconds)")
    ax1.set_ylabel("Primary Axis Values")
    ax2.set_ylabel("Secondary Axis Values")
    ax3.set_ylabel("Tertiary Axis Values")
    ax4.set_ylabel("Quaternary Axis Values")

    # Adjust the titles of the axes so they are a little closer to the labels.
    ax1.yaxis.set_label_coords(-0.025, 0.5)
    ax2.yaxis.set_label_coords(-0.1, 0.5)
    ax3.yaxis.set_label_coords(1.025, 0.5)
    ax4.yaxis.set_label_coords(1.1, 0.5)

    return ax1, ax2, ax3, ax4


def calculateMaxAbsValues(df, columns, num_columns, ignore_cols, primary_cols, secondary_cols, tertiary_cols, quaternary_cols):
    """
    Calculates the maximum absolute values for the primary, secondary, tertiary, and quaternary axes. This aligns all axes at the zero point.

    Args:
        df:                 The pandas DataFrame object.
        columns:            List of all column names with data to plot.
        num_columns:        List of column indices.
        ignore_cols:        List of column indices to ignore from plotting.
        primary_cols:       List of column indices for the primary axis.
        secondary_cols:     List of column indices for the secondary axis.
        tertiary_cols:      List of column indices for the tertiary axis.
        quaternary_cols:    List of column indices for the quaternary axis.

    Returns:
        Tuple of max absolute values for all axes.
    """
    max_vals = {'primary': 0, 'secondary': 0, 'tertiary': 0, 'quaternary': 0}

    for x in num_columns:
        if x not in ignore_cols:
            column_name = columns[x]
            try:
                # Ensure column is numeric before calculating max/min.
                if pd.api.types.is_numeric_dtype(df[column_name]):
                     max_axis_value = max(abs(df[column_name].max()), abs(df[column_name].min()))
                else:
                     print(f"Non-numeric data in {column_name}. Skipping max value.", file=sys.stderr)
                     continue
            except Exception as e:
                 print(f"Error calculating max value for {column_name} - {e}", file=sys.stderr)
                 continue

            if x in secondary_cols: max_vals['secondary'] = max(max_vals['secondary'], max_axis_value)
            elif x in tertiary_cols: max_vals['tertiary'] = max(max_vals['tertiary'], max_axis_value)
            elif x in quaternary_cols: max_vals['quaternary'] = max(max_vals['quaternary'], max_axis_value)
            elif x in primary_cols: max_vals['primary'] = max(max_vals['primary'], max_axis_value)

    return max_vals['primary'], max_vals['secondary'], max_vals['tertiary'], max_vals['quaternary']


def plotDataOnAxis(ax1, ax2, ax3, ax4, df, columns, num_columns, column_colours, ignore_cols, primary_cols, secondary_cols, tertiary_cols, quaternary_cols):
    """
    Plots the data for each axis.

    Args:
        ax1:                The primary axis.
        ax2:                The secondary axis.
        ax3:                The tertiary axis.
        ax4:                The quaternary axis.
        df:                 The pandas DataFrame.
        columns:            List of all column names with data to plot.
        num_columns:        List of column indices.
        column_colours:     Dictionary mapping column indices to specific colours.
        ignore_cols:        List of column indices to ignore from plotting.
        primary_cols:       List of column indices for the primary axis.
        secondary_cols:     List of column indices for the secondary axis.
        tertiary_cols:      List of column indices for the tertiary axis.
        quaternary_cols:    List of column indices for the quaternary axis.

    Returns:
        Tuple of lists of lines created for each axis.
    """
    primary_lines = []
    secondary_lines = []
    tertiary_lines = []
    quaternary_lines = []
    tickMs = columns[1]

    for x in num_columns:
        if x not in ignore_cols:
            column_name = columns[x]

            # Ensure data column is valid and numeric before plotting.
            if column_name not in df.columns or not pd.api.types.is_numeric_dtype(df[column_name]):
                 print(f"Invalid/Non-numeric data in {column_name}", file=sys.stderr)
                 continue

            line_colour = column_colours.get(x, 'black') # Default line colour to black if it does not exist in the column_colour dictionary.
            label = column_name.rsplit(':', 1)[0] # Strip the axes suffix from the column name for the legend.
            try:
                if x in secondary_cols:
                    line, = ax2.plot(df[tickMs], df[column_name], label=label, linestyle=':', color=line_colour)
                    secondary_lines.append(line)
                elif x in tertiary_cols:
                    line, = ax3.plot(df[tickMs], df[column_name], label=label, linestyle='--', color=line_colour)
                    tertiary_lines.append(line)
                elif x in quaternary_cols:
                    line, = ax4.plot(df[tickMs], df[column_name], label=label, color=line_colour)
                    quaternary_lines.append(line)
                else:
                    # Plot on primary axis.
                    line, = ax1.plot(df[tickMs], df[column_name], label=label, color=line_colour)
                    primary_lines.append(line)
            except Exception as e:
                 print(f"Error plotting column: {column_name} - {e}", file=sys.stderr)

    return primary_lines, secondary_lines, tertiary_lines, quaternary_lines


def getLegendProperties():
    """
    Returns the legend properties for the plot.

    Returns:
        dict: Dictionary of legend property settings.
    """
    return {'fontsize': 9, 'framealpha': 0.8, 'edgecolor': '#666666', 'handlelength': 4, 'handleheight': 1}


def customCoordFormatter(x, selected_line):
    """
    Traces the mouse cursor x position when hovering over a selected line and identifies the value of the closest point.

    Args:
        x:              The x-coordinate of the mouse cursor.
        selected_line:  The currently selected Line2D object.

    Returns:
        The formatted string to display in the text box.
    """
    # Only consider the selected line if there is one.
    if selected_line and selected_line.get_visible():
        try:
            x_data = selected_line.get_xdata()
            y_data = selected_line.get_ydata()

            if len(x_data) > 0:
                # Find closest point based on x-coordinate.
                closest_index = min(range(len(x_data)), key=lambda i: abs(x_data[i] - x))

                # Get data point coordinates.
                point_y = y_data[closest_index]

                label = selected_line.get_label().strip().replace('|', '').replace('\n', ' ')

                unit = ""
                # Use integer formatting only for true ints, else float formatting
                if isinstance(point_y, int) or (isinstance(point_y, float) and point_y.is_integer()):
                    value_str = f"{int(point_y):d}"
                else:
                    value_str = f"{point_y:.2f}"

                if "Position" in label: unit = ""
                elif "Speed" in label: unit = ""
                elif "output" in label: unit = " % Duty Cycle"
                elif "current" in label: unit = " mA"

                return f"Line: {label}\nValue: {value_str}{unit}"

        except Exception as e:
            print(f"Formatter error: {e}", file=sys.stderr)

    # Return default string.
    return "Click a line to view live data"


def createPlot(filename):
    """
    Opens filename as a dataframe and plots it. The order of code in this function is very important.

    Args:
        filename: The name of the file.
    """
    try:
        df = pd.read_csv(filename)
    except FileNotFoundError:
        print(f"\nPlotting file not found: {filename}\n", file=sys.stderr)
        return
    except Exception as e:
        print(f"\nError plotting {filename}: {e}\n", file=sys.stderr)
        return

    print(f"\nPlotting file: {filename}\n")

    # Gather column names with data to plot.
    columns = df.columns.values.tolist()
    num_columns = list(range(len(columns)))
    print(f"Index/Column Name Below:")
    for x in num_columns:
        print(f"{x}) {columns[x].strip()}")

    # Work out what axes each column should be on.
    ignore_cols, primary_cols, secondary_cols, tertiary_cols, quaternary_cols = identifyAxes(columns)

    # Adjust the figure and margins.
    fig = plt.figure(figsize=(17, 9.5))
    fig.subplots_adjust(top=0.95, left=0.1)
    ax1, ax2, ax3, ax4 = setupAxes(fig, filename)

    # Colour palette for each plot line. If you want to customise another column, you must add in its ID and colour, otherwise it will be set to the default colour.
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

    # Calculate the max values and set the limits of the Y axes, this align zero with all axes.
    max_abs_values = calculateMaxAbsValues(df, columns, num_columns, ignore_cols, primary_cols, secondary_cols, tertiary_cols, quaternary_cols)

    # Set the limits for Y axis for all axes, this aligns all columns to the zero point.
    min_range = 0.1
    ax1.set_ylim(-max(max_abs_values[0] * MARGIN_FACTOR, min_range), max(max_abs_values[0] * MARGIN_FACTOR, min_range))
    ax2.set_ylim(-max(max_abs_values[1] * MARGIN_FACTOR, min_range), max(max_abs_values[1] * MARGIN_FACTOR, min_range))
    ax3.set_ylim(-max(max_abs_values[2] * MARGIN_FACTOR, min_range), max(max_abs_values[2] * MARGIN_FACTOR, min_range))
    ax4.set_ylim(-max(max_abs_values[3] * MARGIN_FACTOR, min_range), max(max_abs_values[3] * MARGIN_FACTOR, min_range))

    # Get the plot lines for each axis.
    primary_lines, secondary_lines, tertiary_lines, quaternary_lines = plotDataOnAxis(ax1, ax2, ax3, ax4, df, columns, num_columns, column_colours,
        ignore_cols, primary_cols, secondary_cols, tertiary_cols, quaternary_cols
    )

    # Spaces out the individual axes plot lines.
    spacer1_line = Line2D([0], [0], color='white', lw=0, label=' ')
    spacer2_line = Line2D([0], [0], color='white', lw=0, label=' ')
    spacer3_line = Line2D([0], [0], color='white', lw=0, label=' ')

    # Combine all lines and labels.
    all_lines = primary_lines + [spacer1_line] + secondary_lines + [spacer2_line] + tertiary_lines + [spacer3_line] + quaternary_lines
    all_labels = [line.get_label() for line in all_lines]

    # Define all_axes to include the axes for each line.
    all_axes = ([ax1] * len(primary_lines) + [None] + [ax2] * len(secondary_lines) + [None] + [ax3] * len(tertiary_lines) + [None] + [ax4] * len(quaternary_lines))

    # Create the legend - Call helper directly.
    legend_properties = getLegendProperties()
    legend = fig.legend(all_lines, all_labels, fancybox=True, shadow=True, bbox_to_anchor=(0.20, 0.52), **legend_properties)
    legend.set_draggable(True)

    # Make legend interactive.
    lined = {}
    for legline, legtext, origline in zip(legend.get_lines(), legend.get_texts(), all_lines):
        # Check if origline is valid before setting picker.
        if isinstance(origline, Line2D):
            legline.set_picker(True)
            legtext.set_picker(True)
            lined[legline] = origline
            lined[legtext] = origline


    #----------------------------------------------- ON PICK -----------------------------------------------


    def onPick(event):
        """
        Event handler for picking legend items to show/hide corresponding plot lines.
        This function toggles the visibility of the plot line associated with the clicked legend item.
        It also adjusts the transparency of the legend entry to indicate visibility.
        """
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

    # Connect the onPick event.
    fig.canvas.mpl_connect('pick_event', onPick)


    #----------------------------------------------- LINE VALUE BOX -----------------------------------------------


    selected_line = None
    text_display = fig.text(0.825, 0.02, "Click a line to view live data",
                        ha='center', va='bottom',
                        bbox=dict(facecolor='white', alpha=0.9, edgecolor='red', boxstyle='round,pad=0.5'),
                        fontsize=12)

    hide_flags = {'all': False, 'primary': False, 'secondary': False, 'tertiary': False, 'quaternary': False}
    button_refs = {}


    def onHover(event):
        """
        Event handler for mouse movement over the plot area. Updates the text box with the value at the cursor for the selected line.
        """
        if event.inaxes and text_display:
            # Only update if we have a selected line.
            if selected_line and selected_line.get_visible():
                x = event.xdata
                if x is not None: # Check if xdata is valid.
                    string = customCoordFormatter(x, selected_line)
                    text_display.set_text(string)
                    fig.canvas.draw_idle()


    # Connect the onHover event.
    fig.canvas.mpl_connect('motion_notify_event', onHover)


    #----------------------------------------------- ON CLICK -----------------------------------------------


    def onClick(event):
        """
        Click event.
        Finds the closest point on a line to the click and selects it.
        Locates the data for the chosen line and mouse cursor location and updates the text value box.
        """
        nonlocal selected_line
        # First check if we're inside one of the plot axes.
        if event.inaxes in [ax1, ax2, ax3, ax4]:
            # Check if the click was inside the legend's bbox.
            if legend and legend.get_window_extent().contains(event.x, event.y):
                # Click is inside legend, do nothing.
                return

            # Get the data coordinates of the click.
            x = event.xdata
            y = event.ydata
            if x is None or y is None: return # Click outside data area.

            # Convert click point to display coordinates (pixels).
            click_display = event.inaxes.transData.transform((x, y))

            # Find the closest line to the click.
            min_distance = float('inf')
            closest_line = None
            click_tolerance = 10 # pixels.

            for line, ax in zip(all_lines, all_axes):
                # Skip spacer lines or invisible lines.
                if ax is None or not isinstance(line, Line2D) or not line.get_visible():
                    continue

                try:
                    # Get the data from the line.
                    x_data, y_data = line.get_data()

                    if len(x_data) > 0:
                        # Pixel distance calculation (more accurate for picking).
                        display_coords = ax.transData.transform(list(zip(x_data, y_data)))
                        distances = ((display_coords[:, 0] - click_display[0])**2 +
                                     (display_coords[:, 1] - click_display[1])**2)**0.5
                        current_min_dist = distances.min()

                        if current_min_dist < min_distance:
                            min_distance = current_min_dist
                            closest_line = line
                except Exception as e:
                    print(f"Error finding closest point {e}", file=sys.stderr)
                    continue

            newly_selected = None # Track if a new line was just selected.
            # Check if we're clicking near a line
            if closest_line and min_distance < click_tolerance:
                 # Check if clicking the already selected line to deselect.
                if selected_line == closest_line:
                    selected_line = None # Deselect.
                else:
                    # Select the new closest line.
                    selected_line = closest_line
                    newly_selected = selected_line # Mark as newly selected.
            elif selected_line: # Clicked away from any line, deselect if one was selected.
                 selected_line = None

            # Update visuals (line width, legend text colour).
            for line in all_lines:
                if isinstance(line, Line2D) and line.get_visible():
                    line.set_linewidth(3.0 if line == selected_line else 1.5)

            for legtext in legend.get_texts():
                 # Check if the text object is in our mapping before getting label.
                 legtext.set_color('red' if legtext in lined and lined[legtext] == selected_line else 'black')

            # Update text box.
            if newly_selected: # Update text immediately on new selection.
                 string = customCoordFormatter(x, newly_selected) # Use newly selected line.
                 text_display.set_text(string)
            elif selected_line is None: # Deselected or clicked away.
                 text_display.set_text("Click a line to view live data")

            fig.canvas.draw_idle()  # Refresh figure.

    # Connect the click handler.
    fig.canvas.mpl_connect('button_press_event', onClick)


    #----------------------------------------------- SHOW/HIDE BUTTONS -----------------------------------------------


    def toggleVisibilityGroup(event, group_key, lines_list, set_visibility=None):
        """
        Toggles visibility for a group of lines and updates legend and button label.

        Args:
            event:          The button click event.
            group_key:      The key for the group ('primary', 'secondary', etc.).
            lines_list:     The list of Line2D objects for the group.
            set_visibility: If not None, force visibility to this value.
        """
        nonlocal hide_flags
        # Determine current visibility by checking the first line (if any)
        current_visible = lines_list and lines_list[0].get_visible()
        # If set_visibility is provided, use it; otherwise, toggle
        new_visibility = set_visibility if set_visibility is not None else not current_visible
        new_alpha = 1.0 if new_visibility else 0.2
        new_button_text = f"Hide {group_key.capitalize()}" if new_visibility else f"Show {group_key.capitalize()}"

        for line in lines_list:
            if isinstance(line, Line2D):
                line.set_visible(new_visibility)
                # Update legend items.
                for legline, legtext in zip(legend.get_lines(), legend.get_texts()):
                    if legline in lined and lined[legline] == line: legline.set_alpha(new_alpha)
                    if legtext in lined and lined[legtext] == line: legtext.set_alpha(new_alpha)

        hide_flags[group_key] = not new_visibility  # True means hidden, False means visible
        if group_key in button_refs: button_refs[group_key].label.set_text(new_button_text)
        fig.canvas.draw_idle()


    def toggleShowHideAll(event):
        """
        Toggles visibility for all groups and updates the 'Show All/Hide All' button label.
        """
        nonlocal hide_flags
        hide_flags['all'] = not hide_flags['all']
        if 'all' in button_refs:
            button_refs['all'].label.set_text('Show All' if hide_flags['all'] else 'Hide All')

        # Explicitly set visibility for all groups
        toggleVisibilityGroup(event, 'primary', primary_lines, set_visibility=not hide_flags['all'])
        toggleVisibilityGroup(event, 'secondary', secondary_lines, set_visibility=not hide_flags['all'])
        toggleVisibilityGroup(event, 'tertiary', tertiary_lines, set_visibility=not hide_flags['all'])
        toggleVisibilityGroup(event, 'quaternary', quaternary_lines, set_visibility=not hide_flags['all'])

        fig.canvas.draw_idle()


    # Create buttons and connect handlers.
    button_positions = {
        'all': [0.01, 0.01, 0.08, 0.05], 'primary': [0.10, 0.01, 0.08, 0.05],
        'secondary': [0.19, 0.01, 0.08, 0.05], 'tertiary': [0.28, 0.01, 0.08, 0.05],
        'quaternary': [0.37, 0.01, 0.08, 0.05]
    }

    # Map keys to the lines.
    button_lines = {
        'primary': primary_lines, 'secondary': secondary_lines,
        'tertiary': tertiary_lines, 'quaternary': quaternary_lines
    }

    for key, pos in button_positions.items():
        ax_btn = fig.add_axes(pos)
        # Initial label based on initial hide_flags state (False).
        label = f"Hide {key.capitalize()}"
        btn = Button(ax_btn, label)
        button_refs[key] = btn # Store button ref.
        if key == 'all':
            btn.on_clicked(toggleShowHideAll)
        else:
            btn.on_clicked(lambda event, k=key, l=button_lines[key]: toggleVisibilityGroup(event, k, l))


    #----------------------------------------------- SHOW -----------------------------------------------


    try:
        plt.show()
    except Exception as e:
        print(f"Error displaying plot: {e}", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Missing parameters")
        sys.exit(1)

    filename = sys.argv[1]
    createPlot(filename)