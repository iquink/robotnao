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

            # Говорим "Начинаем упражнение наклоны туловища"
            self.logger.info("Saying start message")
            self.tts.say("Naamne harjoituksen vartalon kallistukset")

            # Пауза 2 секунды
            time.sleep(2.0)

            # Говорим "Начали"
            self.logger.info("Saying 'Aloitetaan'")
            self.tts.say("Aloitetaan")

            # Пауза 1 секунда
            time.sleep(1.0)

            # Наклоны туловища
            self.logger.info("Starting body tilts")
            self.tts.say("Siirrymme vartalon kallistuksiin")  # "Переходим к наклонам туловища"
            time.sleep(2.0)
            for i in range(1, 11):  # 10 повторений
                self.logger.info("Tilting body, repetition %d" % i)
                self.tts.say(str(i))

                # Наклон вперёд (сгибание корпуса и рук)
                self.logger.info("Tilting forward %d" % i)
                names = ["LHipPitch", "RHipPitch", "LShoulderPitch", "RShoulderPitch"]
                keys = [[0.0, -0.65], [0.0, -0.65], [0.0, 1.2], [0.0, 1.2]]  # Наклон вперёд на -0.65 рад (~-37°), руки вниз на 1.2 рад (~69°)
                times = [[0.5, 3.0], [0.5, 3.0], [0.5, 3.0], [0.5, 3.0]]
                self.motion.angleInterpolation(names, keys, times, True)

                # Пауза для наблюдения
                time.sleep(3.0)

                # Возвращение в вертикальное положение с подъёмом рук
                self.logger.info("Returning to upright %d" % i)
                names = ["LHipPitch", "RHipPitch", "LShoulderPitch", "RShoulderPitch"]
                keys = [[-0.65, 0.0], [-0.65, 0.0], [1.2, -1.57], [1.2, -1.57]]  # Корпус выпрямляется, руки наверх
                times = [[0.5, 3.0], [0.5, 3.0], [0.5, 3.0], [0.5, 3.0]]
                self.motion.angleInterpolation(names, keys, times, True)

                # Пауза
                time.sleep(1.0)

                # Возврат рук в нейтральное положение для следующего повторения
                self.logger.info("Returning arms to neutral for next repetition %d" % i)
                names = ["LShoulderPitch", "RShoulderPitch"]
                keys = [[-1.57, 0.0], [-1.57, 0.0]]
                times = [[0.5, 1.0], [0.5, 1.0]]
                self.motion.angleInterpolation(names, keys, times, True)

                # Пауза перед следующим повторением
                time.sleep(0.5)

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