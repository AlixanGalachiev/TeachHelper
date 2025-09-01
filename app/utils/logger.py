import logging

logger = logging.getLogger("teachHelper")

logging.basicConfig(
	level=logging.INFO,
)

formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

logger = logging.getLogger("my_app")


file_handler = logging.FileHandler("app.log", encoding="utf-8")
file_handler.setLevel(logging.ERROR)
file_handler.setFormater(formatter)


console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)