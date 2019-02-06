from dataflows import Flow

from .config import Config
from .context import Context


class BaseDataGenusProcessor:

    def __init__(self, config: Config, context: Context, *args, **kwargs):
        self.config = config
        self.context = context
        self.errors = []
        if hasattr(self, 'PRE_CHECKS'):
            self.errors.extend(self.PRE_CHECKS.check(config))
        self.steps = []
        self.init(*args, **kwargs)

    def init(self):
        pass

    def test(self):
        return True

    def init_classes(self, classes):
        return [
            cls(self.config, self.context)
            for cls in classes
        ]

    def analyze(self):
        if self.test():
            for step in self.steps:
                if not step.analyze():
                    self.errors.extend(step.errors)
                    return False
        else:
            return False
        return True

    def flow(self):
        flows = [step.flow() for step in self.steps]
        return Flow(*list(filter(lambda x: x is not None, flows)))


class BaseAnalyzer(BaseDataGenusProcessor):
    
    def run(self):
        raise NotImplementedError()

    def test(self):
        if hasattr(self, 'REQUIRES'):
            self.errors.extend(self.REQUIRES.check(self.config))
        return len(self.errors) == 0
        
    def analyze(self):
        if self.test():
            self.run()
            return True
        return False

    def flow(self):
        return None


class BaseProcessor(BaseDataGenusProcessor):
    
    def run(self):
        raise NotImplementedError()

    def flow(self):
        if self.test():
            return self.run()

    def analyze(self):
        return True