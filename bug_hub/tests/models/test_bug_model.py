from django.test import TestCase
from bug_hub.models import Bug
from django.core.exceptions import ValidationError
import time


# pylint: disable=E1101
class BugModelTestCase(TestCase):
    def setUp(self):
        """
        Create a sample bug instance for testing
        """
        self.sample_bug = Bug.objects.create(
            title="Sample Bug",
            description="This is a sample bug description.",
            bug_type="error",
            status="todo",
        )

    def test_bug_creation(self):
        """
        Test if a bug instance can be created correctly.
        """
        self.assertEqual(
            self.sample_bug.title, "Sample Bug", "Bug creation failed: title mismatch."
        )
        self.assertEqual(
            self.sample_bug.description,
            "This is a sample bug description.",
            "Bug creation failed: description mismatch.",
        )
        self.assertEqual(
            self.sample_bug.bug_type, "error", "Bug creation failed: bug_type mismatch."
        )
        self.assertEqual(
            self.sample_bug.status, "todo", "Bug creation failed: status mismatch."
        )

    def test_bug_str_representation(self):
        """
        Test the string representation of a bug instance.
        """
        self.assertEqual(
            str(self.sample_bug), "Sample Bug", "String representation failed."
        )

    def test_bug_report_date_auto_generated(self):
        """
        Test if the report_date field is auto-generated.
        """
        self.assertIsNotNone(
            self.sample_bug.report_date, "Report date not auto-generated."
        )

    def test_bug_title_unique(self):
        """
        Test that bug titles' uniqueness constraint is enforced.
        """
        duplicate_bug = Bug(
            title="Sample Bug",
            description="This is a duplicate bug description.",
            bug_type="error",
            status="todo",
        )
        with self.assertRaises(Exception) as context:
            duplicate_bug.save()
        self.assertEqual(
            str(context.exception), "UNIQUE constraint failed: bug_hub_bug.title"
        )

    def test_bug_type_choices(self):
        """
        Ensure that only valid choices for 'bug_type' are allowed when creating a Bug instance.
        """
        bug = Bug.objects.create(
            title="Test Bug",
            description="This is a test bug.",
            bug_type="invalid_type",
        )
        with self.assertRaises(Exception) as context:
            bug.full_clean()
        self.assertIn(
            "bug_type",
            context.exception.message_dict,
            "Select a valid choice for the bug type",
        )

    def test_status_choices(self):
        """
        Ensure that only valid choices for 'status' are allowed when creating a Bug instance.
        """
        bug = Bug.objects.create(
            title="Test Bug",
            description="This is a test bug.",
            bug_type="error",
            status="invalid_status",
        )
        with self.assertRaises(Exception) as context:
            bug.full_clean()
        self.assertIn(
            "status",
            context.exception.message_dict,
            "Select a valid choice for the bug status",
        )

    def test_bug_description_length(self):
        """
        Verify that a Bug instance can be saved with a very long 'description.'
        """
        long_description = "A" * 1000
        bug = Bug.objects.create(
            title="Test Bug", description=long_description, bug_type="error"
        )
        self.assertEqual(
            bug.description,
            long_description,
            "Ensure the description has at most 1000 characters.",
        )

    def test_bug_title_max_length(self):
        """
        Verify that a Bug instance cannot be saved with a very long 'title.'
        """
        long_title = "A" * 255
        bug = Bug.objects.create(
            title=long_title, description="This is a test bug.", bug_type="error"
        )
        with self.assertRaises(ValidationError) as context:
            bug.full_clean()
        self.assertIn(
            "title",
            context.exception.message_dict,
            "Ensure the bug title has at most 250 characters.",
        )

    def test_bug_title_min_length(self):
        """
        Verify that a Bug instance cannot be saved with a very short 'title.'
        """
        short_title = "A" * 5
        bug = Bug.objects.create(
            title=short_title, description="This is a test bug.", bug_type="error"
        )
        with self.assertRaises(ValidationError) as context:
            bug.full_clean()
        self.assertIn(
            "title",
            context.exception.message_dict,
            "Ensure the bug title has at least 10 characters.",
        )

    def test_bug_listing(self):
        """
        Verify that a list of Bug instances can be retrieved, and it contains the expected bugs.
        """
        bug1 = Bug.objects.create(
            title="Bug 1", description="This is bug 1.", bug_type="error"
        )
        bug2 = Bug.objects.create(
            title="Bug 2", description="This is bug 2.", bug_type="feature_request"
        )
        bug_list = Bug.objects.all()
        self.assertIn(bug1, bug_list)
        self.assertIn(bug2, bug_list)

    def test_bug_ordering(self):
        """
        Verify that Bug instances are correctly ordered by 'report_date.'
        """
        time.sleep(1)
        bug2 = Bug.objects.create(
            title="Bug 2", description="This is bug 2.", bug_type="feature_request"
        )
        bug_list = Bug.objects.all()
        self.assertEqual(bug_list[0], bug2)
        self.assertEqual(bug_list[1], self.sample_bug)
