import torch

from yolo_detection import text_detection, yolo_result_to_boxes
from trOCR_utils import boxes_to_groups, combining_boxes
from transformers import GenerationConfig, TrOCRProcessor, VisionEncoderDecoderModel

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

    for group in groups:
        for box in group:
            x1, y1, x2, y2 = map(int, box)
            crop = image[y1:y2, x1:x2]
            word = recognize(crop)
            result += word + ' '

        result = result[:-1]
        result += '\n'

    result = result[:-1]
    return result



def recognize_text(img_path):
	yolo_result = text_detection(img_path, conf=0.3)[0]
	yolo_boxes = yolo_result_to_boxes(yolo_result)
	yolo_groups = boxes_to_groups(yolo_boxes)
	combined_groups = combining_boxes(yolo_groups)

	return recognize_text(img_path, combined_groups)