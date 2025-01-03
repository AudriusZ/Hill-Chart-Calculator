
from PyQt6.QtWidgets import (    
    QMessageBox, QWidget, QVBoxLayout,
    QTabWidget, QTreeWidget, QFileDialog,
    QPushButton, QSizePolicy 
    )

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class PlotManager:
    def __init__(self, tab_widget: QTabWidget):
        """
        Initialize the PlotManager.
        Args:
            tab_widget (QTabWidget): The QTabWidget to manage.
        """
        self.tab_widget = tab_widget
        self.tab_widget.setTabsClosable(True)  # Enable the close button on tabs
        self.tab_widget.tabCloseRequested.connect(self.close_tab)  # Connect to the tab close signal      

        # Dictionary to map tab titles to cleanup actions
        self.tab_cleanup_actions = {}
  

    def embed_textEdit(self, text_widget, title):
        """
        Embed a QTextEdit widget into a new tab.

        Args:
            text_widget (QTextEdit): The QTextEdit widget to embed.
            title (str): Title of the new tab.
        """
        tab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(text_widget)

        tab.setLayout(layout)
        self.tab_widget.addTab(tab, title)
        self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)

    
    def embed_plot(self, fig, tab_name: str, add_export_button=False):
        """
        Embed a matplotlib figure into a new tab, with an optional 'Export' button.

        Args:
            fig (matplotlib.figure.Figure): The matplotlib figure to embed.
            tab_name (str): The name of the new tab.
            add_export_button (bool): Whether to add an 'Export' button to the tab.

        Returns:
            FigureCanvas: The canvas object for the embedded plot.
        """
        canvas = FigureCanvas(fig)
        new_tab = QWidget()
        layout = QVBoxLayout(new_tab)

        # Add the plot canvas to the tab
        layout.addWidget(canvas)

        if add_export_button:
            # Add an 'Export' button to the tab
            export_button = QPushButton("Export CSV", new_tab)
            export_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            export_button.setFixedSize(100, 30)  # Set standard button size
            export_button.clicked.connect(lambda _, fig=fig, tab_name=tab_name: self.export_plot_to_csv(fig, tab_name))
            layout.addWidget(export_button)

        self.tab_widget.addTab(new_tab, tab_name)
        self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)

        return canvas  # Return the canvas for further updates

    def export_plot_to_csv(self, fig, title):
        """
        Export data from the given figure to a CSV file. Handles multiple subplots and overlapping data.

        Args:
            fig (matplotlib.figure.Figure): The figure containing the plots.
            title (str): The title of the plot for naming the file.
        """
        import csv
        from collections import defaultdict

        def replace_special_characters(label):
            """
            Replace special characters in the label.
            """
            return label.replace("³", "^3").replace("²", "^2").replace("¹", "^1").replace("°","deg.")

        try:
            # Step 1: Prepare to extract data
            combined_data = defaultdict(list)  # Store aligned datasets by column names
            x_data_set = set()  # Track unique X values for alignment
            all_x_data = []  # Store all X data (used for alignment)
            final_x_label = None  # Store the X-axis label from the last subplot

            # Step 2: Extract data from all axes in the figure
            for ax in fig.get_axes():
                final_x_label = ax.get_xlabel() or "X"  # Get X-axis label from the last subplot
                for line in ax.get_lines():
                    # Extract X and Y data
                    x_data = line.get_xdata()
                    y_data = line.get_ydata()
                    y_label = line.get_label() or ax.get_ylabel() or "Y"  # Prioritize line label, fallback to Y-axis label

                    # Ensure unique X data for alignment
                    x_data_set.update(x_data)
                    all_x_data.append((x_data, y_label, y_data))

            # Step 3: Align data by unique X values
            sorted_x_data = sorted(x_data_set)  # Create a sorted list of unique X values
            combined_data[replace_special_characters(final_x_label)] = sorted_x_data  # Add X column to combined data

            for x_data, y_label, y_data in all_x_data:
                # Map Y data to sorted X values
                aligned_y_data = []
                x_to_y = dict(zip(x_data, y_data))  # Map X to corresponding Y
                for x in sorted_x_data:
                    aligned_y_data.append(x_to_y.get(x, None))  # Use None for missing values
                combined_data[replace_special_characters(y_label)].extend(aligned_y_data)

            # Step 4: Ask the user for the save location
            file_path, _ = QFileDialog.getSaveFileName(
                self.tab_widget, "Save Chart Data", f"{title}.csv", "CSV Files (*.csv)"
            )
            if not file_path:
                return  # User cancelled

            # Step 5: Write combined data to a CSV file
            with open(file_path, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                # Write the header
                writer.writerow(combined_data.keys())
                # Write the rows
                rows = zip(*combined_data.values())
                for row in rows:
                    writer.writerow(row)

            QMessageBox.information(self.tab_widget, "Export Successful", f"Data exported to {file_path}")

        except Exception as e:
            QMessageBox.critical(self.tab_widget, "Export Error", f"An error occurred: {str(e)}")
    
    def register_tab_action(self, title, cleanup_action):
        """
        Register a cleanup action for a specific tab.
        Args:
            title (str): The title of the tab.
            cleanup_action (callable): A callable for cleanup when the tab is closed.
        """
        self.tab_cleanup_actions[title] = cleanup_action

    def close_tab(self, index):
        """
        Handle closing of a tab.
        Args:
            index (int): The index of the tab to close.
        """
        tab_title = self.tab_widget.tabText(index)

        # Perform cleanup if a specific action is registered
        if tab_title in self.tab_cleanup_actions:
            self.tab_cleanup_actions[tab_title]()

        # Remove the tab from the widget
        self.tab_widget.removeTab(index)
    
    def expand_tree(self, tree_widget: QTreeWidget):
        """
        Expands all items in a QTreeWidget.
        Args:
            tree_widget (QTreeWidget): The tree widget to expand.
        """
        tree_widget.expandAll()