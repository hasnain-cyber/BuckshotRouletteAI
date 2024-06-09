from PySide6.QtWidgets import QMainWindow, QSplitter, QWidget, QVBoxLayout, \
    QFormLayout, QLineEdit, QLabel, QCheckBox, QHBoxLayout, QPushButton

from datatypes.Item import ItemType
from datatypes.State import State, BulletType
from utils.Constants import WINDOW_WIDTH, WINDOW_HEIGHT
from utils.MarkovChain import get_success_prob


class MainWindow(QMainWindow):
    def __init__(self, state: State = State()):
        super().__init__()
        self.setWindowTitle("Buckshot Roulette AI")
        self.state = state

        # Set window size
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        # Initialize the number of bullets
        self.n_bullets: str = "0"

        # Update the UI to reflect the initial state
        self.state = state

        # Create a main layout
        main_layout = QVBoxLayout()

        # Create a form layout
        form_layout = QFormLayout()

        # Add label and input for max_health to the form
        self.max_health_input = QLineEdit(str(self.state.max_health))
        self.max_health_input.editingFinished.connect(
            lambda: self.update_state("max_health", self.max_health_input.text()))
        form_layout.addRow(QLabel("Max Health"), self.max_health_input)

        # Add checkbox for is_handcuffed to the form
        self.handcuffed_checkbox = QCheckBox()
        self.handcuffed_checkbox.setChecked(self.state.is_handcuffed)
        self.handcuffed_checkbox.stateChanged.connect(
            lambda: self.update_state("is_handcuffed",
                                      self.handcuffed_checkbox.isChecked()))
        form_layout.addRow(QLabel("Is Handcuffed"), self.handcuffed_checkbox)

        # Add checkbox for is_sawed_off to the form
        self.sawed_off_checkbox = QCheckBox()
        self.sawed_off_checkbox.setChecked(self.state.is_sawed_off)
        self.sawed_off_checkbox.stateChanged.connect(
            lambda: self.update_state("is_sawed_off",
                                      self.sawed_off_checkbox.isChecked()))
        form_layout.addRow(QLabel("Is Sawed Off"), self.sawed_off_checkbox)

        # Add label and input for n_bullets to the form
        self.n_bullets_input = QLineEdit(self.n_bullets)
        self.n_bullets_input.editingFinished.connect(lambda: self.update_n_bullets(
            self.n_bullets_input.text()))
        form_layout.addRow(QLabel("Number of Bullets"), self.n_bullets_input)

        # Create a horizontal layout for the bullets
        self.bullets_layout = QHBoxLayout()

        # Add a widget for each bullet
        for bullet in self.state.bullets:
            bullet_widget = QWidget()
            bullet_widget.setFixedSize(20, 20)  # Set a fixed size for the bullet widgets

            # Set the background color of the widget to the color of the bullet
            bullet_color = bullet.properties()['color'].name()
            bullet_widget.setStyleSheet(f"background-color: {bullet_color};")

            # Add the bullet widget to the layout
            self.bullets_layout.addWidget(bullet_widget)

        # Add the bullets layout to the main layout
        form_layout.addRow(QLabel("Bullets"), self.bullets_layout)

        # Add label and input for n_live_bullets to the form
        self.n_live_bullets_input = QLineEdit(str(self.state.n_live_bullets))
        self.n_live_bullets_input.editingFinished.connect(
            lambda: self.update_state("n_live_bullets",
                                      self.n_live_bullets_input.text()))
        form_layout.addRow(QLabel("Live Bullets"), self.n_live_bullets_input)

        # Add the form layout to the main layout
        main_layout.addLayout(form_layout)

        # Create a splitter to divide the window into two halves
        splitter = QSplitter()

        # Create a widget for the left half
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_form = QFormLayout()

        # Add label and input field for player health
        self.player_health_input = QLineEdit(str(self.state.player.current_health))
        self.player_health_input.editingFinished.connect(
            lambda: self.update_state("player_health",
                                      self.player_health_input.text()))
        left_form.addRow(QLabel("Player Health"), self.player_health_input)

        # Add label and input field for each player item and its quantity
        self.player_items_inputs = {}
        for item_type in ItemType:
            item_name = item_type.name
            item_quantity = self.state.player.items.get(item_name, 0)
            item_input = QLineEdit(str(item_quantity))
            item_input.editingFinished.connect(
                lambda item_name_to_update=item_name, item_input_to_update=item_input:
                self.update_state(
                    f"player"
                    f"_{item_name_to_update}",
                    item_input_to_update.text()))
            self.player_items_inputs[item_name] = item_input
            left_form.addRow(QLabel(item_name), item_input)

        left_layout.addLayout(left_form)
        left_widget.setLayout(left_layout)

        # Create a widget for the right half
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_form = QFormLayout()

        # Add label and input field for enemy health
        self.enemy_health_input = QLineEdit(str(self.state.enemy.current_health))
        self.enemy_health_input.editingFinished.connect(
            lambda: self.update_state("enemy_health",
                                      self.enemy_health_input.text()))
        right_form.addRow(QLabel("Enemy Health"), self.enemy_health_input)

        # Add label and input field for each enemy item and its quantity
        self.enemy_items_inputs = {}
        for item_type in ItemType:
            item_name = item_type.name
            item_quantity = self.state.enemy.items.get(item_name, 0)
            item_input = QLineEdit(str(item_quantity))
            item_input.editingFinished.connect(
                lambda item_name_to_update=item_name, item_input_to_update=item_input:
                self.update_state(
                    f"enemy"
                    f"_{item_name_to_update}",
                    item_input_to_update.text()))
            self.enemy_items_inputs[item_name] = item_input
            right_form.addRow(QLabel(item_name), item_input)

        right_layout.addLayout(right_form)
        right_widget.setLayout(right_layout)

        # Add the left and right widgets to the splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)

        # Add the splitter to the main layout
        main_layout.addWidget(splitter)

        # Create a button for evaluating the action
        self.evaluate_button = QPushButton("Evaluate")
        self.evaluate_button.clicked.connect(
            lambda state_to_evaluate=self.state: self.action_label.setText(str(
                get_success_prob(state_to_evaluate)[1]))
        )
        main_layout.addWidget(self.evaluate_button)

        # Create a label for displaying the action
        self.action_label = QLabel()
        main_layout.addWidget(self.action_label)

        # Create a central widget and set the main layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def update_ui(self):
        # Update max_health
        self.max_health_input.setText(str(self.state.max_health))

        # Update is_handcuffed
        self.handcuffed_checkbox.setChecked(self.state.is_handcuffed)

        # Update n_bullets
        self.n_bullets_input.setText(self.n_bullets)

        # Clear the bullets layout
        for i in reversed(range(self.bullets_layout.count())):
            self.bullets_layout.itemAt(i).widget().setParent(None)

        # Update bullets
        for i in range(int(self.n_bullets)):
            bullet_widget = QWidget()
            bullet_widget.setFixedSize(20, 20)  # Set a fixed size for the bullet widgets

            # Set the background color of the widget to the color of the bullet
            if i < len(self.state.bullets):
                bullet_color = self.state.bullets[i].color.name()
            else:
                bullet_color = BulletType.UNKNOWN.color.name()
            bullet_widget.setStyleSheet(f"background-color: {bullet_color};")

            # Add a mouse click event listener to the bullet widget
            bullet_widget.mousePressEvent = lambda event, index=i: self.cycle_bullet_type(
                index)

            # Add the bullet widget to the layout
            self.bullets_layout.addWidget(bullet_widget)

        # Update n_live_bullets
        self.n_live_bullets_input.setText(str(self.state.n_live_bullets))

        # Update player_health
        self.player_health_input.setText(str(self.state.player.current_health))

        # Update player items
        for item_type in ItemType:
            item_name = item_type.name
            item_quantity = self.state.player.items.get(item_name, 0)
            self.player_items_inputs[item_name].setText(str(item_quantity))

        # Update enemy_health
        self.enemy_health_input.setText(str(self.state.enemy.current_health))

        # Update enemy items
        for item_type in ItemType:
            item_name = item_type.name
            item_quantity = self.state.enemy.items.get(item_name, 0)
            self.enemy_items_inputs[item_name].setText(str(item_quantity))

    def update_state(self, field_name, new_value):
        if not new_value:
            new_value = ("0" if field_name != "is_handcuffed" and field_name !=
                                "is_sawed_off" else "false")

        # Update the state based on the field name and new value
        if field_name == "max_health":
            self.state.max_health = int(new_value)
        elif field_name == "is_handcuffed":
            self.state.is_handcuffed = new_value == "true"
        if field_name == "is_sawed_off":
            self.state.is_sawed_off = new_value == "true"
        elif field_name == "n_live_bullets":
            self.state.n_live_bullets = int(new_value)
        elif field_name == "player_health":
            self.state.player.current_health = int(new_value)
        elif field_name == "enemy_health":
            self.state.enemy.current_health = int(new_value)
        else:
            for item_type in ItemType:
                item_name = item_type.name
                if field_name == f"player_{item_name}":
                    self.state.player.items[item_name] = int(new_value)
                elif field_name == f"enemy_{item_name}":
                    self.state.enemy.items[item_name] = int(new_value)

        print(self.state)

    def update_n_bullets(self, n_bullets):
        if not n_bullets:
            n_bullets = "0"

        # Update the number of bullets
        self.n_bullets = n_bullets

        # Reset the bullets to unknown
        self.state.bullets = [BulletType.UNKNOWN] * int(n_bullets)

        # Update UI to reflect the new number of bullets
        self.update_ui()

        print(self.state)

    def cycle_bullet_type(self, index):
        # Cycle through the BulletType enum values
        if self.state.bullets[index] == BulletType.LIVE:
            self.state.bullets[index] = BulletType.BLANK
        elif self.state.bullets[index] == BulletType.BLANK:
            self.state.bullets[index] = BulletType.UNKNOWN
        else:
            self.state.bullets[index] = BulletType.LIVE

        # Update UI to reflect the new bullet type
        self.update_ui()
