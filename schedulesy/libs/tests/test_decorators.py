from time import sleep

from django.test import TestCase

from ..decorators import MemoizeWithTimeout


class MemoizeWithTimeoutTestCase(TestCase):
    def test_with_timeout(self):
        function1_call = 0

        def mocked_function1():
            nonlocal function1_call
            function1_call += 1
            return {'result': function1_call}

        m = MemoizeWithTimeout(timeout=1)
        result = m(mocked_function1)()

        # self.assertEqual(m._timeouts[mocked_function1], 3600)
        # self.assertDictEqual(m._caches[mocked_function1][(), ()][0], {'result': 1})
        self.assertDictEqual(result, {'result': 1})
        self.assertDictEqual(m(mocked_function1)(), {'result': 1})

        # Clear old cache results
        sleep(2)
        # self.assertDictEqual(m._caches[mocked_function1][(), ()][0], {'result': 1})
        self.assertDictEqual(m(mocked_function1)(), {'result': 1})

    # def test_without_timeout(self):
    #     function2_call = 0
    #
    #     def mocked_function2():
    #         nonlocal function2_call
    #         function2_call += 1
    #         return {'result': function2_call}
    #
    #     m = MemoizeWithTimeout(timeout=0)
    #     result = m(mocked_function2)()
    #
    #     #self.assertEqual(m._timeouts[mocked_function2], 0)
    #     #self.assertDictEqual(m._caches[mocked_function2][(), ()][0], {'result': 1})
    #     self.assertDictEqual(result, {'result': 1})
    #     self.assertDictEqual(m(mocked_function2)(), {'result': 2})
    #
    #     # Clear old cache results
    #     #m.collect()
    #     #self.assertDictEqual(m._caches[mocked_function2], {})
    #     self.assertDictEqual(m(mocked_function2)(), {'result': 3})
