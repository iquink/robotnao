class MyClass(GeneratedClass):
    def __init__(self):
        GeneratedClass.__init__(self)

    def onLoad(self):
        # Инициализация прокси для NAOqi
        try:
            self.motion = ALProxy("ALMotion")  # Прокси для движения
            self.tts = ALProxy("ALTextToSpeech")  # Прокси для речи
            self.autonomous = ALProxy("ALAutonomousLife")  # Прокси для Autonomous Life
            self.autonomous.setState("disabled")  # Отключаем Autonomous Life
            self.tts.setLanguage("Finnish")  # Устанавливаем финский язык
            self.behavior = ALProxy("ALBehaviorManager")  # Для остановки поведений
        except Exception as e:
            self.logger.info("Error initializing proxies: " + str(e))

    def onUnload(self):
        # Очистка: перевод робота в режим отдыха
        try:
            self.motion.wbEnable(False)  # Отключаем balancer
            self.motion.rest()  # Засыпаем робота
        except Exception as e:
            self.logger.info("Error during rest: " + str(e))

    def onInput_onStart(self):
        import time
        try:
            # Просыпаемся и активируем жёсткость ног и рук
            self.logger.info("Waking up robot")
            self.motion.wakeUp()
            self.motion.setStiffnesses("Legs", 1.0)  # Активируем моторы ног
            self.motion.setStiffnesses("Arms", 1.0)  # Активируем моторы рук

            # Включаем whole body balancer для стабильности
            self.motion.wbEnable(True)
            self.motion.wbFootState("Plane", "Legs")  # Фиксируем ступни на плоскости
            self.motion.wbGoToBalance("Legs", 1.0)  # Переходим к балансу на ногах

            # Говорим "Начинаем упражнение марш на месте"
            self.logger.info("Saying start message")
            self.tts.say("Naamne harjoituksen marssi paikallaan")

            # Пауза 2 секунды
            time.sleep(2.0)

            # Говорим "Начали"
            self.logger.info("Saying 'Aloitetaan'")
            self.tts.say("Aloitetaan")

            # Пауза 1 секунда
            time.sleep(1.0)

            # Махи руками
            self.logger.info("Starting arm swings")
            self.tts.say("Siirrymme käsien heilutuksiin")  # "Переходим к махам руками"
            time.sleep(2.0)
            for i in range(1, 11):  # 10 повторений
                self.logger.info("Swinging arms, repetition %d" % i)
                self.tts.say(str(i))

                # Левая рука вверх (ShoulderPitch), правая опускается вниз
                self.logger.info("Raising left arm %d" % i)
                names = ["LShoulderPitch", "RShoulderPitch"]
                keys = [[0.0, -1.5], [0.0, 1.5]]  # -1.5 рад (~86°) вверх, правая опускается вниз
                times = [[0.5, 2.0], [0.5, 2.0]]
                self.motion.angleInterpolation(names, keys, times, True)

                # Пауза
                time.sleep(1.0)

                # Левая рука вниз, правая вверх
                self.logger.info("Lowering left, raising right arm %d" % i)
                names = ["LShoulderPitch", "RShoulderPitch"]
                keys = [[-1.5, 1.5], [1.5, -1.5]]  # Левая опускается вниз, правая поднимается вверх
                times = [[0.5, 2.0], [0.5, 2.0]]
                self.motion.angleInterpolation(names, keys, times, True)

                # Пауза
                time.sleep(1.0)

            # Завершаем и засыпаем
            self.logger.info("Exercise completed, resting robot")
            self.motion.wbEnable(False)  # Отключаем balancer
            self.motion.rest()

            # Активируем выход onStopped
            self.onStopped()
        except Exception as e:
            self.logger.info("Error during execution: " + str(e))
            self.motion.wbEnable(False)
            self.motion.rest()  # Засыпаем в случае ошибки
            self.onStopped()

    def onInput_onStop(self):
        # Остановка всех движений и поведений перед unload
        try:
            self.motion.stopMove()  # Остановить текущие движения
            self.behavior.stopAllBehaviors()  # Остановить все поведения
            self.motion.wbEnable(False)  # Отключаем balancer
        except Exception as e:
            self.logger.info("Error stopping behaviors: " + str(e))
        self.onUnload()  # Очистка
        self.onStopped()  # Активируем выход