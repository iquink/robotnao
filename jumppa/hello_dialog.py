class MyClass(GeneratedClass):
    def __init__(self):
        GeneratedClass.__init__(self)

    def onLoad(self):
        try:
            self.motion = ALProxy("ALMotion")
            self.tts = ALProxy("ALTextToSpeech")
            self.speech = ALProxy("ALSpeechRecognition")
        except Exception as e:
            self.logger.info("Error initializing proxies: " + str(e))

    def onUnload(self):
        try:
            self.motion.rest()
        except Exception as e:
            self.logger.info("Error during rest: " + str(e))

    def onInput_onStart(self):
        import time
        try:
            self.motion.wakeUp()
            self.motion.setStiffnesses("Arms", 1.0)

            # Поднимаем правую руку
            self.motion.angleInterpolation("RShoulderPitch", [-1.0], [1.0], True)

            # Приветствие и вопрос
            self.tts.say("Terve! mitä kuuluu?")

            # Настройка распознавания речи (финский, простые ответы)
            vocabulary = ["hyvää", "huonoa", "kiitos", "ok", "väsynyt", "iloista", "surullinen"]
            self.speech.setLanguage("Finnish")
            self.speech.setVocabulary(vocabulary, False)
            self.speech.subscribe("hello_test")

            # Ожидание ответа (до 5 секунд)
            response = None
            start = time.time()
            while time.time() - start < 5:
                data = self.getData("WordRecognized")
                if data and isinstance(data, list) and data[1] > 0.4:
                    response = data[0]
                    break
                time.sleep(0.1)

            self.speech.unsubscribe("hello_test")

            # Повторить ответ пользователя
            if response:
                self.tts.say("Sinä sanoit: " + response)
            else:
                self.tts.say("En kuullut vastausta.")

            # Опустить руку
            self.motion.angleInterpolation("RShoulderPitch", [1.5], [1.0], True)

            self.motion.rest()
            self.onStopped()
        except Exception as e:
            self.logger.info("Error during execution: " + str(e))
            self.motion.rest()
            self.onStopped()

    def onInput_onStop(self):
        try:
            self.motion.rest()
        except Exception as e:
            self.logger.info("Error during stop: " + str(e))
        self.onStopped()