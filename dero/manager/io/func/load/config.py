from dero.manager.io.func.load.args import FunctionArgsExtractor

class FunctionConfigExtractor(FunctionArgsExtractor):

    def extract_config(self):
        args = super().extract_args()

        # Parse into config