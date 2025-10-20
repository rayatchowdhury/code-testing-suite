"""
Validator Status View - migrated to StatusViewBase.

Reduced from 215 lines to ~65 lines following Phase 3B migration pattern.
Inherits common status view behavior from StatusViewBase.

NOTE: ValidatorRunner uses 'validator_runner' attribute (not 'validator')
"""

from src.app.presentation.base.status_view_base import StatusViewBase
from src.app.presentation.widgets.status_view import TestResult, ValidatorTestCard
from src.app.presentation.widgets.test_detail_view import ValidatorDetailDialog


class ValidatorStatusView(StatusViewBase):
    """
    Validator-specific status view.
    
    Responsibilities:
    - Translate validator worker signals to TestResult
    - Create validator-specific cards
    - Show validator detail dialogs with 3 sections
    """
    
    def __init__(self, parent=None):
        super().__init__(parent, test_type="validator")
    
    # ===== Template Methods (Required by StatusViewBase) =====
    
    def _get_runner_attribute_name(self) -> str:
        """Return 'validator_runner' (NOTE: different from benchmarker!)"""
        return "validator_runner"
    
    def _get_card_class(self):
        """Return ValidatorTestCard class."""
        return ValidatorTestCard
    
    def _get_detail_dialog_class(self):
        """Return ValidatorDetailDialog class."""
        return ValidatorDetailDialog
    
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
        memory: float = 0.0
    ):
        """
        Handle test completion from worker.
        
        Translates validator worker signal (9 params) to TestResult.
        """
        # Create TestResult
        result = TestResult.from_validator(
            test_number=test_number,
            passed=passed,
            input_data=input_data,
            test_output=test_output,
            validation_message=validation_message,
            error_details=error_details,
            validator_exit_code=validator_exit_code,
            time=time,
            memory=memory
        )
        
        # Store for detail view
        self.test_results[test_number] = result
        
        # Update UI through presenter
        self.presenter.handle_test_result(result)
        
        # Create and add card
        card = ValidatorTestCard(result)
        card.clicked.connect(self.show_test_detail)
        self.cards_section.add_card(card, result.passed)
    
    def show_test_detail(self, test_number: int):
        """Show detail dialog with 3 sections: Input, Output, Validator Log."""
        if test_number not in self.test_results:
            return
        
        result = self.test_results[test_number]
        data = result.data
        
        dialog = ValidatorDetailDialog(
            test_number=test_number,
            passed=result.passed,
            time=result.time,
            memory=result.memory,
            input_data=data.get('input_data', 'No input data'),
            test_output=data.get('test_output', 'No output'),
            validation_message=data.get('validation_message', 'Unknown'),
            error_details=data.get('error_details', ''),
            validator_exit_code=data.get('validator_exit_code', -1),
            parent=self
        )
        dialog.exec()
