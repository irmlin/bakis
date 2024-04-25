import onnxruntime as ort


def init_session(model_path):
    sess = ort.InferenceSession(model_path, providers=['CUDAExecutionProvider'])
    print(f'Initialized ONNX runtime session for model {model_path}, session device: {ort.get_device()}')
    return sess


class PickableInferenceSession:
    def __init__(self, model_path):
        self.model_path = model_path
        self.sess = init_session(self.model_path)

    def run(self, *args):
        return self.sess.run(*args)

    def __getstate__(self):
        return {'model_path': self.model_path}

    def __setstate__(self, values):
        self.model_path = values['model_path']
        self.sess = init_session(self.model_path)
