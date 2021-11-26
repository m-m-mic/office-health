# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils

import os
import boto3

from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput



from ask_sdk_model import Response

from ask_sdk_dynamodb.adapter import DynamoDbAdapter


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ddb_region = os.environ.get('DYNAMODB_PERSISTENCE_REGION')
ddb_table_name = os.environ.get('DYNAMODB_PERSISTENCE_TABLE_NAME')

ddb_resource = boto3.resource('dynamodb', region_name=ddb_region)
dynamodb_adapter = DynamoDbAdapter(table_name=ddb_table_name, create_table=False, dynamodb_resource=ddb_resource)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        

        attr = handler_input.attributes_manager.persistent_attributes
        #worktime: wie lang insgesamt gearbeitet wird; breaks: wieviele breaks genommen werden; 
        #exercisenum: wieviele übungen in einer break gemacht wurden; breaknum: wieviele breaks schon während der arbeit gemacht wurden;
        #workintervt: dauer der arbeits intervalle
        attr['exercisenum'] = 0
        attr['worktime'] = 0
        attr['breaks'] = 0 
        attr['breaknum'] = 0
        attr['workintervt'] = 0
        
        handler_input.attributes_manager.save_persistent_attributes()
            
        speak_output = "Hallo, ich bin Ihr Office Health Assistent! Ich sorge dafür, dass Sie beim Arbeiten weiterhin aktiv und gesund bleiben. Für wie lange wollen Sie heute arbeiten?"
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class runtimeHandler(AbstractRequestHandler):
    """Handler for runtime Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("runtime")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Wie häufig möchten Sie währenddessen Health Breaks nehmen?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                #.ask("Okay, wie viel Stunden möchtest du also arbeiten?")
                .response
        )

class intervalsHandler(AbstractRequestHandler):
    """Handler for intervals Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("intervals")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Wenn ja, dann sag einfach: Los."

        return (
            handler_input.response_builder
                .speak(speak_output)
                #.ask("Wie viele Pausen möchtest du also nehmen?")
                .response
        )

class session_initHandler(AbstractRequestHandler):
    """Handler for session_init Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("session_init")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Ihre erste Health Break beginnt in 20 Sekunden. Wenn du bereit bist, sag: Ich bin bereit!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                #.ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class workout_explanationHandler(AbstractRequestHandler):
    """Handler for workout_explanation Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("workout_explanation")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Deine nächste Übung heißt Hampelmänner. (Hier Hampelmänner Übungsanleitung einfügen) Wir wiederholen die Übung 15 mal. Soll ich die Anleitung wiederholen oder kann es los gehen?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                #.ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class workout_initHandler(AbstractRequestHandler):
    """Handler for workout_init Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("workout_init")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attr = handler_input.attributes_manager.persistent_attributes
        outp = ""
        if not attr:
            attr['exercisenum'] = 0
        attr['exercisenum'] += 1
        
        outp = "Dann, auf die Plätze, fertig, los! 1 (Sprechpause), 2 (Sprechpause), 3 (Sprechpause) ..., 15 (Sprechpause)."#" Die Übung hast Du hinter dir! Jetzt hast Du 15 Sekunden Pause. (15 Sekunden Pause hier einfügen). Wenn du bereit für die nächste Übung bist sag: Nächste Übung."

        if attr['exercisenum'] < 3:
            if attr['exercisenum'] == 1:
                outp += ("Die erste Übung hast du geschafft, wenn du bereitfür die Nächste bist sag Bescheid")
            else:
                outp += ("Super. noch Eine. Sag wieder wenn du bereit bist")
        else:
            outp += ("So das wars erstmal. jetzt erstmal zurück zur arbeit. sag los wenn du beginnst zu arbeiten")
            attr['exercisenum'] = 0
            
        handler_input.attributes_manager.save_persistent_attributes()
        
        #testing
        speak_output = outp
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                #.ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class workout_finishHandler(AbstractRequestHandler):
    """Handler for workout_finish Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("workout_finish")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Du hast deine Health Break geschafft!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                #.ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class BackToWorkHandler(AbstractRequestHandler):
    """Handler for BackToWork Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("BackToWork")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Du hast jetzt 1 Minute lang Zeit, dich zu erholen, bevor es weiter an die Arbeit geht. (1 Minute Pause hier einfügen) Ich melde mich bald wieder."

        return (
            handler_input.response_builder
                .speak(speak_output)
                #.ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class session_finishHandler(AbstractRequestHandler):
    """Handler for session_finish Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("session_finish")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Das wars für heute! Super, dass Du mitgemacht hast."

        return (
            handler_input.response_builder
                .speak(speak_output)
                #.ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure. You can say Hello or Help. What would you like to do?"
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = CustomSkillBuilder(persistence_adapter = dynamodb_adapter)


sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(runtimeHandler())
sb.add_request_handler(intervalsHandler())
sb.add_request_handler(session_initHandler())
sb.add_request_handler(workout_explanationHandler())
sb.add_request_handler(workout_initHandler())
sb.add_request_handler(workout_finishHandler())
sb.add_request_handler(BackToWorkHandler())
sb.add_request_handler(session_finishHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()