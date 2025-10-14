"""
Validator-specific status view.

Extends BaseStatusView to show validator test execution with test cards
displaying input, output, validation messages, and error details.
"""

from src.app.presentation.widgets.test_cards import ValidatorTestCard
from src.app.presentation.widgets.test_detail_view import ValidatorDetailDialog
from src.app.presentation.widgets.unified_status_view import BaseStatusView


class ValidatorStatusView(BaseStatusView):
    """
    Status view for validator tests.

    Shows execution progress with cards for each test, displaying:
    - Test number and pass/fail status
    - Time and memory metrics
    - Input data
    - Test output
    - Validation message from validator
    - Error details (if any)
    - Validator exit code

    Clicking a card shows detailed validation results in a dialog.
    """

    def __init__(self, parent=None):
        """
        Initialize validator status view.

        Args:
            parent: Parent widget
        """
        super().__init__("validator", parent)

        # Store test data for detail views
        self.test_data = (
            {}
        )  # {test_number: {input, output, validation_message, error_details, exit_code, time, memory}}

    def on_test_completed(
        self,
        test_number: int,
        passed: bool,
        input_data: str,
        test_output: str,
        validation_message: str,
        error_details: str,
        validator_exit_code: int,
        time: float = 0.0,
        memory: float = 0.0,
    ):
        """
        Handle validator test completion.

        Args:
            test_number: Test case number (1-indexed)
            passed: Whether test passed validation
            input_data: Test input
            test_output: Program output
            validation_message: Message from validator
            error_details: Error details (if any)
            validator_exit_code: Exit code from validator
            time: Execution time in seconds
            memory: Memory usage in MB
        """
        # Update counters and progress (base class)
        super().on_test_completed(
            test_number,
            passed,
            time=time,
            memory=memory,
            input_data=input_data,
            test_output=test_output,
            validation_message=validation_message,
            error_details=error_details,
            validator_exit_code=validator_exit_code,
        )

        # Store test data for detail view
        self.test_data[test_number] = {
            "passed": passed,
            "input_data": input_data,
            "test_output": test_output,
            "validation_message": validation_message,
            "error_details": error_details,
            "validator_exit_code": validator_exit_code,
            "time": time,
            "memory": memory,
        }

        # Create validator-specific card
        card = ValidatorTestCard(
            test_number=test_number,
            passed=passed,
            time=time,
            memory=memory,
            expected_output=validation_message,  # What the validator expected/reported
            actual_output=test_output,  # What the test program output
        )

        # Add card to section (will trigger layout switch on first failure)
        self.add_test_card(card)

    def show_test_detail(self, test_number: int):
        """
        Show detail view for a validator test.

        Args:
            test_number: Test case number to show details for
        """
        if test_number not in self.test_data:
            return

        data = self.test_data[test_number]

        # Create and show detail dialog with 3 sections: Input, Output, Validator Log
        dialog = ValidatorDetailDialog(
            test_number=test_number,
            passed=data["passed"],
            time=data["time"],
            memory=data["memory"],
            input_data=data.get("input_data", "No input data"),
            test_output=data.get("test_output", "No output"),
            validation_message=data.get("validation_message", "Unknown"),
            error_details=data.get("error_details", ""),
            validator_exit_code=data.get("validator_exit_code", -1),
            parent=self,
        )

        dialog.exec()
