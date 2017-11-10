import os
import sys
import time
import warnings
from unittest import TextTestRunner, TestResult, TestSuite, TestCase, TestLoader
from colors import TermColors

class EpitaTestResult(TestResult):
    def printErrors(self):
        self.stream.write(TermColors.fg_yellow)
        self.printErrorList('ERROR', self.errors)
        self.stream.write(TermColors.fg_red)
        self.printErrorList('FAIL', self.failures)
        self.stream.write(TermColors.fg_default)

    def printErrorList(self, flavour, errors):
        for test, err in errors:
            self.stream.writeln("%s" % err)



class EpitaTestRunner(TextTestRunner):
    resultclass = EpitaTestResult
    title = None
    bar_width = 78
    def __init__(self, title=None, **kwargs):
        super(EpitaTestRunner, self).__init__(**kwargs)
        self.title = title

    def run(self, test):

        if isinstance(test, type) and issubclass(test, TestCase):
            test = TestLoader().loadTestsFromTestCase(test)

        test_classes = set([test.__class__.__name__ for test in test._tests])
        self.stream.write(TermColors.fg_blue)
        self.stream.write(" ".join(test_classes))
        if hasattr(test, 'parametrized') and test.parametrized:
            self.stream.write(' with parameter = ')
            self.stream.write(TermColors.fg_default)
            self.stream.write(test.param)
        self.stream.write('\n')

        test_methods = set([test._testMethodName for test in test._tests])
        self.stream.write(TermColors.fg_magenta)
        self.stream.write("Tests: ")
        self.stream.write(TermColors.fg_default)
        self.stream.writeln(" ".join(test_methods))

        result = self._makeResult()
        result.stream = self.stream
        result.failfast = self.failfast
        result.buffer = self.buffer
        result.tb_locals = self.tb_locals

        with warnings.catch_warnings():
            if self.warnings:
                warnings.simplefilter(self.warnings)
                if self.warnings in ['default', 'always']:
                    warnings.filterwarnings('module',
                            category=DeprecationWarning,
                            message=r'Please use assert\w+ instead.')
            startTime = time.time()
            startTestRun = getattr(result, 'startTestRun', None)
            if startTestRun is not None:
                startTestRun()
            try:
                test(result)
            finally:
                stopTestRun = getattr(result, 'stopTestRun', None)
                if stopTestRun is not None:
                    stopTestRun()
            stopTime = time.time()
        timeTaken = stopTime - startTime

        self.stream.write(TermColors.fg_green if result.wasSuccessful() else
                          TermColors.fg_red)
        self.stream.write("{} Tests Run, {} Failures, "
                          "{} Errors - Ran in {:.2} seconds\n".format(
                          result.testsRun, len(result.failures),
                          len(result.errors), timeTaken))
        self.stream.write(TermColors.fg_default)
        if (result.errors):
            self.stream.write('\n')
            result.printErrors()

        self.stream.write('\n')

        return result

    def run_all(self, tests):

        if (self.title):
            try:
                width, _ = os.get_terminal_size()
            except:
                width = 78
            os.system('clear')
            self.stream.write(TermColors.fg_cyan)
            centered_title = '\n'.join(["{0:^{1}}".format(line, width)
                                       for line in self.title.split('\n')])
            self.stream.write(centered_title)
            self.stream.write(TermColors.fg_default)
            self.stream.write('\n\n')

        results = [self.run(test) for test in tests]

        ratio = (len([result for result in results if result.wasSuccessful()]) /
                len(results))
        self.printBar(ratio)

        if (self.title):
            input()

    def printBar(self, ratio):
        bar_text = []
        bar_text.append(' ' + '▁' * (self.bar_width - 2) + ' ')
        bar_text.append('▕')
        blocks = int(ratio * (self.bar_width - 2))
        bar_text[-1] += ('█' * blocks + ' ' * (self.bar_width - blocks - 2))
        bar_text[-1] += ('▏')
        bar_text.append(' ' + '▔' * (self.bar_width - 2) + ' ')
        bar_text.append('{0:^{width}}'.format(
                        " {}% Successful ".format(int(ratio * 100)),
                        width=self.bar_width
                        ))
        self.stream.write(TermColors.fg_green if ratio == 1 else
                          TermColors.fg_red)
        try:
            width, _ = os.get_terminal_size()
        except:
            width = 78
        [self.stream.writeln("{0:^{1}}".format(line, width)) for line in bar_text]
        self.stream.write(TermColors.fg_default)
