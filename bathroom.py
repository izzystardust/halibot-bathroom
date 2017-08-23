# Bathroom halibot module
# Tracks how noxious the bathroom is

from halibot import HalModule, HalConfigurer, Message
import time



statuses = [
        {"condition": 5, "status": "Lowest state of readiness"},
        {"condition": 4, "status": "Increased intelligence watch and strengthened security measures"},
        {"condition": 3, "status": "Increase in force readiness above that required for normal readiness"},
        {"condition": 2, "status": "Next step to nuclear war"},
        {"condition": 1, "status": "Nuclear war is iminent"},
    ]

class Bathroom(HalModule):

    class Configurer(HalConfigurer):
        def configure(self):
            self.optionInt('period_length', prompt="Period in minutes for lowering status", default=12)

    # Called when the module is initialized
    #  Put any initialization logic here, instead of __init__()
    #  In this case, no initialization is needed, thus it is a no-op
    #  This is already defined in HalModule, so it can be excluded if not needed
    def init(self):
        self.status = 0
        self.last_set = time.time()

    def possibly_update(self, msg=None):
        now = time.time()
        elapsed = now - self.last_set
        periods = int(elapsed / (self.config.get('period_length')*60))

        if msg is not None:
            self.reply(msg, body="elapsed: %f, periods: %d"%(elapsed, periods))

        if periods > 0:
            self.last_set = now
            self.status = max(0, self.status-periods)

    def set(self, msg, to):
        try:
            to = int(to)
            if to not in range(1, 6):
                self.reply(msg, "valid range is 1 to 5")
                return
            self.last_set = time.time()
            self.status = 5-(to)
            self.reply(msg, body=statuses[self.status]["status"])
        except e:
            pass

    # Called when a new message from the Halibot base is received
    #  The `msg` argument is in the standard Halibot message format, regardless of the actual source
    #  Thus, even it was from IRC, XMPP, etc, it should have keys like "body", for the actual text.
    #  To where it comes from, check the "context" field.
    def receive(self, msg):
        # The "body" field should always be populated, thus this is a safe assumption.(otherwise, an agent isn't working properly!
        if msg.body.startswith("!bathroom"):
            self.possibly_update()
            words = msg.body.split()
            if len(words) < 2:
                self.reply(msg, body="set {1-5}, status")
                return

            if words[1].lower() == "status":
                self.reply(msg, body="CONDITION %d: %s" % (statuses[self.status]["condition"], statuses[self.status]["status"]))
            
            if words[1].lower() == "set":
                if len(words) < 3:
                    self.reply(msg, body="set to what.")
                    return
                self.set(msg, words[2])
