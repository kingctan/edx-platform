"""
Tests for course_metadata_utils.
"""
from datetime import timedelta, datetime

from django.utils import timezone
from django.utils.translation import ugettext

from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase, ModuleStoreEnum
from xmodule.modulestore.tests.factories import CourseFactory
from xmodule.course_metadata_utils import *

from util.date_utils import strftime_localized


_TODAY = timezone.now()
_LAST_MONTH = _TODAY - timedelta(days=30)
_LAST_WEEK = _TODAY - timedelta(days=7)
_NEXT_WEEK = _TODAY + timedelta(days=7)


class CourseMetadataUtilsTestCase(ModuleStoreTestCase):
    """
    Tests for course_metadata_utils.
    """

    def setUp(self):
        """
        Set up module store testing capabilities and initialize test courses.
        """
        super(CourseMetadataUtilsTestCase, self).setUp()
        self.demo_course = CourseFactory.create(
            org="edX",
            course="DemoX.1",
            run="Fall_2014",
            default_store=ModuleStoreEnum.Type.mongo,
            start=_LAST_MONTH,
            end=_LAST_WEEK,
        )
        self.html_course = CourseFactory.create(
            org="UniversityX",
            course="CS-203",
            run="Y2096",
            display_name="Intro to <html>",
            default_store=ModuleStoreEnum.Type.split,
            start=_NEXT_WEEK,
            advertised_start="2038-01-19 03:14:07"
        )

    def test_course_metadata_utils(self):
        """
        Test every single function in course_metadata_utils.
        """
        to_test = [
            (clean_course_key, [
                ((self.demo_course.id, '='), "course_MVSFQL2EMVWW6WBOGEXUMYLMNRPTEMBRGQ======"),
                ((self.html_course.id, '~'), "course_MNXXK4TTMUWXMMJ2KVXGS5TFOJZWS5DZLAVUGUZNGIYDGK2ZGIYDSNQ~"),
            ]),
            (url_name_for_course_location, [
                ((self.demo_course.location,), self.demo_course.location.name),
                ((self.html_course.location,), self.html_course.location.name),
            ]),
            (display_name_with_default, [
                ((self.demo_course,), "Run 0"),
                ((self.html_course,), "Intro to &lt;html&gt;"),
            ]),
            (has_course_started, [
                ((self.demo_course.start,), True),
                ((self.html_course.start,), False),
            ]),
            (has_course_ended, [
                ((self.demo_course.end,), True),
                ((self.html_course.end,), False),
            ]),
            (course_start_date_is_default, [
                ((self.demo_course.start, self.demo_course.advertised_start), False),
                ((self.html_course.start, None), False),
                ((DEFAULT_START_DATE, self.demo_course.advertised_start), True),
                ((DEFAULT_START_DATE, self.html_course.advertised_start), False),
            ]),
            (course_start_datetime_text, [
                (
                    (
                        datetime(1945, 02, 06, 4, 20, 00, tzinfo=timezone.UTC()),
                        self.demo_course.advertised_start,
                        'SHORT_DATE',
                        ugettext,
                        strftime_localized
                    ),
                    "Feb 06, 1945",
                ), (
                    (
                        DEFAULT_START_DATE,
                        self.html_course.advertised_start,
                        'DATE_TIME',
                        ugettext,
                        strftime_localized
                    ),
                    "Jan 19, 2038 at 03:14 UTC",
                ), (
                    (
                        DEFAULT_START_DATE,
                        None,
                        'DATE_TIME',
                        ugettext,
                        strftime_localized
                    ),
                    # Translators: TBD stands for 'To Be Determined' and is used when a course
                    # does not yet have an announced start date.
                    ugettext('TBD'),
                )
            ]),
            (course_end_datetime_text, [
                (
                    (datetime(1945, 02, 06, 4, 20, 00, tzinfo=timezone.UTC()), 'DATE_TIME', strftime_localized),
                    "Feb 06, 1945 at 04:20 UTC"
                ), (
                    (None, 'DATE_TIME', strftime_localized),
                    ""
                )
            ]),
            (may_certify_for_course, [
                (('early_with_info', True, True), True),
                (('early_no_info', False, False), True),
                (('end', True, False), True),
                (('end', False, True), True),
                (('end', False, False), False),
            ]),
        ]
        for function_to_test, values in to_test:
            for arguments, expected_return in values:
                self.assertEqual(function_to_test(*arguments), expected_return)
