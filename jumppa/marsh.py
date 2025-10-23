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

            # Цикл для марша на месте
            self.logger.info("Starting march exercise loop")
            numbers = ["yksi", "kaksi", "kolme", "neljä", "viisi", "kuusi", "seitsemän", "kahdeksan", "yhdeksän", "kymmenen"]
            for i, number in enumerate(numbers, 1):
                self.logger.info("Saying number %d: %s" % (i, number))
                self.tts.say(number)

                # Поднимаем левое колено
                self.logger.info("Raising left knee %d" % i)
                names = ["LHipPitch", "LKneePitch", "LAnklePitch"]
                keys = [[0.0, -0.6], [0.0, 1.0], [0.0, -0.6]]
                times = [[0.5, 3.0], [0.5, 3.0], [0.5, 3.0]]
                self.motion.angleInterpolation(names, keys, times, True)

                # Пауза и опускаем левое колено
                time.sleep(1.0)
                self.logger.info("Lowering left knee %d" % i)
                names = ["LHipPitch", "LKneePitch", "LAnklePitch"]
                keys = [[-0.6, 0.0], [1.0, 0.0], [-0.6, 0.0]]
                times = [[0.5, 3.0], [0.5, 3.0], [0.5, 3.0]]
                self.motion.angleInterpolation(names, keys, times, True)

                # Поднимаем правое колено
                self.logger.info("Raising right knee %d" % i)
                names = ["RHipPitch", "RKneePitch", "RAnklePitch"]
                keys = [[0.0, -0.6], [0.0, 1.0], [0.0, -0.6]]
                times = [[0.5, 3.0], [0.5, 3.0], [0.5, 3.0]]
                self.motion.angleInterpolation(names, keys, times, True)

                # Пауза и опускаем правое колено
                time.sleep(1.0)
                self.logger.info("Lowering right knee %d" % i)
                names = ["RHipPitch", "RKneePitch", "RAnklePitch"]
                keys = [[-0.6, 0.0], [1.0, 0.0], [-0.6, 0.0]]
                times = [[0.5, 3.0], [0.5, 3.0], [0.5, 3.0]]
                self.motion.angleInterpolation(names, keys, times, True)

                # Короткая пауза между повторениями
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