from app.models.model_work import Work
import torch
import cv2
import os
import requests
import numpy as np

from yolo_detection import text_detection, yolo_result_to_boxes
from trOCR_utils import boxes_to_groups, show_errors
from transformers import GenerationConfig, TrOCRProcessor, VisionEncoderDecoderModel

from app.utils.logger import logger


def beam_search(model, processor):
	model.config.decoder_start_token_id = processor.tokenizer.cls_token_id
	model.config.pad_token_id = processor.tokenizer.pad_token_id
	model.config.vocab_size = model.config.decoder.vocab_size


	# set beam search parameters
	generation_config = GenerationConfig(
		max_length=64,
		early_stopping=True,
		no_repeat_ngram_size=3,
		length_penalty=2.0,
		num_beams=4
	)
	model.generation_config = generation_config

	model.generation_config.eos_token_id = processor.tokenizer.sep_token_id
	model.generation_config.decoder_start_token_id = processor.tokenizer.cls_token_id
	model.generation_config.pad_token_id = processor.tokenizer.pad_token_id


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_name = "Daniil-Domino/trocr-base-ru-dialectic"


text_processor = TrOCRProcessor.from_pretrained(model_name)
text_recognition = VisionEncoderDecoderModel.from_pretrained(model_name)

beam_search(text_recognition, text_processor)
text_recognition.to(device)



def recognize(image):
	pixel_values = text_processor(images=image, return_tensors="pt").pixel_values.to(device)

	generated_ids = text_recognition.generate(pixel_values)
	generated_text = text_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
	return generated_text



def recognize_text(image, groups):
	result = ''
	metadata: dict[str, list]= {}

	for group in groups:
		for box in group:
			x1, y1, x2, y2 = map(int, box)
			crop = image[y1:y2, x1:x2]
			word = recognize(crop)
			result += word + ' '
			if word in metadata:
				metadata[word].append(box)
			else:
				metadata[word] = [box]

		result = result[:-1]
		result += '\n'

	result = result[:-1]
	return {
		"metadata": metadata,
		"text": result
	}


def handle_images(images_paths: list[str]) -> list[dict[str, np.ndarray]]:
	results = []
	for image_path in images_paths:
		try:
			image = cv2.imread(image_path)
			image = cv2.resize(image, (1280, 900))

			yolo_result = text_detection(image, conf=0.3)[0]
			yolo_boxes = yolo_result_to_boxes(yolo_result)
			yolo_groups = boxes_to_groups(yolo_boxes)

			recognition_result = recognize_text(image, yolo_groups)

			finded_errors = check_text(recognition_result['text'])
			if len(finded_errors) > 0:
				error_boxes = []
				for speller_data in finded_errors:
					if speller_data['word'] in recognition_result['metadata']:
						error_boxes.append(recognition_result['metadata'][speller_data['word']])
				
				results.append({image_path: show_errors(image, error_boxes)})

		except Exception as e:
			logger.error(f"{e} картинка - {image_path}", exc_info=True)


def check_text(text: str):
	try:
		url = "https://speller.yandex.net/services/spellservice.json/checkText"
		params = {'text': text}

		response = requests.get(url, params=params)
		return response.json()

	except Exception as e:
		raise Exception(f"Ошибка запроса Яндекс спеллера: {response.status_code}")