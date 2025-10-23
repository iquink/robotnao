class MyClass(GeneratedClass):
    def __init__(self):
        GeneratedClass.__init__(self)

    def onLoad(self):
        try:
            self.motion = ALProxy("ALMotion")
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
            self.motion.setStiffnesses("Legs", 1.0)

            for i in range(6):
                # Левое колено вверх, правая нога и корпус ровно
                self.motion.angleInterpolation(
                    ["LHipPitch", "LKneePitch", "LAnklePitch", "RHipPitch", "RKneePitch", "RAnklePitch"],
                    [[0.0, -0.6], [0.0, 1.0], [0.0, -0.6], [0.0], [0.0], [0.0]],
                    [[0.5, 1.0], [0.5, 1.0], [0.5, 1.0], [1.0], [1.0], [1.0]],
                    True
                )
                time.sleep(0.5)
                # Левое колено вниз
                self.motion.angleInterpolation(
                    ["LHipPitch", "LKneePitch", "LAnklePitch"],
                    [[-0.6, 0.0], [1.0, 0.0], [-0.6, 0.0]],
                    [[0.5, 1.0], [0.5, 1.0], [0.5, 1.0]],
                    True
                )
                time.sleep(0.5)
                # Правое колено вверх, левая нога и корпус ровно
                self.motion.angleInterpolation(
                    ["RHipPitch", "RKneePitch", "RAnklePitch", "LHipPitch", "LKneePitch", "LAnklePitch"],
                    [[0.0, -0.6], [0.0, 1.0], [0.0, -0.6], [0.0], [0.0], [0.0]],
                    [[0.5, 1.0], [0.5, 1.0], [0.5, 1.0], [1.0], [1.0], [1.0]],
                    True
                )
                time.sleep(0.5)
                # Правое колено вниз
                self.motion.angleInterpolation(
                    ["RHipPitch", "RKneePitch", "RAnklePitch"],
                    [[-0.6, 0.0], [1.0, 0.0], [-0.6, 0.0]],
                    [[0.5, 1.0], [0.5, 1.0], [0.5, 1.0]],
                    True
                )
                time.sleep(0.5)

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