import unittest

from tests.mocks.mock_file_logger import MockFileLogger


class FileLoggerMemoryTests(unittest.TestCase):
    def setUp(self):
        self._filename = "test"
        self._directory = "logs"

    def test_file_logger_creates_empty_log_file(self):
        file_logger = MockFileLogger.new_for(self._filename, self._directory)

        self.assertTrue(file_logger.is_empty())

    def test_file_logger_can_add_log_successfully(self):
        file_logger = MockFileLogger.new_for(self._filename, self._directory)
        mocked_object = {"key": "value"}

        file_logger.add_log(mocked_object)

        logged_json_data = file_logger.all_logs_as_json()
        self.assertTrue(logged_json_data == mocked_object)


if __name__ == '__main__':
    unittest.main()
