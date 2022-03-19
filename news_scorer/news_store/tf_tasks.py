import logging

import numpy as np
import tensorflow as tf

logger = logging.getLogger(__name__)


def dummy_task_tf():
    print("pass")


def array_generator(qs, cased):
    data = []

    for row in list(qs.values('title', 'body')):
        try:
            title = row['title']
        except:
            title = ''

        try:
            body = row['body']
        except:
            body = ''

        sentence = f'{title}. {body}'
        if cased is False:
            sentence = sentence.lower()

        data.append(sentence)

    data_array = np.array(data)

    sentence_array = data_array[:]
    label_array = None
    # print(sentence_array)
    return sentence_array, label_array


def dataset_generator(tokenizer, sentence_array, batch_size):
    logger.info(f"Tokenizing array...")
    raw_tokenize_array = tokenizer(list(sentence_array), padding=True, truncation=True, max_length=512,
                                   return_tensors="tf")
    print(raw_tokenize_array)
    tokenize_array = raw_tokenize_array
    logger.info(f"Generating tensorflow dataset")

    tf_dataset = tf.data.Dataset.from_tensor_slices((
        dict(tokenize_array), None))
    tf_dataset = tf_dataset.batch(batch_size)
    return tf_dataset
