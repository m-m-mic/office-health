# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
import ask_sdk_model

import os
import boto3

#damit wir auf die json Datei zugreifen können
import json
#random modul
import random

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
        
        #attribute in denen die 3 verschiedenen zufälligen übungen während einem workout gespeichert werden
        attr['stretch_1'] = ['', 0, False, '']
        attr['sport'] = ['', 0, False, '']
        attr['stretch_2'] = ['', 0, False, '']
        
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
        # logger.info(handler_input.request_envelope.request.intent.confirmation_status)
        # hier wird abgefragt, ob der confirmation_status des Intents auf CONFIRMED oder DENIED steht; wenn er auf DENIED steht wird die Frage wiederholt
        if handler_input.request_envelope.request.intent.confirmation_status == ask_sdk_model.intent_confirmation_status.IntentConfirmationStatus.CONFIRMED:
            speak_output = "Wie häufig möchten Sie währenddessen Health Breaks nehmen?"
        else:
            speak_output = "Okay, wie lange willst du heute arbeiten?"
        
        # type: (HandlerInput) -> Response
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class intervalsHandler(AbstractRequestHandler):
    """Handler for intervals Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("intervals")(handler_input)

    def handle(self, handler_input):
        # logger.info(handler_input.request_envelope.request.intent.confirmation_status)
        if handler_input.request_envelope.request.intent.confirmation_status == ask_sdk_model.intent_confirmation_status.IntentConfirmationStatus.CONFIRMED:
            speak_output = "Bist du bereit? Wenn ja, sag: Los!"
        else:
            speak_output = "Okay, wie viele Pausen willst du also nehmen?"
        
        # type: (HandlerInput) -> Response
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class session_initHandler(AbstractRequestHandler):
    """Handler for session_init Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("session_init")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        exercisesDict = json.load(open('exercise.json', 'r'))
        #liste aller dehnübungen
        stretches = exercisesDict['stretch']
        #liste aller sportübungen
        sports = exercisesDict['sport']
        
        #persistent attributes laden
        attr = handler_input.attributes_manager.persistent_attributes
        #var für die jeweiligen längen der listen
        stl = len(stretches)
        spl = len(sports)
        
        #zufällige indizes für die listen
        r1 = random.randrange(0, stl)
        r2 = random.randrange(0, spl)
        r3 = r1
        while r3 == r1:
            r3 = random.randrange(0, stl)
            
        #funktion die anhand der zufälligen Zahlen eine Übung in den attributen speichert
        def listifyExercise(attrName, exList, rn):
            attr[attrName][0] = exList[rn]['name']
            attr[attrName][1] = int(exList[rn]['dauer'])
            attr[attrName][2] = exList[rn]['seitenwechsel'] == 'TRUE'
            attr[attrName][3] = exList[rn]['beschreibung']
        
        listifyExercise('stretch_1', stretches, r1)
        listifyExercise('sport', sports, r2)
        listifyExercise('stretch_2', stretches, r3)
        
        speak_output = "Ihre erste Health Break beginnt in 20 Sekunden. Wenn du bereit bist, sag: Ich bin bereit!" + ' ' + attr['stretch_1'][0] + ' ' + attr['sport'][0] + ' ' + attr['stretch_2'][0]

        
        reprompt_output = "Sag ich bin bereit, wenn du bereit bist!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(reprompt_output)
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
        reprompt_output = "Willst du, dass ich die Anleitung wiederhole? Oder soll es losgehen?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(reprompt_output)
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
                outp += ("Die erste Übung hast du geschafft, wenn du bereit für die nächste Übung bist, sag Bescheid!")
            else:
                outp += ("Super. Noch eine Übung! Sag nächste Übung, wenn du weiter machen willst.")
        else:
            outp += ("So das wars erstmal. Du hast jetzt 1 Minute lang Zeit, dich zu erholen, bevor es weiter an die Arbeit geht. (Hier eine Minute Pause einzufügen) Die Pause ist vorüber. Sag weiter, wenn Sie zurück an die Arbeit wollen. Sag fertig, wenn du das Programm beenden willst.")
            attr['exercisenum'] = 0
            
        handler_input.attributes_manager.save_persistent_attributes()
        
        #testing
        speak_output = outp
        reprompt_output = outp
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(reprompt_output)
                .response
        )

class workout_finishHandler(AbstractRequestHandler):
    """Handler for workout_finish Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("workout_finish")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Viel Spaß bei der Arbeit!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class BackToWorkHandler(AbstractRequestHandler):
    """Handler for BackToWork Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("BackToWork")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = " (1 Minute Pause hier einfügen)"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("Ich melde mich bald wieder.")
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
                .ask(speak_output)
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
