"""
Build a deep neural network for regression predictions
"""

import json
import spylunking.log.setup_logging as log_utils
import keras.models as keras_models
import keras.layers as keras_layers

log = log_utils.build_colorized_logger(
    name=__name__)


def build_regression_dnn(
        num_features,
        compile_config,
        model_json=None,
        model_config=None):
    """build_regression_dnn

    :param num_features: input_dim for the number of
                         features in the data
    :param compile_config: dictionary of compile options
    :param model_json: keras model json to build the model
    :param model_config: optional dictionary for model
    """

    model = None
    num_layers = 0

    if model_json:
        log.info(
            f'loading from model_json={model_json}')
        model = keras_models.model_from_json(
            json.dumps(model_json))
    elif model_config:
        model = keras_models.Sequential()
        log.info(
            f'building '
            f'dnn num_features={num_features} '
            f'model_config={model_config}')
        for idx, node in enumerate(model_config['layers']):
            layer_type = node.get(
                'layer_type',
                'dense').lower()
            if layer_type == 'dense':
                if num_layers == 0:
                    model.add(
                        keras_layers.Dense(
                            int(node['num_neurons']),
                            input_dim=num_features,
                            kernel_initializer=node['init'],
                            activation=node['activation']))
                else:
                    model.add(
                        keras_layers.Dense(
                            int(node['num_neurons']),
                            kernel_initializer=node['init'],
                            activation=node['activation']))
            else:
                if layer_type == 'dropout':
                    model.add(
                        keras_models.Dropout(
                            float(node['rate'])))
            # end of supported model types
            num_layers += 1
        # end of all layers
    else:
        # https://machinelearningmastery.com/regression-tutorial-keras-deep-learning-library-python/  # noqa
        log.info(
            f'default dnn num_features={num_features}')
        model.add(
            keras_layers.Dense(
                8,
                input_dim=num_features,
                kernel_initializer='normal',
                activation='relu'))
        model.add(
            keras_layers.Dense(
                6,
                kernel_initializer='normal',
                activation='relu'))
        model.add(
            keras_layers.Dense(
                1,
                kernel_initializer='normal'))
    # end of building a regression dnn

    # if model was defined
    if model:
        log.info(
            f'compiling={compile_config}')
        # compile the model
        loss = compile_config.get(
            'loss',
            'mse')
        optimizer = compile_config.get(
            'optimizer',
            'adam')
        metrics = compile_config.get(
            'metrics',
            [
                'mse',
                'mae',
                'mape',
                'cosine'
            ])
        model.compile(
            loss=loss,
            optimizer=optimizer,
            metrics=metrics)
    else:
        log.error(
            f'failed building regression model={model}')
    # if could compile model

    return model
# end of build_regression_dnn
