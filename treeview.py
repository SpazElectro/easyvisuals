import tkinter as tk
from PIL import ImageTk, Image
from typing import List, Optional, Tuple, Any
from collections import namedtuple

# Namedtuple representing a tree node
TreeNode = namedtuple('TreeNode', ['name', 'image', 'children'], defaults=[None, []])

class TreeGraph:
    def __init__(self, data: TreeNode, parent: tk.Widget):
        """
        Initialize the TreeGraph.

        Args:
            data (TreeNode): The root node of the tree.
            parent (tk.Widget): The parent widget where the tree graph will be displayed.
        """
        self.data = data
        self.parent = parent

        # Calculate the size of the tree
        self.tree_size = self.calculate_tree_size(data)

        # Initialize the canvas dimensions
        self.canvas_width = 800
        self.canvas_height = 600

        # Calculate the initial node spacing based on the canvas size and tree size
        self.x_spacing, self.y_spacing = self.calculate_node_spacing()

        # Create a scrollable frame
        self.scrollable_frame = tk.Frame(self.parent)
        self.scrollable_frame.pack(fill=tk.BOTH, expand=True)

        # Create a horizontal scrollbar
        self.x_scrollbar = tk.Scrollbar(self.scrollable_frame, orient=tk.HORIZONTAL)
        self.x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Create a vertical scrollbar
        self.y_scrollbar = tk.Scrollbar(self.scrollable_frame)
        self.y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create a canvas
        self.canvas = tk.Canvas(self.scrollable_frame, width=self.canvas_width, height=self.canvas_height,
                                xscrollcommand=self.x_scrollbar.set, yscrollcommand=self.y_scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure the scrollbars
        self.x_scrollbar.config(command=self.canvas.xview)
        self.y_scrollbar.config(command=self.canvas.yview)

        # Configure canvas scrolling region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        # Bind the canvas configuration event to adjust the scroll region
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        self.inner_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor=tk.NW)

        self.preloaded_images = {}
        self.preload_images(self.data)

    def calculate_tree_size(self, node: TreeNode) -> Tuple[int, int]:
        """
        Recursively calculates the size of the tree.

        Args:
            node (TreeNode): The current node being processed.

        Returns:
            Tuple[int, int]: The width and height of the tree.
        """
        if not node.children:
            return 1, 1

        child_sizes = [self.calculate_tree_size(child) for child in node.children]
        max_child_width = max(size[0] for size in child_sizes)
        total_height = sum(size[1] for size in child_sizes)
        return max(max_child_width, len(node.children)), total_height + 1

    def calculate_node_spacing(self) -> Tuple[int, int]:
        """
        Calculates the spacing between nodes based on the canvas size and tree size.

        Returns:
            Tuple[int, int]: The x-spacing and y-spacing between nodes.
        """
        x_spacing = self.canvas_width // self.tree_size[0]
        y_spacing = self.canvas_height // self.tree_size[1]
        return x_spacing, y_spacing

    def preload_images(self, node: TreeNode) -> None:
        """
        Preloads the images recursively.

        Args:
            node (TreeNode): The current node being processed.
        """
        if node.image:
            try:
                image = Image.open(node.image)
                image = image.resize((80, 60), Image.LANCZOS)
                self.preloaded_images[node.image] = ImageTk.PhotoImage(image)
            except Exception as e:
                raise ValueError(f"Failed to load image: {node.image}. {str(e)}")

        for child in node.children:
            self.preload_images(child)

    def draw_tree(self, node: TreeNode, x: int, y: int) -> int:
        """
        Recursively draws the tree on the canvas.

        Args:
            node (TreeNode): The current node being processed.
            x (int): The x-coordinate of the current node.
            y (int): The y-coordinate of the current node.

        Returns:
            int: The total width of the current subtree.
        """
        node_width = 80
        node_height = 60

        # Load image if available
        if node.image:
            try:
                image = self.preloaded_images[node.image]
                self.canvas.create_image(x, y, image=image)
            except Exception as e:
                raise ValueError(f"Failed to load image: {node.image}. {str(e)}")
        else:
            self.canvas.create_rectangle(x - node_width // 2, y - node_height // 2,
                                         x + node_width // 2, y + node_height // 2, fill='lightblue')

        # Draw current node label
        self.canvas.create_text(x, y, text=node.name, fill='black')

        if node.children:
            num_children = len(node.children)
            total_width = num_children * self.x_spacing
            start_x = x - total_width // 2

            for child in node.children:
                try:
                    self.canvas.create_line(x, y + node_height // 2, start_x + self.x_spacing // 2,
                                            y + self.y_spacing - node_height // 2, arrow='last')
                    child_width = self.draw_tree(child, start_x + self.x_spacing // 2, y + self.y_spacing)
                    start_x += child_width
                except ValueError as e:
                    raise ValueError(f"Error drawing tree: {str(e)}")

            return total_width
        else:
            return node_width

    def display_tree(self) -> None:
        """
        Displays the tree graph on the canvas.
        """
        try:
            root_width = self.draw_tree(self.data, self.canvas_width // 2, 30)

            # Update the canvas dimensions based on the root width
            self.canvas.configure(scrollregion=(-root_width // 2, -30, root_width // 2, self.canvas_height))
        except ValueError as e:
            raise ValueError(f"Error displaying tree: {str(e)}")

    def on_canvas_configure(self, event: tk.Event) -> None:
        """
        Callback function for canvas configuration event.
        Adjusts the scroll region of the canvas.
        """
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

if __name__ == "__main__":
    # Example usage
    tree_data = TreeNode(
        name="",
        image="test.png",
        children=[
            TreeNode(name="Hello", children=[TreeNode(name="World")]),
            TreeNode(name="Not", children=[TreeNode(name="goodbye", children=[TreeNode(name="world")])])
        ]
    )

    root = tk.Tk()
    root.title("Tree Graph App")

    try:
        tree_graph = TreeGraph(tree_data, parent=root)
        tree_graph.display_tree()
    except ValueError as e:
        tk.messagebox.showerror("Error", str(e))

    root.mainloop()